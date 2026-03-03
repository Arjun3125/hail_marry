"""Google OAuth token verification."""
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from config import settings


async def verify_google_token(token: str) -> dict | None:
    """
    Verify a Google OAuth ID token.
    Returns user info dict or None if invalid.
    """
    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
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
        return None
