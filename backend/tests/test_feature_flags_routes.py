from uuid import uuid4


def _create_user(db_session, tenant_id, *, email: str, role: str, password: str = "pass123!"):
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context

    user = User(
        id=uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=f"{role.title()} User",
        role=role,
        hashed_password=pwd_context.hash(password),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def _login(client, email: str, password: str = "pass123!") -> str:
    response = client.post("/api/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200
    token = response.json().get("access_token")
    assert token
    return token


def test_feature_flags_require_admin_role(client, db_session, active_tenant):
    student = _create_user(
        db_session,
        active_tenant.id,
        email="student-features@testschool.edu",
        role="student",
    )
    _ = student
    token = _login(client, "student-features@testschool.edu")

    response = client.get("/api/features", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 403


def test_feature_flag_toggle_creates_audit_log(client, db_session, active_tenant):
    from src.domains.platform.models.audit import AuditLog
    from src.domains.platform.models.feature_flag import FeatureFlag

    _create_user(
        db_session,
        active_tenant.id,
        email="admin-features@testschool.edu",
        role="admin",
    )
    token = _login(client, "admin-features@testschool.edu")

    feature = db_session.query(FeatureFlag).filter(FeatureFlag.feature_id == "ai_chat").first()
    if feature is None:
        feature = FeatureFlag(feature_id="ai_chat", name="AI Chat", category="AI", enabled=False)
        db_session.add(feature)
        db_session.commit()
    feature.enabled = True
    db_session.commit()

    response = client.post(
        "/api/features/ai_chat/toggle",
        headers={"Authorization": f"Bearer {token}"},
        json={"enabled": False},
    )
    assert response.status_code == 200
    assert response.json()["enabled"] is False

    audit = db_session.query(AuditLog).filter(AuditLog.action == "feature_flag.toggled").first()
    assert audit is not None
    assert audit.tenant_id == active_tenant.id
    assert audit.metadata_["feature_id"] == "ai_chat"
    assert audit.metadata_["old_enabled"] is True
    assert audit.metadata_["new_enabled"] is False
