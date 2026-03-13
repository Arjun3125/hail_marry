"""add qr_login_expires_at to users

Revision ID: 20260312_0005
Revises: 20260307_0004
Create Date: 2026-03-12

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.engine.reflection import Inspector


revision = "20260312_0005"
down_revision = "20260307_0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    if "users" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("users")]
        if "qr_login_expires_at" not in columns:
            op.add_column("users", sa.Column("qr_login_expires_at", sa.DateTime(timezone=True), nullable=True))


def downgrade() -> None:
    conn = op.get_bind()
    inspector = Inspector.from_engine(conn)
    if "users" in inspector.get_table_names():
        columns = [c["name"] for c in inspector.get_columns("users")]
        if "qr_login_expires_at" in columns:
            op.drop_column("users", "qr_login_expires_at")
