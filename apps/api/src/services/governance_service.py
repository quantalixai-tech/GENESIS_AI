import uuid
from datetime import UTC, datetime
from typing import Any

from sqlmodel import Session

import genesis_db
from core.errors import ErrorCode, GenesisError
from core.logging import get_logger

logger = get_logger(__name__)


class GovernanceError(GenesisError):
    def __init__(self, message: str):
        super().__init__(message=message, code=ErrorCode.INTERNAL_SERVER_ERROR)


def create_ai_run(
    session: Session,
    run_type: str,
    project_id: uuid.UUID | None = None,
    agent_id: uuid.UUID | None = None,
    model_id: uuid.UUID | None = None,
    prompt_id: uuid.UUID | None = None,
    triggered_by_user_id: uuid.UUID | None = None,
    input_summary: dict[str, Any] | None = None,
) -> genesis_db.AIRun:
    """
    Create a new AIRun record before executing an AI operation.
    """
    logger.info(
        f"Creating AIRun of type {run_type}",
        extra={"agent_id": str(agent_id) if agent_id else None},
    )

    # In a full implementation, we'd check if agent requires approval
    # For Phase 4 MVP, we just create the pending record

    run = genesis_db.AIRun(
        run_type=run_type,
        status=genesis_db.AIRunStatus.PENDING,
        project_id=project_id,
        agent_id=agent_id,
        model_id=model_id,
        prompt_id=prompt_id,
        triggered_by_user_id=triggered_by_user_id,
        input_summary=input_summary,
        started_at=datetime.now(UTC),
    )

    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def complete_ai_run(
    session: Session,
    run_id: uuid.UUID,
    output_summary: dict[str, Any] | None = None,
    usage_stats: dict[str, Any] | None = None,
) -> genesis_db.AIRun:
    """
    Mark an AIRun as completed and record its output summary and usage stats.
    """
    run = session.get(genesis_db.AIRun, run_id)
    if not run:
        raise GovernanceError(f"AIRun {run_id} not found")

    logger.info(f"Completing AIRun {run_id}")

    run.status = genesis_db.AIRunStatus.COMPLETED
    run.completed_at = datetime.now(UTC)
    run.output_summary = output_summary

    if usage_stats:
        run.duration_ms = usage_stats.get("duration_ms")
        run.prompt_tokens = usage_stats.get("prompt_tokens")
        run.completion_tokens = usage_stats.get("completion_tokens")
        run.total_tokens = usage_stats.get("total_tokens")

    session.add(run)
    session.commit()
    session.refresh(run)
    return run


def fail_ai_run(
    session: Session,
    run_id: uuid.UUID,
    error_message: str,
) -> genesis_db.AIRun:
    """
    Mark an AIRun as failed and record the sanitized error message.
    """
    run = session.get(genesis_db.AIRun, run_id)
    if not run:
        raise GovernanceError(f"AIRun {run_id} not found")

    logger.error(f"Failing AIRun {run_id}", extra={"error": error_message})

    run.status = genesis_db.AIRunStatus.FAILED
    run.completed_at = datetime.now(UTC)
    run.error_message = error_message

    session.add(run)
    session.commit()
    session.refresh(run)
    return run
