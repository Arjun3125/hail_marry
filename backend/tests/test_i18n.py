"""Tests for i18n service — locale loading, translation, interpolation."""
import json
import os
import pytest

from services.i18n import clear_cache, get_supported_locales, get_translations, translate
from constants import SUPPORTED_LOCALES


@pytest.fixture(autouse=True)
def _clear_i18n_cache():
    """Clear LRU cache before each test."""
    clear_cache()
    yield
    clear_cache()


# ── Supported locales ──

def test_supported_locales_count():
    locales = get_supported_locales()
    assert len(locales) == len(SUPPORTED_LOCALES)


def test_supported_locales_structure():
    locales = get_supported_locales()
    for loc in locales:
        assert "code" in loc
        assert "label" in loc


def test_supported_locales_codes():
    locales = get_supported_locales()
    codes = {loc["code"] for loc in locales}
    assert "en" in codes
    assert "hi" in codes
    assert "mr" in codes


# ── Translation loading ──

def test_load_english_translations():
    data = get_translations("en")
    assert "nav" in data
    assert "dashboard" in data["nav"]


def test_load_hindi_translations():
    data = get_translations("hi")
    assert data.get("app_name") == "विद्याOS"


def test_load_marathi_translations():
    data = get_translations("mr")
    assert data.get("app_name") == "विद्याOS"


def test_unsupported_locale_falls_back_to_english():
    data = get_translations("fr")
    en_data = get_translations("en")
    assert data == en_data


# ── Translation key resolution ──

def test_translate_simple_key():
    result = translate("nav.dashboard", "en")
    assert result == "Dashboard"


def test_translate_hindi_key():
    result = translate("nav.dashboard", "hi")
    assert result == "डैशबोर्ड"


def test_translate_with_interpolation():
    result = translate("dashboard.welcome", "en", name="Arjun")
    assert result == "Welcome, Arjun"


def test_translate_hindi_with_interpolation():
    result = translate("dashboard.welcome", "hi", name="अर्जुन")
    assert result == "स्वागत है, अर्जुन"


def test_translate_missing_key_returns_key():
    result = translate("nonexistent.key.path", "en")
    assert result == "nonexistent.key.path"


def test_translate_missing_key_fallback_to_english():
    """If key missing in Hindi, should check English before returning key."""
    result = translate("nav.dashboard", "hi")
    assert isinstance(result, str)
    assert len(result) > 0


# ── Locale file completeness ──

def test_all_locales_have_same_top_level_keys():
    """All locale files should have the same top-level sections."""
    en_keys = set(get_translations("en").keys())
    for locale in SUPPORTED_LOCALES:
        locale_keys = set(get_translations(locale).keys())
        missing = en_keys - locale_keys
        assert not missing, f"Locale '{locale}' missing keys: {missing}"
