from fastapi import APIRouter

from .routes import support
from .routes import i18n
from .routes import demo
from .routes import demo_management
from .routes import notifications
from .routes import whatsapp

router = APIRouter()
router.include_router(support.router)
router.include_router(i18n.router)
router.include_router(demo.router)
router.include_router(demo_management.router)
router.include_router(notifications.router)
router.include_router(whatsapp.router)
