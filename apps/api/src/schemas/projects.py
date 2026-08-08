"""
Genesis API — Project and Workspace Schemas

API-layer request/response schemas for workspace and project endpoints.
Separated from DB models to decouple the API contract from the database schema.
"""

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# =============================================================================
# Workspace schemas
# =============================================================================


class WorkspaceCreateRequest(BaseModel):
    """Request body for POST /api/v1/workspaces"""

    name: str = Field(
        min_length=1,
        max_length=255,
        description="Workspace name.",
        examples=["My Projects"],
    )


class WorkspaceResponse(BaseModel):
    """Response schema for workspace objects."""

    id: uuid.UUID
    name: str
    user_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# Project schemas
# =============================================================================


class ProjectCreateRequest(BaseModel):
    """Request body for POST /api/v1/projects"""

    workspace_id: uuid.UUID = Field(description="ID of the parent workspace.")
    name: str = Field(
        min_length=1,
        max_length=255,
        description="Project name.",
        examples=["My Portfolio Website"],
    )
    description: Optional[str] = Field(
        default=None,
        max_length=2000,
        description="Optional project description.",
    )


class ProjectResponse(BaseModel):
    """Response schema for project objects."""

    id: uuid.UUID
    workspace_id: uuid.UUID
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
