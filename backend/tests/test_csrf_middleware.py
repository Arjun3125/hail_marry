"""Tests for middleware/csrf.py — CSRF protection boundary conditions."""
import os
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from starlette.requests import Request
from starlette.responses import JSONResponse
from middleware.csrf import CSRFMiddleware


def _make_request(method="POST", path="/api/student/upload", origin=None, referer=None):
    headers = []
    headers.append((b"host", b"localhost:8000"))
    if origin:
        headers.append((b"origin", origin.encode()))
    if referer:
        headers.append((b"referer", referer.encode()))
    scope = {
        "type": "http",
        "method": method,
        "path": path,
        "headers": headers,
        "query_string": b"",
    }
    return Request(scope)


async def _ok_handler(request):
    return JSONResponse({"ok": True}, status_code=200)


class CSRFMiddlewareTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        self.middleware = CSRFMiddleware(
            app=None,
            allowed_origins=["http://localhost:3000", "http://localhost:8000"],
        )

    async def test_get_request_passes_without_origin(self):
        request = _make_request(method="GET")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_head_request_passes_without_origin(self):
        request = _make_request(method="HEAD")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_options_request_passes_without_origin(self):
        request = _make_request(method="OPTIONS")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_post_with_valid_origin_passes(self):
        request = _make_request(origin="http://localhost:3000")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_post_with_invalid_origin_returns_403(self):
        request = _make_request(origin="https://evil.com")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 403)

    async def test_post_with_valid_referer_passes(self):
        request = _make_request(referer="http://localhost:3000/dashboard")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_post_with_invalid_referer_returns_403(self):
        from middleware.csrf import settings
        original = settings.app.debug
        settings.app.debug = False
        try:
            request = _make_request(referer="https://evil.com/phish")
            response = await self.middleware.dispatch(request, _ok_handler)
            self.assertEqual(response.status_code, 403)
        finally:
            settings.app.debug = original

    async def test_post_no_origin_no_referer_debug_passes(self):
        from middleware.csrf import settings
        original = settings.app.debug
        settings.app.debug = True
        try:
            request = _make_request()
            response = await self.middleware.dispatch(request, _ok_handler)
            self.assertEqual(response.status_code, 200)
        finally:
            settings.app.debug = original

    async def test_post_no_origin_no_referer_non_debug_returns_403(self):
        from middleware.csrf import settings
        original = settings.app.debug
        settings.app.debug = False
        try:
            request = _make_request()
            response = await self.middleware.dispatch(request, _ok_handler)
            self.assertEqual(response.status_code, 403)
        finally:
            settings.app.debug = original

    async def test_exempt_path_bypasses_csrf(self):
        request = _make_request(path="/api/auth/google")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_health_exempt(self):
        request = _make_request(path="/health")
        response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(response.status_code, 200)

    async def test_vercel_preview_blocked_in_debug(self):
        from middleware.csrf import settings
        original = settings.app.debug
        settings.app.debug = True
        try:
            request = _make_request(origin="https://my-app-abc123.vercel.app")
            response = await self.middleware.dispatch(request, _ok_handler)
            self.assertEqual(response.status_code, 403)
        finally:
            settings.app.debug = original


if __name__ == "__main__":
    unittest.main()
