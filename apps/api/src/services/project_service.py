"""
Genesis API — Project & Workspace Service

Contains all business logic for workspace and project management.
Route handlers call this service; they do not contain business logic directly.

Responsibilities:
    - Create / list workspaces
    - Create / list / delete projects
    - Authorization checks (user owns workspace)

This module does NOT:
    - Handle HTTP concerns
    - Know about response schemas

Raising:
    NotFoundError   — workspace or project not found, or user not authorized
"""

import uuid
from datetime import datetime, timezone

from sqlmodel import Session, select

import genesis_db
from core.errors import ErrorCode, NotFoundError
from core.logging import get_logger
from schemas.projects import ProjectCreateRequest, WorkspaceCreateRequest

logger = get_logger(__name__)


# =============================================================================
# Workspace operations
# =============================================================================


def list_workspaces(session: Session, user: genesis_db.User) -> list[genesis_db.Workspace]:
    """Return all workspaces owned by the given user."""
    return list(
        session.exec(
            select(genesis_db.Workspace).where(genesis_db.Workspace.user_id == user.id)
        ).all()
    )


def create_workspace(
    session: Session,
    user: genesis_db.User,
    request: WorkspaceCreateRequest,
) -> genesis_db.Workspace:
    """
    Create a new workspace for the authenticated user.

    Returns:
        The newly created Workspace.
    """
    workspace = genesis_db.Workspace(name=request.name, user_id=user.id)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    logger.info(
        "Workspace created",
        extra={"workspace_id": str(workspace.id), "user_id": str(user.id)},
    )
    return workspace


# =============================================================================
# Project operations
# =============================================================================


def _get_workspace_for_user(
    session: Session, workspace_id: uuid.UUID, user: genesis_db.User
) -> genesis_db.Workspace:
    """
    Return the workspace if it exists and belongs to the user.

    Raises:
        NotFoundError: If workspace is not found or belongs to a different user.
        Uses WORKSPACE_NOT_FOUND for both cases to avoid leaking ownership info.
    """
    workspace = session.get(genesis_db.Workspace, workspace_id)
    if not workspace or workspace.user_id != user.id:
        raise NotFoundError("Workspace not found.", code=ErrorCode.WORKSPACE_NOT_FOUND)
    return workspace


def list_projects(
    session: Session, workspace_id: uuid.UUID, user: genesis_db.User
) -> list[genesis_db.Project]:
    """
    Return all projects in a workspace, after verifying user ownership.

    Raises:
        NotFoundError: If workspace not found or not owned by user.
    """
    _get_workspace_for_user(session, workspace_id, user)
    return list(
        session.exec(
            select(genesis_db.Project).where(genesis_db.Project.workspace_id == workspace_id)
        ).all()
    )


def create_project(
    session: Session,
    user: genesis_db.User,
    request: ProjectCreateRequest,
) -> genesis_db.Project:
    """
    Create a new project in the given workspace, after verifying ownership.

    Raises:
        NotFoundError: If workspace not found or not owned by user.
    """
    _get_workspace_for_user(session, request.workspace_id, user)

    project = genesis_db.Project(
        name=request.name,
        description=request.description,
        workspace_id=request.workspace_id,
    )
    session.add(project)
    session.commit()
    session.refresh(project)
    logger.info(
        "Project created",
        extra={
            "project_id": str(project.id),
            "workspace_id": str(project.workspace_id),
            "user_id": str(user.id),
        },
    )
    return project


def delete_project(
    session: Session,
    project_id: uuid.UUID,
    user: genesis_db.User,
) -> None:
    """
    Delete a project after verifying the user owns its workspace.

    Raises:
        NotFoundError: If project not found or user does not own its workspace.
    """
    project = session.get(genesis_db.Project, project_id)
    if not project:
        raise NotFoundError("Project not found.", code=ErrorCode.PROJECT_NOT_FOUND)

    # Verify workspace ownership (returns not found if user doesn't own it)
    _get_workspace_for_user(session, project.workspace_id, user)

    session.delete(project)
    session.commit()
    logger.info(
        "Project deleted",
        extra={"project_id": str(project_id), "user_id": str(user.id)},
    )
