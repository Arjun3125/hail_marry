"""Add notebook_id to kg_concepts table.

Revision ID: 20260327_0009
Revises: 20260327_0008
Create Date: 2026-03-27 16:30:00.000000+00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from sqlalchemy.engine.reflection import Inspector

# revision identifiers, used by Alembic.
revision: str = '20260327_0009'
down_revision: Union[str, None] = '20260327_0008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_index(inspector: Inspector, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in inspector.get_indexes(table_name))


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    inspector = Inspector.from_engine(conn)

    table_names = inspector.get_table_names()
    if "kg_concepts" not in table_names:
        return

    columns = {col["name"] for col in inspector.get_columns("kg_concepts")}
    if "notebook_id" not in columns:
        op.add_column(
            "kg_concepts",
            sa.Column("notebook_id", postgresql.UUID(as_uuid=True), nullable=True),
        )
        columns.add("notebook_id")

        if dialect == "postgresql" and "notebooks" in table_names:
            op.create_foreign_key(
                "fk_kg_concepts_notebook_id",
                "kg_concepts",
                "notebooks",
                ["notebook_id"],
                ["id"],
                ondelete="CASCADE",
            )

    inspector = Inspector.from_engine(conn)
    if "notebook_id" in columns and not _has_index(
        inspector, "kg_concepts", "idx_kg_concepts_notebook_id"
    ):
        op.create_index(
            "idx_kg_concepts_notebook_id",
            "kg_concepts",
            ["notebook_id"],
        )

    if {"tenant_id", "notebook_id"}.issubset(columns) and not _has_index(
        inspector, "kg_concepts", "idx_kg_concepts_tenant_notebook"
    ):
        op.create_index(
            "idx_kg_concepts_tenant_notebook",
            "kg_concepts",
            ["tenant_id", "notebook_id"],
        )


def downgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    inspector = Inspector.from_engine(conn)

    if "kg_concepts" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("kg_concepts")}
    if "notebook_id" not in columns:
        return

    if _has_index(inspector, "kg_concepts", "idx_kg_concepts_tenant_notebook"):
        op.drop_index("idx_kg_concepts_tenant_notebook", "kg_concepts")
    if _has_index(inspector, "kg_concepts", "idx_kg_concepts_notebook_id"):
        op.drop_index("idx_kg_concepts_notebook_id", "kg_concepts")

    if dialect == "postgresql":
        foreign_keys = {
            fk["name"]
            for fk in inspector.get_foreign_keys("kg_concepts")
            if fk.get("name")
        }
        if "fk_kg_concepts_notebook_id" in foreign_keys:
            op.drop_constraint("fk_kg_concepts_notebook_id", "kg_concepts", type_="foreignkey")

    op.drop_column("kg_concepts", "notebook_id")
