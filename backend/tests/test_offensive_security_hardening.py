import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from uuid import uuid4

from fastapi import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))


def _make_ai_request(user_id: str, tenant_id: str | None = None) -> Request:
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/student/upload",
        "headers": [(b"host", b"localhost:8000")],
        "query_string": b"",
        "state": {},
    }
    request = Request(scope)
    request.state.user_id = user_id
    request.state.tenant_id = tenant_id
    return request


async def _ok_handler(_request):
    return JSONResponse({"ok": True}, status_code=200)


class SecurityHardeningTests(unittest.IsolatedAsyncioTestCase):
    async def test_require_role_enforces_roles_even_in_demo_mode(self):
        from auth.dependencies import require_role

        checker = require_role("admin")
        with self.assertRaises(HTTPException) as ctx:
            await checker(current_user=SimpleNamespace(role="student"))
        self.assertEqual(ctx.exception.status_code, 403)

    async def test_saml_metadata_rejects_link_local_metadata_url(self):
        from src.domains.identity.services.saml_sso import import_tenant_saml_metadata

        tenant = SimpleNamespace(
            saml_metadata_url=None,
            saml_metadata_xml=None,
            saml_idp_entity_id=None,
            saml_idp_sso_url=None,
            saml_idp_slo_url=None,
            saml_x509_cert=None,
            saml_entity_id=None,
            domain="demo-school",
            id=uuid4(),
        )
        with self.assertRaises(HTTPException) as ctx:
            await import_tenant_saml_metadata(
                tenant,
                metadata_url="http://169.254.169.254/latest/meta-data/",
            )
        self.assertEqual(ctx.exception.status_code, 400)

    async def test_captcha_fails_securely_when_secret_missing_in_non_debug(self):
        from middleware import captcha

        original_secret = os.environ.pop("RECAPTCHA_SECRET_KEY", None)
        original_debug = captcha.settings.app.debug
        original_env = captcha.settings.app.env
        captcha.settings.app.debug = False
        captcha.settings.app.env = "production"
        try:
            result = await captcha.verify_recaptcha("token")
        finally:
            captcha.settings.app.debug = original_debug
            captcha.settings.app.env = original_env
            if original_secret is not None:
                os.environ["RECAPTCHA_SECRET_KEY"] = original_secret
        self.assertFalse(result["success"])
        self.assertEqual(result["action"], "misconfigured")

    async def test_captcha_middleware_blocks_when_secret_missing_in_non_debug(self):
        from middleware.captcha import CaptchaMiddleware
        from middleware import captcha

        original_secret = os.environ.pop("RECAPTCHA_SECRET_KEY", None)
        original_debug = captcha.settings.app.debug
        original_env = captcha.settings.app.env
        captcha.settings.app.debug = False
        captcha.settings.app.env = "production"
        try:
            middleware = CaptchaMiddleware(app=None)
            request = Request(
                {
                    "type": "http",
                    "method": "POST",
                    "path": "/api/auth/login",
                    "headers": [(b"host", b"localhost:8000")],
                    "query_string": b"",
                }
            )
            response = await middleware.dispatch(request, _ok_handler)
        finally:
            captcha.settings.app.debug = original_debug
            captcha.settings.app.env = original_env
            if original_secret is not None:
                os.environ["RECAPTCHA_SECRET_KEY"] = original_secret
        self.assertEqual(response.status_code, 503)

    async def test_document_view_rejects_paths_outside_private_storage(self):
        from src.interfaces.rest_api.ai.routes.documents import view_document

        tenant_id = uuid4()
        doc = SimpleNamespace(
            id=uuid4(),
            tenant_id=tenant_id,
            storage_path=str(Path(__file__).resolve()),
            file_name="secrets.txt",
        )

        class _Query:
            def __init__(self, document):
                self.document = document

            def filter(self, *_args, **_kwargs):
                return self

            def first(self):
                return self.document

        class _DB:
            def __init__(self, document):
                self.document = document

            def query(self, _model):
                return _Query(self.document)

        with self.assertRaises(HTTPException) as ctx:
            await view_document(str(doc.id), current_user=SimpleNamespace(tenant_id=tenant_id), db=_DB(doc))
        self.assertEqual(ctx.exception.status_code, 403)

    async def test_rate_limit_memory_fallback_is_bounded(self):
        import middleware.rate_limit as rate_limit

        original_max_keys = rate_limit._MEMORY_STORE_MAX_KEYS
        rate_limit._MEMORY_STORE_MAX_KEYS = 2
        rate_limit._memory_store.clear()
        rate_limit._redis_initialized = True
        rate_limit._redis = None
        try:
            middleware = rate_limit.RateLimitMiddleware(app=lambda *_args, **_kwargs: None)
            middleware.MAX_REQUESTS = 10
            middleware.WINDOW_SECONDS = 60

            for idx in range(3):
                request = _make_ai_request(str(uuid4()))
                response = await middleware.dispatch(request, _ok_handler)
                self.assertEqual(response.status_code, 200)
            self.assertEqual(len(rate_limit._memory_store), 2)
        finally:
            rate_limit._MEMORY_STORE_MAX_KEYS = original_max_keys
            rate_limit._memory_store.clear()
