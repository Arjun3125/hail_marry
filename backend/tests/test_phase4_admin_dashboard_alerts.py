from __future__ import annotations

import uuid

from auth.dependencies import get_current_user
from src.domains.academic.models.core import Class
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context


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


def test_admin_dashboard_exposes_student_risk_summary_and_alerts(client, db_session, active_tenant, monkeypatch):
    import src.domains.administrative.routes.admin as admin_routes

    admin_user = _user(
        tenant_id=active_tenant.id,
        role="admin",
        email="admin-risk@testschool.edu",
        full_name="Admin Risk",
    )
    student_user = _user(
        tenant_id=active_tenant.id,
        role="student",
        email="student-risk@testschool.edu",
        full_name="Aarav Kumar",
    )
    school_class = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Class 10",
        grade_level="10",
    )
    student_profile = StudentProfile(
        tenant_id=active_tenant.id,
        user_id=student_user.id,
        current_class_id=school_class.id,
        attendance_pct=58.0,
        overall_score_pct=39.0,
        absent_streak=5,
        academic_risk="high",
        fee_risk="medium",
        dropout_risk="high",
    )
    db_session.add_all([admin_user, student_user, school_class, student_profile])
    db_session.commit()

    client.app.dependency_overrides[get_current_user] = lambda: admin_user
    monkeypatch.setattr(admin_routes, "load_queue_metrics", lambda _tenant_id: {"pending_depth": 0, "processing_depth": 0, "failure_rate_pct": 0, "stuck_jobs": 0})
    monkeypatch.setattr(admin_routes, "list_active_alerts", lambda _tenant_id: [])
    try:
        response = client.get("/api/admin/dashboard")
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 200
    payload = response.json()
    assert payload["student_risk_summary"] == {
        "high_risk_students": 1,
        "medium_risk_students": 0,
        "academic_high_risk": 1,
        "fee_high_risk": 0,
        "dropout_high_risk": 1,
    }
    assert len(payload["student_risk_alerts"]) == 1
    alert = payload["student_risk_alerts"][0]
    assert alert["student_name"] == "Aarav Kumar"
    assert alert["class_name"] == "Class 10"
    assert alert["academic_risk"] == "high"
    assert alert["fee_risk"] == "medium"
    assert alert["dropout_risk"] == "high"
    assert alert["attendance_pct"] == 58.0
    assert alert["overall_score_pct"] == 39.0
