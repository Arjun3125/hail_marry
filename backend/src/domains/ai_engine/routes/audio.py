"""Audio overview route backed by the AI gateway."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from src.domains.identity.models.user import User
from src.domains.ai_engine.schemas.ai_runtime import AudioOverviewRequest, InternalAudioOverviewRequest
from src.domains.ai_engine.services.ai_gateway import run_audio_overview

router = APIRouter(prefix="/api/ai", tags=["AI Audio"])


@router.post("/audio-overview")
async def audio_overview(
    request: AudioOverviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a podcast-style dialogue about a topic from study materials."""
    _ = db
    return await run_audio_overview(
        InternalAudioOverviewRequest(
            **request.model_dump(),
            tenant_id=str(current_user.tenant_id),
        )
    )
