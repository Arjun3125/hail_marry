"""Internationalization service — locale loading, translation lookup, interpolation."""
import json
import os
from functools import lru_cache
from typing import Any

from constants import SUPPORTED_LOCALES

_LOCALES_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "locales")


@lru_cache(maxsize=10)
def _load_locale_file(locale: str) -> dict:
    """Load and cache a locale JSON file."""
    filepath = os.path.join(_LOCALES_DIR, f"{locale}.json")
    if not os.path.isfile(filepath):
        return {}
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def get_supported_locales() -> list[dict]:
    """Return list of supported locales with labels."""
    return [{"code": code, "label": label} for code, label in SUPPORTED_LOCALES.items()]


def get_translations(locale: str) -> dict:
    """Get full translation bundle for a locale.

    Falls back to English if locale not found.
    """
    if locale not in SUPPORTED_LOCALES:
        locale = "en"
    return _load_locale_file(locale)


def _resolve_key(data: dict, key: str) -> Any:
    """Resolve a dotted key path in nested dict (e.g., 'nav.dashboard')."""
    parts = key.split(".")
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return None
    return current


def translate(key: str, locale: str = "en", **kwargs) -> str:
    """Resolve a translation key with variable interpolation.

    Examples:
        translate("dashboard.welcome", "hi", name="Arjun")
        → "स्वागत है, Arjun"

        translate("nav.dashboard", "mr")
        → "डॅशबोर्ड"
    """
    data = get_translations(locale)
    value = _resolve_key(data, key)

    if value is None:
        # Fallback to English
        en_data = get_translations("en")
        value = _resolve_key(en_data, key)

    if value is None:
        return key  # Return the key itself as last resort

    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except KeyError:
            return value

    return str(value) if not isinstance(value, dict) else json.dumps(value, ensure_ascii=False)


def clear_cache():
    """Clear the locale file cache (useful in tests)."""
    _load_locale_file.cache_clear()
