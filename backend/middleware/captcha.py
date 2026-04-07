"""reCAPTCHA / bot protection middleware.

Validates Google reCAPTCHA v3 tokens on public endpoints
(registration, admission, login) to prevent automated abuse.
"""
from __future__ import annotations

import json
import os
from typing import Optional

import httpx
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

from config import settings

RECAPTCHA_SECRET = os.getenv("RECAPTCHA_SECRET_KEY", "")
RECAPTCHA_VERIFY_URL = "https://www.google.com/recaptcha/api/siteverify"
RECAPTCHA_SCORE_THRESHOLD = float(os.getenv("RECAPTCHA_THRESHOLD", "0.5"))
RECAPTCHA_HEADER = "x-recaptcha-token"
_NON_PRODUCTION_ENVS = {"local", "development", "dev", "test"}

# Endpoints that require captcha validation
PROTECTED_ENDPOINTS = {
    "/api/onboarding/register",
    "/api/admission/apply",
    "/api/auth/login",
}


def _get_recaptcha_secret() -> str:
    return os.getenv("RECAPTCHA_SECRET_KEY", RECAPTCHA_SECRET).strip()


def _allow_recaptcha_bypass() -> bool:
    return settings.app.debug and (settings.app.env or "local").strip().lower() in _NON_PRODUCTION_ENVS


async def verify_recaptcha(token: str, remote_ip: Optional[str] = None) -> dict:
    """Verify a reCAPTCHA token with Google's API.

    Returns:
        {"success": bool, "score": float, "action": str, "error_codes": list}
    """
    secret = _get_recaptcha_secret()
    if not secret:
        if _allow_recaptcha_bypass():
            return {"success": True, "score": 1.0, "action": "bypass", "error_codes": []}
        return {"success": False, "score": 0.0, "action": "misconfigured", "error_codes": ["recaptcha_not_configured"]}

    payload = {
        "secret": secret,
        "response": token,
    }
    if remote_ip:
        payload["remoteip"] = remote_ip

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.post(RECAPTCHA_VERIFY_URL, data=payload)
            resp.raise_for_status()
            data = resp.json()
    except Exception as exc:
        return {"success": False, "score": 0.0, "action": "error", "error_codes": [str(exc)]}

    return {
        "success": data.get("success", False),
        "score": data.get("score", 0.0),
        "action": data.get("action", ""),
        "error_codes": data.get("error-codes", []),
    }


def is_human(result: dict) -> bool:
    """Check if the reCAPTCHA result indicates a human user."""
    return result.get("success", False) and result.get("score", 0.0) >= RECAPTCHA_SCORE_THRESHOLD


def is_protected_endpoint(path: str) -> bool:
    """Check if an endpoint requires captcha validation."""
    return path in PROTECTED_ENDPOINTS


def _extract_token_from_payload(payload: dict) -> str | None:
    return (
        payload.get("recaptcha_token")
        or payload.get("recaptchaToken")
        or payload.get("captcha_token")
        or payload.get("captchaToken")
    )


class CaptchaMiddleware(BaseHTTPMiddleware):
    """Enforce reCAPTCHA on protected public endpoints."""

    async def dispatch(self, request: Request, call_next):
        if request.method in {"GET", "HEAD", "OPTIONS"}:
            return await call_next(request)

        if not is_protected_endpoint(request.url.path):
            return await call_next(request)

        if not _get_recaptcha_secret():
            if _allow_recaptcha_bypass():
                return await call_next(request)
            return JSONResponse(status_code=503, content={"detail": "reCAPTCHA is not configured"})

        token = request.headers.get(RECAPTCHA_HEADER) or request.headers.get(RECAPTCHA_HEADER.upper())

        if not token and request.headers.get("content-type", "").startswith("application/json"):
            body_bytes = await request.body()
            request._body = body_bytes
            if body_bytes:
                try:
                    payload = json.loads(body_bytes.decode("utf-8"))
                except (ValueError, UnicodeDecodeError):
                    payload = None
                if isinstance(payload, dict):
                    token = _extract_token_from_payload(payload)

        if not token:
            return JSONResponse(status_code=400, content={"detail": "reCAPTCHA token required"})

        result = await verify_recaptcha(
            token,
            remote_ip=request.client.host if request.client else None,
        )
        if not is_human(result):
            return JSONResponse(
                status_code=403,
                content={
                    "detail": "reCAPTCHA verification failed",
                    "score": result.get("score", 0.0),
                    "error_codes": result.get("error_codes", []),
                },
            )

        return await call_next(request)
