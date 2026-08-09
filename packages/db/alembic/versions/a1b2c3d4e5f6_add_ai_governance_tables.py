"""Add AI governance tables

Revision ID: a1b2c3d4e5f6
Revises: 14ef95c22141
Create Date: 2026-08-08

Adds the foundational AI governance tables:
    - model_registry
    - prompt_registry
    - agent_registry
    - ai_run

These tables establish the governance infrastructure that must exist
before any AI agent code is written.

See: docs/AI_GOVERNANCE.md
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "a1b2c3d4e5f6"
down_revision: str | Sequence[str] | None = "14ef95c22141"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create AI governance tables."""

    # -------------------------------------------------------------------------
    # model_registry
    # -------------------------------------------------------------------------
    op.create_table(
        "model_registry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("model_id", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("provider", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("version", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column("context_window", sa.Integer(), nullable=True),
        sa.Column("max_output_tokens", sa.Integer(), nullable=True),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # prompt_registry
    # -------------------------------------------------------------------------
    op.create_table(
        "prompt_registry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("prompt_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("model_id", sa.Uuid(), nullable=True),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("owner", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("evaluation_status", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["model_id"], ["model_registry.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_prompt_registry_prompt_key"), "prompt_registry", ["prompt_key"], unique=False
    )

    # -------------------------------------------------------------------------
    # agent_registry
    # -------------------------------------------------------------------------
    op.create_table(
        "agent_registry",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("agent_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("agent_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("description", sqlmodel.sql.sqltypes.AutoString(length=1000), nullable=True),
        sa.Column("purpose", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("model_id", sa.Uuid(), nullable=True),
        sa.Column("system_prompt_id", sa.Uuid(), nullable=True),
        sa.Column("allowed_tools", sa.JSON(), nullable=True),
        sa.Column("capabilities", sa.JSON(), nullable=True),
        sa.Column("risk_level", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("max_execution_seconds", sa.Integer(), nullable=False, server_default="300"),
        sa.Column("max_retries", sa.Integer(), nullable=False, server_default="3"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["model_id"], ["model_registry.id"]),
        sa.ForeignKeyConstraint(["system_prompt_id"], ["prompt_registry.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("agent_key"),
    )
    op.create_index(
        op.f("ix_agent_registry_agent_key"), "agent_registry", ["agent_key"], unique=True
    )

    # -------------------------------------------------------------------------
    # ai_run
    # -------------------------------------------------------------------------
    op.create_table(
        "ai_run",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=True),
        sa.Column("agent_id", sa.Uuid(), nullable=True),
        sa.Column("model_id", sa.Uuid(), nullable=True),
        sa.Column("prompt_id", sa.Uuid(), nullable=True),
        sa.Column("triggered_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("run_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("status", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
        sa.Column("parent_run_id", sa.Uuid(), nullable=True),
        sa.Column("input_summary", sa.JSON(), nullable=True),
        sa.Column("output_summary", sa.JSON(), nullable=True),
        sa.Column("tools_used", sa.JSON(), nullable=True),
        sa.Column("error_message", sqlmodel.sql.sqltypes.AutoString(length=2000), nullable=True),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("prompt_tokens", sa.Integer(), nullable=True),
        sa.Column("completion_tokens", sa.Integer(), nullable=True),
        sa.Column("total_tokens", sa.Integer(), nullable=True),
        sa.Column("estimated_cost_usd", sa.Float(), nullable=True),
        sa.Column("policy_decision", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("approval_state", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=True),
        sa.Column("approved_by_user_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["agent_id"], ["agent_registry.id"]),
        sa.ForeignKeyConstraint(["approved_by_user_id"], ["user.id"]),
        sa.ForeignKeyConstraint(["model_id"], ["model_registry.id"]),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"]),
        sa.ForeignKeyConstraint(["prompt_id"], ["prompt_registry.id"]),
        sa.ForeignKeyConstraint(["triggered_by_user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_ai_run_project_id"), "ai_run", ["project_id"], unique=False)
    op.create_index(op.f("ix_ai_run_status"), "ai_run", ["status"], unique=False)


def downgrade() -> None:
    """Drop AI governance tables in reverse dependency order."""
    op.drop_index(op.f("ix_ai_run_status"), table_name="ai_run")
    op.drop_index(op.f("ix_ai_run_project_id"), table_name="ai_run")
    op.drop_table("ai_run")
    op.drop_index(op.f("ix_agent_registry_agent_key"), table_name="agent_registry")
    op.drop_table("agent_registry")
    op.drop_index(op.f("ix_prompt_registry_prompt_key"), table_name="prompt_registry")
    op.drop_table("prompt_registry")
    op.drop_table("model_registry")
