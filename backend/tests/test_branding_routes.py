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


def test_branding_save_requires_admin_role(client, db_session, active_tenant):
    _create_user(
        db_session,
        active_tenant.id,
        email="student-branding@testschool.edu",
        role="student",
    )
    token = _login(client, "student-branding@testschool.edu")

    response = client.patch(
        "/api/branding/save",
        headers={"Authorization": f"Bearer {token}"},
        json={"primary_color": "#112233"},
    )
    assert response.status_code == 403


def test_branding_save_updates_tenant_and_audit_log(client, db_session, active_tenant):
    from src.domains.identity.models.tenant import Tenant
    from src.domains.platform.models.audit import AuditLog

    _create_user(
        db_session,
        active_tenant.id,
        email="admin-branding@testschool.edu",
        role="admin",
    )
    token = _login(client, "admin-branding@testschool.edu")

    response = client.patch(
        "/api/branding/save",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "primary_color": "#112233",
            "secondary_color": "#445566",
            "font_family": "Poppins",
        },
    )
    assert response.status_code == 200
    assert response.json()["success"] is True

    tenant = db_session.query(Tenant).filter(Tenant.id == active_tenant.id).first()
    assert tenant is not None
    assert tenant.primary_color == "#112233"
    assert tenant.secondary_color == "#445566"
    assert tenant.font_family == "Poppins"

    audit = db_session.query(AuditLog).filter(AuditLog.action == "branding.updated").first()
    assert audit is not None
    assert audit.tenant_id == active_tenant.id
    assert audit.metadata_["primary_color"] == "#112233"
    assert audit.metadata_["secondary_color"] == "#445566"
    assert audit.metadata_["font_family"] == "Poppins"
