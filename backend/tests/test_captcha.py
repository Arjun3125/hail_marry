"""Tests for reCAPTCHA / bot protection."""
import pytest
from middleware.captcha import (
    PROTECTED_ENDPOINTS, RECAPTCHA_SCORE_THRESHOLD,
    is_human, is_protected_endpoint,
)


def test_protected_endpoints():
    assert "/api/onboarding/register" in PROTECTED_ENDPOINTS
    assert "/api/admission/apply" in PROTECTED_ENDPOINTS
    assert "/api/auth/login" in PROTECTED_ENDPOINTS


def test_non_protected_endpoint():
    assert not is_protected_endpoint("/api/ai/query")


def test_is_human_success():
    result = {"success": True, "score": 0.9}
    assert is_human(result) is True


def test_is_human_low_score():
    result = {"success": True, "score": 0.2}
    assert is_human(result) is False


def test_is_human_failed_captcha():
    result = {"success": False, "score": 0.9}
    assert is_human(result) is False


def test_threshold_default():
    assert RECAPTCHA_SCORE_THRESHOLD == 0.5
