from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
import genesis_db
from core.security import get_current_user

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

@router.get("/", response_model=list[genesis_db.WorkspacePublic])
def read_workspaces(
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user)
):
    workspaces = session.exec(
        select(genesis_db.Workspace).where(genesis_db.Workspace.user_id == current_user.id)
    ).all()
    return workspaces

@router.post("/", response_model=genesis_db.WorkspacePublic)
def create_workspace(
    workspace_in: genesis_db.WorkspaceBase,
    session: Session = Depends(genesis_db.get_session),
    current_user: genesis_db.User = Depends(get_current_user)
):
    workspace = genesis_db.Workspace(**workspace_in.model_dump(), user_id=current_user.id)
    session.add(workspace)
    session.commit()
    session.refresh(workspace)
    return workspace
