import importlib
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


def test_ai_query_audit_mode_bypasses_cache_and_returns_retrieval_audit(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    from config import settings

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="audit-ai@testschool.edu",
    )

    ai_routes = importlib.import_module("src.interfaces.rest_api.ai.routes.ai")

    async def fake_prepare_ai_query(**kwargs):
        return kwargs["query"], [], kwargs["query"], ""

    async def fake_run_text_query(request, trace_id=None):
        assert request.audit_retrieval is True
        return {
            "answer": "Grounded answer [biology.pdf_p4]",
            "citations": [],
            "token_usage": 8,
            "mode": "qa",
            "has_context": True,
            "citation_valid": True,
            "citation_count": 1,
            "retrieval_audit": {
                "chunk_count": 1,
                "returned_chunk_count": 1,
                "thresholds": {"min_vector_score": 0.2, "min_rerank_score": 0.0},
                "chunks": [
                    {
                        "document_id": "doc-1",
                        "source": "biology.pdf",
                        "page": "4",
                        "section": "10.1",
                        "citation": "[biology.pdf_p4]",
                        "vector_score": 0.88,
                        "rerank_score": 0.91,
                        "compressed": False,
                    }
                ],
            },
        }

    def fail_cache_read(*args, **kwargs):
        raise AssertionError("audit mode should bypass cache reads")

    def fail_cache_write(*args, **kwargs):
        raise AssertionError("audit mode should bypass cache writes")

    monkeypatch.setattr(settings.app, "demo_mode", False)
    monkeypatch.setattr(ai_routes, "_prepare_ai_query", fake_prepare_ai_query)
    monkeypatch.setattr(ai_routes, "run_text_query", fake_run_text_query)
    monkeypatch.setattr(ai_routes, "get_cached_response", fail_cache_read)
    monkeypatch.setattr(ai_routes, "cache_response", fail_cache_write)

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Explain topic 10.1", "mode": "qa", "audit_retrieval": True},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "retrieval_audit" in payload
    assert payload["retrieval_audit"]["chunk_count"] == 1
    assert payload["retrieval_audit"]["chunks"][0]["document_id"] == "doc-1"


def test_ai_query_job_demo_mode_marks_mock_result(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    from config import settings

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="demo-ai-job@testschool.edu",
    )

    monkeypatch.setattr(settings.app, "demo_mode", True)

    response = client.post(
        "/api/ai/query/jobs",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Explain photosynthesis briefly", "mode": "qa"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] == "demo"
    assert payload["is_demo_response"] is True
    assert "Demo mode preview" in payload["demo_notice"]
    assert payload["result"]["runtime_mode"] == "demo"
    assert payload["result"]["is_demo_response"] is True
    assert payload["result"]["has_context"] is False
    assert payload["result"]["citation_valid"] is False


def test_student_generate_tool_demo_mode_marks_mock_result(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    from config import settings

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="demo-student-tool@testschool.edu",
    )

    monkeypatch.setattr(settings.app, "demo_mode", True)

    response = client.post(
        "/api/student/tools/generate",
        headers={"Authorization": f"Bearer {token}"},
        json={"tool": "mindmap", "topic": "photosynthesis"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] == "demo"
    assert payload["is_demo_response"] is True
    assert "Demo mode preview" in payload["demo_notice"]
    assert payload["demo_sources"] == ["demo-mode"]


def test_student_generate_tool_job_demo_mode_marks_mock_result(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    from config import settings

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="demo-student-tool-job@testschool.edu",
    )

    monkeypatch.setattr(settings.app, "demo_mode", True)

    response = client.post(
        "/api/student/tools/generate/jobs",
        headers={"Authorization": f"Bearer {token}"},
        json={"tool": "quiz", "topic": "photosynthesis"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["runtime_mode"] == "demo"
    assert payload["is_demo_response"] is True
    assert "Demo mode preview" in payload["demo_notice"]
    assert payload["result"]["runtime_mode"] == "demo"
    assert payload["result"]["is_demo_response"] is True


def test_ai_query_applies_personalized_defaults_when_request_uses_defaults(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    ai_routes = importlib.import_module("src.interfaces.rest_api.ai.routes.ai")

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="personalized-ai-defaults@testschool.edu",
    )

    async def fake_prepare_ai_query(**kwargs):
        return kwargs["query"], [], kwargs["query"], ""

    async def fake_run_text_query(request, trace_id=None):
        assert request.language == "hindi"
        assert request.response_length == "brief"
        assert request.expertise_level == "simple"
        assert request.learner_profile["preferred_language"] == "hindi"
        assert request.learner_profile["primary_subjects"] == ["Biology"]
        assert request.learner_topic_context["topic"] == "Photosynthesis"
        assert request.learner_topic_context["focus_concepts"] == ["chlorophyll"]
        assert request.learner_topic_context["repeated_confusion_count"] == 2
        return {
            "answer": "Grounded answer",
            "citations": [],
            "token_usage": 5,
            "mode": "qa",
            "has_context": True,
            "citation_valid": True,
            "citation_count": 0,
        }

    monkeypatch.setattr(ai_routes, "_prepare_ai_query", fake_prepare_ai_query)
    monkeypatch.setattr(ai_routes, "run_text_query", fake_run_text_query)
    monkeypatch.setattr(
        ai_routes,
        "get_learner_profile_dict",
        lambda *args, **kwargs: {
            "preferred_language": "hindi",
            "preferred_response_length": "brief",
            "inferred_expertise_level": "simple",
            "primary_subjects": ["Biology"],
        },
    )
    monkeypatch.setattr(
        ai_routes,
        "get_topic_mastery_snapshot",
        lambda *args, **kwargs: {
            "topic": "Photosynthesis",
            "mastery_score": 39.0,
            "confidence_score": 0.32,
            "concepts": [{"concept": "chlorophyll"}],
        },
    )
    monkeypatch.setattr(ai_routes, "count_recent_confusion_queries", lambda *args, **kwargs: 2)
    monkeypatch.setattr(ai_routes, "record_ai_confusion_pattern", lambda *args, **kwargs: [])

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Explain photosynthesis", "mode": "qa"},
    )

    assert response.status_code == 200


def test_ai_query_preserves_explicit_user_style_overrides(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    ai_routes = importlib.import_module("src.interfaces.rest_api.ai.routes.ai")

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="personalized-ai-overrides@testschool.edu",
    )

    async def fake_prepare_ai_query(**kwargs):
        return kwargs["query"], [], kwargs["query"], ""

    async def fake_run_text_query(request, trace_id=None):
        assert request.language == "english"
        assert request.response_length == "detailed"
        assert request.expertise_level == "advanced"
        return {
            "answer": "Grounded answer",
            "citations": [],
            "token_usage": 5,
            "mode": "qa",
            "has_context": True,
            "citation_valid": True,
            "citation_count": 0,
        }

    monkeypatch.setattr(ai_routes, "_prepare_ai_query", fake_prepare_ai_query)
    monkeypatch.setattr(ai_routes, "run_text_query", fake_run_text_query)
    monkeypatch.setattr(
        ai_routes,
        "get_learner_profile_dict",
        lambda *args, **kwargs: {
            "preferred_language": "marathi",
            "preferred_response_length": "brief",
            "inferred_expertise_level": "simple",
            "primary_subjects": ["Biology"],
        },
    )
    monkeypatch.setattr(
        ai_routes,
        "get_topic_mastery_snapshot",
        lambda *args, **kwargs: {
            "topic": "Photosynthesis",
            "mastery_score": 82.0,
            "confidence_score": 0.8,
            "concepts": [{"concept": "chlorophyll"}],
        },
    )
    monkeypatch.setattr(ai_routes, "count_recent_confusion_queries", lambda *args, **kwargs: 0)

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": "Explain photosynthesis",
            "mode": "qa",
            "language": "english",
            "response_length": "detailed",
            "expertise_level": "advanced",
        },
    )

    assert response.status_code == 200


def test_ai_query_uses_fallback_model_when_token_budget_is_hot(
    client,
    db_session,
    active_tenant,
    monkeypatch,
):
    from src.domains.platform.services.usage_governance import record_usage_event
    from config import settings

    ai_routes = importlib.import_module("src.interfaces.rest_api.ai.routes.ai")

    token = _create_student_and_login(
        client,
        db_session,
        active_tenant.id,
        email="fallback-ai@testschool.edu",
    )

    user = db_session.query(importlib.import_module("src.domains.identity.models.user").User).filter_by(
        email="fallback-ai@testschool.edu"
    ).first()
    record_usage_event(
        db_session,
        tenant_id=active_tenant.id,
        user_id=user.id,
        metric="llm_tokens",
        token_usage=26000,
        model_used=settings.llm.model,
    )
    db_session.commit()

    async def fake_prepare_ai_query(**kwargs):
        return kwargs["query"], [], kwargs["query"], ""

    async def fake_run_text_query(request, trace_id=None):
        assert request.model_override == settings.llm.fallback_model
        assert request.max_prompt_tokens == 2000
        assert request.max_completion_tokens == 800
        return {
            "answer": "Grounded answer",
            "citations": [],
            "token_usage": 9,
            "mode": "qa",
            "has_context": True,
            "citation_valid": True,
            "citation_count": 0,
            "model_used": request.model_override,
        }

    monkeypatch.setattr(ai_routes, "_prepare_ai_query", fake_prepare_ai_query)
    monkeypatch.setattr(ai_routes, "run_text_query", fake_run_text_query)
    monkeypatch.setattr(ai_routes, "record_ai_confusion_pattern", lambda *args, **kwargs: [])

    response = client.post(
        "/api/ai/query",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Explain photosynthesis", "mode": "qa"},
    )

    assert response.status_code == 200
