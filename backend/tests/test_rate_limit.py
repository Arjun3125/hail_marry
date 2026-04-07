"""Tests for rate limiting middleware."""
import pytest

from constants import RATE_LIMIT_WINDOW_SECONDS


class TestRateLimitConstants:
    """Verify rate limit configuration."""

    def test_window_is_60_seconds(self):
        assert RATE_LIMIT_WINDOW_SECONDS == 60

    def test_rate_limit_middleware_uses_constant(self):
        """RateLimitMiddleware.WINDOW_SECONDS should match the centralized constant."""
        from middleware.rate_limit import RateLimitMiddleware
        assert RateLimitMiddleware.WINDOW_SECONDS == RATE_LIMIT_WINDOW_SECONDS

    def test_default_max_requests_is_5(self):
        """Default burst limit should be 5 per minute."""
        from middleware.rate_limit import RateLimitMiddleware
        assert RateLimitMiddleware.MAX_REQUESTS == 5


class TestRateLimitIntegration:
    """Integration tests for rate limiting via TestClient."""

    def test_non_ai_path_not_rate_limited(self, client):
        """Regular endpoints should never be rate limited."""
        for _ in range(20):
            resp = client.get("/health")
            assert resp.status_code == 200

    def test_ai_path_rate_limited_after_burst(self, client, db_session, active_tenant, stub_ai_query_runtime):
        """AI endpoints should return 429 after exceeding burst limit."""
        from src.domains.identity.models.user import User
        from src.domains.identity.routes.auth import pwd_context
        import uuid

        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            tenant_id=active_tenant.id,
            email="ratelimit@testschool.edu",
            full_name="Rate Limit Tester",
            role="student",
            hashed_password=pwd_context.hash("pass123!"),
            is_active=True,
        )
        db_session.add(user)
        db_session.commit()

        resp = client.post("/api/auth/login", json={
            "email": "ratelimit@testschool.edu",
            "password": "pass123!"
        })
        token = resp.json().get("access_token")
        if not token:
            pytest.skip("Login failed — rate limit test requires auth")

        hit_429 = False
        for _ in range(15):
            resp = client.post(
                "/api/ai/query",
                headers={"Authorization": f"Bearer {token}"},
                json={"query": "test", "mode": "qa"},
            )
            if resp.status_code == 429:
                hit_429 = True
                assert "Rate limit exceeded" in resp.json()["detail"]
                assert "Retry-After" in resp.headers
                assert int(resp.headers["Retry-After"]) >= 1
                break

        assert hit_429, "Rate limiter should have triggered"
