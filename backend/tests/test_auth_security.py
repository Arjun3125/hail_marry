from uuid import uuid4

def test_login_brute_force_rate_limit(client, db_session, active_tenant, stub_ai_query_runtime):
    """Ensure governed AI requests trip the burst limiter before the AI stack matters."""
    hit_rate_limit = False
    
    # Need valid user token up front to pass into the AI query gateway and fetch user_id in middleware
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context
    import uuid
    
    student_id = uuid.uuid4()
    student = User(
        id=student_id,
        tenant_id=active_tenant.id,
        email="test@testschool.edu",
        full_name="Test User",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True
    )
    db_session.add(student)
    db_session.commit()

    resp = client.post("/api/auth/login", json={"email": "test@testschool.edu", "password": "pass123!"})
    token = resp.json().get("access_token")
    assert token is not None, "Failed to login for rate limit test"
    
    # Default rate limit is 5 requests per minute. Use a stubbed AI runtime so the test
    # exercises middleware behavior rather than embeddings/retrieval latency.
    for _ in range(15):
        resp = client.post(
            "/api/ai/query", 
            headers={"Authorization": f"Bearer {token}"},
            json={"query": "test query", "mode": "qa"}
        )
        if resp.status_code == 429:
            hit_rate_limit = True
            break
            
    assert hit_rate_limit, "Rate Limiter did not trigger on brute force AI requests."

def test_jwt_none_algorithm_rejection(client):
    """Ensure the backend actively rejects forged JWTs using alg: 'none'."""
    # A forged token with {"alg":"none","typ":"JWT"}
    forged_token = "eyJhbGciOiJub25lIiwidHlwIjoiSldUIn0.eyJzdWIiOiJ1c2VyMTIzIiwidGVuYW50X2lkIjoiMTIzIn0."
    
    resp = client.get(
        "/api/auth/me", 
        headers={"Authorization": f"Bearer {forged_token}"}
    )
    assert resp.status_code == 401

def test_student_cannot_access_admin_endpoints(client, db_session, active_tenant):
    """Ensure Role-Based Access Control (RBAC) boundary explicitly bounces Students from Admin routes."""
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context
    
    student_id = uuid4()
    student = User(
        id=student_id,
        tenant_id=active_tenant.id,
        email="student@testschool.edu",
        full_name="Test Student",
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True
    )
    db_session.add(student)
    db_session.commit()
    
    # Login to get JWT
    resp = client.post("/api/auth/login", json={"email": "student@testschool.edu", "password": "pass123!"})
    token = resp.json().get("access_token")
    
    # Try hitting an admin-exclusive endpoint
    resp_admin = client.post(
        "/api/admin/onboard/teachers", 
        headers={"Authorization": f"Bearer {token}"},
        files={"file": ("test.csv", b"dummy content", "text/csv")}
    )
    
    assert resp_admin.status_code == 403
    assert "not authorized" in resp_admin.text.lower()
