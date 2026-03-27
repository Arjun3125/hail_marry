"""create generated_content table

Revision ID: 20260327_0008
Revises: 20260327_0007
Create Date: 2026-03-27

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector
from sqlalchemy.dialects.postgresql import UUID, JSONB


revision = "20260327_0008"
down_revision = "20260327_0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    # Create generated_content table
    if "generated_content" not in inspector.get_table_names():
        op.create_table(
            "generated_content",
            sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
            sa.Column("notebook_id", UUID(as_uuid=True), sa.ForeignKey("notebooks.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True),
            sa.Column("type", sa.String(50), nullable=False, index=True),  # 'quiz', 'flashcards', 'mindmap', 'flowchart', 'concept_map'
            sa.Column("title", sa.String(255), nullable=True),
            sa.Column("content", JSONB, nullable=False),
            sa.Column("source_query", sa.Text(), nullable=True),
            sa.Column("parent_conversation_id", UUID(as_uuid=True), sa.ForeignKey("ai_history.id", ondelete="SET NULL"), nullable=True),
            sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()")),
            sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("NOW()"), onupdate=sa.text("NOW()")),
            sa.Column("is_archived", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        )
        
        # Create composite index for efficient querying
        op.create_index(
            "idx_generated_content_notebook_type",
            "generated_content",
            ["notebook_id", "type"]
        )


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    
    if "generated_content" in inspector.get_table_names():
        op.drop_index("idx_generated_content_notebook_type", "generated_content")
        op.drop_table("generated_content")
