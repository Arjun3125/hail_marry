"""Audio overview route backed by the AI gateway."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.schemas.ai_runtime import AudioOverviewRequest, InternalAudioOverviewRequest
from src.domains.platform.services.ai_gateway import run_audio_overview
from src.domains.platform.services.usage_governance import (
    apply_model_override,
    approximate_token_count,
    evaluate_governance,
    record_usage_event,
)
from config import settings

router = APIRouter(prefix="/api/ai", tags=["AI Audio"])


@router.post("/audio-overview")
async def audio_overview(
    request: AudioOverviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a podcast-style dialogue about a topic from study materials."""
    governance = evaluate_governance(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric="audio_overviews",
        mode="audio_overview",
        estimated_prompt_tokens=approximate_token_count(request.topic),
    )
    if not governance.allowed:
        raise HTTPException(status_code=429, detail=governance.detail)
    result = await run_audio_overview(
        InternalAudioOverviewRequest(
            **request.model_dump(),
            tenant_id=str(current_user.tenant_id),
            model_override=apply_model_override(settings.llm.model, settings.llm.fallback_model, governance.model_override),
            max_prompt_tokens=governance.max_prompt_tokens,
            max_completion_tokens=governance.max_completion_tokens,
        )
    )
    record_usage_event(
        db,
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        metric="audio_overviews",
        token_usage=int(result.get("token_usage", 0) or 0) if isinstance(result, dict) else 0,
        model_used=apply_model_override(settings.llm.model, settings.llm.fallback_model, governance.model_override),
        used_fallback_model=governance.model_override == "fallback",
        metadata={"route": "ai.audio"},
    )
    db.commit()
    return result
