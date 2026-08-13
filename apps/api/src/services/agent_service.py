"""
Genesis API — Agent Service

Manages the lifecycle of AI agent invocations within the governance framework.

Responsibilities:
    - Verify agent is registered in agent_registry
    - Enforce risk-level approval gates before dispatch
    - Create and update ai_run records (mandatory for every AI operation)
    - Dispatch tasks to NATS for worker execution
    - Retrieve and list agent runs

This service does NOT:
    - Contain agent logic (that lives in the worker)
    - Handle HTTP concerns
    - Invoke LLMs directly (that is llm_service.py)

Architecture (per ADR-005):
    API service  →  creates ai_run  →  publishes NATS message
    Worker       →  receives message → executes agent → updates ai_run

Raises:
    NotFoundError       — agent_key not found in registry
    PolicyViolationError — agent is disabled or not authorized
    ApprovalRequiredError — risk_level requires human approval
"""

import json
import uuid
from datetime import UTC, datetime

import nats
import sqlalchemy as sa
from sqlmodel import Session, select

import genesis_db
from core.config import settings
from core.errors import ApprovalRequiredError, ErrorCode, NotFoundError, PolicyViolationError
from core.logging import get_logger

logger = get_logger(__name__)


# =============================================================================
# NATS subject convention (per ADR-005)
# =============================================================================

_NATS_SUBJECT_PREFIX = "genesis.agents"


def _agent_subject(agent_type: str) -> str:
    """Return the NATS subject for a given agent type."""
    return f"{_NATS_SUBJECT_PREFIX}.{agent_type.lower()}"


# =============================================================================
# Agent lookup
# =============================================================================


def get_agent_by_key(session: Session, agent_key: str) -> genesis_db.AgentRegistry:
    """
    Retrieve a registered agent by its stable key.

    Raises:
        NotFoundError: If agent_key is not in agent_registry or is inactive.
    """
    agent = session.exec(
        select(genesis_db.AgentRegistry).where(
            genesis_db.AgentRegistry.agent_key == agent_key,
            genesis_db.AgentRegistry.is_active == True,  # noqa: E712
        )
    ).first()

    if not agent:
        raise NotFoundError(
            f"Agent '{agent_key}' is not registered or is inactive.",
            code=ErrorCode.AGENT_NOT_FOUND,
        )
    return agent


def list_agents(session: Session) -> list[genesis_db.AgentRegistry]:
    """Return all active registered agents."""
    return list(
        session.exec(
            select(genesis_db.AgentRegistry).where(
                genesis_db.AgentRegistry.is_active == True  # noqa: E712
            )
        ).all()
    )


# =============================================================================
# AI Run management
# =============================================================================


def create_ai_run(
    session: Session,
    *,
    run_type: str,
    agent: genesis_db.AgentRegistry | None = None,
    project_id: uuid.UUID | None = None,
    triggered_by_user_id: uuid.UUID | None = None,
    input_summary: dict | None = None,
) -> genesis_db.AIRun:
    """
    Create an ai_run record before any agent execution begins.

    This is MANDATORY for every AI operation (per AI_GOVERNANCE.md §7).
    Creates the record in PENDING state before dispatch.

    Args:
        session: Database session.
        run_type: Semantic name for this operation (e.g., 'requirement_extraction').
        agent: AgentRegistry instance (if agent-driven).
        project_id: Associated project.
        triggered_by_user_id: User who triggered this run.
        input_summary: Non-sensitive summary of inputs. Never include PII or secrets.

    Returns:
        The newly created AIRun record.
    """
    run = genesis_db.AIRun(
        run_type=run_type,
        status=genesis_db.AIRunStatus.PENDING,
        agent_id=agent.id if agent else None,
        model_id=agent.model_id if agent else None,
        prompt_id=agent.system_prompt_id if agent else None,
        project_id=project_id,
        triggered_by_user_id=triggered_by_user_id,
        input_summary=input_summary,
    )
    session.add(run)
    session.commit()
    session.refresh(run)

    logger.info(
        "AI run created",
        extra={
            "run_id": str(run.id),
            "run_type": run_type,
            "agent_key": agent.agent_key if agent else None,
            "project_id": str(project_id) if project_id else None,
        },
    )
    return run


def update_ai_run_status(
    session: Session,
    run: genesis_db.AIRun,
    status: genesis_db.AIRunStatus,
    *,
    output_summary: dict | None = None,
    error_message: str | None = None,
    tools_used: list | None = None,
    prompt_tokens: int | None = None,
    completion_tokens: int | None = None,
    estimated_cost_usd: float | None = None,
) -> genesis_db.AIRun:
    """
    Update an ai_run record after execution completes or fails.

    Calculates duration_ms automatically from started_at if available.
    """
    now = datetime.now(UTC)

    run.status = status
    if status == genesis_db.AIRunStatus.RUNNING and run.started_at is None:
        run.started_at = now
    if status in (
        genesis_db.AIRunStatus.COMPLETED,
        genesis_db.AIRunStatus.FAILED,
        genesis_db.AIRunStatus.CANCELLED,
    ):
        run.completed_at = now
        if run.started_at:
            run.duration_ms = int((now - run.started_at).total_seconds() * 1000)

    if output_summary is not None:
        run.output_summary = output_summary
    if error_message is not None:
        run.error_message = error_message[:2000]  # Enforce field limit
    if tools_used is not None:
        run.tools_used = tools_used
    if prompt_tokens is not None:
        run.prompt_tokens = prompt_tokens
    if completion_tokens is not None:
        run.completion_tokens = completion_tokens
        run.total_tokens = (run.prompt_tokens or 0) + completion_tokens
    if estimated_cost_usd is not None:
        run.estimated_cost_usd = estimated_cost_usd

    session.add(run)
    session.commit()
    session.refresh(run)

    logger.info(
        "AI run updated",
        extra={
            "run_id": str(run.id),
            "status": status,
            "duration_ms": run.duration_ms,
        },
    )
    return run


def get_ai_run(session: Session, run_id: uuid.UUID) -> genesis_db.AIRun:
    """
    Retrieve an AI run record by ID.

    Raises:
        NotFoundError: If run not found.
    """
    run = session.get(genesis_db.AIRun, run_id)
    if not run:
        raise NotFoundError("AI run not found.", code=ErrorCode.NOT_FOUND)
    return run


def list_ai_runs(
    session: Session,
    project_id: uuid.UUID,
    limit: int = 50,
    offset: int = 0,
) -> list[genesis_db.AIRun]:
    """Return AI run records for a project, most recent first."""
    return list(
        session.exec(
            select(genesis_db.AIRun)
            .where(genesis_db.AIRun.project_id == project_id)
            .order_by(sa.col(genesis_db.AIRun.created_at).desc())
            .limit(limit)
            .offset(offset)
        ).all()
    )


# =============================================================================
# Risk-level enforcement (per AI_GOVERNANCE.md §4.3)
# =============================================================================


def _check_risk_policy(agent: genesis_db.AgentRegistry) -> None:
    """
    Enforce risk-level policy before dispatch.

    LOW / MEDIUM: allowed without approval (MEDIUM is audit-logged automatically via ai_run).
    HIGH: requires explicit human approval — raises ApprovalRequiredError.
    CRITICAL: requires synchronous human-in-the-loop — raises ApprovalRequiredError.

    Raises:
        PolicyViolationError: If agent requires_approval but approval check fails.
        ApprovalRequiredError: If risk level mandates approval before execution.
    """
    risk = agent.risk_level

    if risk in (genesis_db.AgentRiskLevel.HIGH, genesis_db.AgentRiskLevel.CRITICAL):
        if agent.requires_approval:
            raise ApprovalRequiredError(
                f"Agent '{agent.agent_key}' has risk_level={risk} and requires human "
                "approval before execution. Please review and approve the pending AI run."
            )


# =============================================================================
# Approval processing
# =============================================================================


def process_approval(
    session: Session,
    run: genesis_db.AIRun,
    *,
    decision: str,
    approver_user_id: uuid.UUID,
) -> genesis_db.AIRun:
    """
    Process a human approval or rejection for a pending AI run.

    Args:
        session: Database session.
        run: The AIRun in APPROVAL_REQUIRED state.
        decision: 'approve' or 'reject'.
        approver_user_id: ID of the user making the decision.

    Returns:
        Updated AIRun with new approval_state.

    Raises:
        PolicyViolationError: If run is not in APPROVAL_REQUIRED state.
    """
    if run.status != genesis_db.AIRunStatus.APPROVAL_REQUIRED:
        raise PolicyViolationError(
            f"Cannot approve/reject run {run.id}: current status is {run.status}."
        )

    if decision == "approve":
        run.approval_state = "approved"
        run.status = genesis_db.AIRunStatus.APPROVED
    elif decision == "reject":
        run.approval_state = "rejected"
        run.status = genesis_db.AIRunStatus.REJECTED
    else:
        raise PolicyViolationError(f"Invalid decision '{decision}'. Must be 'approve' or 'reject'.")

    run.approved_by_user_id = approver_user_id

    session.add(run)
    session.commit()
    session.refresh(run)

    logger.info(
        "AI run approval processed",
        extra={
            "run_id": str(run.id),
            "decision": decision,
            "approver_user_id": str(approver_user_id),
        },
    )
    return run


# =============================================================================
# Agent dispatch (per ADR-005 — NATS-based)
# =============================================================================


async def dispatch_agent(
    session: Session,
    *,
    agent_key: str,
    project_id: uuid.UUID,
    triggered_by_user: genesis_db.User,
    run_type: str,
    task_id: uuid.UUID | None = None,
    context: dict | None = None,
) -> genesis_db.AIRun:
    """
    Dispatch an agent task via NATS and create the governing ai_run record.

    Flow:
        1. Look up agent in registry (raises NotFoundError if missing/inactive)
        2. Enforce risk-level policy (raises ApprovalRequiredError if needed)
        3. Create ai_run record in PENDING state
        4. Publish task to NATS subject genesis.agents.<agent_type>
        5. Return ai_run to caller (status=PENDING)

    The worker picks up the NATS message, updates status to RUNNING,
    executes the agent, and updates status to COMPLETED/FAILED.

    Args:
        session: Database session.
        agent_key: Stable agent identifier from agent_registry.
        project_id: Project this agent run belongs to.
        triggered_by_user: User whose action triggered this dispatch.
        run_type: Semantic name for this operation (e.g., 'requirement_extraction').
        task_id: Optional ImplementationTask this run is executing.
        context: Non-sensitive context payload for the worker.

    Returns:
        The newly created AIRun record (status=PENDING).
    """
    agent = get_agent_by_key(session, agent_key)

    # Enforce governance policy before creating any record
    _check_risk_policy(agent)

    # Create ai_run BEFORE dispatch (mandatory per AI_GOVERNANCE.md §7.1)
    input_summary: dict = {
        "agent_key": agent_key,
        "project_id": str(project_id),
        "run_type": run_type,
    }
    if task_id:
        input_summary["task_id"] = str(task_id)

    run = create_ai_run(
        session,
        run_type=run_type,
        agent=agent,
        project_id=project_id,
        triggered_by_user_id=triggered_by_user.id,
        input_summary=input_summary,
    )

    # Publish to NATS (fire-and-forget; worker processes asynchronously)
    try:
        nc = await nats.connect(settings.nats_url)
        payload = {
            "run_id": str(run.id),
            "agent_key": agent_key,
            "agent_type": agent.agent_type,
            "project_id": str(project_id),
            "task_id": str(task_id) if task_id else None,
            "run_type": run_type,
            "allowed_tools": agent.allowed_tools or [],
            "max_execution_seconds": agent.max_execution_seconds,
            "context": context or {},
        }
        subject = _agent_subject(agent.agent_type)
        await nc.publish(subject, json.dumps(payload).encode())
        await nc.drain()

        logger.info(
            "Agent task dispatched to NATS",
            extra={
                "run_id": str(run.id),
                "subject": subject,
                "agent_key": agent_key,
            },
        )
    except Exception as exc:
        # Dispatch failed — mark run as failed without losing the record
        update_ai_run_status(
            session,
            run,
            genesis_db.AIRunStatus.FAILED,
            error_message=f"NATS dispatch failed: {exc!s}",
        )
        logger.error(
            "Agent dispatch failed",
            extra={"run_id": str(run.id), "error": str(exc)},
        )
        raise

    return run
