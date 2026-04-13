import json
import uuid
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock

# Pre-compute the password hash ONCE at module load (not per-test).
from src.domains.identity.routes.auth import pwd_context
_PRECOMPUTED_HASH = pwd_context.hash("pass123!")


def _create_user_and_login(client, db_session, tenant_id, *, email: str, role: str = "student"):
    from auth.jwt import create_access_token
    from src.domains.identity.models.user import User

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="Mascot Tester",
        role=role,
        hashed_password=_PRECOMPUTED_HASH,
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    # Mint JWT directly — skip the HTTP round-trip through /api/auth/login.
    token = create_access_token({
        "user_id": str(user.id),
        "tenant_id": str(tenant_id),
        "email": email,
        "role": role,
    })
    return user, token


def test_mascot_creates_notebook_and_returns_ai_studio_navigation(client, db_session, active_tenant):
    from src.domains.platform.models.notebook import Notebook

    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-create@testschool.edu",
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create notebook for Biology Chapter 10", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "notebook_create"
    assert payload["navigation"]["href"] == "/student/ai-studio"
    assert payload["notebook_id"]
    notebook = db_session.query(Notebook).filter(Notebook.id == uuid.UUID(payload["notebook_id"])).first()
    assert notebook is not None
    assert notebook.name == "Biology Chapter 10"


def test_mascot_generates_flashcards_and_saves_generated_content(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.generated_content import GeneratedContent
    from src.domains.platform.models.notebook import Notebook

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-flashcards@testschool.edu",
    )

    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Biology",
        subject="Biology",
    )
    db_session.add(notebook)
    db_session.commit()

    run_study_tool = AsyncMock(
        return_value={
            "data": [{"front": "Light reaction", "back": "Captures sunlight", "citation": "[Bio_10]"}],
            "citations": [{"source": "Class 10 Biology", "page": "10"}],
        }
    )
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.run_study_tool", run_study_tool)

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Generate flashcards for photosynthesis",
            "channel": "web",
            "notebook_id": str(notebook.id),
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "study_tool"
    assert payload["artifacts"][0]["tool"] == "flashcards"
    saved = db_session.query(GeneratedContent).filter(GeneratedContent.notebook_id == notebook.id).first()
    assert saved is not None
    assert saved.type == "flashcards"
    run_study_tool.assert_awaited_once()


def test_mascot_navigation_request_returns_teacher_route(client, db_session, active_tenant):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher@testschool.edu",
        role="teacher",
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Open attendance page", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "navigate"
    assert payload["navigation"]["href"] == "/teacher/attendance"


def test_mascot_study_path_report_returns_plan_summary(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-study-path@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.get_or_create_study_path",
        lambda *args, **kwargs: {
            "id": "plan-1",
            "focus_topic": "Photosynthesis",
            "status": "active",
            "items": [
                {"id": "guide", "title": "Relearn Photosynthesis", "target_tool": "study_guide", "status": "pending"},
                {"id": "flashcards", "title": "Memorize weak concepts", "target_tool": "flashcards", "status": "pending"},
            ],
            "next_action": {"id": "guide", "title": "Relearn Photosynthesis", "target_tool": "study_guide", "status": "pending"},
            "source_context": {},
        },
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show my study path", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "study_path_report"
    assert payload["artifacts"][0]["tool"] == "study_path"
    assert "Photosynthesis" in payload["reply_text"]
    assert payload["follow_up_suggestions"][0] == "Continue learning"


def test_mascot_continue_learning_executes_next_study_path_step(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-continue-learning@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.get_or_create_study_path",
        lambda *args, **kwargs: {
            "id": "plan-2",
            "focus_topic": "Cell division",
            "status": "active",
            "items": [
                {"id": "flashcards", "title": "Memorize weak concepts in Cell division", "target_tool": "flashcards", "status": "pending"},
            ],
            "next_action": {
                "id": "flashcards",
                "title": "Memorize weak concepts in Cell division",
                "target_tool": "flashcards",
                "prompt": "Generate flashcards for Cell division prioritizing chromosomes.",
                "status": "pending",
            },
            "source_context": {},
        },
    )
    run_study_tool = AsyncMock(
        return_value={
            "data": [{"front": "Chromosomes", "back": "Carry genetic material", "citation": "[bio_p1]"}],
            "citations": [{"source": "Biology", "page": "1"}],
        }
    )
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.run_study_tool", run_study_tool)

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Continue learning", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "study_path_execute"
    assert payload["artifacts"][0]["tool"] == "study_path"
    assert payload["artifacts"][1]["tool"] == "flashcards"
    assert "Started your study path" in payload["reply_text"]
    run_study_tool.assert_awaited_once()


def test_mascot_archive_requires_confirmation_and_confirm_executes(client, db_session, active_tenant):
    from src.domains.platform.models.notebook import Notebook

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-confirm@testschool.edu",
    )

    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Biology",
        subject="Biology",
    )
    db_session.add(notebook)
    db_session.commit()

    first = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Delete Biology notebook", "channel": "web", "notebook_id": str(notebook.id)},
    )
    assert first.status_code == 200
    first_payload = first.json()
    assert first_payload["requires_confirmation"] is True
    assert first_payload["confirmation_id"]

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": first_payload["confirmation_id"], "approved": True, "channel": "web"},
    )
    assert second.status_code == 200
    db_session.refresh(notebook)
    assert notebook.is_active is False


def test_mascot_duplicate_notebook_create_is_deduplicated_within_session(client, db_session, active_tenant):
    from src.domains.platform.models.notebook import Notebook

    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-dedupe@testschool.edu",
    )

    first = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create notebook for Biology Chapter 11", "channel": "web", "session_id": "dedupe-session"},
    )
    assert first.status_code == 200, first.text

    second = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create notebook for Biology Chapter 11", "channel": "web", "session_id": "dedupe-session"},
    )
    assert second.status_code == 200, second.text
    payload = second.json()
    assert "skipped the duplicate request" in payload["reply_text"].lower()

    notebooks = db_session.query(Notebook).filter(Notebook.tenant_id == active_tenant.id, Notebook.name == "Biology Chapter 11").all()
    assert len(notebooks) == 1


def test_mascot_multiple_navigation_targets_requires_clarification(client, db_session, active_tenant):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-nav-clarify@testschool.edu",
        role="teacher",
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Open attendance and marks page", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "clarify_request"
    assert "one page at a time" in payload["reply_text"].lower()


def test_mascot_ambiguous_notebook_name_requires_clarification(client, db_session, active_tenant):
    from src.domains.platform.models.notebook import Notebook

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-ambiguous-notebook@testschool.edu",
    )

    db_session.add_all(
        [
            Notebook(id=uuid.uuid4(), tenant_id=active_tenant.id, user_id=user.id, name="Biology Chapter 1", subject="Biology"),
            Notebook(id=uuid.uuid4(), tenant_id=active_tenant.id, user_id=user.id, name="Biology Chapter 2", subject="Biology"),
        ]
    )
    db_session.commit()

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Delete Biology notebook", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "notebook_update"
    assert "multiple notebooks matching" in payload["reply_text"].lower()
    assert payload["actions"][0]["kind"] == "clarify"


def test_mascot_study_tool_rejects_inaccessible_explicit_notebook_scope(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.notebook import Notebook

    owner, _ = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-owner@testschool.edu",
    )
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-outsider@testschool.edu",
    )

    foreign_notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=owner.id,
        name="Private Biology",
        subject="Biology",
    )
    db_session.add(foreign_notebook)
    db_session.commit()

    run_study_tool = AsyncMock(return_value={"data": [], "citations": []})
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.run_study_tool", run_study_tool)

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Generate flashcards for photosynthesis",
            "channel": "web",
            "notebook_id": str(foreign_notebook.id),
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "can't access that notebook" in payload["reply_text"].lower()
    assert payload["actions"][0]["status"] == "failed"
    run_study_tool.assert_not_awaited()


def test_mascot_student_cannot_confirm_admin_only_import_action(client, db_session, active_tenant):
    from src.domains.platform.services.mascot_schemas import PendingMascotAction
    from src.domains.platform.services.mascot_session_store import store_pending_action

    student, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-student-forbidden@testschool.edu",
        role="student",
    )

    pending = PendingMascotAction(
        kind="structured_import",
        channel="web",
        tenant_id=str(active_tenant.id),
        user_id=str(student.id),
        role="student",
        payload={
            "intent": "admin_teacher_import",
            "kind": "structured_import",
            "rows": [{"name": "Teacher One", "email": "teacher1@example.com", "password": "Teacher123!"}],
            "message": "Import teachers",
            "translated_message": "Import teachers",
        },
    )
    store_pending_action(pending)

    response = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": pending.confirmation_id, "approved": True, "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "not available for your account" in payload["reply_text"].lower()
    assert payload["actions"][0]["status"] == "failed"


def test_mascot_mixed_language_flashcards_uses_translated_message(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.notebook import Notebook

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-mixed@testschool.edu",
    )

    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Biology",
        subject="Biology",
    )
    db_session.add(notebook)
    db_session.commit()

    class _Provider:
        async def generate_structured(self, prompt, schema):
            return {
                "response": {
                    "normalized_message": "mala flashcards pahije photosynthesis var",
                    "translated_message": "Generate flashcards for photosynthesis",
                    "intent": "study_tool",
                    "tool": "flashcards",
                    "topic": "photosynthesis",
                }
            }

    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.get_llm_provider", lambda: _Provider())
    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.run_study_tool",
        AsyncMock(return_value={"data": [{"front": "F", "back": "B", "citation": "[p1]"}], "citations": []}),
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "mala flashcards pahije photosynthesis var",
            "channel": "web",
            "notebook_id": str(notebook.id),
        },
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["translated_message"] == "Generate flashcards for photosynthesis"
    assert payload["intent"] == "study_tool"


def test_mascot_whatsapp_flashcards_are_compact_and_readable(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-whatsapp-flashcards@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.run_study_tool",
        AsyncMock(
            return_value={
                "data": [
                    {"front": "Chlorophyll", "back": "Green pigment that captures light"},
                    {"front": "Stomata", "back": "Leaf pores for gas exchange"},
                ],
                "citations": [],
            }
        ),
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Generate flashcards for photosynthesis", "channel": "whatsapp"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "study_tool"
    assert "flashcards preview:" in payload["reply_text"].lower()
    assert "1. chlorophyll: green pigment that captures light" in payload["reply_text"].lower()
    assert payload["navigation"] is None


def test_mascot_whatsapp_quiz_includes_question_preview(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-whatsapp-quiz@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.run_study_tool",
        AsyncMock(
            return_value={
                "data": [
                    {
                        "question": "What is the main role of chlorophyll?",
                        "options": [
                            "Absorb sunlight",
                            "Store water",
                            "Release nitrogen",
                            "Build roots",
                        ],
                    }
                ],
                "citations": [],
            }
        ),
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Generate quiz for photosynthesis", "channel": "whatsapp"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "study_tool"
    assert "quiz preview:" in payload["reply_text"].lower()
    assert "1. what is the main role of chlorophyll?" in payload["reply_text"].lower()
    assert "a. absorb sunlight" in payload["reply_text"].lower()


def test_mascot_whatsapp_mindmap_expands_key_branches(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-whatsapp-mindmap@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.run_study_tool",
        AsyncMock(
            return_value={
                "data": {
                    "label": "Photosynthesis",
                    "children": [
                        {"label": "Light reaction", "children": [{"label": "ATP formation"}]},
                        {"label": "Calvin cycle"},
                    ],
                },
                "citations": [],
            }
        ),
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create mind map for photosynthesis", "channel": "whatsapp"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "mind map preview:" in payload["reply_text"].lower()
    assert "- photosynthesis" in payload["reply_text"].lower()
    assert "- light reaction" in payload["reply_text"].lower()
    assert "- atp formation" in payload["reply_text"].lower()


def test_mascot_whatsapp_flowchart_shows_ordered_steps(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-whatsapp-flowchart@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.run_study_tool",
        AsyncMock(
            return_value={
                "data": {
                    "mermaid": "flowchart TD\nA[Light] --> B[Glucose]",
                    "steps": [
                        {"label": "Capture light", "detail": "Chlorophyll absorbs sunlight"},
                        {"label": "Make glucose", "detail": "Energy is stored as sugar"},
                    ],
                },
                "citations": [],
            }
        ),
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create flowchart for photosynthesis", "channel": "whatsapp"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "flowchart preview:" in payload["reply_text"].lower()
    assert "1. capture light: chlorophyll absorbs sunlight" in payload["reply_text"].lower()
    assert "2. make glucose: energy is stored as sugar" in payload["reply_text"].lower()
    assert "flowchart td" not in payload["reply_text"].lower()


def test_mascot_whatsapp_concept_map_shows_relationships(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-whatsapp-conceptmap@testschool.edu",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.run_study_tool",
        AsyncMock(
            return_value={
                "data": {
                    "nodes": [
                        {"id": "1", "label": "Leaf"},
                        {"id": "2", "label": "Chloroplast"},
                        {"id": "3", "label": "Glucose"},
                    ],
                    "edges": [
                        {"from": "1", "to": "2", "label": "contains"},
                        {"from": "2", "to": "3", "label": "produces"},
                    ],
                },
                "citations": [],
            }
        ),
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create concept map for photosynthesis", "channel": "whatsapp"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "concept map preview:" in payload["reply_text"].lower()
    assert "- leaf -> contains -> chloroplast" in payload["reply_text"].lower()
    assert "- chloroplast -> produces -> glucose" in payload["reply_text"].lower()


def test_mascot_teacher_can_fetch_class_insights_summary(client, db_session, active_tenant):
    from datetime import time

    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.academic.models.timetable import Timetable
    from src.domains.identity.models.user import User

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-insights@testschool.edu",
        role="teacher",
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 10 A", grade_level="10")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Biology", class_id=school_class.id)
    exam = Exam(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Unit Test", subject_id=subject.id, max_marks=100)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="mascot-student-insights@testschool.edu",
        full_name="Mascot Student",
        role="student",
        hashed_password="unused",
        is_active=True,
    )
    mark = Mark(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=student.id, exam_id=exam.id, marks_obtained=42)
    db_session.add_all([school_class, subject, exam, timetable, mark])
    db_session.commit()

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show class insights", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "teacher_insights_report"
    assert "Class 10 A" in payload["reply_text"]
    assert payload["artifacts"][0]["tool"] == "teacher_insights_report"


def test_mascot_parent_can_fetch_child_progress_summary(client, db_session, active_tenant):
    from datetime import date

    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.academic.models.parent_link import ParentLink
    from src.domains.identity.models.user import User

    parent, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-parent@testschool.edu",
        role="parent",
    )
    child = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="mascot-child@testschool.edu",
        full_name="Child Learner",
        role="student",
        hashed_password="unused",
        is_active=True,
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 8 A", grade_level="8")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Science", class_id=school_class.id)
    exam = Exam(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Midterm", subject_id=subject.id, max_marks=100)
    link = ParentLink(id=uuid.uuid4(), tenant_id=active_tenant.id, parent_id=parent.id, child_id=child.id)
    attendance_present = Attendance(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=child.id, class_id=school_class.id, date=date(2026, 3, 20), status="present")
    attendance_absent = Attendance(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=child.id, class_id=school_class.id, date=date(2026, 3, 21), status="absent")
    mark = Mark(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=child.id, exam_id=exam.id, marks_obtained=78)
    db_session.add_all([child, school_class, subject, exam, link, attendance_present, attendance_absent, mark])
    db_session.commit()

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show my child report", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "parent_progress_report"
    assert "attendance is" in payload["reply_text"].lower()
    assert payload["artifacts"][0]["tool"] == "parent_progress_report"
    assert payload["artifacts"][0]["child"]["name"] == child.full_name


def test_mascot_admin_can_fetch_release_gate_summary(client, db_session, active_tenant, monkeypatch):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-admin-release@testschool.edu",
        role="admin",
    )

    monkeypatch.setattr(
        "src.domains.platform.services.whatsapp_gateway.get_whatsapp_metrics",
        lambda tenant_id=None: {
            "inbound_total": 100,
            "routing_success_total": 96,
            "routing_failure_total": 4,
            "duplicate_inbound_total": 3,
            "visible_failure_total": 2,
            "outbound_success_total": 90,
            "outbound_failure_total": 10,
            "outbound_retryable_failure_total": 5,
        },
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show WhatsApp health", "channel": "web"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "admin_release_gate_report"
    assert "routing failure 4.0%" in payload["reply_text"]
    assert payload["artifacts"][0]["tool"] == "admin_release_gate_report"


def test_mascot_admin_can_fetch_onboarding_progress_summary(client, db_session, active_tenant):
    from src.domains.academic.models.core import Class
    from src.domains.identity.models.user import User

    admin, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-admin-onboarding@testschool.edu",
        role="admin",
    )
    teacher = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="teacher-onboarding@testschool.edu",
        full_name="Teacher One",
        role="teacher",
        hashed_password="unused",
        is_active=True,
    )
    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="student-onboarding@testschool.edu",
        full_name="Student One",
        role="student",
        hashed_password="unused",
        is_active=True,
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 6 A", grade_level="6")
    db_session.add_all([teacher, student, school_class])
    db_session.commit()

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show setup progress", "channel": "web"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "admin_onboarding_report"
    assert "1 classes" in payload["reply_text"]
    assert payload["artifacts"][0]["tool"] == "admin_onboarding_report"


def test_mascot_admin_can_fetch_ai_review_summary(client, db_session, active_tenant):
    from src.domains.platform.models.ai import AIQuery
    from src.domains.platform.models.audit import AuditLog

    admin, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-admin-review@testschool.edu",
        role="admin",
    )
    q1 = AIQuery(id=uuid.uuid4(), tenant_id=active_tenant.id, user_id=admin.id, query_text="Explain photosynthesis", mode="qa")
    q2 = AIQuery(id=uuid.uuid4(), tenant_id=active_tenant.id, user_id=admin.id, query_text="Create quiz", mode="quiz")
    review = AuditLog(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=admin.id,
        action="ai_review.approved",
        entity_type="ai_review",
        entity_id=q1.id,
        metadata_={},
    )
    db_session.add_all([q1, q2, review])
    db_session.commit()

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Show AI review summary", "channel": "web"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "admin_ai_review_report"
    assert "1 pending" in payload["reply_text"]
    assert payload["artifacts"][0]["tool"] == "admin_ai_review_report"


def test_mascot_teacher_can_generate_assessment(client, db_session, active_tenant, monkeypatch):
    from datetime import time

    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.timetable import Timetable

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-assessment@testschool.edu",
        role="teacher",
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9 A", grade_level="9")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Biology", class_id=school_class.id)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=2,
        start_time=time(10, 0),
        end_time=time(11, 0),
    )
    db_session.add_all([school_class, subject, timetable])
    db_session.commit()

    run_text_query = AsyncMock(return_value={"answer": '[{"q":"What is photosynthesis?","options":["A","B"]}]', "citations": []})
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.run_text_query", run_text_query)

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Generate assessment with 4 questions for photosynthesis in Biology", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "teacher_assessment_generate"
    assert payload["artifacts"][0]["tool"] == "teacher_assessment_generate"
    assert payload["artifacts"][0]["subject"] == "Biology"
    run_text_query.assert_awaited_once()


def test_mascot_teacher_attendance_mark_requires_confirmation_and_applies_rows(client, db_session, active_tenant):
    from datetime import time

    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.academic.models.timetable import Timetable
    from src.domains.identity.models.user import User

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-attendance@testschool.edu",
        role="teacher",
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9 A", grade_level="9")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Biology", class_id=school_class.id)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    rohan = User(id=uuid.uuid4(), tenant_id=active_tenant.id, email="rohan@testschool.edu", full_name="Rohan Sharma", role="student")
    priya = User(id=uuid.uuid4(), tenant_id=active_tenant.id, email="priya@testschool.edu", full_name="Priya Singh", role="student")
    db_session.add_all([
        school_class,
        subject,
        timetable,
        rohan,
        priya,
        Enrollment(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=rohan.id, class_id=school_class.id),
        Enrollment(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=priya.id, class_id=school_class.id),
    ])
    db_session.commit()

    first = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Mark attendance for Class 9 A absent Rohan", "channel": "web"},
    )
    assert first.status_code == 200, first.text
    first_payload = first.json()
    assert first_payload["intent"] == "teacher_attendance_mark"
    assert first_payload["requires_confirmation"] is True

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": first_payload["confirmation_id"], "approved": True, "channel": "web"},
    )
    assert second.status_code == 200, second.text
    second_payload = second.json()
    assert "Marked attendance for Class 9 A" in second_payload["reply_text"]

    rows = db_session.query(Attendance).filter(Attendance.class_id == school_class.id).all()
    status_by_student = {row.student_id: row.status for row in rows}
    assert status_by_student[rohan.id] == "absent"
    assert status_by_student[priya.id] == "present"


def test_mascot_teacher_homework_create_requires_confirmation_and_enqueues_notifications(client, db_session, active_tenant, monkeypatch):
    from datetime import time

    from src.domains.academic.models.assignment import Assignment
    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.academic.models.parent_link import ParentLink
    from src.domains.academic.models.timetable import Timetable
    from src.domains.identity.models.user import User

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-homework@testschool.edu",
        role="teacher",
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9 A", grade_level="9")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Biology", class_id=school_class.id)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    student = User(id=uuid.uuid4(), tenant_id=active_tenant.id, email="student-homework@testschool.edu", full_name="Student One", role="student")
    parent = User(id=uuid.uuid4(), tenant_id=active_tenant.id, email="parent-homework@testschool.edu", full_name="Parent One", role="parent")
    db_session.add_all([
        school_class,
        subject,
        timetable,
        student,
        parent,
        Enrollment(id=uuid.uuid4(), tenant_id=active_tenant.id, student_id=student.id, class_id=school_class.id),
        ParentLink(id=uuid.uuid4(), tenant_id=active_tenant.id, parent_id=parent.id, child_id=student.id, relationship_type="parent"),
    ])
    db_session.commit()

    submit_mock = MagicMock(return_value=SimpleNamespace(result=lambda timeout=None: None))
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.submit_async_job", submit_mock)

    first = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Assign homework for Biology in Class 9 A due 2026-04-10: Solve exercise 3", "channel": "web"},
    )
    assert first.status_code == 200, first.text
    first_payload = first.json()
    assert first_payload["intent"] == "teacher_homework_create"
    assert first_payload["requires_confirmation"] is True

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": first_payload["confirmation_id"], "approved": True, "channel": "web"},
    )
    assert second.status_code == 200, second.text
    second_payload = second.json()
    assert "Created homework" in second_payload["reply_text"]

    assignment = db_session.query(Assignment).filter(Assignment.subject_id == subject.id).one()
    assert assignment.title == "Biology homework"
    assert assignment.description.startswith("Solve exercise 3")
    submit_mock.assert_called_once()


def test_mascot_admin_teacher_import_requires_confirmation_and_creates_teachers(client, db_session, active_tenant):
    from src.domains.identity.models.user import User

    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-admin-import-teachers@testschool.edu",
        role="admin",
    )

    first = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "message": "Import teachers",
            "current_route": "/admin/setup-wizard",
            "current_page_entity": "setup_step",
            "current_page_entity_id": "teachers",
            "context_metadata": json.dumps({"setup_step": "teachers"}),
        },
        files={"file": ("teachers.csv", b"Priya Sharma,,\nRaj Patel,raj@example.com,\n", "text/csv")},
    )
    assert first.status_code == 200, first.text
    payload = first.json()
    assert payload["intent"] == "admin_teacher_import"
    assert payload["requires_confirmation"] is True

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": payload["confirmation_id"], "approved": True, "channel": "web"},
    )
    assert second.status_code == 200, second.text
    teachers = db_session.query(User).filter(User.tenant_id == active_tenant.id, User.role == "teacher").all()
    assert len(teachers) == 2


def test_mascot_admin_student_import_requires_confirmation_and_creates_students(client, db_session, active_tenant):
    from src.domains.academic.models.core import Class, Enrollment
    from src.domains.identity.models.user import User

    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-admin-import-students@testschool.edu",
        role="admin",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9A", grade_level="9")
    db_session.add(school_class)
    db_session.commit()

    first = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "message": "Import students",
            "current_route": "/admin/setup-wizard",
            "current_page_entity": "setup_step",
            "current_page_entity_id": "students",
            "context_metadata": json.dumps({"setup_step": "students"}),
        },
        files={"file": ("students.csv", b"full_name,email,password,class_name\nAnanya Kumari,ananya@example.com,Student123!,Class 9A\n", "text/csv")},
    )
    assert first.status_code == 200, first.text
    payload = first.json()
    assert payload["intent"] == "admin_student_import"
    assert payload["requires_confirmation"] is True

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": payload["confirmation_id"], "approved": True, "channel": "web"},
    )
    assert second.status_code == 200, second.text
    student = db_session.query(User).filter(User.tenant_id == active_tenant.id, User.role == "student", User.email == "ananya@example.com").one()
    enrollment = db_session.query(Enrollment).filter(Enrollment.student_id == student.id, Enrollment.class_id == school_class.id).one()
    assert enrollment is not None


def test_mascot_teacher_youtube_ingestion_uses_subject_context(client, db_session, active_tenant, monkeypatch):
    from datetime import time

    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.timetable import Timetable
    from src.domains.platform.models.notebook import Notebook

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-youtube@testschool.edu",
        role="teacher",
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 11 A", grade_level="11")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Chemistry", class_id=school_class.id)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=3,
        start_time=time(8, 0),
        end_time=time(9, 0),
    )
    notebook = Notebook(id=uuid.uuid4(), tenant_id=active_tenant.id, user_id=teacher.id, name="Chemistry Lectures", subject="Chemistry")
    db_session.add_all([school_class, subject, timetable, notebook])
    db_session.commit()

    observed: dict[str, str | None] = {"subject_id": None}

    def _ingest_youtube(**kwargs):
        observed["subject_id"] = kwargs.get("subject_id")
        return [
            SimpleNamespace(
                text="Chemical bonding basics.",
                document_id=kwargs["document_id"],
                page_number=1,
                section_title="Lecture",
                subject_id=kwargs.get("subject_id") or "",
                notebook_id=kwargs.get("notebook_id") or "",
                source_file="youtube",
            )
        ]

    class _EmbeddingProvider:
        async def embed_batch(self, texts):
            return [[0.4, 0.5] for _ in texts]

    class _VectorStore:
        def add_chunks(self, chunk_dicts, embeddings):
            assert chunk_dicts
            assert embeddings

    monkeypatch.setattr("src.infrastructure.vector_store.ingestion.ingest_youtube", _ingest_youtube)
    monkeypatch.setattr("src.infrastructure.llm.providers.get_embedding_provider", lambda: _EmbeddingProvider())
    monkeypatch.setattr("src.infrastructure.llm.providers.get_vector_store_provider", lambda tenant_id: _VectorStore())

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "message": "Add this Chemistry lecture to the knowledge base https://youtube.com/watch?v=test123",
            "channel": "web",
            "notebook_id": str(notebook.id),
        },
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["intent"] == "content_ingest"
    assert observed["subject_id"] == str(subject.id)


def test_mascot_upload_image_returns_ocr_metadata(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.document import Document
    from src.domains.platform.models.notebook import Notebook

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-upload@testschool.edu",
    )

    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Biology",
        subject="Biology",
    )
    db_session.add(notebook)
    db_session.commit()

    monkeypatch.setattr("src.infrastructure.vector_store.ocr_service.validate_image_size", lambda content: None)
    monkeypatch.setattr(
        "src.infrastructure.vector_store.ocr_service.image_bytes_to_pdf",
        lambda *args, **kwargs: SimpleNamespace(
            review_required=True,
            warning="Review OCR before relying on faint text.",
            languages=["en", "hi"],
            preprocessing_applied=["deskew"],
            confidence=0.72,
        ),
    )
    monkeypatch.setattr(
        "src.infrastructure.vector_store.ingestion.ingest_document",
        lambda **kwargs: [
            SimpleNamespace(
                text="Photosynthesis uses sunlight.",
                document_id=kwargs["document_id"],
                page_number=1,
                section_title="Chapter 10",
                subject_id="",
                notebook_id=kwargs.get("notebook_id") or "",
                source_file="notes.jpg",
            )
        ],
    )

    class _EmbeddingProvider:
        async def embed_batch(self, texts):
            return [[0.1, 0.2] for _ in texts]

    class _VectorStore:
        def add_chunks(self, chunk_dicts, embeddings):
            assert len(chunk_dicts) == 1
            assert len(embeddings) == 1

    monkeypatch.setattr("src.infrastructure.llm.providers.get_embedding_provider", lambda: _EmbeddingProvider())
    monkeypatch.setattr("src.infrastructure.llm.providers.get_vector_store_provider", lambda tenant_id: _VectorStore())

    response = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"notebook_id": str(notebook.id)},
        files={"file": ("notes.jpg", b"fake-image", "image/jpeg")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "content_ingest"
    assert payload["artifacts"][0]["ocr_processed"] is True
    assert payload["artifacts"][0]["ocr_review_required"] is True
    assert payload["artifacts"][0]["ocr_confidence"] == 0.72
    document = db_session.query(Document).filter(Document.notebook_id == notebook.id).first()
    assert document is not None
    assert document.ingestion_status == "completed"


def test_mascot_upload_can_chain_follow_up_request(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.notebook import Notebook
    from src.domains.platform.services.mascot_schemas import MascotAction, MascotMessageResponse

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-upload-followup@testschool.edu",
    )

    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Biology",
        subject="Biology",
    )
    db_session.add(notebook)
    db_session.commit()

    monkeypatch.setattr(
        "src.infrastructure.vector_store.ingestion.ingest_document",
        lambda **kwargs: [
            SimpleNamespace(
                text="Photosynthesis converts light to energy.",
                document_id=kwargs["document_id"],
                page_number=1,
                section_title="Chapter 10",
                subject_id="",
                notebook_id=kwargs.get("notebook_id") or "",
                source_file="lecture.pdf",
            )
        ],
    )

    class _EmbeddingProvider:
        async def embed_batch(self, texts):
            return [[0.2, 0.3] for _ in texts]

    class _VectorStore:
        def add_chunks(self, chunk_dicts, embeddings):
            assert chunk_dicts
            assert embeddings

    monkeypatch.setattr("src.infrastructure.llm.providers.get_embedding_provider", lambda: _EmbeddingProvider())
    monkeypatch.setattr("src.infrastructure.llm.providers.get_vector_store_provider", lambda tenant_id: _VectorStore())
    monkeypatch.setattr(
        "src.domains.platform.services.mascot_orchestrator.handle_mascot_message",
        AsyncMock(
            return_value=MascotMessageResponse(
                reply_text="Here is a summary from the uploaded lecture.",
                intent="query",
                normalized_message="Summarize this upload",
                actions=[MascotAction(kind="query", status="completed", result_summary="Answered using qa mode.")],
                artifacts=[{"tool": "qa", "answer": "Here is a summary from the uploaded lecture."}],
                follow_up_suggestions=["Generate flashcards", "Create a flowchart"],
                notebook_id=str(notebook.id),
                trace_id="mascot-upload-followup",
            )
        ),
    )

    response = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"notebook_id": str(notebook.id), "message": "Summarize this upload"},
        files={"file": ("lecture.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["intent"] == "query"
    assert "Ingested lecture.pdf into Biology." in payload["reply_text"]
    assert "Here is a summary from the uploaded lecture." in payload["reply_text"]
    assert payload["actions"][0]["kind"] == "content_ingest"
    assert payload["actions"][1]["kind"] == "query"


def test_mascot_upload_rejects_inaccessible_notebook_scope(client, db_session, active_tenant):
    from src.domains.platform.models.notebook import Notebook

    owner, _ = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-upload-owner@testschool.edu",
    )
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-upload-outsider@testschool.edu",
    )

    foreign_notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=owner.id,
        name="Private Uploads",
        subject="Science",
    )
    db_session.add(foreign_notebook)
    db_session.commit()

    response = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"notebook_id": str(foreign_notebook.id)},
        files={"file": ("notes.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )

    assert response.status_code == 400, response.text
    assert "can't access that notebook" in response.json()["detail"].lower()


def test_mascot_teacher_roster_upload_requires_confirmation_and_imports_students(client, db_session, active_tenant):
    from src.domains.identity.models.user import User

    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-roster@testschool.edu",
        role="teacher",
    )

    first = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "current_route": "/teacher/classes",
            "context_metadata": json.dumps({"import_kind": "teacher_roster_import"}),
        },
        files={"file": ("students.csv", b"Aarav Shah,,\nDiya Patil,diya@example.com,\n", "text/csv")},
    )

    assert first.status_code == 200, first.text
    first_payload = first.json()
    assert first_payload["intent"] == "teacher_roster_import"
    assert first_payload["requires_confirmation"] is True
    assert first_payload["actions"][0]["kind"] == "structured_import"

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": first_payload["confirmation_id"], "approved": True, "channel": "web"},
    )

    assert second.status_code == 200, second.text
    payload = second.json()
    assert "Imported 2 students." in payload["reply_text"]
    students = db_session.query(User).filter(User.tenant_id == active_tenant.id, User.role == "student").all()
    assert len(students) == 2


def test_mascot_suggestions_use_student_personalization(client, db_session, active_tenant):
    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.performance import SubjectPerformance

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-suggestions-notebook@testschool.edu",
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 10", grade_level="10")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, name="Biology")
    db_session.add_all([school_class, subject])
    db_session.commit()
    db_session.add(
        SubjectPerformance(
            tenant_id=active_tenant.id,
            student_id=user.id,
            subject_id=subject.id,
            average_score=42.0,
            attendance_rate=88.0,
        )
    )
    db_session.commit()

    response = client.get(
        "/api/mascot/suggestions",
        headers={"Authorization": f"Bearer {token}"},
        params={"current_route": "/student/assistant"},
    )

    assert response.status_code == 200, response.text
    suggestions = response.json()["suggestions"]
    assert suggestions
    assert any("Biology" in item or "guided explanation" in item.lower() or "quick revision" in item.lower() for item in suggestions)


def test_mascot_suggestions_use_teacher_page_entity(client, db_session, active_tenant):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-suggestions-teacher@testschool.edu",
        role="teacher",
    )

    response = client.get(
        "/api/mascot/suggestions",
        headers={"Authorization": f"Bearer {token}"},
        params={"current_route": "/teacher/attendance", "current_page_entity": "class"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["suggestions"] == [
        "Import attendance from image",
        "Review OCR attendance rows",
        "Summarize this class attendance",
    ]


def test_mascot_suggestions_use_admin_setup_context(client, db_session, active_tenant):
    _, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-suggestions-admin@testschool.edu",
        role="admin",
    )

    response = client.get(
        "/api/mascot/suggestions",
        headers={"Authorization": f"Bearer {token}"},
        params={"current_route": "/admin/setup-wizard", "current_page_entity": "setup_step"},
    )

    assert response.status_code == 200, response.text
    assert response.json()["suggestions"] == [
        "Show setup progress",
        "Import teachers",
        "Import students",
    ]


def test_mascot_message_records_metrics_and_audit_log(client, db_session, active_tenant):
    from src.domains.platform.models.audit import AuditLog
    from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-observability@testschool.edu",
    )

    response = client.post(
        "/api/mascot/message",
        headers={"Authorization": f"Bearer {token}"},
        json={"message": "Create notebook for Biology Chapter 12", "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    metrics = {(row["stage"], row["operation"], row["outcome"]): row for row in snapshot_stage_latency_metrics()}
    assert ("mascot", "interpretation", "success") in metrics
    assert ("mascot", "execution", "success") in metrics

    audit = db_session.query(AuditLog).filter(
        AuditLog.tenant_id == active_tenant.id,
        AuditLog.user_id == user.id,
        AuditLog.action == "mascot.message",
    ).order_by(AuditLog.created_at.desc()).first()
    assert audit is not None
    assert audit.metadata_["trace_id"] == payload["trace_id"]
    assert audit.metadata_["intent"] == "notebook_create"
    assert audit.metadata_["status"] == "success"


def test_mascot_upload_records_metrics_and_audit_log(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.audit import AuditLog
    from src.domains.platform.models.notebook import Notebook
    from src.domains.platform.services.metrics_registry import snapshot_stage_latency_metrics

    user, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-upload-observability@testschool.edu",
    )

    notebook = Notebook(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        user_id=user.id,
        name="Biology",
        subject="Biology",
    )
    db_session.add(notebook)
    db_session.commit()

    monkeypatch.setattr(
        "src.infrastructure.vector_store.ingestion.ingest_document",
        lambda **kwargs: [
            SimpleNamespace(
                text="Photosynthesis converts light to energy.",
                document_id=kwargs["document_id"],
                page_number=1,
                section_title="Chapter 10",
                subject_id="",
                notebook_id=kwargs.get("notebook_id") or "",
                source_file="lecture.pdf",
            )
        ],
    )

    class _EmbeddingProvider:
        async def embed_batch(self, texts):
            return [[0.2, 0.3] for _ in texts]

    class _VectorStore:
        def add_chunks(self, chunk_dicts, embeddings):
            assert chunk_dicts
            assert embeddings

    monkeypatch.setattr("src.infrastructure.llm.providers.get_embedding_provider", lambda: _EmbeddingProvider())
    monkeypatch.setattr("src.infrastructure.llm.providers.get_vector_store_provider", lambda tenant_id: _VectorStore())

    response = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={"notebook_id": str(notebook.id)},
        files={"file": ("lecture.pdf", b"%PDF-1.4 fake", "application/pdf")},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    metrics = {(row["stage"], row["operation"], row["outcome"]): row for row in snapshot_stage_latency_metrics()}
    assert ("mascot", "upload", "success") in metrics

    audit = db_session.query(AuditLog).filter(
        AuditLog.tenant_id == active_tenant.id,
        AuditLog.user_id == user.id,
        AuditLog.action == "mascot.upload",
    ).order_by(AuditLog.created_at.desc()).first()
    assert audit is not None
    assert audit.metadata_["trace_id"] == payload["trace_id"]
    assert audit.metadata_["filename"] == "lecture.pdf"
    assert audit.metadata_["status"] == "success"


def test_mascot_release_gate_snapshot_includes_metrics_and_alerts(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.audit import AuditLog

    admin, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-release-gate@testschool.edu",
        role="admin",
    )

    db_session.add_all([
        AuditLog(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            user_id=admin.id,
            action="mascot.message",
            entity_type="mascot_session",
            entity_id=None,
            metadata_={"trace_id": "mascot-a", "status": "success"},
        ),
        AuditLog(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            user_id=admin.id,
            action="mascot.upload",
            entity_type="mascot_session",
            entity_id=None,
            metadata_={"trace_id": "mascot-b", "status": "error"},
        ),
    ])
    db_session.commit()

    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.snapshot_stage_latency_metrics",
        lambda: [
            {"stage": "mascot", "operation": "interpretation", "outcome": "success", "count": 5.0, "duration_ms_sum": 900.0, "duration_ms_max": 300.0},
            {"stage": "mascot", "operation": "execution", "outcome": "success", "count": 4.0, "duration_ms_sum": 1400.0, "duration_ms_max": 500.0},
            {"stage": "mascot", "operation": "execution", "outcome": "error", "count": 1.0, "duration_ms_sum": 200.0, "duration_ms_max": 200.0},
            {"stage": "mascot", "operation": "upload", "outcome": "success", "count": 2.0, "duration_ms_sum": 1000.0, "duration_ms_max": 600.0},
            {"stage": "mascot", "operation": "confirmation", "outcome": "cancelled", "count": 1.0, "duration_ms_sum": 50.0, "duration_ms_max": 50.0},
        ],
    )
    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.get_active_alerts",
        lambda tenant_id: [
            {"code": "mascot_failure_rate_high", "severity": "critical", "message": "Mascot execution failure rate reached 20.0%.", "stage": "mascot", "operation": "execution"},
            {"code": "queue_depth_high", "severity": "warning", "message": "Queue depth high."},
        ],
    )

    response = client.get(
        "/api/mascot/release-gate-snapshot?days=7",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["analytics"]["total_actions"] == 2
    assert payload["analytics"]["unique_users"] == 1
    assert payload["release_gate_metrics"]["execution_failure_total"] == 1
    assert payload["release_gate_metrics"]["confirmation_cancelled_total"] == 1
    assert payload["derived_rates"]["execution_failure_pct"] == 20.0
    assert len(payload["active_alerts"]) == 1
    assert payload["active_alerts"][0]["code"] == "mascot_failure_rate_high"


def test_mascot_release_gate_evidence_prefills_markdown(client, db_session, active_tenant, monkeypatch):
    from src.domains.platform.models.audit import AuditLog

    admin, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-release-evidence@testschool.edu",
        role="admin",
    )

    db_session.add(
        AuditLog(
            id=uuid.uuid4(),
            tenant_id=active_tenant.id,
            user_id=admin.id,
            action="mascot.message",
            entity_type="mascot_session",
            entity_id=None,
            metadata_={"trace_id": "mascot-evidence", "status": "success"},
        )
    )
    db_session.commit()

    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.snapshot_stage_latency_metrics",
        lambda: [
            {"stage": "mascot", "operation": "interpretation", "outcome": "success", "count": 8.0, "duration_ms_sum": 1000.0, "duration_ms_max": 200.0},
            {"stage": "mascot", "operation": "execution", "outcome": "error", "count": 2.0, "duration_ms_sum": 500.0, "duration_ms_max": 300.0},
            {"stage": "mascot", "operation": "upload", "outcome": "success", "count": 3.0, "duration_ms_sum": 700.0, "duration_ms_max": 400.0},
        ],
    )
    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.get_active_alerts",
        lambda tenant_id: [
            {"code": "mascot_failure_rate_high", "severity": "critical", "message": "Mascot execution failure rate reached 20.0%.", "stage": "mascot", "operation": "execution"},
        ],
    )

    response = client.get(
        "/api/mascot/release-gate-evidence?days=7",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["filename"].startswith("mascot_release_gate_evidence_")
    assert payload["snapshot"]["analytics"]["total_actions"] == 1
    assert "Mascot Release Gate Evidence" in payload["markdown"]
    assert "- total mascot actions: 1" in payload["markdown"]
    assert "- execution failure %: 100.0" in payload["markdown"]
    assert "mascot_failure_rate_high" in payload["markdown"]


def test_mascot_staging_packet_combines_whatsapp_and_mascot_snapshots(client, db_session, active_tenant, monkeypatch):
    admin, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-staging-packet@testschool.edu",
        role="admin",
    )

    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.snapshot_stage_latency_metrics",
        lambda: [
            {"stage": "mascot", "operation": "interpretation", "outcome": "success", "count": 4.0, "duration_ms_sum": 500.0, "duration_ms_max": 200.0},
            {"stage": "mascot", "operation": "execution", "outcome": "success", "count": 3.0, "duration_ms_sum": 800.0, "duration_ms_max": 350.0},
        ],
    )
    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.get_active_alerts",
        lambda tenant_id: [],
    )
    monkeypatch.setattr(
        "src.domains.platform.routes.mascot._build_whatsapp_usage_snapshot",
        lambda current_user, db, days: {
            "total_messages": 42,
            "inbound": 21,
            "outbound": 21,
            "unique_users": 9,
            "avg_latency_ms": 812,
        },
    )
    monkeypatch.setattr(
        "src.domains.platform.routes.mascot.get_whatsapp_metrics",
        lambda tenant_id: {
            "inbound_total": 21,
            "routing_success_total": 20,
            "routing_failure_total": 1,
            "duplicate_inbound_total": 1,
            "visible_failure_total": 1,
            "outbound_success_total": 20,
            "outbound_failure_total": 1,
            "outbound_retryable_failure_total": 1,
            "upload_ingest_failure_total": 0,
            "link_ingest_failure_total": 0,
        },
    )

    response = client.get(
        "/api/mascot/staging-packet?days=7",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["filename"].startswith("mascot_whatsapp_staging_packet_")
    assert payload["whatsapp_snapshot"]["analytics"]["total_messages"] == 42
    assert payload["mascot_snapshot"]["analytics"]["total_actions"] == 0
    assert "Mascot WhatsApp Staging Packet" in payload["markdown"]
    assert "- total messages: 42" in payload["markdown"]
    assert "- total mascot actions: 0" in payload["markdown"]


def test_mascot_teacher_attendance_upload_requires_confirmation_and_imports_rows(client, db_session, active_tenant):
    from datetime import time

    from src.domains.academic.models.attendance import Attendance
    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.academic.models.timetable import Timetable
    from src.domains.identity.models.user import User

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-attendance@testschool.edu",
        role="teacher",
    )

    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="attendance-student@testschool.edu",
        full_name="Riya Sharma",
        role="student",
        hashed_password="unused",
        is_active=True,
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 7 A", grade_level="7")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Science", class_id=school_class.id)
    enrollment = Enrollment(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, student_id=student.id)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=1,
        start_time=time(9, 0),
        end_time=time(10, 0),
    )
    db_session.add_all([student, school_class, subject, enrollment, timetable])
    db_session.commit()

    first = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "message": "Import attendance",
            "current_route": "/teacher/attendance",
            "current_page_entity": "class",
            "current_page_entity_id": str(school_class.id),
            "context_metadata": json.dumps({"class_id": str(school_class.id), "date": "2026-03-30"}),
        },
        files={"file": ("attendance.csv", b"name,status\nRiya Sharma,present\n", "text/csv")},
    )

    assert first.status_code == 200, first.text
    first_payload = first.json()
    assert first_payload["intent"] == "teacher_attendance_import"
    assert first_payload["requires_confirmation"] is True

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": first_payload["confirmation_id"], "approved": True, "channel": "web"},
    )

    assert second.status_code == 200, second.text
    payload = second.json()
    assert "Imported 1 attendance row." in payload["reply_text"]
    attendance = db_session.query(Attendance).filter(Attendance.class_id == school_class.id).all()
    assert len(attendance) == 1
    assert attendance[0].status == "present"


def test_mascot_teacher_marks_upload_requires_confirmation_and_imports_rows(client, db_session, active_tenant):
    from datetime import time

    from src.domains.academic.models.core import Class, Enrollment, Subject
    from src.domains.academic.models.marks import Exam, Mark
    from src.domains.academic.models.timetable import Timetable
    from src.domains.identity.models.user import User

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-marks@testschool.edu",
        role="teacher",
    )

    student = User(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        email="marks-student@testschool.edu",
        full_name="Kabir Singh",
        role="student",
        hashed_password="unused",
        is_active=True,
    )
    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 8 B", grade_level="8")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Science", class_id=school_class.id)
    enrollment = Enrollment(id=uuid.uuid4(), tenant_id=active_tenant.id, class_id=school_class.id, student_id=student.id)
    timetable = Timetable(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        subject_id=subject.id,
        teacher_id=teacher.id,
        day_of_week=2,
        start_time=time(10, 0),
        end_time=time(11, 0),
    )
    db_session.add_all([student, school_class, subject, enrollment, timetable])
    db_session.commit()

    first = client.post(
        "/api/mascot/upload",
        headers={"Authorization": f"Bearer {token}"},
        data={
            "message": "Import marks for science",
            "current_route": "/teacher/marks",
            "current_page_entity": "subject",
            "current_page_entity_id": str(subject.id),
            "context_metadata": json.dumps(
                {
                    "class_id": str(school_class.id),
                    "subject_id": str(subject.id),
                    "exam_name": "Unit Test 1",
                    "exam_date": "2026-03-30",
                    "max_marks": 100,
                }
            ),
        },
        files={"file": ("marks.csv", b"name,marks_obtained\nKabir Singh,78\n", "text/csv")},
    )

    assert first.status_code == 200, first.text
    first_payload = first.json()
    assert first_payload["intent"] == "teacher_marks_import"
    assert first_payload["requires_confirmation"] is True

    second = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": first_payload["confirmation_id"], "approved": True, "channel": "web"},
    )

    assert second.status_code == 200, second.text
    payload = second.json()
    assert "Imported 1 marks row for Unit Test 1." in payload["reply_text"]
    exam = db_session.query(Exam).filter(Exam.subject_id == subject.id).one()
    mark = db_session.query(Mark).filter(Mark.exam_id == exam.id, Mark.student_id == student.id).one()
    assert mark.marks_obtained == 78


def test_mascot_confirm_rejects_teacher_marks_import_outside_scope(client, db_session, active_tenant):
    from src.domains.academic.models.core import Class, Subject
    from src.domains.academic.models.marks import Exam
    from src.domains.platform.services.mascot_schemas import PendingMascotAction
    from src.domains.platform.services.mascot_session_store import store_pending_action

    teacher, token = _create_user_and_login(
        client,
        db_session,
        active_tenant.id,
        email="mascot-teacher-scope@testschool.edu",
        role="teacher",
    )

    school_class = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 12 A", grade_level="12")
    subject = Subject(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Physics", class_id=school_class.id)
    db_session.add_all([school_class, subject])
    db_session.commit()

    pending = PendingMascotAction(
        kind="structured_import",
        channel="web",
        tenant_id=str(active_tenant.id),
        user_id=str(teacher.id),
        role="teacher",
        payload={
            "intent": "teacher_marks_import",
            "kind": "structured_import",
            "class_id": str(school_class.id),
            "subject_id": str(subject.id),
            "exam_name": "Unauthorized Exam",
            "exam_date": "2026-03-30",
            "max_marks": 100,
            "rows": [{"identifier": "Someone", "marks_obtained": 78}],
            "message": "Import marks",
            "translated_message": "Import marks",
        },
    )
    store_pending_action(pending)

    response = client.post(
        "/api/mascot/confirm",
        headers={"Authorization": f"Bearer {token}"},
        json={"confirmation_id": pending.confirmation_id, "approved": True, "channel": "web"},
    )

    assert response.status_code == 200, response.text
    payload = response.json()
    assert "outside your allowed teaching scope" in payload["reply_text"].lower()
    exams = db_session.query(Exam).filter(Exam.subject_id == subject.id, Exam.name == "Unauthorized Exam").all()
    assert exams == []
