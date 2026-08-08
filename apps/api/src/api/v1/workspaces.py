"""
Genesis API — Workspace Routes (v1)

Thin route handlers for workspace management. All business logic in project_service.
"""

from fastapi import APIRouter, Depends
from sqlmodel import Session

import genesis_db
from core.security import get_current_user
from schemas.projects import WorkspaceCreateRequest, WorkspaceResponse
from services import project_service

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get(
    "/",
    response_model=list[WorkspaceResponse],
    summary="List all workspaces for the authenticated user",
)
def list_workspaces(
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user),
) -> list[WorkspaceResponse]:
    """Return all workspaces owned by the authenticated user."""
    workspaces = project_service.list_workspaces(session, current_user)
    return [WorkspaceResponse.model_validate(w) for w in workspaces]


@router.post(
    "/",
    response_model=WorkspaceResponse,
    status_code=201,
    summary="Create a new workspace",
)
def create_workspace(
    request: WorkspaceCreateRequest,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user),
) -> WorkspaceResponse:
    """Create a new workspace for the authenticated user."""
    workspace = project_service.create_workspace(session, current_user, request)
    return WorkspaceResponse.model_validate(workspace)
