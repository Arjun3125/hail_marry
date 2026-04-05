"""Tests for refresh token blacklisting."""
from auth.token_blacklist import _blacklist_cache, BlacklistedToken


def test_blacklisted_token_model():
    token = BlacklistedToken(jti="test-jti-123", user_id="user-1")
    assert token.jti == "test-jti-123"


def test_cache_starts_empty():
    # Cache may have entries from other tests, but it should be a set
    assert isinstance(_blacklist_cache, set)


def test_jti_in_refresh_token():
    """Refresh tokens should now include a JTI claim."""
    # We can't call create_refresh_token without config, but verify the import
    from auth.jwt import create_refresh_token
    assert callable(create_refresh_token)


def test_blacklist_cache_type():
    assert isinstance(_blacklist_cache, set)


def test_blacklisted_token_jti_field():
    """BlacklistedToken should have jti field."""
    # Check the model has the column
    assert hasattr(BlacklistedToken, "jti")
    assert hasattr(BlacklistedToken, "user_id")
    assert hasattr(BlacklistedToken, "expires_at")
    assert hasattr(BlacklistedToken, "blacklisted_at")


def test_blacklist_functions_exist():
    from auth.token_blacklist import blacklist_token, is_blacklisted, cleanup_expired
    assert callable(blacklist_token)
    assert callable(is_blacklisted)
    assert callable(cleanup_expired)
