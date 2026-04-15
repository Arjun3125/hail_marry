"""Tests for mascot multi-role context assemblers and routing."""
import uuid
from unittest.mock import MagicMock


def _make_db():
    db = MagicMock()
    db.query.return_value.filter.return_value.first.return_value = None
    db.query.return_value.filter.return_value.all.return_value = []
    db.query.return_value.filter.return_value.limit.return_value.all.return_value = []
    db.query.return_value.filter.return_value.order_by.return_value.limit.return_value.all.return_value = []
    return db


def test_assemble_teacher_context_returns_dataclass():
    from src.domains.mascot.services.teacher_context_assembler import (
        TeacherContext,
        assemble_teacher_context,
    )

    db = _make_db()
    ctx = assemble_teacher_context(db, uuid.uuid4(), uuid.uuid4(), "Sir Ramesh")

    assert isinstance(ctx, TeacherContext)
    assert ctx.teacher_name == "Sir Ramesh"
    assert ctx.absent_count_today == 0
    assert isinstance(ctx.absent_students, list)
    assert isinstance(ctx.todays_classes, list)
    assert isinstance(ctx.consecutive_absentees, list)
    assert ctx.to_prompt_context().startswith("TEACHER:")


def test_assemble_parent_context_returns_dataclass():
    from src.domains.mascot.services.parent_context_assembler import (
        ParentContext,
        assemble_parent_context,
    )

    db = _make_db()
    ctx = assemble_parent_context(db, uuid.uuid4(), uuid.uuid4(), "Sunita Ji")

    assert isinstance(ctx, ParentContext)
    assert ctx.parent_name == "Sunita Ji"
    assert ctx.attendance_today in ("Present", "Absent", "Unknown")
    assert isinstance(ctx.latest_marks, list)
    assert isinstance(ctx.weak_subjects, list)
    assert isinstance(ctx.fee_due, bool)
    assert ctx.to_prompt_context().startswith("PARENT:")


def test_assemble_admin_context_returns_dataclass():
    from src.domains.mascot.services.admin_context_assembler import (
        AdminContext,
        assemble_admin_context,
    )

    db = _make_db()
    db.query.return_value.filter.return_value.count.return_value = 0
    ctx = assemble_admin_context(db, uuid.uuid4(), uuid.uuid4(), "Principal Sharma")

    assert isinstance(ctx, AdminContext)
    assert ctx.admin_name == "Principal Sharma"
    assert isinstance(ctx.total_students, int)
    assert isinstance(ctx.open_alerts, int)
    assert isinstance(ctx.queue_pending, int)
    assert ctx.to_prompt_context().startswith("ADMIN:")
