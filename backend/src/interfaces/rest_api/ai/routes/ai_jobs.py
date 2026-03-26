"""Queued AI job routes for heavy workloads."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from src.infrastructure.vector_store.citation_linker import make_citations_clickable
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.schemas.ai_runtime import (
    AIQueryRequest,
    AudioOverviewRequest,
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalVideoOverviewRequest,
    VideoOverviewRequest,
)
from src.domains.platform.services.ai_queue import (
    JOB_TYPE_AUDIO,
    JOB_TYPE_QUERY,
    JOB_TYPE_VIDEO,
    build_public_job_response,
    enqueue_job,
    get_job,
)

router = APIRouter(prefix="/api/ai", tags=["AI Jobs"])


def _authorize_job_access(job: dict, current_user: User) -> None:
    same_tenant = job.get("tenant_id") == str(current_user.tenant_id)
    owns_job = job.get("user_id") == str(current_user.id)
    is_admin = current_user.role == "admin"

    if not same_tenant:
        raise HTTPException(status_code=404, detail="Job not found.")
    if not owns_job and not is_admin:
        raise HTTPException(status_code=403, detail="Not authorized to access this AI job.")


@router.post("/query/jobs")
async def enqueue_text_query_job(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user),
):
    payload = InternalAIQueryRequest(
        **request.model_dump(),
        tenant_id=str(current_user.tenant_id),
    )
    
    from config import settings
    if settings.app.demo_mode:
        import uuid
        import time
        import random
        from database import SessionLocal
        from src.domains.platform.models.ai import AIQuery
        from src.domains.platform.services.ai_queue import STATUS_COMPLETED, _persist_job_state
        
        db = SessionLocal()
        try:
            demo_log = db.query(AIQuery).filter(
                AIQuery.tenant_id == current_user.tenant_id,
                AIQuery.mode == request.mode
            ).first()
            response_text = demo_log.response_text if demo_log else f"This is a mocked response for {request.mode} mode generated in Demo Mode."
        finally:
            db.close()
            
        now_str = time.strftime("%Y-%m-%dT%H:%M:%S.%fZ", time.gmtime())
        mock_job = {
            "job_id": str(uuid.uuid4()),
            "job_type": JOB_TYPE_QUERY,
            "priority": 30,
            "trace_id": str(uuid.uuid4())[:8],
            "status": STATUS_COMPLETED,
            "tenant_id": str(current_user.tenant_id),
            "user_id": str(current_user.id),
            "worker_id": "demo-worker",
            "request": payload.model_dump(),
            "result": {
                "answer": response_text,
                "mode": request.mode,
                "citations": [],
                "token_usage": random.randint(150, 500),
                "citation_count": 0,
                "has_context": True,
                "citation_valid": True,
            },
            "error": None,
            "attempts": 1,
            "max_retries": 3,
            "created_at": now_str,
            "updated_at": now_str,
            "started_at": now_str,
            "completed_at": now_str,
            "events": []
        }
        _persist_job_state(mock_job)
        return build_public_job_response(mock_job)

    return enqueue_job(
        JOB_TYPE_QUERY,
        payload.model_dump(),
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )


@router.post("/audio-overview/jobs")
async def enqueue_audio_overview_job(
    request: AudioOverviewRequest,
    current_user: User = Depends(get_current_user),
):
    payload = InternalAudioOverviewRequest(
        **request.model_dump(),
        tenant_id=str(current_user.tenant_id),
    )
    return enqueue_job(
        JOB_TYPE_AUDIO,
        payload.model_dump(),
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )


@router.post("/video-overview/jobs")
async def enqueue_video_overview_job(
    request: VideoOverviewRequest,
    current_user: User = Depends(get_current_user),
):
    payload = InternalVideoOverviewRequest(
        **request.model_dump(),
        tenant_id=str(current_user.tenant_id),
    )
    return enqueue_job(
        JOB_TYPE_VIDEO,
        payload.model_dump(),
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )


@router.get("/jobs/{job_id}")
async def get_ai_job_status(
    job_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    _authorize_job_access(job, current_user)
    response = build_public_job_response(job)
    result = response.get("result")
    if isinstance(result, dict) and result.get("citations"):
        response["result"] = make_citations_clickable(result, current_user.tenant_id, db)
    return response
