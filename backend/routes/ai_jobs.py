"""Queued AI job routes for heavy workloads."""
from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from auth.dependencies import get_current_user
from models.user import User
from schemas.ai_runtime import (
    AIQueryRequest,
    AudioOverviewRequest,
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalVideoOverviewRequest,
    VideoOverviewRequest,
)
from services.ai_queue import (
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
):
    job = get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found.")
    _authorize_job_access(job, current_user)
    return build_public_job_response(job)
