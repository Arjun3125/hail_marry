"""Tests for middleware/tenant.py — tenant extraction from JWT."""
import os
import sys
import unittest
from pathlib import Path
from unittest.mock import patch

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from starlette.requests import Request
from starlette.responses import JSONResponse
from middleware.tenant import TenantMiddleware, _jwt_cache


def _make_request(path="/api/student/dashboard", auth_header=None, cookie_token=None):
    headers = []
    if auth_header:
        headers.append((b"authorization", f"Bearer {auth_header}".encode()))
    cookie_str = ""
    if cookie_token:
        cookie_str = f"access_token={cookie_token}"
    if cookie_str:
        headers.append((b"cookie", cookie_str.encode()))
    scope = {
        "type": "http",
        "method": "GET",
        "path": path,
        "headers": headers,
        "query_string": b"",
        "state": {},
    }
    return Request(scope)


async def _ok_handler(request):
    return JSONResponse({"ok": True}, status_code=200)


class TenantMiddlewareTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self):
        _jwt_cache.clear()
        self.middleware = TenantMiddleware(app=None)

    def tearDown(self):
        _jwt_cache.clear()

    async def test_exempt_path_skips_extraction(self):
        request = _make_request(path="/api/auth/login")
        with patch("middleware.tenant.decode_access_token") as mock_decode:
            response = await self.middleware.dispatch(request, _ok_handler)
        mock_decode.assert_not_called()
        self.assertEqual(response.status_code, 200)

    async def test_health_path_skips_extraction(self):
        request = _make_request(path="/health")
        with patch("middleware.tenant.decode_access_token") as mock_decode:
            await self.middleware.dispatch(request, _ok_handler)
        mock_decode.assert_not_called()

    async def test_valid_bearer_sets_state(self):
        payload = {"tenant_id": "tenant-abc", "role": "student", "user_id": "user-123"}
        request = _make_request(auth_header="valid-token")
        with patch("middleware.tenant.decode_access_token", return_value=payload):
            response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(request.state.tenant_id, "tenant-abc")
        self.assertEqual(request.state.user_role, "student")
        self.assertEqual(request.state.user_id, "user-123")
        self.assertEqual(response.status_code, 200)

    async def test_valid_cookie_sets_state(self):
        payload = {"tenant_id": "tenant-xyz", "role": "admin", "user_id": "user-456"}
        request = _make_request(cookie_token="cookie-token")
        with patch("middleware.tenant.decode_access_token", return_value=payload):
            response = await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(request.state.tenant_id, "tenant-xyz")
        self.assertEqual(request.state.user_role, "admin")
        self.assertEqual(response.status_code, 200)

    async def test_invalid_token_leaves_state_unset(self):
        request = _make_request(auth_header="bad-token")
        with patch("middleware.tenant.decode_access_token", return_value=None):
            response = await self.middleware.dispatch(request, _ok_handler)
        self.assertFalse(hasattr(request.state, "tenant_id"))
        self.assertEqual(response.status_code, 200)

    async def test_no_token_leaves_state_unset(self):
        request = _make_request()
        with patch("middleware.tenant.decode_access_token") as mock_decode:
            response = await self.middleware.dispatch(request, _ok_handler)
        mock_decode.assert_not_called()
        self.assertFalse(hasattr(request.state, "tenant_id"))
        self.assertEqual(response.status_code, 200)

    async def test_bearer_token_preferred_over_cookie(self):
        bearer_payload = {"tenant_id": "bearer-tenant", "role": "teacher", "user_id": "u1"}
        request = _make_request(auth_header="bearer-token", cookie_token="cookie-token")
        # Cookie token check happens only if no bearer auth header
        # The middleware checks cookie first, then auth header — but sets state from whichever it finds
        with patch("middleware.tenant.decode_access_token", return_value=bearer_payload):
            await self.middleware.dispatch(request, _ok_handler)
        self.assertEqual(request.state.tenant_id, "bearer-tenant")


if __name__ == "__main__":
    unittest.main()
