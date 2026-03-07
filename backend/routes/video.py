"""Video overview route backed by the AI gateway."""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from database import get_db
from models.user import User
from schemas.ai_runtime import InternalVideoOverviewRequest, VideoOverviewRequest
from services.ai_gateway import run_video_overview

router = APIRouter(prefix="/api/ai", tags=["AI Video"])


@router.post("/video-overview")
async def video_overview(
    request: VideoOverviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a narrated slide deck from study materials."""
    _ = db
    return await run_video_overview(
        InternalVideoOverviewRequest(
            **request.model_dump(),
            tenant_id=str(current_user.tenant_id),
        )
    )
