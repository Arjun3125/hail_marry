import uuid


def _create_student_and_login(client, db_session, tenant_id, email: str):
    from src.domains.identity.models.user import User
    from src.domains.identity.routes.auth import pwd_context

    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name="AI Query Tester",
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
    token = response.json().get("access_token")
    assert token, "Failed to obtain auth token for AI query test"
    return token


def test_ai_query_rejects_invalid_mode(client, db_session, active_tenant):
    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="invalid-mode@testschool.edu",
    )

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Explain photosynthesis", "mode": "not_a_real_mode"},
    )

    assert response.status_code == 422
    assert "mode" in response.text


def test_ai_query_rejects_empty_query(client, db_session, active_tenant):
    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="empty-query@testschool.edu",
    )

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "   ", "mode": "qa"},
    )

    assert response.status_code == 422
    assert "Query must not be empty" in response.text


def test_demo_mode_returns_prompt_aware_content_instead_of_stale_history(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    from config import settings
    from src.domains.platform.models.ai import AIQuery

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="demo-ai@testschool.edu",
    )

    stale_log = AIQuery(
        tenant_id=active_tenant.id,
        user_id=uuid.uuid4(),
        query_text="Old unrelated prompt",
        mode="quiz",
        response_text="STALE SALT MARCH QUIZ CONTENT",
        token_usage=10,
        response_time_ms=1,
        citation_count=0,
    )
    db_session.add(stale_log)
    db_session.commit()

    monkeypatch.setattr(settings.app, "demo_mode", True)

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Explain photosynthesis briefly", "mode": "quiz"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["mode"] == "quiz"
    assert payload["runtime_mode"] == "demo"
    assert payload["is_demo_response"] is True
    assert "Demo mode preview" in payload["demo_notice"]
    assert "photosynthesis" in payload["answer"].lower()
    assert "STALE SALT MARCH QUIZ CONTENT" not in payload["answer"]
    assert payload["citations"] == []
    assert payload["citation_valid"] is False
