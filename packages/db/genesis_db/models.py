"""
Genesis Database — Core SQLModel Models

Defines the foundational database models for the Genesis platform.

Model layers:
    *Base     — Shared fields for Pydantic validation (no table=True)
    *Table    — Database table model (table=True)

    These are separate from API schemas in apps/api/src/schemas/.
    API response shapes are defined there; DB shapes are defined here.

Convention:
    - All primary keys are UUIDs generated at application level
    - All tables have created_at and updated_at timestamps (UTC)
    - updated_at uses SQLAlchemy's onupdate= so it is set on every UPDATE
    - Foreign keys use explicit naming
    - Soft deletion not implemented in this phase (tracked in PROJECT_AUDIT.md as P2)

Table summary (Phase 0.3):
    user       — registered users
    workspace  — user-owned project containers
    project    — individual AI-generated software projects

Future tables (defined in docs/BACKEND_SCHEMA.md):
    conversation, conversation_message, requirement, feature, use_case,
    screen, technical_requirement, implementation_plan, implementation_task,
    task_dependency, project_file, project_index, index_relationship,
    agent_run, validation_run, error, repair, git_commit, environment,
    feedback — plus AI governance tables in governance.py
"""

import uuid
from datetime import UTC, datetime

from sqlalchemy import func
from sqlmodel import Column, DateTime, Field, Relationship, SQLModel


def _utcnow() -> datetime:
    """Return the current UTC time as a timezone-aware datetime."""
    return datetime.now(UTC)


# =============================================================================
# User
# =============================================================================


class UserBase(SQLModel):
    email: str = Field(unique=True, index=True, max_length=255)


class User(UserBase, table=True):
    __tablename__ = "user"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str = Field(max_length=255)

    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=func.now(),  # Automatically updated on every UPDATE
        ),
    )

    workspaces: list["Workspace"] = Relationship(back_populates="user")


class UserPublic(UserBase):
    """
    Legacy alias — prefer schemas.auth.UserResponse for new code.
    Retained for backward compatibility during transition.
    """

    id: uuid.UUID
    created_at: datetime


# =============================================================================
# Workspace
# =============================================================================


class WorkspaceBase(SQLModel):
    name: str = Field(max_length=255)


class Workspace(WorkspaceBase, table=True):
    __tablename__ = "workspace"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)

    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=func.now(),
        ),
    )

    user: User = Relationship(back_populates="workspaces")
    projects: list["Project"] = Relationship(back_populates="workspace", cascade_delete=True)


class WorkspacePublic(WorkspaceBase):
    """
    Legacy alias — prefer schemas.projects.WorkspaceResponse for new code.
    """

    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime


# =============================================================================
# Project
# =============================================================================


class ProjectBase(SQLModel):
    name: str = Field(max_length=255)
    description: str | None = Field(default=None, max_length=2000)


class Project(ProjectBase, table=True):
    __tablename__ = "project"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id", index=True)

    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            onupdate=func.now(),
        ),
    )

    workspace: Workspace = Relationship(back_populates="projects")


class ProjectPublic(ProjectBase):
    """
    Legacy alias — prefer schemas.projects.ProjectResponse for new code.
    """

    id: uuid.UUID
    workspace_id: uuid.UUID
    created_at: datetime


class ProjectCreate(ProjectBase):
    """
    Legacy alias — prefer schemas.projects.ProjectCreateRequest for new code.
    """

    workspace_id: uuid.UUID
