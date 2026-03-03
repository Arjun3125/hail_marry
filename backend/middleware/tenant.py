"""Tenant context middleware — extracts tenant_id from JWT for all requests."""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from auth.jwt import decode_access_token


class TenantMiddleware(BaseHTTPMiddleware):
    """Sets request.state.tenant_id from JWT on every authenticated request."""

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
            payload = decode_access_token(token)
            if payload:
                request.state.tenant_id = payload.get("tenant_id")
                request.state.user_role = payload.get("role")
                request.state.user_id = payload.get("user_id")

        return await call_next(request)
