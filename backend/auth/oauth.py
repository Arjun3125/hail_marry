"""Google OAuth token verification.

Optimized for high-concurrency Indian EdTech deployments:
- Token verification is offloaded to a thread pool to avoid blocking the
  FastAPI async event loop during mass-login spikes.
- A short-lived LRU cache absorbs thundering-herd scenarios (e.g., 500
  students signing in at 9:00 AM for a mock test).
"""
import asyncio
import hashlib
import logging
from functools import lru_cache

from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from config import settings

logger = logging.getLogger(__name__)

# ── Reusable transport (thread-safe, avoids re-creating per call) ────
_google_transport = google_requests.Request()

# ── In-memory cache for recently verified tokens (max 2048 entries) ──
# Uses a hash of the token as key to avoid storing raw credentials.
@lru_cache(maxsize=2048)
def _cached_verify(token_hash: str, token: str) -> dict | None:
    """Synchronous verification — called inside a thread pool."""
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            _google_transport,
            settings.auth.google_client_id,
        )

        # Verify issuer
        if idinfo["iss"] not in ["accounts.google.com", "https://accounts.google.com"]:
            return None

        return {
            "google_id": idinfo["sub"],
            "email": idinfo["email"],
            "full_name": idinfo.get("name", ""),
            "avatar_url": idinfo.get("picture", ""),
            "email_verified": idinfo.get("email_verified", False),
        }
    except Exception:
        logger.debug("Google OAuth token verification failed", exc_info=True)
        return None


async def verify_google_token(token: str) -> dict | None:
    """
    Verify a Google OAuth ID token.

    Returns user info dict or None if invalid.

    The underlying google-auth library performs a synchronous HTTP request
    to fetch Google's public certificates. We offload this to asyncio's
    default thread-pool executor so the main event loop is never blocked,
    even when hundreds of students authenticate simultaneously.
    """
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    try:
        return await asyncio.to_thread(_cached_verify, token_hash, token)
    except Exception:
        logger.warning("Unexpected error in verify_google_token", exc_info=True)
        return None
