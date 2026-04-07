"""
Burst Rate Limiter Middleware — Redis-backed with in-memory fallback.
Limits AI queries to N per minute per user.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
import os
from constants import RATE_LIMIT_WINDOW_SECONDS


from config import settings


# ─── Redis Client (lazy init) ────────────────
_redis = None
_redis_available = None


def _get_redis():
    """Lazy-load Redis client. Falls back to in-memory if unavailable."""
    global _redis, _redis_available
    if _redis_available is None:
        try:
            import redis as redis_lib
            redis_url = (
                os.getenv("REDIS_STATE_URL")
                or os.getenv("REDIS_URL")
                or settings.redis.state_url
            )
            _redis = redis_lib.from_url(redis_url, decode_responses=True)
            _redis.ping()
            _redis_available = True
        except Exception:
            _redis_available = False
            _redis = None
    return _redis if _redis_available else None


# ─── In-memory fallback ──────────────────────
_memory_store: dict = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit governed endpoints with per-user and per-tenant burst controls."""

    AI_PATHS = (
        "/api/ai/",
        "/api/student/tools/",
        "/api/student/upload",
        "/api/teacher/upload",
        "/api/teacher/youtube",
        "/api/mascot/upload",
    )
    MAX_REQUESTS = int(os.getenv("BURST_LIMIT_PER_MINUTE", "5"))
    TENANT_MAX_REQUESTS = int(os.getenv("TENANT_BURST_LIMIT_PER_MINUTE", "100"))
    WINDOW_SECONDS = RATE_LIMIT_WINDOW_SECONDS

    def _rate_limit_response(self, limit: int, retry_after: int, *, scope: str) -> JSONResponse:
        return JSONResponse(
            status_code=429,
            content={
                "detail": f"Rate limit exceeded. Max {limit} governed requests per minute for this {scope}.",
                "retry_after": max(retry_after, 1),
            },
            headers={"Retry-After": str(max(retry_after, 1))}
        )

    def _check_with_redis(self, redis_client, key: str, limit: int, now: float):
        pipe = redis_client.pipeline()
        pipe.zremrangebyscore(key, 0, now - self.WINDOW_SECONDS)
        pipe.zadd(key, {str(now): now})
        pipe.zcard(key)
        pipe.expire(key, self.WINDOW_SECONDS)
        results = pipe.execute()
        count = results[2]
        if count > limit:
            ttl = redis_client.ttl(key)
            return False, int(ttl or 1)
        return True, 0

    def _check_in_memory(self, key: str, limit: int, now: float):
        if key not in _memory_store:
            _memory_store[key] = []
        _memory_store[key] = [t for t in _memory_store[key] if t > now - self.WINDOW_SECONDS]
        if len(_memory_store[key]) >= limit:
            oldest = min(_memory_store[key])
            retry_after = int(self.WINDOW_SECONDS - (now - oldest)) + 1
            return False, retry_after
        _memory_store[key].append(now)
        return True, 0

    async def dispatch(self, request: Request, call_next):
        if not any(request.url.path.startswith(p) for p in self.AI_PATHS):
            return await call_next(request)

        if request.method in ("GET", "OPTIONS", "HEAD"):
            return await call_next(request)

        # Get user and tenant IDs from request state (set by TenantMiddleware)
        user_id = getattr(request.state, "user_id", None)
        tenant_id = getattr(request.state, "tenant_id", None)
        if not user_id and not tenant_id:
            return await call_next(request)

        now = time.time()

        # Try Redis first
        redis_client = _get_redis()
        if redis_client:
            try:
                if user_id:
                    allowed, retry_after = self._check_with_redis(
                        redis_client,
                        f"ratelimit:user:{user_id}",
                        self.MAX_REQUESTS,
                        now,
                    )
                    if not allowed:
                        return self._rate_limit_response(self.MAX_REQUESTS, retry_after, scope="user")
                if tenant_id:
                    allowed, retry_after = self._check_with_redis(
                        redis_client,
                        f"ratelimit:tenant:{tenant_id}",
                        self.TENANT_MAX_REQUESTS,
                        now,
                    )
                    if not allowed:
                        return self._rate_limit_response(self.TENANT_MAX_REQUESTS, retry_after, scope="tenant")
                return await call_next(request)
            except Exception:
                pass  # Fall through to in-memory

        # In-memory fallback
        if user_id:
            allowed, retry_after = self._check_in_memory(f"ratelimit:user:{user_id}", self.MAX_REQUESTS, now)
            if not allowed:
                return self._rate_limit_response(self.MAX_REQUESTS, retry_after, scope="user")
        if tenant_id:
            allowed, retry_after = self._check_in_memory(f"ratelimit:tenant:{tenant_id}", self.TENANT_MAX_REQUESTS, now)
            if not allowed:
                return self._rate_limit_response(self.TENANT_MAX_REQUESTS, retry_after, scope="tenant")
        return await call_next(request)
