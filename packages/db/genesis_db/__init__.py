"""
Genesis Database Package

Public API for the genesis_db package.
Import from here, not from sub-modules directly.

Example:
    import genesis_db
    user = genesis_db.User(email="...", hashed_password="...")
"""

from .database import create_db_and_tables_for_tests, engine, get_session
from .governance import (
    AgentRegistry,
    AgentRiskLevel,
    AIRun,
    AIRunStatus,
    ModelProvider,
    ModelRegistry,
    PromptRegistry,
    PromptStatus,
)
from .models import (
    Project,
    ProjectBase,
    ProjectCreate,
    ProjectPublic,
    User,
    UserBase,
    UserPublic,
    Workspace,
    WorkspaceBase,
    WorkspacePublic,
)

__all__ = [
    # Database utilities
    "engine",
    "get_session",
    "create_db_and_tables_for_tests",
    # Core models
    "User",
    "UserBase",
    "UserPublic",
    "Workspace",
    "WorkspaceBase",
    "WorkspacePublic",
    "Project",
    "ProjectBase",
    "ProjectPublic",
    "ProjectCreate",
    # Governance models
    "ModelRegistry",
    "ModelProvider",
    "PromptRegistry",
    "PromptStatus",
    "AgentRegistry",
    "AgentRiskLevel",
    "AIRun",
    "AIRunStatus",
]
