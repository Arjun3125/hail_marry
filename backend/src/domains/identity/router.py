from fastapi import APIRouter

from .routes import auth
from .routes import enterprise
from .routes import invitations
from .routes import onboarding

router = APIRouter()
router.include_router(auth.router)
router.include_router(enterprise.router)
router.include_router(invitations.router)
router.include_router(onboarding.router)
