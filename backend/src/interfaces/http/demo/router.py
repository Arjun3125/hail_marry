"""Demo HTTP interface composition."""

from fastapi import APIRouter

from src.domains.platform.routes import demo, demo_management

router = APIRouter()
router.include_router(demo.router)
router.include_router(demo_management.router)

__all__ = ["router"]
