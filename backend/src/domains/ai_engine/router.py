from fastapi import APIRouter

from .routes import ai
from .routes import ai_jobs
from .routes import audio
from .routes import video
from .routes import discovery
from .routes import documents
from .routes import openai_compat

router = APIRouter()
router.include_router(ai.router)
router.include_router(ai_jobs.router)
router.include_router(audio.router)
router.include_router(video.router)
router.include_router(discovery.router)
router.include_router(documents.router)
router.include_router(openai_compat.router)
