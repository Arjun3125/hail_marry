"""i18n API routes — locale listing and translation bundles."""
from fastapi import APIRouter, HTTPException

from src.domains.platform.services.i18n import get_supported_locales, get_translations
from constants import SUPPORTED_LOCALES

router = APIRouter(prefix="/api/i18n", tags=["i18n"])


@router.get("/locales")
def list_locales():
    """List all supported locales with labels."""
    return {"locales": get_supported_locales()}


@router.get("/translations/{locale}")
def get_locale_translations(locale: str):
    """Get full translation bundle for a locale."""
    if locale not in SUPPORTED_LOCALES:
        raise HTTPException(status_code=404, detail=f"Locale '{locale}' not supported")
    return {"locale": locale, "translations": get_translations(locale)}
