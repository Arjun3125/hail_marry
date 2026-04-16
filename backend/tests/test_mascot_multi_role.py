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


def test_assemble_context_for_role_dispatches_correctly():
    from src.domains.mascot.services.context_assembler import assemble_context_for_role
    from src.domains.mascot.services.teacher_context_assembler import TeacherContext
    from src.domains.mascot.services.parent_context_assembler import ParentContext
    from src.domains.mascot.services.admin_context_assembler import AdminContext

    db = _make_db()
    db.query.return_value.filter.return_value.count.return_value = 0
    uid = uuid.uuid4()
    tid = uuid.uuid4()

    teacher_ctx = assemble_context_for_role(db, uid, tid, "Sir Ramesh", "teacher")
    parent_ctx = assemble_context_for_role(db, uid, tid, "Sunita Ji", "parent")
    admin_ctx = assemble_context_for_role(db, uid, tid, "Principal", "admin")

    assert isinstance(teacher_ctx, TeacherContext)
    assert isinstance(parent_ctx, ParentContext)
    assert isinstance(admin_ctx, AdminContext)


def test_build_teacher_system_prompt_contains_role_identity():
    from src.domains.mascot.services.teacher_context_assembler import TeacherContext
    from src.domains.mascot.services.prompt_builder import build_mascot_system_prompt

    ctx = TeacherContext(teacher_name="Sir Ramesh", user_id="x", tenant_id="y")
    prompt = build_mascot_system_prompt(ctx, role="teacher")
    assert "teacher" in prompt.lower() or "Teacher" in prompt


def test_find_tool_returns_spec_for_valid_role():
    from src.domains.mascot.services.tool_dispatcher import _find_tool

    spec = _find_tool("get_student_attendance", "student")
    assert spec is not None
    assert spec.name == "get_student_attendance"

    no_spec = _find_tool("get_student_attendance", "teacher")
    assert no_spec is None


def test_find_tool_returns_none_for_unknown_tool():
    from src.domains.mascot.services.tool_dispatcher import _find_tool

    assert _find_tool("nonexistent_tool", "student") is None
