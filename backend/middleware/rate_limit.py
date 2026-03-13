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


# ─── Redis Client (lazy init) ────────────────
_redis = None
_redis_available = None


def _get_redis():
    """Lazy-load Redis client. Falls back to in-memory if unavailable."""
    global _redis, _redis_available
    if _redis_available is None:
        try:
            import redis as redis_lib
            url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            _redis = redis_lib.from_url(url, decode_responses=True)
            _redis.ping()
            _redis_available = True
        except Exception:
            _redis_available = False
            _redis = None
    return _redis if _redis_available else None


# ─── In-memory fallback ──────────────────────
_memory_store: dict = {}


class RateLimitMiddleware(BaseHTTPMiddleware):
    """Rate limit AI endpoints: 5 queries/min per user (Redis-backed)."""

    AI_PATHS = ("/api/ai/", "/api/student/tools/")
    MAX_REQUESTS = int(os.getenv("BURST_LIMIT_PER_MINUTE", "5"))
    WINDOW_SECONDS = RATE_LIMIT_WINDOW_SECONDS

    async def dispatch(self, request: Request, call_next):
        if not any(request.url.path.startswith(p) for p in self.AI_PATHS):
            return await call_next(request)

        if request.method in ("GET", "OPTIONS", "HEAD"):
            return await call_next(request)

        # Get user ID from request state (set by TenantMiddleware)
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)

        key = f"ratelimit:{user_id}"
        now = time.time()

        # Try Redis first
        redis_client = _get_redis()
        if redis_client:
            try:
                pipe = redis_client.pipeline()
                pipe.zremrangebyscore(key, 0, now - self.WINDOW_SECONDS)
                pipe.zadd(key, {str(now): now})
                pipe.zcard(key)
                pipe.expire(key, self.WINDOW_SECONDS)
                results = pipe.execute()
                count = results[2]

                if count > self.MAX_REQUESTS:
                    ttl = redis_client.ttl(key)
                    return JSONResponse(
                        status_code=429,
                        content={
                            "detail": f"Rate limit exceeded. Max {self.MAX_REQUESTS} AI requests per minute.",
                            "retry_after": max(ttl, 1),
                        },
                    )
                return await call_next(request)
            except Exception:
                pass  # Fall through to in-memory

        # In-memory fallback
        if key not in _memory_store:
            _memory_store[key] = []

        _memory_store[key] = [t for t in _memory_store[key] if t > now - self.WINDOW_SECONDS]

        if len(_memory_store[key]) >= self.MAX_REQUESTS:
            oldest = min(_memory_store[key])
            retry_after = int(self.WINDOW_SECONDS - (now - oldest)) + 1
            return JSONResponse(
                status_code=429,
                content={
                    "detail": f"Rate limit exceeded. Max {self.MAX_REQUESTS} AI requests per minute.",
                    "retry_after": retry_after,
                },
            )

        _memory_store[key].append(now)
        return await call_next(request)
