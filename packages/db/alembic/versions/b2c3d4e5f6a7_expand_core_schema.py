"""Expand core schema — add project fields and all domain tables

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-08-13

Adds:
    Project table changes:
        - project_type VARCHAR(50) NOT NULL DEFAULT 'custom'
        - status VARCHAR(30) NOT NULL DEFAULT 'discovery'
        - repository_path TEXT NULL
        - current_commit_id UUID NULL

    New tables (in FK dependency order):
        conversation
        conversation_message
        requirement
        feature
        use_case
        screen
        technical_requirement
        implementation_plan
        implementation_task
        task_dependency
        project_file
        project_index
        index_relationship
        validation_run
        project_error
        repair
        git_commit
        environment
        feedback

See docs/BACKEND_SCHEMA.md for full schema specification.
"""

from collections.abc import Sequence

import sqlalchemy as sa
import sqlmodel
from alembic import op

revision: str = "b2c3d4e5f6a7"
down_revision: str | Sequence[str] | None = "a1b2c3d4e5f6"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add all V1 domain tables and extend project table."""

    # -------------------------------------------------------------------------
    # Extend project table
    # -------------------------------------------------------------------------
    op.add_column(
        "project",
        sa.Column(
            "project_type",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
            server_default="custom",
        ),
    )
    op.add_column(
        "project",
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="discovery",
        ),
    )
    op.add_column("project", sa.Column("repository_path", sa.Text(), nullable=True))
    op.add_column("project", sa.Column("current_commit_id", sa.Uuid(), nullable=True))
    op.create_index("ix_project_status", "project", ["status"], unique=False)

    # -------------------------------------------------------------------------
    # conversation
    # -------------------------------------------------------------------------
    op.create_table(
        "conversation",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="active",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversation_project_id", "conversation", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # conversation_message
    # -------------------------------------------------------------------------
    op.create_table(
        "conversation_message",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=False),
        sa.Column("role", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column(
            "message_type",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
            server_default="chat",
        ),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["conversation_id"], ["conversation.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_conversation_message_conversation_id",
        "conversation_message",
        ["conversation_id"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # requirement
    # -------------------------------------------------------------------------
    op.create_table(
        "requirement",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "category",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
            server_default="functional",
        ),
        sa.Column(
            "priority",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("source_message_id", sa.Uuid(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_requirement_project_id", "requirement", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # feature
    # -------------------------------------------------------------------------
    op.create_table(
        "feature",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("feature_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="proposed",
        ),
        sa.Column("priority", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feature_project_id", "feature", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # use_case
    # -------------------------------------------------------------------------
    op.create_table(
        "use_case",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("use_case_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("actor", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("preconditions", sa.JSON(), nullable=True),
        sa.Column("postconditions", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_use_case_project_id", "use_case", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # screen
    # -------------------------------------------------------------------------
    op.create_table(
        "screen",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("screen_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("route", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("ui_spec", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="planned",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_screen_project_id", "screen", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # technical_requirement
    # -------------------------------------------------------------------------
    op.create_table(
        "technical_requirement",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("requirement_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column(
            "priority",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default="medium",
        ),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_technical_requirement_project_id",
        "technical_requirement",
        ["project_id"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # implementation_plan
    # -------------------------------------------------------------------------
    op.create_table(
        "implementation_plan",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="draft",
        ),
        sa.Column("plan_data", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_implementation_plan_project_id",
        "implementation_plan",
        ["project_id"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # implementation_task
    # -------------------------------------------------------------------------
    op.create_table(
        "implementation_task",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("plan_id", sa.Uuid(), nullable=True),
        sa.Column("task_key", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("title", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column(
            "task_type",
            sqlmodel.sql.sqltypes.AutoString(length=50),
            nullable=False,
            server_default="backend",
        ),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("priority", sqlmodel.sql.sqltypes.AutoString(length=20), nullable=True),
        sa.Column("agent_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("agent_run_id", sa.Uuid(), nullable=True),
        sa.Column("parallelizable", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("retry_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("context", sa.JSON(), nullable=True),
        sa.Column("output", sa.JSON(), nullable=True),
        sa.Column(
            "error_message",
            sqlmodel.sql.sqltypes.AutoString(length=2000),
            nullable=True,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["plan_id"], ["implementation_plan.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_implementation_task_project_id",
        "implementation_task",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_implementation_task_status",
        "implementation_task",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_implementation_task_plan_id",
        "implementation_task",
        ["plan_id"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # task_dependency
    # -------------------------------------------------------------------------
    op.create_table(
        "task_dependency",
        sa.Column("task_id", sa.Uuid(), nullable=False),
        sa.Column("depends_on_task_id", sa.Uuid(), nullable=False),
        sa.Column(
            "dependency_type",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="finish_to_start",
        ),
        sa.ForeignKeyConstraint(["task_id"], ["implementation_task.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["depends_on_task_id"], ["implementation_task.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("task_id", "depends_on_task_id"),
    )
    op.create_index("ix_task_dependency_task_id", "task_dependency", ["task_id"], unique=False)
    op.create_index(
        "ix_task_dependency_depends_on_task_id",
        "task_dependency",
        ["depends_on_task_id"],
        unique=False,
    )

    # -------------------------------------------------------------------------
    # project_file
    # -------------------------------------------------------------------------
    op.create_table(
        "project_file",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("path", sa.Text(), nullable=False),
        sa.Column("file_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("language", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("content_hash", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column("size_bytes", sa.BigInteger(), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="tracked",
        ),
        sa.Column("last_indexed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_file_project_id", "project_file", ["project_id"], unique=False)
    op.create_index("ix_project_file_path", "project_file", ["path"], unique=False)

    # -------------------------------------------------------------------------
    # project_index
    # -------------------------------------------------------------------------
    op.create_table(
        "project_index",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("file_id", sa.Uuid(), nullable=False),
        sa.Column("symbol_name", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("symbol_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column("line_start", sa.Integer(), nullable=True),
        sa.Column("line_end", sa.Integer(), nullable=True),
        sa.Column("route", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("api_reference", sqlmodel.sql.sqltypes.AutoString(length=500), nullable=True),
        sa.Column("entity_reference", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=True),
        sa.Column("requirement_ids", sa.JSON(), nullable=True),
        sa.Column("dependency_ids", sa.JSON(), nullable=True),
        sa.Column("test_ids", sa.JSON(), nullable=True),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.Column("content_hash", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column("indexed_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["file_id"], ["project_file.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_index_project_id", "project_index", ["project_id"], unique=False)
    op.create_index("ix_project_index_file_id", "project_index", ["file_id"], unique=False)

    # -------------------------------------------------------------------------
    # index_relationship
    # -------------------------------------------------------------------------
    op.create_table(
        "index_relationship",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("source_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("source_id", sa.Uuid(), nullable=False),
        sa.Column("target_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=False),
        sa.Column("target_id", sa.Uuid(), nullable=False),
        sa.Column(
            "relationship_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False
        ),
        sa.Column("metadata", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_index_relationship_project_id",
        "index_relationship",
        ["project_id"],
        unique=False,
    )
    op.create_index(
        "ix_index_relationship_source_id", "index_relationship", ["source_id"], unique=False
    )
    op.create_index(
        "ix_index_relationship_target_id", "index_relationship", ["target_id"], unique=False
    )

    # -------------------------------------------------------------------------
    # validation_run
    # -------------------------------------------------------------------------
    op.create_table(
        "validation_run",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("commit_id", sa.Uuid(), nullable=True),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("validation_type", sqlmodel.sql.sqltypes.AutoString(length=30), nullable=False),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("output", sa.Text(), nullable=True),
        sa.Column("exit_code", sa.Integer(), nullable=True),
        sa.Column("duration_ms", sa.BigInteger(), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_validation_run_project_id", "validation_run", ["project_id"], unique=False)
    op.create_index("ix_validation_run_status", "validation_run", ["status"], unique=False)

    # -------------------------------------------------------------------------
    # project_error
    # -------------------------------------------------------------------------
    op.create_table(
        "project_error",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("validation_run_id", sa.Uuid(), nullable=True),
        sa.Column("error_type", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=False),
        sa.Column("error_code", sqlmodel.sql.sqltypes.AutoString(length=100), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("stack_trace", sa.Text(), nullable=True),
        sa.Column("affected_files", sa.JSON(), nullable=True),
        sa.Column("line_number", sa.Integer(), nullable=True),
        sa.Column("column_number", sa.Integer(), nullable=True),
        sa.Column(
            "severity",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default="high",
        ),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="open",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["validation_run_id"], ["validation_run.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_project_error_project_id", "project_error", ["project_id"], unique=False)
    op.create_index(
        "ix_project_error_validation_run_id",
        "project_error",
        ["validation_run_id"],
        unique=False,
    )
    op.create_index("ix_project_error_status", "project_error", ["status"], unique=False)

    # -------------------------------------------------------------------------
    # repair
    # -------------------------------------------------------------------------
    op.create_table(
        "repair",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("error_id", sa.Uuid(), nullable=False),
        sa.Column("ai_run_id", sa.Uuid(), nullable=True),
        sa.Column("diagnosis", sa.Text(), nullable=True),
        sa.Column("repair_plan", sa.JSON(), nullable=True),
        sa.Column("changed_files", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("attempt_number", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("confidence_score", sa.Float(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["error_id"], ["project_error.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_repair_project_id", "repair", ["project_id"], unique=False)
    op.create_index("ix_repair_error_id", "repair", ["error_id"], unique=False)
    op.create_index("ix_repair_status", "repair", ["status"], unique=False)

    # -------------------------------------------------------------------------
    # git_commit
    # -------------------------------------------------------------------------
    op.create_table(
        "git_commit",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("commit_hash", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("parent_commit_hash", sqlmodel.sql.sqltypes.AutoString(length=64), nullable=True),
        sa.Column(
            "author_type",
            sqlmodel.sql.sqltypes.AutoString(length=20),
            nullable=False,
            server_default="ai",
        ),
        sa.Column("task_id", sa.Uuid(), nullable=True),
        sa.Column("requirement_ids", sa.JSON(), nullable=True),
        sa.Column("files_changed", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_git_commit_project_id", "git_commit", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # environment
    # -------------------------------------------------------------------------
    op.create_table(
        "environment",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(length=255), nullable=False),
        sa.Column(
            "environment_type",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="local",
        ),
        sa.Column("configuration", sa.JSON(), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="active",
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_environment_project_id", "environment", ["project_id"], unique=False)

    # -------------------------------------------------------------------------
    # feedback
    # -------------------------------------------------------------------------
    op.create_table(
        "feedback",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("project_id", sa.Uuid(), nullable=False),
        sa.Column("user_id", sa.Uuid(), nullable=False),
        sa.Column("conversation_id", sa.Uuid(), nullable=True),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column("feedback_type", sqlmodel.sql.sqltypes.AutoString(length=50), nullable=True),
        sa.Column(
            "status",
            sqlmodel.sql.sqltypes.AutoString(length=30),
            nullable=False,
            server_default="pending",
        ),
        sa.Column("impact_analysis", sa.JSON(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_feedback_project_id", "feedback", ["project_id"], unique=False)
    op.create_index("ix_feedback_user_id", "feedback", ["user_id"], unique=False)
    op.create_index("ix_feedback_status", "feedback", ["status"], unique=False)


def downgrade() -> None:
    """Drop all V1 tables in reverse dependency order."""
    # Execution / observability
    op.drop_index("ix_feedback_status", table_name="feedback")
    op.drop_index("ix_feedback_user_id", table_name="feedback")
    op.drop_index("ix_feedback_project_id", table_name="feedback")
    op.drop_table("feedback")

    op.drop_index("ix_environment_project_id", table_name="environment")
    op.drop_table("environment")

    op.drop_index("ix_git_commit_project_id", table_name="git_commit")
    op.drop_table("git_commit")

    op.drop_index("ix_repair_status", table_name="repair")
    op.drop_index("ix_repair_error_id", table_name="repair")
    op.drop_index("ix_repair_project_id", table_name="repair")
    op.drop_table("repair")

    op.drop_index("ix_project_error_status", table_name="project_error")
    op.drop_index("ix_project_error_validation_run_id", table_name="project_error")
    op.drop_index("ix_project_error_project_id", table_name="project_error")
    op.drop_table("project_error")

    op.drop_index("ix_validation_run_status", table_name="validation_run")
    op.drop_index("ix_validation_run_project_id", table_name="validation_run")
    op.drop_table("validation_run")

    op.drop_index("ix_index_relationship_target_id", table_name="index_relationship")
    op.drop_index("ix_index_relationship_source_id", table_name="index_relationship")
    op.drop_index("ix_index_relationship_project_id", table_name="index_relationship")
    op.drop_table("index_relationship")

    op.drop_index("ix_project_index_file_id", table_name="project_index")
    op.drop_index("ix_project_index_project_id", table_name="project_index")
    op.drop_table("project_index")

    op.drop_index("ix_project_file_path", table_name="project_file")
    op.drop_index("ix_project_file_project_id", table_name="project_file")
    op.drop_table("project_file")

    op.drop_index("ix_task_dependency_depends_on_task_id", table_name="task_dependency")
    op.drop_index("ix_task_dependency_task_id", table_name="task_dependency")
    op.drop_table("task_dependency")

    op.drop_index("ix_implementation_task_plan_id", table_name="implementation_task")
    op.drop_index("ix_implementation_task_status", table_name="implementation_task")
    op.drop_index("ix_implementation_task_project_id", table_name="implementation_task")
    op.drop_table("implementation_task")

    op.drop_index("ix_implementation_plan_project_id", table_name="implementation_plan")
    op.drop_table("implementation_plan")

    op.drop_index("ix_technical_requirement_project_id", table_name="technical_requirement")
    op.drop_table("technical_requirement")

    op.drop_index("ix_screen_project_id", table_name="screen")
    op.drop_table("screen")

    op.drop_index("ix_use_case_project_id", table_name="use_case")
    op.drop_table("use_case")

    op.drop_index("ix_feature_project_id", table_name="feature")
    op.drop_table("feature")

    op.drop_index("ix_requirement_project_id", table_name="requirement")
    op.drop_table("requirement")

    op.drop_index("ix_conversation_message_conversation_id", table_name="conversation_message")
    op.drop_table("conversation_message")

    op.drop_index("ix_conversation_project_id", table_name="conversation")
    op.drop_table("conversation")

    # Project table column removals
    op.drop_index("ix_project_status", table_name="project")
    op.drop_column("project", "current_commit_id")
    op.drop_column("project", "repository_path")
    op.drop_column("project", "status")
    op.drop_column("project", "project_type")
