from datetime import datetime, timedelta, timezone
from uuid import uuid4


def _create_student_with_qr_token(db_session, tenant_id, *, email: str, token: str):
    from src.domains.identity.models.user import User

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="QR Student",
        role="student",
        is_active=True,
        is_deleted=False,
        qr_login_token=token,
        qr_login_expires_at=datetime.now(timezone.utc) + timedelta(minutes=10),
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_qr_login_route_is_registered_once(client):
    routes = [
        route
        for route in client.app.routes
        if getattr(route, "path", "") == "/api/auth/qr-login/{token}" and "GET" in getattr(route, "methods", set())
    ]
    assert len(routes) == 1


def test_qr_login_redirect_sets_cookies_and_invalidates_token(client, db_session, active_tenant):

    student = _create_student_with_qr_token(
        db_session,
        active_tenant.id,
        email="qr-student@testschool.edu",
        token="qr-token-12345",
    )

    response = client.get("/api/auth/qr-login/qr-token-12345", follow_redirects=False)
    assert response.status_code in {302, 307}
    assert response.headers["location"] == "/student/overview"
    assert "access_token=" in response.headers.get("set-cookie", "")

    db_session.refresh(student)
    assert student.qr_login_token is None
    assert student.qr_login_expires_at is None

    second_response = client.get("/api/auth/qr-login/qr-token-12345", follow_redirects=False)
    assert second_response.status_code == 401
