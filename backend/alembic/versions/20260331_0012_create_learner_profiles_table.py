"""create learner_profiles table

Revision ID: 20260331_0012
Revises: 20260331_0011
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision = "20260331_0012"
down_revision = "20260331_0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name
    json_array_default = sa.text("'[]'::jsonb") if dialect == "postgresql" else sa.text("'[]'")
    json_object_default = sa.text("'{}'::jsonb") if dialect == "postgresql" else sa.text("'{}'")

    if "learner_profiles" in inspector.get_table_names():
        return

    op.create_table(
        "learner_profiles",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("preferred_language", sa.String(length=32), nullable=False, server_default="english"),
        sa.Column("inferred_expertise_level", sa.String(length=32), nullable=False, server_default="standard"),
        sa.Column("preferred_response_length", sa.String(length=32), nullable=False, server_default="default"),
        sa.Column("primary_subjects", JSONB(astext_type=sa.Text()), nullable=False, server_default=json_array_default),
        sa.Column("engagement_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("consistency_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("signal_summary", JSONB(astext_type=sa.Text()), nullable=False, server_default=json_object_default),
        sa.Column("last_recomputed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "user_id", name="uq_learner_profiles_tenant_user"),
    )
    op.create_index("ix_learner_profiles_tenant_id", "learner_profiles", ["tenant_id"])
    op.create_index("ix_learner_profiles_user_id", "learner_profiles", ["user_id"])

    if dialect == "postgresql":
        op.create_foreign_key("fk_learner_profiles_tenant", "learner_profiles", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key("fk_learner_profiles_user", "learner_profiles", "users", ["user_id"], ["id"], ondelete="CASCADE")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "learner_profiles" not in inspector.get_table_names():
        return

    if dialect == "postgresql":
        op.drop_constraint("fk_learner_profiles_user", "learner_profiles", type_="foreignkey")
        op.drop_constraint("fk_learner_profiles_tenant", "learner_profiles", type_="foreignkey")

    op.drop_index("ix_learner_profiles_user_id", table_name="learner_profiles")
    op.drop_index("ix_learner_profiles_tenant_id", table_name="learner_profiles")
    op.drop_table("learner_profiles")
