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


def _index_names(inspector, table_name: str) -> set[str]:
    return {index["name"] for index in inspector.get_indexes(table_name)}


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    table_names = set(inspector.get_table_names())

    if "analytics_events" not in table_names:
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
        analytics_event_indexes: set[str] = set()
    else:
        analytics_event_indexes = _index_names(inspector, "analytics_events")

    index_definitions = (
        (op.f("ix_analytics_events_tenant_id"), ["tenant_id"]),
        (op.f("ix_analytics_events_user_id"), ["user_id"]),
        (op.f("ix_analytics_events_event_name"), ["event_name"]),
        (op.f("ix_analytics_events_event_family"), ["event_family"]),
        (op.f("ix_analytics_events_surface"), ["surface"]),
        (op.f("ix_analytics_events_target"), ["target"]),
        (op.f("ix_analytics_events_channel"), ["channel"]),
        (op.f("ix_analytics_events_event_date"), ["event_date"]),
        (op.f("ix_analytics_events_occurred_at"), ["occurred_at"]),
    )
    for index_name, columns in index_definitions:
        if index_name not in analytics_event_indexes:
            op.create_index(index_name, "analytics_events", columns, unique=False)


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
