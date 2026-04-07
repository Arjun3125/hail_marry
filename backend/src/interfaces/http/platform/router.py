"""Platform HTTP interface composition without demo-specific routes."""

from fastapi import APIRouter

from src.domains.platform.routes import (
    ai_history,
    ai_studio,
    branding,
    feature_flags,
    generated_content,
    i18n,
    mascot,
    notebooks,
    notifications,
    personalization,
    support,
    telemetry,
    whatsapp,
    whatsapp_bridge,
)

router = APIRouter()
router.include_router(support.router)
router.include_router(telemetry.router)
router.include_router(i18n.router)
router.include_router(notifications.router)
router.include_router(whatsapp.router)
router.include_router(whatsapp_bridge.router)
router.include_router(feature_flags.router)
router.include_router(branding.router)
router.include_router(ai_history.router)
router.include_router(notebooks.router)
router.include_router(generated_content.router)
router.include_router(ai_studio.router)
router.include_router(mascot.router)
router.include_router(personalization.router)

__all__ = ["router"]
