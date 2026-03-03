"""Add unique constraint for assignment submissions per student.

Revision ID: 20260303_0001
Revises:
Create Date: 2026-03-03
"""

from typing import Sequence, Union

from alembic import op
from sqlalchemy import inspect

# revision identifiers, used by Alembic.
revision: str = "20260303_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "assignment_submissions" not in inspector.get_table_names():
        return

    existing = {constraint.get("name") for constraint in inspector.get_unique_constraints("assignment_submissions")}
    if "uq_assignment_submissions_student" in existing:
        return

    op.create_unique_constraint(
        "uq_assignment_submissions_student",
        "assignment_submissions",
        ["tenant_id", "assignment_id", "student_id"],
    )


def downgrade() -> None:
    bind = op.get_bind()
    inspector = inspect(bind)
    if "assignment_submissions" not in inspector.get_table_names():
        return

    existing = {constraint.get("name") for constraint in inspector.get_unique_constraints("assignment_submissions")}
    if "uq_assignment_submissions_student" not in existing:
        return

    op.drop_constraint(
        "uq_assignment_submissions_student",
        "assignment_submissions",
        type_="unique",
    )
