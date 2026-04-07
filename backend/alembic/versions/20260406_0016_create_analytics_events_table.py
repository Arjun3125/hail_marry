"""create analytics events table

Revision ID: 20260406_0016
Revises: 20260406_0015
Create Date: 2026-04-06
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "20260406_0016"
down_revision = "20260406_0015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "analytics_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("event_name", sa.String(length=100), nullable=False),
        sa.Column("event_family", sa.String(length=50), nullable=True),
        sa.Column("surface", sa.String(length=50), nullable=True),
        sa.Column("target", sa.String(length=100), nullable=True),
        sa.Column("channel", sa.String(length=30), nullable=True),
        sa.Column("value", sa.Float(), nullable=False, server_default="1.0"),
        sa.Column("event_date", sa.Date(), nullable=False, server_default=sa.text("CURRENT_DATE")),
        sa.Column("metadata", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("CURRENT_TIMESTAMP")),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_analytics_events_tenant_id"), "analytics_events", ["tenant_id"], unique=False)
    op.create_index(op.f("ix_analytics_events_user_id"), "analytics_events", ["user_id"], unique=False)
    op.create_index(op.f("ix_analytics_events_event_name"), "analytics_events", ["event_name"], unique=False)
    op.create_index(op.f("ix_analytics_events_event_family"), "analytics_events", ["event_family"], unique=False)
    op.create_index(op.f("ix_analytics_events_surface"), "analytics_events", ["surface"], unique=False)
    op.create_index(op.f("ix_analytics_events_target"), "analytics_events", ["target"], unique=False)
    op.create_index(op.f("ix_analytics_events_channel"), "analytics_events", ["channel"], unique=False)
    op.create_index(op.f("ix_analytics_events_event_date"), "analytics_events", ["event_date"], unique=False)
    op.create_index(op.f("ix_analytics_events_occurred_at"), "analytics_events", ["occurred_at"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_analytics_events_occurred_at"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_event_date"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_channel"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_target"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_surface"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_event_family"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_event_name"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_user_id"), table_name="analytics_events")
    op.drop_index(op.f("ix_analytics_events_tenant_id"), table_name="analytics_events")
    op.drop_table("analytics_events")
