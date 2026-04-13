"""
Burst Rate Limiter Middleware — Redis-backed for distributed environments.
Limits AI queries to N per minute per user.
Requires Redis in production (multi-server deployments).
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
import time
import os
from collections import OrderedDict
import logging
from constants import RATE_LIMIT_WINDOW_SECONDS
from config import settings

logger = logging.getLogger(__name__)

# ─── In-Memory Fallback (dev/test only) ────────────────────
_memory_store: OrderedDict = OrderedDict()
_MEMORY_STORE_MAX_KEYS = 10000

# ─── Redis Client (required for production) ────────────────
_redis = None
_redis_initialized = False


def _get_redis():
    """Get Redis client. REQUIRED for multi-server deployments."""
    global _redis, _redis_initialized
    
    if _redis_initialized:
        return _redis
    
    _redis_initialized = True
    
    try:
        import redis as redis_lib
        
        # Try multiple config sources
        redis_url = (
            os.getenv("REDIS_STATE_URL") or
            os.getenv("REDIS_URL") or
            settings.redis.state_url
        )
        
        if not redis_url:
            # For local dev only, allow in-memory (with warning)
            if os.getenv("APP_ENV", "").lower() in ("local", "development", "test"):
                logger.warning(
                    "⚠️  Redis not configured. Rate limiting disabled (dev mode). "
                    "Set REDIS_URL for production."
                )
                return None
            else:
                raise ValueError(
                    "REDIS_URL not configured. Rate limiting requires Redis in production. "
                    "Set REDIS_URL or REDIS_STATE_URL environment variable."
                )
        
        _redis = redis_lib.from_url(redis_url, decode_responses=True, socket_connect_timeout=5)
        _redis.ping()
        logger.info("✅ Rate limiter connected to Redis")
        return _redis
        
    except Exception as e:
        app_env = os.getenv("APP_ENV", "production").lower()
        if app_env not in ("local", "development", "test"):
            # Production: Redis is REQUIRED
            logger.error(f"🚨 CRITICAL: Rate limiter cannot connect to Redis: {e}")
            raise RuntimeError(
                f"Rate limiter failed to initialize Redis connection: {e}. "
                "This is required for production deployments."
            )
        else:
            # Dev: allow fallback
            logger.warning(f"⚠️  Redis connection failed in dev mode: {e}. Using degraded rate limiting.")
            return None


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
        timestamps = [t for t in _memory_store.pop(key, []) if t > now - self.WINDOW_SECONDS]
        if len(timestamps) >= limit:
            oldest = min(timestamps)
            _memory_store[key] = timestamps
            retry_after = int(self.WINDOW_SECONDS - (now - oldest)) + 1
            return False, retry_after
        if key not in _memory_store and len(_memory_store) >= _MEMORY_STORE_MAX_KEYS:
            _memory_store.popitem(last=False)
        timestamps.append(now)
        _memory_store[key] = timestamps
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

        # Get Redis client (required in production)
        redis_client = _get_redis()
        
        # Redis is REQUIRED for production (multi-server deployments)
        if not redis_client:
            app_env = os.getenv("APP_ENV", "production").lower()
            if app_env not in ("local", "development", "test"):
                logger.error("🚨 Rate limiter: Redis unavailable in production. Rejecting request.")
                return JSONResponse(
                    status_code=503,
                    content={"detail": "Rate limiting service unavailable. Try again later."},
                )
            # Development/test mode: use in-memory fallback
            if user_id:
                allowed, retry_after = self._check_in_memory(
                    f"ratelimit:user:{user_id}",
                    self.MAX_REQUESTS,
                    now,
                )
                if not allowed:
                    return self._rate_limit_response(self.MAX_REQUESTS, retry_after, scope="user")
            if tenant_id:
                allowed, retry_after = self._check_in_memory(
                    f"ratelimit:tenant:{tenant_id}",
                    self.TENANT_MAX_REQUESTS,
                    now,
                )
                if not allowed:
                    return self._rate_limit_response(self.TENANT_MAX_REQUESTS, retry_after, scope="tenant")
            return await call_next(request)

        # Redis available: enforce rate limits
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
        except Exception as e:
            logger.error(f"Rate limiter Redis error: {e}. Rejecting request for safety.")
            return JSONResponse(
                status_code=503,
                content={"detail": "Rate limiting service error. Try again later."},
            )
