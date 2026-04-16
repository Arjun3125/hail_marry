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


def test_run_mascot_agent_accepts_role_param():
    import inspect
    from src.domains.mascot.services.mascot_agent import run_mascot_agent
    sig = inspect.signature(run_mascot_agent)
    assert "role" in sig.parameters


def test_mascot_agent_state_has_role_field():
    from src.domains.mascot.services.mascot_agent import MascotAgentState
    assert "role" in MascotAgentState.__annotations__
    assert "tool_result" in MascotAgentState.__annotations__


def test_teacher_can_access_mascot_chat(client, db_session, active_tenant):
    """Teacher role must NOT get 403 from /api/mascot/chat."""
    from unittest.mock import patch, AsyncMock
    from src.domains.identity.routes.auth import pwd_context
    from auth.jwt import create_access_token
    from src.domains.identity.models.user import User

    _PRECOMPUTED_HASH = pwd_context.hash("pass123!")

    # Create teacher user
    teacher = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="teacher-mascot@testschool.edu",
        full_name="Sir Ramesh",
        role="teacher",
        hashed_password=_PRECOMPUTED_HASH,
        is_active=True,
    )
    db_session.add(teacher)
    db_session.commit()

    # Mint token
    token = create_access_token({
        "user_id": str(teacher.id),
        "tenant_id": str(active_tenant.id),
        "email": "teacher-mascot@testschool.edu",
        "role": "teacher",
    })

    with patch(
        "src.domains.mascot.routes.chat_route.run_mascot_agent",
        new_callable=AsyncMock,
        return_value={"response": "Namaste Teacher!", "response_type": "text"},
    ):
        response = client.post(
            "/api/mascot/chat",
            headers={"Authorization": f"Bearer {token}"},
            json={"message": "Aaj ki attendance?"},
        )

    assert response.status_code == 200, response.text
    assert "Namaste" in response.json()["response"]


def test_greeting_endpoint_returns_greeting_for_student(client, db_session, active_tenant):
    """GET /api/mascot/greeting returns {greeting, chips, has_urgent} for any role."""
    from unittest.mock import patch, AsyncMock
    from src.domains.identity.routes.auth import pwd_context
    from auth.jwt import create_access_token
    from src.domains.identity.models.user import User

    _PRECOMPUTED_HASH = pwd_context.hash("pass123!")

    # Create student user
    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-greeting@testschool.edu",
        full_name="Arjun",
        role="student",
        hashed_password=_PRECOMPUTED_HASH,
        is_active=True,
    )
    db_session.add(student)
    db_session.commit()

    # Mint token
    token = create_access_token({
        "user_id": str(student.id),
        "tenant_id": str(active_tenant.id),
        "email": "student-greeting@testschool.edu",
        "role": "student",
    })

    with patch(
        "src.domains.mascot.routes.chat_route._generate_greeting",
        new_callable=AsyncMock,
        return_value="Good morning! Ready to learn. 🦉",
    ):
        response = client.get(
            "/api/mascot/greeting",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200, response.text
    data = response.json()
    assert "greeting" in data
    assert "chips" in data
    assert "has_urgent" in data
    assert isinstance(data["chips"], list)
    assert isinstance(data["has_urgent"], bool)
