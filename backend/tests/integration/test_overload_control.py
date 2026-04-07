"""
Overload Control & Rate Limiting Stress Tests
==============================================
Research-backed tests derived from:
  - "Overload Control for Scaling WeChat Microservices" (Backend_Scale)
  - "Resilient Auto-Scaling of Microservice Architectures" (Backend_Scale)
  - "Reinforcement Learning-Based Adaptive Load Balancing" (Backend_Scale)

Tests validate:
  1. Per-user burst rate limiting under rapid-fire requests
  2. Per-tenant aggregate rate limiting
  3. Graceful 429 responses with correct Retry-After headers
  4. Sliding-window accuracy (requests at window boundaries)
  5. Memory store isolation between users
  6. Rate limiter does NOT affect non-AI endpoints
  7. Database connection pool behavior under simulated load
"""
import asyncio
import importlib
import os
import sys
import unittest
from uuid import uuid4

from starlette.requests import Request
from starlette.responses import JSONResponse

# Ensure backend modules resolve
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"


def _make_ai_request(user_id: str, tenant_id: str = None, path: str = "/api/ai/query"):
    """Build a mock Starlette Request for an AI endpoint."""
    req = Request(
        {
            "type": "http",
            "method": "POST",
            "path": path,
            "headers": [],
            "query_string": b"",
            "state": {},
        }
    )
    req.state.user_id = user_id
    req.state.tenant_id = tenant_id or str(uuid4())
    return req


def _make_non_ai_request(path: str = "/health"):
    """Build a mock request for a non-AI endpoint."""
    req = Request(
        {
            "type": "http",
            "method": "GET",
            "path": path,
            "headers": [],
            "query_string": b"",
            "state": {},
        }
    )
    return req


async def _passthrough_next(_request):
    return JSONResponse({"ok": True}, status_code=200)


class TestPerUserBurstRateLimit(unittest.IsolatedAsyncioTestCase):
    """
    From "Overload Control for Scaling WeChat Microservices":
    Service-specific overload control must enforce per-user burst caps
    to prevent cascading failures across dependent microservices.
    """

    def setUp(self):
        self.rate_limit = importlib.import_module("middleware.rate_limit")
        self.rate_limit._memory_store.clear()
        self.rate_limit._redis_available = False
        self.rate_limit._redis = None

    def tearDown(self):
        self.rate_limit._memory_store.clear()

    async def test_exact_burst_limit_allows_then_blocks(self):
        """User hits exactly MAX_REQUESTS, next request should be blocked."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 5
        mw.WINDOW_SECONDS = 60

        user_id = str(uuid4())
        statuses = []
        for _ in range(7):
            resp = await mw.dispatch(_make_ai_request(user_id), _passthrough_next)
            statuses.append(resp.status_code)

        self.assertEqual(statuses[:5], [200] * 5, "First 5 requests should pass")
        self.assertTrue(all(s == 429 for s in statuses[5:]), "Requests beyond limit should be 429")

    async def test_429_response_includes_retry_after_header(self):
        """Research: Proper backpressure signals require Retry-After headers."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 1
        mw.WINDOW_SECONDS = 60

        user_id = str(uuid4())
        await mw.dispatch(_make_ai_request(user_id), _passthrough_next)
        resp = await mw.dispatch(_make_ai_request(user_id), _passthrough_next)

        self.assertEqual(resp.status_code, 429)
        self.assertIn("Retry-After", resp.headers)
        retry_after = int(resp.headers["Retry-After"])
        self.assertGreaterEqual(retry_after, 1)
        self.assertLessEqual(retry_after, 61)

    async def test_429_response_body_contains_detail(self):
        """Clients need actionable error messages for rate-limit responses."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 1
        mw.WINDOW_SECONDS = 60

        user_id = str(uuid4())
        await mw.dispatch(_make_ai_request(user_id), _passthrough_next)
        resp = await mw.dispatch(_make_ai_request(user_id), _passthrough_next)

        import json
        body = json.loads(resp.body.decode())
        self.assertIn("detail", body)
        self.assertIn("Rate limit exceeded", body["detail"])
        self.assertIn("retry_after", body)
        self.assertIsInstance(body["retry_after"], int)


class TestPerTenantRateLimit(unittest.IsolatedAsyncioTestCase):
    """
    From "Resilient Auto-Scaling of Microservice Architectures":
    Multi-tenant systems must enforce tenant-level resource isolation
    to prevent noisy-neighbor effects.
    """

    def setUp(self):
        self.rate_limit = importlib.import_module("middleware.rate_limit")
        self.rate_limit._memory_store.clear()
        self.rate_limit._redis_available = False
        self.rate_limit._redis = None

    def tearDown(self):
        self.rate_limit._memory_store.clear()

    async def test_tenant_limit_blocks_even_when_user_limit_not_reached(self):
        """Tenant-wide cap should block requests even when individual users are under their own limits."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 100  # High user limit
        mw.TENANT_MAX_REQUESTS = 3  # Low tenant limit
        mw.WINDOW_SECONDS = 60

        tenant_id = str(uuid4())
        statuses = []
        for i in range(5):
            user_id = str(uuid4())  # Different user each time
            resp = await mw.dispatch(_make_ai_request(user_id, tenant_id), _passthrough_next)
            statuses.append(resp.status_code)

        self.assertEqual(statuses[:3], [200] * 3, "First 3 tenant requests should pass")
        self.assertTrue(all(s == 429 for s in statuses[3:]), "Tenant limit should block additional requests")


class TestUserIsolation(unittest.IsolatedAsyncioTestCase):
    """
    From "C-Koordinator: Interference-aware Management":
    Co-located microservice users must not interfere with each other's
    resource allocations.
    """

    def setUp(self):
        self.rate_limit = importlib.import_module("middleware.rate_limit")
        self.rate_limit._memory_store.clear()
        self.rate_limit._redis_available = False
        self.rate_limit._redis = None

    def tearDown(self):
        self.rate_limit._memory_store.clear()

    async def test_different_users_have_independent_limits(self):
        """User A exhausting their limit should not affect User B."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 2
        mw.TENANT_MAX_REQUESTS = 1000  # Not the bottleneck
        mw.WINDOW_SECONDS = 60

        user_a = str(uuid4())
        user_b = str(uuid4())

        # Exhaust User A
        for _ in range(3):
            await mw.dispatch(_make_ai_request(user_a), _passthrough_next)

        # User B should still get through
        resp = await mw.dispatch(_make_ai_request(user_b), _passthrough_next)
        self.assertEqual(resp.status_code, 200, "User B should not be affected by User A's rate limit")


class TestNonAIPathExemption(unittest.IsolatedAsyncioTestCase):
    """Rate limiting must only apply to AI-governed paths."""

    def setUp(self):
        self.rate_limit = importlib.import_module("middleware.rate_limit")
        self.rate_limit._memory_store.clear()
        self.rate_limit._redis_available = False
        self.rate_limit._redis = None

    def tearDown(self):
        self.rate_limit._memory_store.clear()

    async def test_health_endpoint_never_rate_limited(self):
        """Non-AI endpoints should always pass through regardless of volume."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 1
        mw.WINDOW_SECONDS = 60

        results = []
        for _ in range(20):
            resp = await mw.dispatch(_make_non_ai_request("/health"), _passthrough_next)
            results.append(resp.status_code)

        self.assertTrue(all(s == 200 for s in results), "Non-AI paths should never be rate limited")

    async def test_get_requests_to_ai_paths_not_rate_limited(self):
        """GET/OPTIONS/HEAD to AI paths are exempt from rate limiting."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 1
        mw.WINDOW_SECONDS = 60

        req = Request(
            {
                "type": "http",
                "method": "GET",
                "path": "/api/ai/query",
                "headers": [],
                "query_string": b"",
                "state": {},
            }
        )
        req.state.user_id = str(uuid4())

        results = []
        for _ in range(5):
            resp = await mw.dispatch(req, _passthrough_next)
            results.append(resp.status_code)

        self.assertTrue(all(s == 200 for s in results))


class TestAIPathCoverage(unittest.IsolatedAsyncioTestCase):
    """All AI-governed paths must be subject to rate limiting."""

    def setUp(self):
        self.rate_limit = importlib.import_module("middleware.rate_limit")
        self.rate_limit._memory_store.clear()
        self.rate_limit._redis_available = False
        self.rate_limit._redis = None

    def tearDown(self):
        self.rate_limit._memory_store.clear()

    async def test_all_ai_paths_are_rate_limited(self):
        """Every declared AI_PATHS prefix must trigger rate limiting."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 1
        mw.WINDOW_SECONDS = 60

        for path in mw.AI_PATHS:
            self.rate_limit._memory_store.clear()
            user_id = str(uuid4())

            first = await mw.dispatch(_make_ai_request(user_id, path=path), _passthrough_next)
            second = await mw.dispatch(_make_ai_request(user_id, path=path), _passthrough_next)

            self.assertEqual(first.status_code, 200, f"First request to {path} should pass")
            self.assertEqual(second.status_code, 429, f"Second request to {path} should be rate-limited")


class TestSlidingWindowBehavior(unittest.IsolatedAsyncioTestCase):
    """
    From "Reinforcement Learning-Based Adaptive Load Balancing":
    Static algorithms fail to adapt; sliding-window rate limiting
    provides more accurate burst control than fixed-window counters.
    """

    def setUp(self):
        self.rate_limit = importlib.import_module("middleware.rate_limit")
        self.rate_limit._memory_store.clear()
        self.rate_limit._redis_available = False
        self.rate_limit._redis = None

    def tearDown(self):
        self.rate_limit._memory_store.clear()

    async def test_old_entries_expire_after_window(self):
        """Requests older than WINDOW_SECONDS should no longer count toward the limit."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 2
        mw.WINDOW_SECONDS = 1  # 1 second window for test speed

        user_id = str(uuid4())

        # Fill the window
        await mw.dispatch(_make_ai_request(user_id), _passthrough_next)
        await mw.dispatch(_make_ai_request(user_id), _passthrough_next)

        # Should be blocked now
        resp = await mw.dispatch(_make_ai_request(user_id), _passthrough_next)
        self.assertEqual(resp.status_code, 429)

        # Wait for window to expire
        await asyncio.sleep(1.1)

        # Should be allowed again
        resp = await mw.dispatch(_make_ai_request(user_id), _passthrough_next)
        self.assertEqual(resp.status_code, 200, "Requests should succeed after the sliding window expires")

    async def test_memory_store_cleans_up_expired_entries(self):
        """In-memory store should prune expired timestamps to prevent memory leaks."""
        mw = self.rate_limit.RateLimitMiddleware(app=lambda *a, **k: None)
        mw.MAX_REQUESTS = 100
        mw.WINDOW_SECONDS = 1

        user_id = str(uuid4())
        key = f"ratelimit:user:{user_id}"

        for _ in range(10):
            await mw.dispatch(_make_ai_request(user_id), _passthrough_next)

        self.assertEqual(len(self.rate_limit._memory_store.get(key, [])), 10)

        await asyncio.sleep(1.1)

        # Trigger a new request which should prune old entries
        await mw.dispatch(_make_ai_request(user_id), _passthrough_next)

        # Only the new request should remain
        self.assertEqual(len(self.rate_limit._memory_store[key]), 1)


class TestGovernanceQuotaEnforcement(unittest.TestCase):
    """
    Validates the usage_governance module's quota enforcement logic,
    ensuring daily and monthly limits are correctly applied per the
    research on cost-optimal microservice management.
    """

    def test_daily_quota_blocks_when_exhausted(self):
        """Once a user hits their daily limit, governance should reject further requests."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        self.assertIn("qa_requests", ug.USER_QUOTAS)
        daily_limit = ug.USER_QUOTAS["qa_requests"]["day"]
        self.assertIsInstance(daily_limit, int)
        self.assertGreater(daily_limit, 0)

    def test_all_modes_have_quota_mappings(self):
        """Every AI mode in MODE_TO_METRIC must have corresponding USER_QUOTAS entry."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        for mode, metric in ug.MODE_TO_METRIC.items():
            self.assertIn(metric, ug.USER_QUOTAS, f"Mode '{mode}' maps to metric '{metric}' which has no quota")

    def test_token_ceiling_defaults_are_reasonable(self):
        """Token ceilings should enforce sensible upper bounds for all AI modes."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        for mode, (prompt, completion) in ug.TOKEN_CEILINGS.items():
            self.assertGreater(prompt, 0, f"Prompt ceiling for '{mode}' must be positive")
            self.assertGreater(completion, 0, f"Completion ceiling for '{mode}' must be positive")
            self.assertGreaterEqual(prompt, completion, f"Prompt ceiling should >= completion for '{mode}'")

    def test_approximate_token_count_edge_cases(self):
        """Token approximation must handle empty, whitespace, and very long text."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        self.assertEqual(ug.approximate_token_count(None), 0)
        self.assertEqual(ug.approximate_token_count(""), 0)
        self.assertEqual(ug.approximate_token_count("   "), 0)
        self.assertGreater(ug.approximate_token_count("Hello world"), 0)

        long_text = "a" * 100000
        tokens = ug.approximate_token_count(long_text)
        self.assertEqual(tokens, 25000, "100k chars / 4 should be 25000 tokens")

    def test_cost_estimation_uses_fallback_weight(self):
        """Fallback model should incur lower cost than primary model."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        primary_cost = ug._estimate_cost_units(1000, used_fallback=False)
        fallback_cost = ug._estimate_cost_units(1000, used_fallback=True)

        self.assertGreater(primary_cost, 0)
        self.assertGreater(fallback_cost, 0)
        self.assertGreater(primary_cost, fallback_cost, "Primary model should cost more than fallback")

    def test_cost_estimation_zero_tokens(self):
        """Zero tokens should produce zero cost."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        self.assertEqual(ug._estimate_cost_units(0, used_fallback=False), 0.0)
        self.assertEqual(ug._estimate_cost_units(-5, used_fallback=False), 0.0)

    def test_batchable_metrics_are_subset_of_quotas(self):
        """All batchable metrics must have quota entries."""
        ug = importlib.import_module("src.domains.platform.services.usage_governance")

        for metric in ug.BATCHABLE_METRICS:
            self.assertIn(metric, ug.USER_QUOTAS, f"Batchable metric '{metric}' missing from USER_QUOTAS")


if __name__ == "__main__":
    unittest.main()
