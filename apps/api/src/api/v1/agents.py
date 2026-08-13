"""
Genesis API — Agent & AI Run Routes

Handles HTTP for agent invocation and AI run management.
All business logic delegates to agent_service.

Routes:
    GET    /api/v1/agents
    GET    /api/v1/agents/{agent_id}
    POST   /api/v1/agents/invoke
    GET    /api/v1/projects/{project_id}/runs
    GET    /api/v1/projects/{project_id}/runs/{run_id}
    POST   /api/v1/runs/{run_id}/approve
    POST   /api/v1/runs/{run_id}/reject
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends
from sqlmodel import Session

import genesis_db
from genesis_db import get_session
from core.errors import ErrorCode, ForbiddenError, NotFoundError
from core.security import get_current_user
from schemas.agents import (
    AgentInvokeRequest,
    AgentInvokeResponse,
    AgentResponse,
    AIRunListResponse,
    AIRunResponse,
    ApprovalRequest,
    ApprovalResponse,
)
from services import agent_service

router = APIRouter(tags=["agents"])


# =============================================================================
# Dependencies
# =============================================================================


def _get_db() -> Session:  # pragma: no cover
    return next(get_session())


SessionDep = Annotated[Session, Depends(_get_db)]
CurrentUser = Annotated[genesis_db.User, Depends(get_current_user)]


# =============================================================================
# Agent registry routes
# =============================================================================


@router.get(
    "/agents",
    response_model=list[AgentResponse],
    summary="List all active registered agents",
)
async def list_agents(
    session: SessionDep,
    _current_user: CurrentUser,
) -> list[genesis_db.AgentRegistry]:
    """Return all active agents from agent_registry."""
    return agent_service.list_agents(session)


@router.get(
    "/agents/{agent_id}",
    response_model=AgentResponse,
    summary="Get a specific agent by ID",
)
async def get_agent(
    agent_id: uuid.UUID,
    session: SessionDep,
    _current_user: CurrentUser,
) -> genesis_db.AgentRegistry:
    """Return a specific agent from agent_registry."""
    agent = session.get(genesis_db.AgentRegistry, agent_id)
    if not agent:
        raise NotFoundError("Agent not found.", code=ErrorCode.AGENT_NOT_FOUND)
    return agent


# =============================================================================
# Agent invocation
# =============================================================================


@router.post(
    "/agents/invoke",
    response_model=AgentInvokeResponse,
    status_code=202,
    summary="Invoke a registered agent for a project task",
)
async def invoke_agent(
    request: AgentInvokeRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> AgentInvokeResponse:
    """
    Dispatch a registered agent for a project task (async via NATS).

    Returns immediately with a run_id. Poll /runs/{run_id} or subscribe
    to the project SSE stream to receive completion status.

    Risk policy (per AI_GOVERNANCE.md):
        LOW/MEDIUM: dispatched immediately
        HIGH/CRITICAL: raises 202 with approval_required=True
    """
    from core.errors import ApprovalRequiredError

    try:
        run = await agent_service.dispatch_agent(
            session,
            agent_key=request.agent_key,
            project_id=request.project_id,
            triggered_by_user=current_user,
            run_type=request.agent_key,
            task_id=request.task_id,
            context=request.context,
        )
        return AgentInvokeResponse(
            run_id=run.id,
            status=run.status,
            message="Agent task dispatched. Use run_id to track progress.",
            requires_approval=False,
        )
    except ApprovalRequiredError as exc:
        # Create a pending run record for approval tracking
        agent = agent_service.get_agent_by_key(session, request.agent_key)
        run = agent_service.create_ai_run(
            session,
            run_type=request.agent_key,
            agent=agent,
            project_id=request.project_id,
            triggered_by_user_id=current_user.id,
            input_summary={"agent_key": request.agent_key},
        )
        run.status = genesis_db.AIRunStatus.APPROVAL_REQUIRED
        run.approval_state = "pending"
        session.add(run)
        session.commit()
        return AgentInvokeResponse(
            run_id=run.id,
            status="approval_required",
            message=str(exc),
            requires_approval=True,
        )


# =============================================================================
# AI Run queries
# =============================================================================


@router.get(
    "/projects/{project_id}/runs",
    response_model=AIRunListResponse,
    summary="List AI runs for a project",
)
async def list_runs(
    project_id: uuid.UUID,
    session: SessionDep,
    _current_user: CurrentUser,
    limit: int = 50,
    offset: int = 0,
) -> AIRunListResponse:
    """Return AI run records for a project, most recent first."""
    runs = agent_service.list_ai_runs(session, project_id, limit=limit, offset=offset)
    return AIRunListResponse(
        items=[AIRunResponse.model_validate(r) for r in runs],
        total=len(runs),
    )


@router.get(
    "/runs/{run_id}",
    response_model=AIRunResponse,
    summary="Get a specific AI run record",
)
async def get_run(
    run_id: uuid.UUID,
    session: SessionDep,
    _current_user: CurrentUser,
) -> genesis_db.AIRun:
    """Return a specific AI run record by ID."""
    return agent_service.get_ai_run(session, run_id)


# =============================================================================
# Approval endpoints
# =============================================================================


@router.post(
    "/runs/{run_id}/approve",
    response_model=ApprovalResponse,
    summary="Approve a pending high-risk AI action",
)
async def approve_run(
    run_id: uuid.UUID,
    request: ApprovalRequest,
    session: SessionDep,
    current_user: CurrentUser,
) -> ApprovalResponse:
    """
    Approve or reject a high-risk AI action pending human review.

    Only runs with approval_state='pending' can be approved/rejected.
    After approval, the worker re-checks and proceeds with execution.
    """
    run = agent_service.get_ai_run(session, run_id)

    if request.decision not in ("approve", "reject"):
        raise ForbiddenError("Decision must be 'approve' or 'reject'.")

    updated = agent_service.process_approval(
        session,
        run,
        decision=request.decision,
        approver_user_id=current_user.id,
    )

    action = "approved" if request.decision == "approve" else "rejected"
    return ApprovalResponse(
        run_id=updated.id,
        approval_state=updated.approval_state or "",
        message=f"AI run {action} successfully.",
    )
