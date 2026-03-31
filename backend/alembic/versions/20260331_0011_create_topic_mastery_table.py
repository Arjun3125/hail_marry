"""create topic_mastery table

Revision ID: 20260331_0011
Revises: 20260328_0010
Create Date: 2026-03-31

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import UUID


revision = "20260331_0011"
down_revision = "20260328_0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "topic_mastery" in inspector.get_table_names():
        return

    op.create_table(
        "topic_mastery",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("tenant_id", UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", UUID(as_uuid=True), nullable=False),
        sa.Column("subject_id", UUID(as_uuid=True), nullable=True),
        sa.Column("topic", sa.String(length=255), nullable=False),
        sa.Column("concept", sa.String(length=255), nullable=False, server_default="core"),
        sa.Column("mastery_score", sa.Float(), nullable=False, server_default="55"),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default="0.15"),
        sa.Column("evidence_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_evidence_type", sa.String(length=50), nullable=True),
        sa.Column("last_evidence_score", sa.Float(), nullable=True),
        sa.Column("last_evidence_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("review_due_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("tenant_id", "user_id", "topic", "concept", name="uq_topic_mastery_user_topic_concept"),
    )
    op.create_index("ix_topic_mastery_tenant_id", "topic_mastery", ["tenant_id"])
    op.create_index("ix_topic_mastery_user_id", "topic_mastery", ["user_id"])
    op.create_index("ix_topic_mastery_subject_id", "topic_mastery", ["subject_id"])
    op.create_index("ix_topic_mastery_topic", "topic_mastery", ["topic"])
    op.create_index("ix_topic_mastery_concept", "topic_mastery", ["concept"])

    if dialect == "postgresql":
        op.create_foreign_key("fk_topic_mastery_tenant", "topic_mastery", "tenants", ["tenant_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key("fk_topic_mastery_user", "topic_mastery", "users", ["user_id"], ["id"], ondelete="CASCADE")
        op.create_foreign_key("fk_topic_mastery_subject", "topic_mastery", "subjects", ["subject_id"], ["id"], ondelete="SET NULL")


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "topic_mastery" not in inspector.get_table_names():
        return

    if dialect == "postgresql":
        op.drop_constraint("fk_topic_mastery_subject", "topic_mastery", type_="foreignkey")
        op.drop_constraint("fk_topic_mastery_user", "topic_mastery", type_="foreignkey")
        op.drop_constraint("fk_topic_mastery_tenant", "topic_mastery", type_="foreignkey")

    op.drop_index("ix_topic_mastery_concept", table_name="topic_mastery")
    op.drop_index("ix_topic_mastery_topic", table_name="topic_mastery")
    op.drop_index("ix_topic_mastery_subject_id", table_name="topic_mastery")
    op.drop_index("ix_topic_mastery_user_id", table_name="topic_mastery")
    op.drop_index("ix_topic_mastery_tenant_id", table_name="topic_mastery")
    op.drop_table("topic_mastery")
