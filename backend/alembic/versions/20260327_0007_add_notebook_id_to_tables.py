"""add notebook_id to ai_history and documents tables

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
    
    # Add notebook_id to ai_history table
    if "ai_history" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("ai_history")]
        if "notebook_id" not in columns:
            op.add_column(
                "ai_history",
                sa.Column("notebook_id", UUID(as_uuid=True), nullable=True)
            )
            # Only create foreign key on PostgreSQL (SQLite doesn't support ALTER for constraints)
            if dialect == "postgresql":
                op.create_foreign_key(
                    "fk_ai_history_notebook",
                    "ai_history",
                    "notebooks",
                    ["notebook_id"],
                    ["id"],
                    ondelete="SET NULL"
                )
            op.create_index("idx_ai_history_notebook", "ai_history", ["notebook_id"])
    
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
    
    # Remove notebook_id from ai_history table
    if "ai_history" in inspector.get_table_names():
        columns = [col["name"] for col in inspector.get_columns("ai_history")]
        if "notebook_id" in columns:
            op.drop_index("idx_ai_history_notebook", "ai_history")
            op.drop_constraint("fk_ai_history_notebook", "ai_history", type_="foreignkey")
            op.drop_column("ai_history", "notebook_id")
