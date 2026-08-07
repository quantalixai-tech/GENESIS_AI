import uuid
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import genesis_db
from core.security import get_current_user

router = APIRouter(prefix="/projects", tags=["projects"])

@router.get("/", response_model=list[genesis_db.ProjectPublic])
def read_projects(
    workspace_id: uuid.UUID,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user)
):
    # Verify user owns the workspace
    workspace = session.get(genesis_db.Workspace, workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    projects = session.exec(
        select(genesis_db.Project).where(genesis_db.Project.workspace_id == workspace_id)
    ).all()
    return projects

@router.post("/", response_model=genesis_db.ProjectPublic)
def create_project(
    project_in: genesis_db.ProjectCreate,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user)
):
    # Verify user owns the workspace
    workspace = session.get(genesis_db.Workspace, project_in.workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Workspace not found")
        
    project = genesis_db.Project(**project_in.model_dump())
    session.add(project)
    session.commit()
    session.refresh(project)
    return project

@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: uuid.UUID,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user)
):
    project = session.get(genesis_db.Project, project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
        
    # Verify user owns the workspace of the project
    workspace = session.get(genesis_db.Workspace, project.workspace_id)
    if not workspace or workspace.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Project not found")
        
    session.delete(project)
    session.commit()
