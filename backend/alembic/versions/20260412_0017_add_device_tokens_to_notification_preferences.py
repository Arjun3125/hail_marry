"""Add device_tokens field to notification_preferences for FCM push notifications.

Revision ID: 20260412_0017
Revises: 20260406_0016
Create Date: 2026-04-12
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260412_0017'
down_revision = '20260406_0016'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add device_tokens column to notification_preferences."""
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    existing_columns = {col["name"] for col in inspector.get_columns("notification_preferences")}
    if "device_tokens" not in existing_columns:
        op.add_column(
            'notification_preferences',
            sa.Column(
                'device_tokens',
                postgresql.JSONB(astext_type=sa.Text()),
                nullable=True,
                comment='Stored as JSON array of FCM device tokens for push notifications'
            )
        )


def downgrade() -> None:
    """Remove device_tokens column from notification_preferences."""
    op.drop_column('notification_preferences', 'device_tokens')
