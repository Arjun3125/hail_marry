import io

def test_admin_onboard_teachers_rejects_empty_csv(client, db_session, active_tenant):
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context
    import uuid
    
    # Establish Admin credentials
    admin_id = uuid.uuid4()
    admin = User(
        id=admin_id,
        tenant_id=active_tenant.id,
        email="admin@testschool.edu",
        full_name="Test Admin",
        role="admin",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()
    
    # Login
    resp = client.post("/api/auth/login", json={"email": "admin@testschool.edu", "password": "pass123!"})
    token = resp.json().get("access_token")
    
    # Test Empty File
    empty_csv = io.BytesIO(b"")
    resp_empty = client.post(
        "/api/admin/onboard/teachers",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("empty.csv", empty_csv, "text/csv")}
    )
    assert resp_empty.status_code == 400
    assert "No readable names found" in resp_empty.text

def test_admin_onboard_teachers_rejects_random_binary(client, db_session, active_tenant):
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context
    import uuid
    import os
    
    # Establish Admin credentials since DB is rolled back per test
    admin_id = uuid.uuid4()
    admin = User(
        id=admin_id,
        tenant_id=active_tenant.id,
        email="admin2@testschool.edu",
        full_name="Test Admin 2",
        role="admin",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True
    )
    db_session.add(admin)
    db_session.commit()

    resp = client.post("/api/auth/login", json={"email": "admin2@testschool.edu", "password": "pass123!"})
    token = resp.json().get("access_token")
    
    # Test Random Binary disguised as CSV
    binary_content = os.urandom(1024)
    malformed_csv = io.BytesIO(binary_content)
    resp_malformed = client.post(
        "/api/admin/onboard/teachers",
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("malformed.csv", malformed_csv, "text/csv")}
    )
    
    assert resp_malformed.status_code == 400
    assert "Invalid text encoding" in resp_malformed.text
