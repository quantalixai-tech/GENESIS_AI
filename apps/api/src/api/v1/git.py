"""
Genesis API — Git History Routes

Handles HTTP for project git history queries.
All business logic delegates to git_service.

Routes:
    GET    /api/v1/projects/{project_id}/commits
    GET    /api/v1/projects/{project_id}/commits/{commit_id}/diff
    POST   /api/v1/projects/{project_id}/commits/{commit_id}/restore
"""

import uuid
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlmodel import Session

import genesis_db
from genesis_db import get_session
from core.errors import ErrorCode, NotFoundError
from core.security import get_current_user
from services import git_service

router = APIRouter(prefix="/projects/{project_id}", tags=["git"])


# =============================================================================
# Schemas
# =============================================================================


class GitCommitResponse(BaseModel):
    id: uuid.UUID
    commit_hash: str
    message: str
    parent_commit_hash: str | None
    author_type: str
    task_id: uuid.UUID | None
    requirement_ids: list | None
    files_changed: list | None
    created_at: datetime

    model_config = {"from_attributes": True}


class DiffResponse(BaseModel):
    from_commit: str
    to_commit: str
    diff: str


class RestoreResponse(BaseModel):
    restored_commit: GitCommitResponse
    message: str


# =============================================================================
# Dependencies
# =============================================================================


def _get_db() -> Session:  # pragma: no cover
    return next(get_session())


SessionDep = Annotated[Session, Depends(_get_db)]
CurrentUser = Annotated[genesis_db.User, Depends(get_current_user)]


def _resolve_project(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> genesis_db.Project:
    from services.project_service import _get_workspace_for_user

    project = session.get(genesis_db.Project, project_id)
    if not project:
        raise NotFoundError("Project not found.", code=ErrorCode.PROJECT_NOT_FOUND)
    _get_workspace_for_user(session, project.workspace_id, current_user)
    return project


# =============================================================================
# Routes
# =============================================================================


@router.get(
    "/commits",
    response_model=list[GitCommitResponse],
    summary="Get git commit history for a project",
)
async def get_commit_history(
    project_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
    limit: int = 50,
    offset: int = 0,
) -> list[genesis_db.GitCommit]:
    """
    Return the git commit history for a project (from DB — fast query).

    Each commit is linked to the task and requirements that produced it,
    providing full traceability per PRD-001 PRINCIPLE-004.
    """
    _resolve_project(project_id, session, current_user)
    return git_service.get_commit_history(session, project_id, limit=limit, offset=offset)


@router.get(
    "/commits/{commit_id}/diff",
    response_model=DiffResponse,
    summary="Get diff for a specific commit",
)
async def get_commit_diff(
    project_id: uuid.UUID,
    commit_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> DiffResponse:
    """Return the unified diff for a specific commit vs its parent."""
    from sqlmodel import select

    project = _resolve_project(project_id, session, current_user)

    commit_record = session.exec(
        select(genesis_db.GitCommit).where(
            genesis_db.GitCommit.id == commit_id,
            genesis_db.GitCommit.project_id == project_id,
        )
    ).first()
    if not commit_record:
        raise NotFoundError("Commit not found.", code=ErrorCode.NOT_FOUND)

    parent = (
        commit_record.parent_commit_hash or "4b825dc642cb6eb9a060e54bf8d69288fbee4904"
    )  # empty tree
    diff = git_service.get_diff(project, parent, commit_record.commit_hash)

    return DiffResponse(
        from_commit=parent[:8],
        to_commit=commit_record.commit_hash[:8],
        diff=diff,
    )


@router.post(
    "/commits/{commit_id}/restore",
    response_model=RestoreResponse,
    summary="Restore project to a previous commit state",
)
async def restore_commit(
    project_id: uuid.UUID,
    commit_id: uuid.UUID,
    session: SessionDep,
    current_user: CurrentUser,
) -> RestoreResponse:
    """
    Restore the project to the state at a previous commit.

    Creates a new restore commit on top of the restored state —
    git history is always preserved.
    """
    project = _resolve_project(project_id, session, current_user)
    restored = git_service.restore_commit(session, project, commit_id)
    return RestoreResponse(
        restored_commit=GitCommitResponse.model_validate(restored),
        message=f"Project restored to commit {restored.commit_hash[:8]}.",
    )
