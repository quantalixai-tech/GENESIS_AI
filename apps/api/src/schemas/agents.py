"""
Genesis API — Agent & LLM Schemas

API-layer request/response schemas for agent and AI run endpoints.
Separate from DB models — decouples API contract from DB schema.
"""

import uuid
from datetime import datetime

from pydantic import BaseModel

# =============================================================================
# Agent Registry
# =============================================================================


class AgentResponse(BaseModel):
    """Public representation of a registered agent."""

    id: uuid.UUID
    agent_key: str
    name: str
    agent_type: str
    purpose: str
    risk_level: str
    requires_approval: bool
    max_execution_seconds: int
    max_retries: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# =============================================================================
# AI Run (Agent Execution Record)
# =============================================================================


class AIRunResponse(BaseModel):
    """Public representation of an AI execution record."""

    id: uuid.UUID
    run_type: str
    status: str
    project_id: uuid.UUID | None
    agent_id: uuid.UUID | None
    model_id: uuid.UUID | None
    input_summary: dict | None
    output_summary: dict | None
    tools_used: list | None
    error_message: str | None
    duration_ms: int | None
    prompt_tokens: int | None
    completion_tokens: int | None
    total_tokens: int | None
    estimated_cost_usd: float | None
    policy_decision: str | None
    approval_state: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class AIRunListResponse(BaseModel):
    """Paginated list of AI run records."""

    items: list[AIRunResponse]
    total: int


# =============================================================================
# Approval
# =============================================================================


class ApprovalRequest(BaseModel):
    """Request body for approving or rejecting a pending high-risk AI action."""

    decision: str  # "approve" or "reject"
    reason: str | None = None


class ApprovalResponse(BaseModel):
    """Response after processing an approval decision."""

    run_id: uuid.UUID
    approval_state: str
    message: str


# =============================================================================
# Agent Invocation
# =============================================================================


class AgentInvokeRequest(BaseModel):
    """Request to invoke a registered agent for a project task."""

    agent_key: str
    project_id: uuid.UUID
    task_id: uuid.UUID | None = None
    context: dict | None = None


class AgentInvokeResponse(BaseModel):
    """Immediate response after dispatching an agent task."""

    run_id: uuid.UUID
    status: str
    message: str
    requires_approval: bool = False
