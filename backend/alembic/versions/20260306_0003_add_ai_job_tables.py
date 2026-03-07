"""Add persistent ai_jobs and ai_job_events tables.

Revision ID: 20260306_0003
Revises: 20260306_0002
Create Date: 2026-03-06
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


revision: str = "20260306_0003"
down_revision: Union[str, None] = "20260306_0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)

    if "ai_jobs" not in inspector.get_table_names():
        op.create_table(
            "ai_jobs",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column("job_type", sa.String(length=100), nullable=False),
            sa.Column("status", sa.String(length=30), nullable=False),
            sa.Column("trace_id", sa.String(length=255), nullable=True),
            sa.Column("priority", sa.Integer(), nullable=True),
            sa.Column("attempts", sa.Integer(), nullable=False),
            sa.Column("max_retries", sa.Integer(), nullable=False),
            sa.Column("worker_id", sa.String(length=255), nullable=True),
            sa.Column("error", sa.Text(), nullable=True),
            sa.Column("request_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("result_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
            sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_ai_jobs_tenant_id"), "ai_jobs", ["tenant_id"], unique=False)
        op.create_index(op.f("ix_ai_jobs_user_id"), "ai_jobs", ["user_id"], unique=False)
        op.create_index(op.f("ix_ai_jobs_job_type"), "ai_jobs", ["job_type"], unique=False)
        op.create_index(op.f("ix_ai_jobs_status"), "ai_jobs", ["status"], unique=False)
        op.create_index(op.f("ix_ai_jobs_trace_id"), "ai_jobs", ["trace_id"], unique=False)

    if "ai_job_events" not in inspector.get_table_names():
        op.create_table(
            "ai_job_events",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("ai_job_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("stage", sa.String(length=100), nullable=False),
            sa.Column("source", sa.String(length=100), nullable=False),
            sa.Column("detail", sa.Text(), nullable=True),
            sa.Column("event_timestamp", sa.DateTime(timezone=True), nullable=False),
            sa.Column("payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
            sa.ForeignKeyConstraint(["ai_job_id"], ["ai_jobs.id"]),
            sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_ai_job_events_ai_job_id"), "ai_job_events", ["ai_job_id"], unique=False)
        op.create_index(op.f("ix_ai_job_events_tenant_id"), "ai_job_events", ["tenant_id"], unique=False)
        op.create_index(op.f("ix_ai_job_events_stage"), "ai_job_events", ["stage"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "ai_job_events" in inspector.get_table_names():
        op.drop_table("ai_job_events")
    if "ai_jobs" in inspector.get_table_names():
        op.drop_table("ai_jobs")
