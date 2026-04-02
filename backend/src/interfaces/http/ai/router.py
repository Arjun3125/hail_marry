"""Cleaned AI HTTP router composition."""

from fastapi import APIRouter

from src.interfaces.rest_api.ai.routes import ai
from src.interfaces.rest_api.ai.routes import ai_jobs
from src.interfaces.rest_api.ai.routes import audio
from src.interfaces.rest_api.ai.routes import discovery
from src.interfaces.rest_api.ai.routes import documents
from src.interfaces.rest_api.ai.routes import openai_compat
from src.interfaces.rest_api.ai.routes import video

router = APIRouter()
router.include_router(ai.router)
router.include_router(ai_jobs.router)
router.include_router(audio.router)
router.include_router(video.router)
router.include_router(discovery.router)
router.include_router(documents.router)
router.include_router(openai_compat.router)

__all__ = ["router"]
