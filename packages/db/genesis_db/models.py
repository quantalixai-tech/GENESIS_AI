import uuid
from datetime import datetime, timezone
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    workspaces: List["Workspace"] = Relationship(back_populates="user")

class UserPublic(UserBase):
    id: uuid.UUID
    created_at: datetime

class WorkspaceBase(SQLModel):
    name: str

class Workspace(WorkspaceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    user: User = Relationship(back_populates="workspaces")
    projects: List["Project"] = Relationship(back_populates="workspace", cascade_delete=True)

class WorkspacePublic(WorkspaceBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime

class ProjectBase(SQLModel):
    name: str
    description: Optional[str] = None

class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    workspace: Workspace = Relationship(back_populates="projects")

class ProjectPublic(ProjectBase):
    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime

class ProjectCreate(ProjectBase):
    workspace_id: uuid.UUID
