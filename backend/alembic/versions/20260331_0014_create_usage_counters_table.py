"""create usage_counters table

Revision ID: 20260331_0014
Revises: 20260331_0013
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import UUID


revision = "20260331_0014"
down_revision = "20260331_0013"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "usage_counters" in inspector.get_table_names():
        return

    op.create_table(
        "usage_counters",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=True),
        sa.Column("scope", sa.String(length=16), nullable=False, server_default="user"),
        sa.Column("metric", sa.String(length=64), nullable=False),
        sa.Column("bucket_type", sa.String(length=16), nullable=False),
        sa.Column("bucket_start", sa.Date(), nullable=False),
        sa.Column("count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("token_total", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("cache_hits", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_cost_units", sa.Float(), nullable=False, server_default="0"),
        sa.Column("last_model", sa.String(length=128), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_usage_counters_tenant_id", "usage_counters", ["tenant_id"])
    op.create_index("ix_usage_counters_user_id", "usage_counters", ["user_id"])
    op.create_index("ix_usage_counters_scope", "usage_counters", ["scope"])
    op.create_index("ix_usage_counters_metric", "usage_counters", ["metric"])
    op.create_index("ix_usage_counters_bucket_type", "usage_counters", ["bucket_type"])
    op.create_index("ix_usage_counters_bucket_start", "usage_counters", ["bucket_start"])

    if dialect == "postgresql":
        op.create_foreign_key("fk_usage_counters_tenant", "usage_counters", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key("fk_usage_counters_user", "usage_counters", "users", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "usage_counters" not in inspector.get_table_names():
        return

    if dialect == "postgresql":
        op.drop_constraint("fk_usage_counters_user", "usage_counters", type_="foreignkey")
        op.drop_constraint("fk_usage_counters_tenant", "usage_counters", type_="foreignkey")

    op.drop_index("ix_usage_counters_bucket_start", table_name="usage_counters")
    op.drop_index("ix_usage_counters_bucket_type", table_name="usage_counters")
    op.drop_index("ix_usage_counters_metric", table_name="usage_counters")
    op.drop_index("ix_usage_counters_scope", table_name="usage_counters")
    op.drop_index("ix_usage_counters_user_id", table_name="usage_counters")
    op.drop_index("ix_usage_counters_tenant_id", table_name="usage_counters")
    op.drop_table("usage_counters")
