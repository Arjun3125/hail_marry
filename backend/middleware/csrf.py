"""
CSRF protection middleware for state-changing requests.
Validates Origin/Referer headers against allowed origins.
"""
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from urllib.parse import urlparse
from config import settings

SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}
EXEMPT_PATHS = {"/api/auth/google", "/api/auth/demo-login", "/docs", "/openapi.json", "/health"}


class CSRFMiddleware(BaseHTTPMiddleware):
    """
    CSRF protection via Origin header validation.
    Blocks state-changing requests (POST/PUT/PATCH/DELETE) without valid Origin.
    """

    def __init__(self, app, allowed_origins: list[str] | None = None):
        super().__init__(app)
        self.allowed_origins = set(allowed_origins or [
            "http://localhost:3000",
            "http://localhost:8000",
            "http://127.0.0.1:3000",
        ])

    def _is_allowed_origin(self, origin: str) -> bool:
        if origin in self.allowed_origins:
            return True
        # Permit preview/frontdoor Vercel domains in debug demo environments.
        return settings.app.debug and origin.startswith("https://") and origin.endswith(".vercel.app")

    def _is_allowed_referer(self, referer: str) -> bool:
        if any(referer.startswith(origin) for origin in self.allowed_origins):
            return True
        if not settings.app.debug:
            return False
        parsed = urlparse(referer)
        return parsed.scheme == "https" and parsed.netloc.endswith(".vercel.app")

    async def dispatch(self, request: Request, call_next):
        if request.method in SAFE_METHODS:
            return await call_next(request)

        if request.url.path in EXEMPT_PATHS:
            return await call_next(request)

        # Check Origin header
        origin = request.headers.get("origin", "")
        referer = request.headers.get("referer", "")

        if origin:
            if not self._is_allowed_origin(origin):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF validation failed: invalid origin"},
                )
        elif referer:
            # Fallback to referer check
            if not self._is_allowed_referer(referer):
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF validation failed: invalid referer"},
                )
        else:
            # Allow missing headers only in debug/local mode.
            if not settings.app.debug:
                return JSONResponse(
                    status_code=403,
                    content={"detail": "CSRF validation failed: missing origin/referer"},
                )

        return await call_next(request)
