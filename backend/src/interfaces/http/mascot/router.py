"""HTTP interface for mascot domain routes."""

from __future__ import annotations

from fastapi import APIRouter

from src.domains.mascot.routes.chat_route import router as chat_router
from src.domains.mascot.routes.mascot_routes import router as mascot_router

router = APIRouter()
router.include_router(mascot_router)
router.include_router(chat_router, prefix="", tags=["mascot"])
