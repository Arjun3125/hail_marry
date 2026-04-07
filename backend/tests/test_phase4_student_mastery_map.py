import uuid
from datetime import datetime, timedelta, timezone

from src.domains.academic.models.core import Class, Subject
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.platform.models.topic_mastery import TopicMastery


def _create_student_and_login(client, db_session, tenant_id, email: str):
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="Mastery Map Student",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()

    response = client.post(
        "/api/auth/login",
        json={"email": email, "password": "pass123!"},
    )
    assert response.status_code == 200
    return user, response.json()["access_token"]


def test_student_mastery_endpoint_returns_live_profile_and_subtopic_signal(client, db_session, active_tenant):
    user, token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        "student-mastery@testschool.edu",
    )

    class_row = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Class 10",
        grade_level="10",
        academic_year="2026-27",
    )
    db_session.add(class_row)
    db_session.flush()

    biology = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=class_row.id,
        name="Biology",
    )
    chemistry = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=class_row.id,
        name="Chemistry",
    )
    db_session.add_all([biology, chemistry])
    db_session.flush()

    profile = StudentProfile(
        tenant_id=active_tenant.id,
        user_id=user.id,
        attendance_pct=83.5,
        absent_streak=1,
        overall_score_pct=66.0,
        exam_readiness_pct=71.0,
        current_streak_days=9,
        total_reviews_completed=14,
        strongest_subject="Biology",
        weakest_subject="Chemistry",
        academic_risk="medium",
        dropout_risk="low",
        fee_risk="low",
        last_review_at=datetime.now(timezone.utc) - timedelta(days=2),
        subject_mastery_map={"Biology": 74.0, "Chemistry": 58.0},
    )
    db_session.add(profile)
    db_session.flush()

    now = datetime.now(timezone.utc)
    db_session.add_all(
        [
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                subject_id=biology.id,
                topic="Photosynthesis",
                concept="core",
                mastery_score=44.0,
                confidence_score=0.61,
                last_evidence_type="quiz_completed",
                review_due_at=now - timedelta(days=1),
                updated_at=now - timedelta(hours=2),
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                subject_id=biology.id,
                topic="Photosynthesis",
                concept="chlorophyll",
                mastery_score=39.0,
                confidence_score=0.57,
                updated_at=now - timedelta(hours=2),
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                subject_id=biology.id,
                topic="Photosynthesis",
                concept="stomata",
                mastery_score=52.0,
                confidence_score=0.6,
                updated_at=now - timedelta(hours=2),
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                subject_id=chemistry.id,
                topic="Chemical Bonding",
                concept="core",
                mastery_score=81.0,
                confidence_score=0.72,
                last_evidence_type="review_completed",
                review_due_at=now + timedelta(days=4),
                updated_at=now - timedelta(hours=1),
            ),
            TopicMastery(
                tenant_id=active_tenant.id,
                user_id=user.id,
                subject_id=chemistry.id,
                topic="Chemical Bonding",
                concept="ionic",
                mastery_score=76.0,
                confidence_score=0.7,
                updated_at=now - timedelta(hours=1),
            ),
        ]
    )
    db_session.commit()

    response = client.get(
        "/api/student/mastery",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["summary"]["exam_readiness_pct"] == 71.0
    assert payload["summary"]["academic_risk"] == "medium"
    assert payload["insights"]["tracked_topics"] == 2
    assert payload["insights"]["due_reviews"] == 1
    assert payload["recommended_actions"] == ["Photosynthesis"]

    assert payload["subject_mastery"] == [
        {"subject": "Biology", "score": 44.0, "fullMark": 100},
        {"subject": "Chemistry", "score": 81.0, "fullMark": 100},
    ]

    first_topic = payload["focus_topics"][0]
    assert first_topic["topic"] == "Photosynthesis"
    assert first_topic["subject"] == "Biology"
    assert first_topic["mastery_score"] == 44.0
    assert [item["concept"] for item in first_topic["concepts"]] == ["chlorophyll", "stomata"]
