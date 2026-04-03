"""add notebook_id to ai query history and documents tables

Revision ID: 20260327_0007
Revises: 20260327_0006
Create Date: 2026-03-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import UUID


revision = "20260327_0007"
down_revision = "20260327_0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    dialect = conn.dialect.name

    history_table = "ai_queries" if "ai_queries" in inspector.get_table_names() else "ai_history"
    history_fk_name = "fk_ai_queries_notebook" if history_table == "ai_queries" else "fk_ai_history_notebook"
    history_idx_name = "idx_ai_queries_notebook" if history_table == "ai_queries" else "idx_ai_history_notebook"

    # Add notebook_id to the persisted AI history table.
    if history_table in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns(history_table)]
        if "notebook_id" not in columns:
            op.add_column(
                history_table,
                sa.Column("notebook_id", UUID(as_uuid=True), nullable=True)
            )
            # Only create foreign key on PostgreSQL (SQLite doesn't support ALTER for constraints)
            if dialect == "postgresql":
                op.create_foreign_key(
                    history_fk_name,
                    history_table,
                    "notebooks",
                    ["notebook_id"],
                    ["id"],
                    ondelete="SET NULL"
                )
            op.create_index(history_idx_name, history_table, ["notebook_id"])
    
    # Add notebook_id to documents table
    if "documents" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("documents")]
        if "notebook_id" not in columns:
            op.add_column(
                "documents",
                sa.Column("notebook_id", UUID(as_uuid=True), nullable=True)
            )
            # Only create foreign key on PostgreSQL (SQLite doesn't support ALTER for constraints)
            if dialect == "postgresql":
                op.create_foreign_key(
                    "fk_documents_notebook",
                    "documents",
                    "notebooks",
                    ["notebook_id"],
                    ["id"],
                    ondelete="SET NULL"
                )
            op.create_index("idx_documents_notebook", "documents", ["notebook_id"])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)

    # Remove notebook_id from documents table
    if "documents" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("documents")]
        if "notebook_id" in columns:
            op.drop_index("idx_documents_notebook", "documents")
            op.drop_constraint("fk_documents_notebook", "documents", type_="foreignkey")
            op.drop_column("documents", "notebook_id")

    for history_table, history_idx_name, history_fk_name in (
        ("ai_queries", "idx_ai_queries_notebook", "fk_ai_queries_notebook"),
        ("ai_history", "idx_ai_history_notebook", "fk_ai_history_notebook"),
    ):
        if history_table in inspector.get_table_names():
            columns = [col["name"] for col in inspector.get_columns(history_table)]
            if "notebook_id" in columns:
                op.drop_index(history_idx_name, history_table)
                op.drop_constraint(history_fk_name, history_table, type_="foreignkey")
                op.drop_column(history_table, "notebook_id")
