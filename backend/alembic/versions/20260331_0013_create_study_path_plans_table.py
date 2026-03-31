"""create study_path_plans table

Revision ID: 20260331_0013
Revises: 20260331_0012
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import JSONB, UUID


revision = "20260331_0013"
down_revision = "20260331_0012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "study_path_plans" in inspector.get_table_names():
        return

    op.create_table(
        "study_path_plans",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("notebook_id", UUID(as_uuid=True), nullable=True),
        sa.Column("subject_id", UUID(as_uuid=True), nullable=True),
        sa.Column("plan_type", sa.String(length=32), nullable=False, server_default="remediation"),
        sa.Column("focus_topic", sa.String(length=255), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False, server_default="active"),
        sa.Column("current_step_index", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("items", JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'[]'::jsonb")),
        sa.Column("source_context", JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_study_path_plans_tenant_id", "study_path_plans", ["tenant_id"])
    op.create_index("ix_study_path_plans_user_id", "study_path_plans", ["user_id"])
    op.create_index("ix_study_path_plans_notebook_id", "study_path_plans", ["notebook_id"])
    op.create_index("ix_study_path_plans_subject_id", "study_path_plans", ["subject_id"])
    op.create_index("ix_study_path_plans_focus_topic", "study_path_plans", ["focus_topic"])

    if dialect == "postgresql":
        op.create_foreign_key("fk_study_path_plans_tenant", "study_path_plans", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key("fk_study_path_plans_user", "study_path_plans", "users", ["user_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key("fk_study_path_plans_notebook", "study_path_plans", "notebooks", ["notebook_id"], ["id"], ondelete="SET NULL")
        op.create_foreign_key("fk_study_path_plans_subject", "study_path_plans", "subjects", ["subject_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "study_path_plans" not in inspector.get_table_names():
        return

    if dialect == "postgresql":
        op.drop_constraint("fk_study_path_plans_subject", "study_path_plans", type_="foreignkey")
        op.drop_constraint("fk_study_path_plans_notebook", "study_path_plans", type_="foreignkey")
        op.drop_constraint("fk_study_path_plans_user", "study_path_plans", type_="foreignkey")
        op.drop_constraint("fk_study_path_plans_tenant", "study_path_plans", type_="foreignkey")

    op.drop_index("ix_study_path_plans_focus_topic", table_name="study_path_plans")
    op.drop_index("ix_study_path_plans_subject_id", table_name="study_path_plans")
    op.drop_index("ix_study_path_plans_notebook_id", table_name="study_path_plans")
    op.drop_index("ix_study_path_plans_user_id", table_name="study_path_plans")
    op.drop_index("ix_study_path_plans_tenant_id", table_name="study_path_plans")
    op.drop_table("study_path_plans")
