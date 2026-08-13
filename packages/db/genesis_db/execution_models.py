"""
Genesis Database — Execution & Observability Models

Covers the execution layer:
    project_file        — tracked files in the generated project
    project_index       — symbol/API/entity index entries per file
    index_relationship  — directed relationship between indexed artifacts
    validation_run      — a single validation pass (lint, typecheck, build, etc.)
    project_error       — error captured from a validation run
    repair              — AI repair attempt for a captured error
    git_commit          — git commit record with task/requirement traceability
    environment         — deployment environment configuration
    feedback            — user feedback associated with a project

See docs/BACKEND_SCHEMA.md §15–25 for schema specification.
"""

import uuid
from datetime import UTC, datetime
from enum import StrEnum

from sqlalchemy import func
from sqlmodel import JSON, Column, DateTime, Field, SQLModel


def _utcnow() -> datetime:
    return datetime.now(UTC)


# =============================================================================
# Enumerations
# =============================================================================


class FileStatus(StrEnum):
    TRACKED = "tracked"
    MODIFIED = "modified"
    DELETED = "deleted"
    IGNORED = "ignored"


class ValidationType(StrEnum):
    SYNTAX = "syntax"
    TYPECHECK = "typecheck"
    LINT = "lint"
    UNIT = "unit"
    INTEGRATION = "integration"
    E2E = "e2e"
    BUILD = "build"
    RUNTIME = "runtime"
    SECURITY = "security"
    UI = "ui"


class ValidationStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


class ErrorSeverity(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    INFO = "info"


class ErrorStatus(StrEnum):
    OPEN = "open"
    IN_REPAIR = "in_repair"
    RESOLVED = "resolved"
    ESCALATED = "escalated"
    IGNORED = "ignored"


class RepairStatus(StrEnum):
    PENDING = "pending"
    ANALYZING = "analyzing"
    PLANNED = "planned"
    APPLYING = "applying"
    VALIDATING = "validating"
    SUCCESS = "success"
    FAILED = "failed"
    ESCALATED = "escalated"


class GitAuthorType(StrEnum):
    USER = "user"
    AI = "ai"
    SYSTEM = "system"


class EnvironmentType(StrEnum):
    LOCAL = "local"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


class FeedbackType(StrEnum):
    BUG = "bug"
    DESIGN_CHANGE = "design_change"
    FEATURE_REQUEST = "feature_request"
    REQUIREMENT_CHANGE = "requirement_change"
    APPROVAL = "approval"
    REJECTION = "rejection"
    QUESTION = "question"


# =============================================================================
# Project File
# =============================================================================


class ProjectFile(SQLModel, table=True):
    """
    A file tracked within a generated project.

    content_hash is used for incremental indexing — only re-index when
    the hash changes. All files are tracked regardless of whether they
    have been indexed yet (last_indexed_at=None until first index run).
    """

    __tablename__ = "project_file"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(
        foreign_key="project.id",
        index=True,
    )
    path: str = Field(
        description="Project-relative file path (e.g., 'frontend/src/App.tsx')",
        index=True,
    )
    file_type: str | None = Field(
        default=None,
        max_length=50,
        description="file | directory | symlink",
    )
    language: str | None = Field(
        default=None,
        max_length=50,
        description="Programming language (python | typescript | javascript | etc.)",
    )
    content_hash: str = Field(
        max_length=64,
        description="SHA-256 of file content — used for incremental index detection",
    )
    size_bytes: int | None = Field(default=None)
    status: str = Field(default=FileStatus.TRACKED, max_length=30)
    last_indexed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=func.now()),
    )


# =============================================================================
# Project Index
# =============================================================================


class ProjectIndex(SQLModel, table=True):
    """
    Index entry for a symbol, route, API, or entity within a project file.

    Used by agents to retrieve relevant context without reading the entire
    project. Each row represents one indexable artifact extracted from a file.

    Examples:
        - A Python function definition (symbol_type=function)
        - A React component (symbol_type=component)
        - An API route (route=/api/v1/users, api_reference=GET /api/v1/users)
        - A database entity (entity_reference=User)
    """

    __tablename__ = "project_index"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    file_id: uuid.UUID = Field(foreign_key="project_file.id", index=True)
    symbol_name: str | None = Field(default=None, max_length=500)
    symbol_type: str | None = Field(
        default=None,
        max_length=50,
        description="function | class | component | hook | model | schema | route | entity",
    )
    line_start: int | None = Field(default=None, description="Start line in source file")
    line_end: int | None = Field(default=None, description="End line in source file")
    route: str | None = Field(default=None, max_length=500)
    api_reference: str | None = Field(
        default=None,
        max_length=500,
        description="e.g., 'GET /api/v1/users'",
    )
    entity_reference: str | None = Field(
        default=None,
        max_length=255,
        description="Database entity name this symbol relates to",
    )
    requirement_ids: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="List of requirement UUIDs this symbol implements",
    )
    dependency_ids: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="List of project_index UUIDs this symbol depends on",
    )
    test_ids: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="List of project_index UUIDs for tests covering this symbol",
    )
    index_metadata: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
    )
    content_hash: str = Field(
        max_length=64,
        description="Hash of the indexed content — for incremental re-indexing",
    )
    indexed_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# =============================================================================
# Index Relationship
# =============================================================================


class IndexRelationship(SQLModel, table=True):
    """
    Directed relationship between two indexed artifacts.

    Examples:
        REQUIREMENT → FEATURE
        FEATURE → USE_CASE
        USE_CASE → SCREEN
        SCREEN → COMPONENT
        COMPONENT → FILE
        FILE → API
        API → ENTITY
        FILE → TEST
        TASK → FILE
        TASK → REQUIREMENT
    """

    __tablename__ = "index_relationship"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    source_type: str = Field(
        max_length=50,
        description="Type of the source artifact (e.g., REQUIREMENT, FILE, TASK)",
    )
    source_id: uuid.UUID = Field(
        index=True,
        description="ID of the source artifact",
    )
    target_type: str = Field(
        max_length=50,
        description="Type of the target artifact",
    )
    target_id: uuid.UUID = Field(index=True)
    relationship_type: str = Field(
        max_length=100,
        description="e.g., IMPLEMENTS, DEPENDS_ON, TESTS, GENERATES",
    )
    index_metadata: dict | None = Field(default=None, sa_column=Column(JSON))


# =============================================================================
# Validation Run
# =============================================================================


class ValidationRun(SQLModel, table=True):
    """
    A single validation pass against the generated project.

    One validation_run per validation type (lint, typecheck, build, etc.).
    A full pipeline creates multiple ValidationRun records — one per step.
    Results are stored in output (truncated to avoid very large records).
    """

    __tablename__ = "validation_run"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    commit_id: uuid.UUID | None = Field(
        default=None,
        description="GitCommit.id this validation was run against",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="ImplementationTask.id that triggered this validation",
    )
    validation_type: str = Field(
        max_length=30,
        description="syntax | typecheck | lint | unit | integration | e2e | build | runtime | security | ui",
    )
    status: str = Field(
        default=ValidationStatus.PENDING,
        max_length=20,
        index=True,
    )
    output: str | None = Field(
        default=None,
        description="Captured stdout/stderr from the validator (truncated to 50KB)",
    )
    exit_code: int | None = Field(default=None)
    duration_ms: int | None = Field(default=None)
    started_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


# =============================================================================
# Project Error (named ProjectError to avoid Python built-in collision)
# =============================================================================


class ProjectError(SQLModel, table=True):
    """
    An error captured from a validation run.

    Errors are classified by type and severity. When status=OPEN, the
    RepairService will attempt to generate a fix. When status=ESCALATED,
    the project moves to status=BLOCKED and the user is notified.

    NOTE: Table name is 'project_error' (not 'error' — reserved in some DBs).
    """

    __tablename__ = "project_error"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    validation_run_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="validation_run.id",
        index=True,
    )
    error_type: str = Field(
        max_length=100,
        description="compilation | type | lint | test | runtime | import | dependency",
    )
    error_code: str | None = Field(
        default=None,
        max_length=100,
        description="Specific error code from the tool (e.g., TS2345, E0001)",
    )
    message: str = Field(description="Human-readable error message (sanitized)")
    stack_trace: str | None = Field(
        default=None,
        description="Stack trace if available (not exposed to end users in production)",
    )
    affected_files: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="List of file paths involved in this error",
    )
    line_number: int | None = Field(default=None)
    column_number: int | None = Field(default=None)
    severity: str = Field(
        default=ErrorSeverity.HIGH,
        max_length=20,
    )
    status: str = Field(
        default=ErrorStatus.OPEN,
        max_length=30,
        index=True,
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# =============================================================================
# Repair
# =============================================================================


class Repair(SQLModel, table=True):
    """
    An AI repair attempt for a captured ProjectError.

    One error may have multiple repair attempts (up to agent_registry.max_retries).
    Each attempt is a separate Repair record. The system escalates to the user
    when max attempts are exhausted or confidence is too low.
    """

    __tablename__ = "repair"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    error_id: uuid.UUID = Field(
        foreign_key="project_error.id",
        index=True,
    )
    ai_run_id: uuid.UUID | None = Field(
        default=None,
        description="ai_run.id for the repair agent execution",
    )
    diagnosis: str | None = Field(
        default=None,
        description="AI-generated root cause analysis",
    )
    repair_plan: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Structured repair plan (files to modify, changes to make)",
    )
    changed_files: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Paths of files modified by this repair attempt",
    )
    status: str = Field(
        default=RepairStatus.PENDING,
        max_length=30,
        index=True,
    )
    attempt_number: int = Field(
        default=1,
        description="Which attempt this is (1-indexed)",
    )
    confidence_score: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="AI confidence in this repair (0.0–1.0)",
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )


# =============================================================================
# Git Commit
# =============================================================================


class GitCommit(SQLModel, table=True):
    """
    Git commit record for a generated project.

    Every meaningful AI-generated change must create a GitCommit record.
    This table mirrors the project's git history in the DB for fast querying
    without filesystem access.

    Traceability: every commit links to the task and/or requirement that
    triggered it, satisfying PRD-001 PRINCIPLE-004.
    """

    __tablename__ = "git_commit"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    commit_hash: str = Field(
        max_length=64,
        description="Full SHA-1 or SHA-256 git commit hash",
    )
    message: str = Field(description="Git commit message (structured)")
    parent_commit_hash: str | None = Field(
        default=None,
        max_length=64,
        description="Parent commit hash (None for initial commit)",
    )
    author_type: str = Field(
        default=GitAuthorType.AI,
        max_length=20,
        description="user | ai | system",
    )
    task_id: uuid.UUID | None = Field(
        default=None,
        description="ImplementationTask.id that produced this commit",
    )
    requirement_ids: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Requirement UUIDs addressed by this commit",
    )
    files_changed: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="List of file paths changed in this commit",
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# =============================================================================
# Environment
# =============================================================================


class Environment(SQLModel, table=True):
    """
    Deployment environment configuration for a project.

    Each project may have multiple environments (local, test, staging, production).
    Configuration is stored as JSONB — contents depend on the target platform.
    """

    __tablename__ = "environment"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    name: str = Field(max_length=255, description="Human-readable environment name")
    environment_type: str = Field(
        default=EnvironmentType.LOCAL,
        max_length=30,
        description="local | test | staging | production",
    )
    configuration: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Environment-specific configuration (no secrets — use env vars)",
    )
    status: str = Field(
        default="active",
        max_length=30,
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=func.now()),
    )


# =============================================================================
# Feedback
# =============================================================================


class Feedback(SQLModel, table=True):
    """
    User feedback associated with a project.

    Feedback triggers the incremental change flow:
        Feedback → impact_analysis → change plan → implementation

    impact_analysis is populated by the RequirementAgent after classification.
    """

    __tablename__ = "feedback"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    project_id: uuid.UUID = Field(foreign_key="project.id", index=True)
    user_id: uuid.UUID = Field(foreign_key="user.id", index=True)
    conversation_id: uuid.UUID | None = Field(
        default=None,
        description="Conversation in which this feedback was given",
    )
    message: str = Field(description="Raw user feedback message")
    feedback_type: str | None = Field(
        default=None,
        max_length=50,
        description="bug | design_change | feature_request | requirement_change | approval | rejection | question",
    )
    status: str = Field(
        default="pending",
        max_length=30,
        index=True,
    )
    impact_analysis: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="AI-generated impact analysis: affected requirements, files, agents needed",
    )
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
