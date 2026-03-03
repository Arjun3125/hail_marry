"""JWT token creation and validation — access + refresh tokens."""
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from config import settings

REFRESH_TOKEN_EXPIRE_DAYS = 7


def create_access_token(data: dict) -> str:
    """Create a JWT access token (short-lived)."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.auth.jwt_expiry_minutes)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc), "type": "access"})
    return jwt.encode(to_encode, settings.auth.jwt_secret, algorithm=settings.auth.jwt_algorithm)


def create_refresh_token(data: dict) -> str:
    """Create a JWT refresh token (long-lived, 7 days)."""
    to_encode = {
        "user_id": data.get("user_id"),
        "tenant_id": data.get("tenant_id"),
        "type": "refresh",
    }
    expire = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp": expire, "iat": datetime.now(timezone.utc)})
    return jwt.encode(to_encode, settings.auth.jwt_secret + "_refresh", algorithm=settings.auth.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    """Decode and validate a JWT access token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token,
            settings.auth.jwt_secret,
            algorithms=[settings.auth.jwt_algorithm],
        )
        if payload.get("type") == "refresh":
            return None  # Don't accept refresh tokens as access tokens
        return payload
    except JWTError:
        return None


def decode_refresh_token(token: str) -> dict | None:
    """Decode a refresh token. Returns payload or None."""
    try:
        payload = jwt.decode(
            token,
            settings.auth.jwt_secret + "_refresh",
            algorithms=[settings.auth.jwt_algorithm],
        )
        if payload.get("type") != "refresh":
            return None
        return payload
    except JWTError:
        return None

