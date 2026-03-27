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


def upgrade() -> None:
    conn = op.get_bind()
    dialect = conn.dialect.name
    inspector = Inspector.from_engine(conn)
    
    # Check if column already exists
    columns = [col["name"] for col in inspector.get_columns("kg_concepts")]
    if "notebook_id" in columns:
        return  # Column already exists, skip migration
    
    # Add notebook_id column to kg_concepts table
    op.add_column(
        'kg_concepts',
        sa.Column('notebook_id', postgresql.UUID(as_uuid=True), nullable=True)
    )
    
    # Create foreign key constraint only on PostgreSQL
    if dialect == "postgresql":
        op.create_foreign_key(
            'fk_kg_concepts_notebook_id',
            'kg_concepts',
            'notebooks',
            ['notebook_id'],
            ['id'],
            ondelete='CASCADE'
        )
    
    # Create index for faster queries
    op.create_index(
        'idx_kg_concepts_notebook_id',
        'kg_concepts',
        ['notebook_id']
    )
    
    # Create composite index for tenant + notebook queries
    op.create_index(
        'idx_kg_concepts_tenant_notebook',
        'kg_concepts',
        ['tenant_id', 'notebook_id']
    )


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_kg_concepts_tenant_notebook')
    op.drop_index('idx_kg_concepts_notebook_id')
    
    # Drop foreign key
    op.drop_constraint('fk_kg_concepts_notebook_id', 'kg_concepts', type_='foreignkey')
    
    # Drop column
    op.drop_column('kg_concepts', 'notebook_id')
