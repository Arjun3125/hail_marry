from fastapi import APIRouter

from .routes import support
from .routes import i18n
from .routes import demo
from .routes import demo_management
from .routes import notifications
from .routes import whatsapp
from .routes import feature_flags
from .routes import branding
from .routes import ai_history
from .routes import notebooks
from .routes import generated_content

router = APIRouter()
router.include_router(support.router)
router.include_router(i18n.router)
router.include_router(demo.router)
router.include_router(demo_management.router)
router.include_router(notifications.router)
router.include_router(whatsapp.router)
router.include_router(feature_flags.router)
router.include_router(branding.router)
router.include_router(ai_history.router)
router.include_router(notebooks.router)
router.include_router(generated_content.router)
