"""create notebooks table

Revision ID: 20260327_0006
Revises: 20260312_0005
Create Date: 2026-03-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import UUID


revision = "20260327_0006"
down_revision = "20260312_0005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Create notebooks table
    if "notebooks" not in inspector.get_table_names():
        op.create_table(
            "notebooks",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
            sa.Column("name", sa.String(255), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("subject", sa.String(100), nullable=True),
            sa.Column("color", sa.String(7), nullable=False, server_default="#6366f1"),
            sa.Column("icon", sa.String(50), nullable=False, server_default="Book"),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        )
        
        # Create indexes
        op.create_index("idx_notebooks_user_id", "notebooks", ["user_id"])
        op.create_index("idx_notebooks_is_active", "notebooks", ["is_active"])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    if "notebooks" in inspector.get_table_names():
        op.drop_index("idx_notebooks_is_active", "notebooks")
        op.drop_index("idx_notebooks_user_id", "notebooks")
        op.drop_table("notebooks")
