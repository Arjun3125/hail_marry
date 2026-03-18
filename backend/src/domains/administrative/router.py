from fastapi import APIRouter

from .routes import admin
from .routes import superadmin
from .routes import billing
from .routes import fees
from .routes import admission
from .routes import library

router = APIRouter()
router.include_router(admin.router)
router.include_router(superadmin.router)
router.include_router(billing.router)
router.include_router(fees.router)
router.include_router(admission.router)
router.include_router(library.router)
