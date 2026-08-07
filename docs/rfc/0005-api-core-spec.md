# RFC 0005 — API Core Specification (Python / FastAPI)

| Field | Value |
|---|---|
| **RFC Number** | 0005 |
| **Title** | API Core Specification |
| **Status** | Draft |
| **Created** | 2026-08-07 |
| **Phase** | 0.3 |

---

## Summary

This RFC defines the core REST API specification, authentication flow, and initial database schema for Genesis Phase 0.3, utilizing Python, FastAPI, and SQLModel.

---

## Motivation

To power the web dashboard and CLI, we need an API that can authenticate users, manage workspaces, and create projects. Because this is an AI platform, we use Python (FastAPI) to ensure seamless integration with AI libraries in future phases.

---

## Database Schema (SQLModel)

The database models map to the domain entities defined in Epic 12. They reside in a shared `genesis_db` package.

```python
from datetime import datetime, timezone
import uuid
from sqlmodel import Field, SQLModel, Relationship

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)

class User(UserBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    workspaces: list["Workspace"] = Relationship(back_populates="user")

class WorkspaceBase(SQLModel):
    name: str

class Workspace(WorkspaceBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="user.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    user: User = Relationship(back_populates="workspaces")
    projects: list["Project"] = Relationship(back_populates="workspace")

class ProjectBase(SQLModel):
    name: str
    description: str | None = None
    workspace_id: uuid.UUID = Field(foreign_key="workspace.id")

class Project(ProjectBase, table=True):
    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    workspace: Workspace = Relationship(back_populates="projects")
```

---

## REST API Endpoints

FastAPI automatically generates OpenAPI documentation at `/docs`.

### Authentication

**`POST /api/auth/signup`**
- Body: `UserCreate(email, password)`
- Response: `{ "access_token": str, "token_type": "bearer", "user": UserPublic }`

**`POST /api/auth/login`**
- Body: OAuth2 `username` (email) and `password` form data (standard FastAPI).
- Response: `{ "access_token": str, "token_type": "bearer" }`

### Workspaces (Requires Auth)

**`GET /api/workspaces`**
- Response: `list[WorkspacePublic]`

**`POST /api/workspaces`**
- Body: `WorkspaceCreate(name)`
- Response: `WorkspacePublic`

### Projects (Requires Auth)

**`GET /api/projects?workspace_id=<id>`**
- Response: `list[ProjectPublic]`

**`POST /api/projects`**
- Body: `ProjectCreate(name, description, workspace_id)`
- Response: `ProjectPublic`

**`DELETE /api/projects/{id}`**
- Response: `204 No Content`

### System

**`GET /api/health`**
- Response: `{ "status": "ok", "db": "connected", "version": "0.3.0" }`

---

## Authentication Flow

1. Client sends credentials to `/api/auth/login`.
2. Server verifies password against the hashed value in the DB (using `passlib`).
3. Server generates a JWT containing the `user_id` (using `PyJWT`).
4. Client passes JWT in the `Authorization: Bearer <token>` header for subsequent requests.

---

## Implementation Plan

1. Create `packages/db` Python package with SQLModel schemas and Alembic migrations.
2. Build `apps/api` using FastAPI.
3. Build `apps/worker` using standard Python asyncio.
4. Integrate with `docker-compose.platform.yml` and turborepo.
