"""
Genesis Database — AI Governance Models

These tables form the governance foundation for all AI operations on the platform.
They must exist BEFORE any AI agent code is written, so governance is structural
rather than retrofitted.

Governance tables defined here:
    model_registry      — registered LLM models and their configurations
    prompt_registry     — versioned prompts with lineage tracking
    agent_registry      — defined agents with capabilities and risk levels
    ai_run              — execution record for every AI operation

Design principles:
    - Every AI execution MUST create an ai_run record (enforced at service level)
    - Agents have explicit risk_level — HIGH risk requires human approval
    - Prompts are versioned — no anonymous inline prompts in application code
    - Models are referenced by registry ID, not hardcoded names

See docs/AI_GOVERNANCE.md for policies and usage rules.
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


class ModelProvider(StrEnum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    GOOGLE = "google"
    OLLAMA = "ollama"  # Local model via Ollama
    CUSTOM = "custom"  # Any other provider


class AgentRiskLevel(StrEnum):
    LOW = "low"  # Read-only, reversible — no approval needed
    MEDIUM = "medium"  # Writes data — audit required
    HIGH = "high"  # Irreversible, external, or destructive — approval required
    CRITICAL = "critical"  # Production changes — explicit human-in-the-loop


class AIRunStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    APPROVAL_REQUIRED = "approval_required"
    APPROVED = "approved"
    REJECTED = "rejected"


class PromptStatus(StrEnum):
    DRAFT = "draft"
    ACTIVE = "active"
    DEPRECATED = "deprecated"
    ARCHIVED = "archived"


# =============================================================================
# Model Registry
# =============================================================================


class ModelRegistry(SQLModel, table=True):
    """
    Registry of all LLM models used by the Genesis platform.

    Every agent MUST reference a model by its registry ID.
    Hardcoding model names (e.g., "gpt-4o") throughout the codebase is forbidden.

    When updating a model or its configuration, create a new registry entry
    and update the agent registry to reference it — this preserves history.
    """

    __tablename__ = "model_registry"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    name: str = Field(max_length=255, description="Human-readable model name")
    model_id: str = Field(
        max_length=255,
        description="Provider-specific model identifier (e.g., 'gpt-4o', 'claude-3-5-sonnet')",
    )
    provider: str = Field(
        max_length=50,
        description="Model provider (openai | anthropic | google | ollama | custom)",
    )
    version: str = Field(
        max_length=50,
        description="Model version or snapshot (e.g., '2024-11-20')",
    )
    description: str | None = Field(default=None, max_length=1000)
    context_window: int | None = Field(
        default=None,
        description="Maximum context window in tokens",
    )
    max_output_tokens: int | None = Field(
        default=None,
        description="Maximum output tokens per completion",
    )
    capabilities: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Model capabilities (e.g., vision, function_calling, json_mode)",
    )
    is_active: bool = Field(default=True, description="Whether this model is available for use")
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )


# =============================================================================
# Prompt Registry
# =============================================================================


class PromptRegistry(SQLModel, table=True):
    """
    Registry of all system prompts used by Genesis agents.

    Every system prompt must be registered here.
    Embedding large prompts directly in application code is forbidden.

    Versioning: when a prompt is updated, increment version and create a new record.
    Set the old record's status to DEPRECATED.
    """

    __tablename__ = "prompt_registry"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    prompt_key: str = Field(
        max_length=100,
        index=True,
        description="Stable identifier for this prompt (e.g., 'requirement_agent_system')",
    )
    version: int = Field(description="Monotonically increasing version number")
    title: str = Field(max_length=255)
    description: str | None = Field(
        default=None,
        max_length=1000,
        description="What this prompt does and when it is used",
    )
    content: str = Field(description="The full prompt content")
    model_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="model_registry.id",
        description="Specific model this prompt is optimized for (null = model-agnostic)",
    )
    status: str = Field(
        default=PromptStatus.DRAFT,
        max_length=50,
        description="draft | active | deprecated | archived",
    )
    owner: str | None = Field(
        default=None,
        max_length=100,
        description="Team or service that owns this prompt",
    )
    evaluation_status: str | None = Field(
        default=None,
        max_length=50,
        description="Evaluation result: passed | failed | pending",
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
# Agent Registry
# =============================================================================


class AgentRegistry(SQLModel, table=True):
    """
    Registry of all AI agents defined in the Genesis platform.

    Every agent must be registered here before it can be instantiated.
    Agents not in the registry cannot be invoked by the orchestrator.

    The risk_level determines approval requirements:
        LOW     → No approval needed
        MEDIUM  → Audit log required
        HIGH    → Async human approval required before execution
        CRITICAL → Synchronous human-in-the-loop required
    """

    __tablename__ = "agent_registry"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)
    agent_key: str = Field(
        max_length=100,
        unique=True,
        index=True,
        description="Stable identifier for this agent (e.g., 'requirement_agent')",
    )
    name: str = Field(max_length=255)
    agent_type: str = Field(
        max_length=50,
        description="REQUIREMENT | PRODUCT | UI | ARCHITECTURE | BACKEND | FRONTEND | "
        "DATABASE | PLANNER | CODER | TEST | BUILD | DEBUG | REPAIR | "
        "DOCUMENTATION | INDEX | REVIEW | ORCHESTRATOR",
    )
    description: str | None = Field(default=None, max_length=1000)
    purpose: str = Field(
        max_length=500,
        description="What this agent is responsible for",
    )
    model_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="model_registry.id",
        description="Default model for this agent",
    )
    system_prompt_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="prompt_registry.id",
        description="Default system prompt for this agent",
    )
    allowed_tools: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Explicit list of tool IDs this agent is permitted to use",
    )
    capabilities: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="What this agent can do",
    )
    risk_level: str = Field(
        default=AgentRiskLevel.MEDIUM,
        max_length=20,
        description="low | medium | high | critical",
    )
    requires_approval: bool = Field(
        default=False,
        description="If true, agent actions require explicit human approval",
    )
    max_execution_seconds: int = Field(
        default=300,
        description="Maximum execution time before the agent is cancelled",
    )
    max_retries: int = Field(
        default=3,
        description="Maximum retry attempts for failed executions",
    )
    is_active: bool = Field(default=True)
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    updated_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False, onupdate=func.now()),
    )


# =============================================================================
# AI Run — Execution Record
# =============================================================================


class AIRun(SQLModel, table=True):
    """
    Execution record for every AI operation performed by the platform.

    An AIRun is created BEFORE execution begins and updated as it progresses.
    Every agent invocation, LLM call, and AI-generated action must have an AIRun.

    This table is the foundation of AI auditability and observability.
    It captures enough information to:
        - Audit what AI did and why
        - Reconstruct the context used
        - Attribute costs to projects and users
        - Detect policy violations
        - Enable human review of AI decisions
        - Support evaluation and regression testing

    DO NOT store full prompt content in this table (use prompt_registry.id).
    DO NOT store sensitive user data in input_summary or output_summary.
    """

    __tablename__ = "ai_run"

    id: uuid.UUID = Field(default_factory=uuid.uuid4, primary_key=True)

    # --- Relationships ---
    project_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="project.id",
        index=True,
        description="Project this run belongs to (null for platform-level runs)",
    )
    agent_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="agent_registry.id",
        description="Agent that performed this run",
    )
    model_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="model_registry.id",
        description="Model used for this run",
    )
    prompt_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="prompt_registry.id",
        description="System prompt used for this run",
    )
    triggered_by_user_id: uuid.UUID | None = Field(
        default=None,
        foreign_key="user.id",
        description="User whose action triggered this run",
    )

    # --- Execution context ---
    run_type: str = Field(
        max_length=100,
        description="What kind of operation this is (e.g., 'requirement_extraction', 'code_generation')",
    )
    status: str = Field(
        default=AIRunStatus.PENDING,
        max_length=30,
        index=True,
    )
    parent_run_id: uuid.UUID | None = Field(
        default=None,
        description="Parent AIRun if this is a sub-run of an orchestrated workflow",
    )

    # --- Input / Output (non-sensitive summaries only) ---
    input_summary: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Non-sensitive summary of inputs (not full content). "
        "Never store user PII or secrets here.",
    )
    output_summary: dict | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="Non-sensitive summary of output. Never store full generated content here "
        "if it contains user data.",
    )
    tools_used: list | None = Field(
        default=None,
        sa_column=Column(JSON),
        description="List of tool IDs called during this run",
    )
    error_message: str | None = Field(
        default=None,
        max_length=2000,
        description="Error message if status=failed. Sanitized — no stack traces.",
    )

    # --- Observability ---
    duration_ms: int | None = Field(
        default=None, description="Total execution time in milliseconds"
    )
    prompt_tokens: int | None = Field(default=None, description="Input token count")
    completion_tokens: int | None = Field(default=None, description="Output token count")
    total_tokens: int | None = Field(default=None, description="Total token count")
    estimated_cost_usd: float | None = Field(default=None, description="Estimated API cost in USD")

    # --- Governance ---
    policy_decision: str | None = Field(
        default=None,
        max_length=50,
        description="allow | deny | require_approval",
    )
    approval_state: str | None = Field(
        default=None,
        max_length=30,
        description="pending | approved | rejected (null if approval not required)",
    )
    approved_by_user_id: uuid.UUID | None = Field(
        default=None,
        description="User who approved this run (if required)",
    )

    # --- Timestamps ---
    created_at: datetime = Field(
        default_factory=_utcnow,
        sa_column=Column(DateTime(timezone=True), nullable=False),
    )
    started_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
    completed_at: datetime | None = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), nullable=True),
    )
