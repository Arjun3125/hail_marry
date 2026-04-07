"""Phase 1 runtime contract tests for ownership and assessment lifecycle."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
import uuid

from auth.dependencies import get_current_user
from src.domains.academic.models.core import Class, Subject
from src.domains.academic.models.test_series import TestSeries as AssessmentSeriesModel
from src.domains.identity.models.tenant import Tenant


def _make_user(*, tenant_id, role: str):
    return type(
        "TestUser",
        (),
        {
            "id": uuid.uuid4(),
            "tenant_id": tenant_id,
            "role": role,
            "is_active": True,
        },
    )()


def test_fee_route_rejects_cross_tenant_class_ownership(client, db_session, active_tenant):
    other_tenant = Tenant(id=uuid.uuid4(), name="Other School", domain="other.example")
    foreign_class = Class(
        id=uuid.uuid4(),
        tenant_id=other_tenant.id,
        name="Class X",
        grade_level="10",
    )
    db_session.add_all([other_tenant, foreign_class])
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: _make_user(
        tenant_id=active_tenant.id,
        role="admin",
    )
    try:
        response = client.post(
            "/api/fees/structures",
            json={
                "fee_type": "tuition",
                "amount": 5000,
                "frequency": "monthly",
                "class_id": str(foreign_class.id),
            },
        )
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 400
    assert response.json()["detail"] == "Class not found"


def test_teacher_test_series_creation_publishes_lifecycle_defaults(client, db_session, active_tenant):
    school_class = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Class 10",
        grade_level="10",
    )
    subject = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        name="Mathematics",
    )
    db_session.add_all([school_class, subject])
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: _make_user(
        tenant_id=active_tenant.id,
        role="teacher",
    )
    try:
        response = client.post(
            "/api/teacher/test-series",
            json={
                "name": "Quarterly Maths Mock",
                "description": "Board prep",
                "total_marks": 100,
                "duration_minutes": 90,
                "class_id": str(school_class.id),
                "subject_id": str(subject.id),
            },
        )
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["status"] == "published"
    assert payload["published_at"] is not None

    stored = db_session.query(AssessmentSeriesModel).filter(AssessmentSeriesModel.id == uuid.UUID(payload["series_id"])).one()
    assert stored.class_id == school_class.id
    assert stored.subject_id == subject.id
    assert stored.assessment_kind == "mock_test"
    assert stored.grading_mode == "manual_review"
    assert stored.status == "published"
    assert stored.published_at is not None


def test_teacher_test_series_creation_rejects_subject_class_mismatch(client, db_session, active_tenant):
    class_a = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 9", grade_level="9")
    class_b = Class(id=uuid.uuid4(), tenant_id=active_tenant.id, name="Class 10", grade_level="10")
    subject = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=class_b.id,
        name="Science",
    )
    db_session.add_all([class_a, class_b, subject])
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: _make_user(
        tenant_id=active_tenant.id,
        role="teacher",
    )
    try:
        response = client.post(
            "/api/teacher/test-series",
            json={
                "name": "Mismatch",
                "description": "",
                "total_marks": 50,
                "duration_minutes": 45,
                "class_id": str(class_a.id),
                "subject_id": str(subject.id),
            },
        )
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 400
    assert response.json()["detail"] == "Subject does not belong to the selected class"


def test_student_mock_test_submission_enforces_lifecycle_and_marks(client, db_session, active_tenant):
    student_user = _make_user(tenant_id=active_tenant.id, role="student")
    draft_series = AssessmentSeriesModel(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Draft Mock",
        total_marks=100,
        duration_minutes=60,
        status="draft",
        created_by=uuid.uuid4(),
    )
    future_series = AssessmentSeriesModel(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Future Mock",
        total_marks=100,
        duration_minutes=60,
        status="published",
        opens_at=datetime.now(timezone.utc) + timedelta(days=1),
        created_by=uuid.uuid4(),
    )
    closed_series = AssessmentSeriesModel(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Closed Mock",
        total_marks=100,
        duration_minutes=60,
        status="published",
        closes_at=datetime.now(timezone.utc) - timedelta(days=1),
        created_by=uuid.uuid4(),
    )
    over_score_series = AssessmentSeriesModel(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Over Score Mock",
        total_marks=100,
        duration_minutes=60,
        status="published",
        created_by=uuid.uuid4(),
    )
    db_session.add_all([draft_series, future_series, closed_series, over_score_series])
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: student_user
    try:
        draft_response = client.post(
            f"/api/student/test-series/{draft_series.id}/submit",
            json={"marks_obtained": 20},
        )
        future_response = client.post(
            f"/api/student/test-series/{future_series.id}/submit",
            json={"marks_obtained": 20},
        )
        closed_response = client.post(
            f"/api/student/test-series/{closed_series.id}/submit",
            json={"marks_obtained": 20},
        )
        invalid_marks_response = client.post(
            f"/api/student/test-series/{over_score_series.id}/submit",
            json={"marks_obtained": 120},
        )
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert draft_response.status_code == 409
    assert draft_response.json()["detail"] == "Test series is not published"
    assert future_response.status_code == 409
    assert future_response.json()["detail"] == "Test series is not open yet"
    assert closed_response.status_code == 409
    assert closed_response.json()["detail"] == "Test series is closed"
    assert invalid_marks_response.status_code == 400
    assert invalid_marks_response.json()["detail"] == "Marks obtained cannot exceed total marks"
