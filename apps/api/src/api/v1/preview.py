import sys
import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlmodel import Session

from core.errors import NotFoundError
from core.logging import get_logger
from genesis_db.database import get_session
from genesis_db.models import Project

sys.path.append("/workspace/packages")
from agents.tools.sandbox_ops import get_sandbox_status, start_sandbox, stop_sandbox

logger = get_logger(__name__)

router = APIRouter(prefix="/projects/{project_id}/preview", tags=["preview"])


class PreviewStatusResponse(BaseModel):
    status: str
    port: int | None = None
    container_id: str | None = None


@router.post("/start", response_model=PreviewStatusResponse)
async def start_project_preview(project_id: uuid.UUID, session: Session = Depends(get_session)):
    """Start a sandbox container for the given project to preview its UI."""
    project = session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found", details={"project_id": str(project_id)})

    try:
        sandbox_info = start_sandbox(str(project.id), project.repository_path)
        return PreviewStatusResponse(**sandbox_info)
    except Exception as e:
        logger.error(f"Error starting preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to start sandbox: {str(e)}",
        ) from e


@router.post("/stop")
async def stop_project_preview(project_id: uuid.UUID, session: Session = Depends(get_session)):
    """Stop a sandbox container for the given project."""
    project = session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found", details={"project_id": str(project_id)})

    try:
        stop_sandbox(str(project.id))
        return {"success": True}
    except Exception as e:
        logger.error(f"Error stopping preview: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to stop sandbox: {str(e)}",
        ) from e


@router.get("/status", response_model=PreviewStatusResponse)
async def get_project_preview_status(
    project_id: uuid.UUID, session: Session = Depends(get_session)
):
    """Get the status of the sandbox container for the given project."""
    project = session.get(Project, project_id)
    if not project:
        raise NotFoundError("Project not found", details={"project_id": str(project_id)})

    try:
        sandbox_info = get_sandbox_status(str(project.id))
        return PreviewStatusResponse(**sandbox_info)
    except Exception as e:
        logger.error(f"Error getting preview status: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get sandbox status: {str(e)}",
        ) from e
