"""Phase 4 — verify /api/student/mastery-map returns real sub-topic signal.

Tests that the mastery map endpoint:
- returns real data from StudentProfile and TopicMastery, not mock placeholders
- exposes sub-topic concept-level breakdown
- surfaces risk indicators from unified profile records
- works correctly when no mastery data exists yet (graceful fallback)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

from auth.dependencies import get_current_user
from src.domains.academic.models.core import Class, Subject
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.platform.models.topic_mastery import TopicMastery


def _user(*, tenant_id, role: str, email: str, full_name: str) -> User:
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )


def test_mastery_map_returns_subtopic_signal_from_real_records(client, db_session, active_tenant):
    """The mastery map must derive its data from TopicMastery + StudentProfile, not mock constants."""
    student = _user(
        tenant_id=active_tenant.id,
        role="student",
        email="mastery-stu@test.edu",
        full_name="Priya Sharma",
    )
    cls = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="10th Grade",
    )
    subject = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=cls.id,
        name="Physics",
    )
    profile = StudentProfile(
        tenant_id=active_tenant.id,
        user_id=student.id,
        attendance_pct=78.5,
        absent_streak=1,
        overall_score_pct=62.0,
        current_streak_days=5,
        dropout_risk="low",
        academic_risk="medium",
        fee_risk="low",
        strongest_subject="Biology",
        weakest_subject="Physics",
    )
    now = datetime.now(timezone.utc)
    core_mastery = TopicMastery(
        tenant_id=active_tenant.id,
        user_id=student.id,
        subject_id=subject.id,
        topic="Electromagnetic Induction",
        concept="core",
        mastery_score=42.0,
        confidence_score=0.55,
        evidence_count=3,
        last_evidence_type="quiz_completed",
        last_evidence_score=55.0,
        last_evidence_at=now,
        review_due_at=now - timedelta(days=1),
        updated_at=now,
    )
    concept_mastery = TopicMastery(
        tenant_id=active_tenant.id,
        user_id=student.id,
        subject_id=subject.id,
        topic="Electromagnetic Induction",
        concept="faraday",
        mastery_score=38.0,
        confidence_score=0.48,
        evidence_count=2,
        last_evidence_type="review_completed",
        updated_at=now,
    )
    db_session.add_all([student, subject, profile, core_mastery, concept_mastery])
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: student
    try:
        response = client.get("/api/student/mastery-map")
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()

    # Summary should come from real StudentProfile
    summary = payload["summary"]
    assert summary["attendance_pct"] == 78.5
    assert summary["absent_streak"] == 1
    assert summary["overall_score_pct"] == 62.0
    assert summary["current_streak_days"] == 5
    assert summary["academic_risk"] == "medium"
    assert summary["dropout_risk"] == "low"
    assert summary["strongest_subject"] == "Biology"
    assert summary["weakest_subject"] == "Physics"

    # Subject mastery should aggregate from TopicMastery, not be hardcoded
    assert len(payload["subject_mastery"]) >= 1
    physics_entry = next(
        (item for item in payload["subject_mastery"] if item["subject"] == "Physics"),
        None,
    )
    assert physics_entry is not None
    assert physics_entry["score"] == 42.0

    # Focus topics must include sub-topic concepts
    assert len(payload["focus_topics"]) >= 1
    topic_entry = payload["focus_topics"][0]
    assert topic_entry["topic"] == "Electromagnetic Induction"
    assert topic_entry["mastery_score"] == 42.0
    assert topic_entry["subject"] == "Physics"
    assert isinstance(topic_entry["concepts"], list)
    assert any(c["concept"] == "faraday" for c in topic_entry["concepts"])

    # Insights should reflect real tracked data
    assert payload["insights"]["tracked_topics"] >= 1
    assert payload["insights"]["low_mastery_topics"] >= 1
    assert payload["insights"]["due_reviews"] >= 1

    # Recommended actions should flag weak topics
    assert "Electromagnetic Induction" in payload["recommended_actions"]


def test_mastery_map_graceful_with_no_data(client, db_session, active_tenant):
    """Mastery map should return a valid shape even for a student with no profile/mastery rows."""
    student = _user(
        tenant_id=active_tenant.id,
        role="student",
        email="mastery-empty@test.edu",
        full_name="Empty Student",
    )
    db_session.add(student)
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: student
    try:
        response = client.get("/api/student/mastery-map")
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()
    assert "summary" in payload
    assert "subject_mastery" in payload
    assert "focus_topics" in payload
    assert "insights" in payload
    assert payload["summary"]["attendance_pct"] == 0.0
    assert payload["insights"]["tracked_topics"] == 0


def test_mastery_map_rejects_non_student(client, db_session, active_tenant):
    """Mastery map must reject non-student roles with 403."""
    teacher = _user(
        tenant_id=active_tenant.id,
        role="teacher",
        email="mastery-teacher@test.edu",
        full_name="Teacher User",
    )
    db_session.add(teacher)
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: teacher
    try:
        response = client.get("/api/student/mastery-map")
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
