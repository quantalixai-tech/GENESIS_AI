"""
Genesis Database Package

Public API for the genesis_db package.
Import from here, not from sub-modules directly.

Example:
    import genesis_db
    user = genesis_db.User(email="...", hashed_password="...")
"""

from .database import create_db_and_tables_for_tests, engine, get_session
from .execution_models import (
    Environment,
    EnvironmentType,
    ErrorSeverity,
    ErrorStatus,
    Feedback,
    FeedbackType,
    FileStatus,
    GitAuthorType,
    GitCommit,
    IndexRelationship,
    ProjectError,
    ProjectFile,
    ProjectIndex,
    Repair,
    RepairStatus,
    ValidationRun,
    ValidationStatus,
    ValidationType,
)
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
    ProjectStatus,
    ProjectType,
    User,
    UserBase,
    UserPublic,
    Workspace,
    WorkspaceBase,
    WorkspacePublic,
)
from .planning_models import (
    DependencyType,
    ImplementationPlan,
    ImplementationTask,
    PlanStatus,
    TaskDependency,
    TaskStatus,
    TaskType,
)
from .project_models import (
    Conversation,
    ConversationMessage,
    ConversationStatus,
    Feature,
    FeatureStatus,
    MessageRole,
    MessageType,
    Requirement,
    RequirementCategory,
    RequirementPriority,
    RequirementStatus,
    Screen,
    ScreenStatus,
    TechnicalRequirement,
    UseCase,
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
    "ProjectType",
    "ProjectStatus",
    # Governance models
    "ModelRegistry",
    "ModelProvider",
    "PromptRegistry",
    "PromptStatus",
    "AgentRegistry",
    "AgentRiskLevel",
    "AIRun",
    "AIRunStatus",
    # Project domain models
    "Conversation",
    "ConversationStatus",
    "ConversationMessage",
    "MessageRole",
    "MessageType",
    "Requirement",
    "RequirementCategory",
    "RequirementPriority",
    "RequirementStatus",
    "Feature",
    "FeatureStatus",
    "UseCase",
    "Screen",
    "ScreenStatus",
    "TechnicalRequirement",
    # Planning models
    "ImplementationPlan",
    "PlanStatus",
    "ImplementationTask",
    "TaskStatus",
    "TaskType",
    "TaskDependency",
    "DependencyType",
    # Execution & observability models
    "ProjectFile",
    "FileStatus",
    "ProjectIndex",
    "IndexRelationship",
    "ValidationRun",
    "ValidationType",
    "ValidationStatus",
    "ProjectError",
    "ErrorSeverity",
    "ErrorStatus",
    "Repair",
    "RepairStatus",
    "GitCommit",
    "GitAuthorType",
    "Environment",
    "EnvironmentType",
    "Feedback",
    "FeedbackType",
]
