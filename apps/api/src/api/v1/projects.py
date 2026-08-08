"""
Genesis API — Project Routes (v1)

Thin route handlers for project management. All business logic in project_service.
"""

import uuid

from fastapi import APIRouter, Depends
from sqlmodel import Session

import genesis_db
from core.security import get_current_user
from schemas.projects import ProjectCreateRequest, ProjectResponse
from services import project_service

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get(
    "/",
    response_model=list[ProjectResponse],
    summary="List projects in a workspace",
)
def list_projects(
    workspace_id: uuid.UUID,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user),
) -> list[ProjectResponse]:
    """
    Return all projects in the specified workspace.
    The workspace must be owned by the authenticated user.
    """
    projects = project_service.list_projects(session, workspace_id, current_user)
    return [ProjectResponse.model_validate(p) for p in projects]


@router.post(
    "/",
    response_model=ProjectResponse,
    status_code=201,
    summary="Create a new project",
)
def create_project(
    request: ProjectCreateRequest,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user),
) -> ProjectResponse:
    """
    Create a new project in the specified workspace.
    The workspace must be owned by the authenticated user.
    """
    project = project_service.create_project(session, current_user, request)
    return ProjectResponse.model_validate(project)


@router.delete(
    "/{project_id}",
    status_code=204,
    summary="Delete a project",
)
def delete_project(
    project_id: uuid.UUID,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user),
) -> None:
    """
    Delete the specified project.
    The project's workspace must be owned by the authenticated user.
    """
    project_service.delete_project(session, project_id, current_user)
