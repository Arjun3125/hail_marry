"""add tenant_id to notebooks and generated_content

Revision ID: 20260328_0010
Revises: 20260327_0009
Create Date: 2026-03-28

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import UUID


revision = "20260328_0010"
down_revision = "20260327_0009"
branch_labels = None
depends_on = None


def _has_index(inspector: Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "notebooks" in inspector.get_table_names():
        notebook_columns = [col["name"] for col in inspector.get_columns("notebooks")]
        if "tenant_id" not in notebook_columns:
            op.add_column("notebooks", sa.Column("tenant_id", UUID(as_uuid=True), nullable=True))
            if dialect == "postgresql":
                op.create_foreign_key(
                    "fk_notebooks_tenant",
                    "notebooks",
                    "tenants",
                    ["tenant_id"],
                    ["id"],
                    ondelete="CASCADE",
                )
        conn.execute(
            sa.text(
                """
                UPDATE notebooks
                SET tenant_id = (
                    SELECT users.tenant_id
                    FROM users
                    WHERE users.id = notebooks.user_id
                )
                WHERE tenant_id IS NULL
                """
            )
        )
        if not _has_index(inspector, "notebooks", "idx_notebooks_tenant_id"):
            op.create_index("idx_notebooks_tenant_id", "notebooks", ["tenant_id"])
        if dialect == "postgresql":
            op.alter_column("notebooks", "tenant_id", nullable=False)

    inspector = Inspector.from_engine(conn)
    if "generated_content" in inspector.get_table_names():
        content_columns = [col["name"] for col in inspector.get_columns("generated_content")]
        if "tenant_id" not in content_columns:
            op.add_column("generated_content", sa.Column("tenant_id", UUID(as_uuid=True), nullable=True))
            if dialect == "postgresql":
                op.create_foreign_key(
                    "fk_generated_content_tenant",
                    "generated_content",
                    "tenants",
                    ["tenant_id"],
                    ["id"],
                    ondelete="CASCADE",
                )
        conn.execute(
            sa.text(
                """
                UPDATE generated_content
                SET tenant_id = (
                    SELECT notebooks.tenant_id
                    FROM notebooks
                    WHERE notebooks.id = generated_content.notebook_id
                )
                WHERE tenant_id IS NULL
                """
            )
        )
        if not _has_index(inspector, "generated_content", "idx_generated_content_tenant_id"):
            op.create_index("idx_generated_content_tenant_id", "generated_content", ["tenant_id"])
        if dialect == "postgresql":
            op.alter_column("generated_content", "tenant_id", nullable=False)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    if "generated_content" in inspector.get_table_names():
        content_columns = [col["name"] for col in inspector.get_columns("generated_content")]
        if "tenant_id" in content_columns:
            if _has_index(inspector, "generated_content", "idx_generated_content_tenant_id"):
                op.drop_index("idx_generated_content_tenant_id", "generated_content")
            if dialect == "postgresql":
                op.drop_constraint("fk_generated_content_tenant", "generated_content", type_="foreignkey")
            op.drop_column("generated_content", "tenant_id")

    inspector = Inspector.from_engine(conn)
    if "notebooks" in inspector.get_table_names():
        notebook_columns = [col["name"] for col in inspector.get_columns("notebooks")]
        if "tenant_id" in notebook_columns:
            if _has_index(inspector, "notebooks", "idx_notebooks_tenant_id"):
                op.drop_index("idx_notebooks_tenant_id", "notebooks")
            if dialect == "postgresql":
                op.drop_constraint("fk_notebooks_tenant", "notebooks", type_="foreignkey")
            op.drop_column("notebooks", "tenant_id")
