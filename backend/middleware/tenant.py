"""Tenant context middleware — extracts tenant_id from JWT for all requests.

Optimized for high-concurrency Indian EdTech deployments:
- Decoded JWT payloads are cached in a TTL-bounded LRU cache so the same
  token is not re-decoded on every HTTP request within a short window.
- This eliminates redundant HMAC-SHA256 computation during exam spikes
  when thousands of students are hitting the API simultaneously.
"""
import hashlib
import logging
import threading
import time
from collections import OrderedDict

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from auth.jwt import decode_access_token

logger = logging.getLogger(__name__)


class _JWTPayloadCache:
    """Thread-safe, TTL-bounded LRU cache for decoded JWT payloads.

    Avoids re-decoding the same access token on every request a student
    makes while navigating the dashboard (dozens of requests/minute with
    the exact same token).

    - maxsize: Maximum number of cached entries.
    - ttl: Time-to-live in seconds for each entry.
    """

    _MISS = object()

    def __init__(self, maxsize: int = 4096, ttl: int = 300):
        self._cache: OrderedDict[str, tuple[dict | None, float]] = OrderedDict()
        self._maxsize = maxsize
        self._ttl = ttl
        self._lock = threading.RLock()

    def get(self, token: str) -> dict | None | object:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._lock:
            entry = self._cache.get(token_hash)
            if entry is None:
                return _JWTPayloadCache._MISS
            payload, ts = entry
            if time.monotonic() - ts > self._ttl:
                self._cache.pop(token_hash, None)
                return _JWTPayloadCache._MISS
            # Move to end (most-recently-used)
            self._cache.move_to_end(token_hash)
            return payload

    def put(self, token: str, payload: dict | None) -> None:
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        with self._lock:
            self._cache[token_hash] = (payload, time.monotonic())
            self._cache.move_to_end(token_hash)
            while len(self._cache) > self._maxsize:
                self._cache.popitem(last=False)

    def clear(self) -> None:
        with self._lock:
            self._cache.clear()


# Module-level singleton — shared across all requests in the process.
_jwt_cache = _JWTPayloadCache(maxsize=4096, ttl=300)


class TenantMiddleware(BaseHTTPMiddleware):
    """Sets request.state.tenant_id from JWT on every authenticated request.

    Uses a TTL-bounded LRU cache to avoid redundant HMAC-SHA256 decryption
    during high-concurrency exam/mock-test spikes.
    """

    EXEMPT_PATHS = {"/", "/api/auth/google", "/api/auth/me", "/docs", "/openapi.json", "/health"}

    async def dispatch(self, request: Request, call_next):
        # Skip for public paths
        if request.url.path in self.EXEMPT_PATHS or request.url.path.startswith("/api/auth"):
            return await call_next(request)

        # Try to extract tenant from JWT (non-blocking, auth dependency handles actual enforcement)
        token = request.cookies.get("access_token")
        if not token:
            auth_header = request.headers.get("Authorization", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]

        if token:
            # Check cache first to avoid redundant HMAC-SHA256 work
            cached = _jwt_cache.get(token)
            if cached is not _JWTPayloadCache._MISS:
                payload = cached
            else:
                payload = decode_access_token(token)
                _jwt_cache.put(token, payload)

            if payload:
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_role = payload.get("role")
                request.state.user_id = payload.get("user_id")

        return await call_next(request)
