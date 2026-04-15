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
