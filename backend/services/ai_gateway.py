"""Gateway for executing AI workflows via the dedicated AI service only."""
from __future__ import annotations

from typing import Any

import httpx
from fastapi import HTTPException

from config import settings
from schemas.ai_runtime import (
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalIngestURLRequest,
    InternalStudyToolGenerateRequest,
    InternalTeacherAssessmentRequest,
    InternalTeacherDocumentIngestRequest,
    InternalTeacherYoutubeIngestRequest,
    InternalVideoOverviewRequest,
)
from services.trace_backend import record_trace_event


def _service_headers(trace_id: str | None = None) -> dict[str, str]:
    headers: dict[str, str] = {}
    if settings.ai_service.api_key:
        headers["X-AI-Service-Key"] = settings.ai_service.api_key
    if trace_id:
        headers["X-Trace-Id"] = trace_id
    return headers


def _extract_error_detail(exc: httpx.HTTPStatusError) -> str:
    try:
        payload = exc.response.json()
    except ValueError:
        payload = None

    if isinstance(payload, dict) and payload.get("detail"):
        return str(payload["detail"])
    return exc.response.text or "Dedicated AI service request failed."


async def _post_to_ai_service(path: str, payload: dict[str, Any], trace_id: str | None = None) -> dict[str, Any]:
    url = f"{settings.ai_service.url.rstrip('/')}{path}"
    tenant_id = payload.get("tenant_id")
    record_trace_event(
        trace_id=trace_id,
        tenant_id=tenant_id,
        source="api-gateway",
        stage="ai_service.requested",
        metadata={"path": path},
    )

    try:
        async with httpx.AsyncClient(timeout=settings.ai_service.timeout_seconds) as client:
            response = await client.post(url, json=payload, headers=_service_headers(trace_id=trace_id))
            response.raise_for_status()
            data = response.json()
    except httpx.HTTPStatusError as exc:
        record_trace_event(
            trace_id=trace_id,
            tenant_id=tenant_id,
            source="api-gateway",
            stage="ai_service.failed",
            status="error",
            detail=_extract_error_detail(exc),
            metadata={"path": path, "status_code": exc.response.status_code},
        )
        raise HTTPException(status_code=exc.response.status_code, detail=_extract_error_detail(exc)) from exc
    except httpx.HTTPError as exc:
        record_trace_event(
            trace_id=trace_id,
            tenant_id=tenant_id,
            source="api-gateway",
            stage="ai_service.unavailable",
            status="error",
            detail="Dedicated AI service is unavailable.",
            metadata={"path": path},
        )
        raise HTTPException(status_code=503, detail="Dedicated AI service is unavailable.") from exc

    if not isinstance(data, dict):
        raise HTTPException(status_code=502, detail="Dedicated AI service returned an invalid payload.")
    if trace_id and not data.get("trace_id"):
        data["trace_id"] = trace_id
    record_trace_event(
        trace_id=trace_id,
        tenant_id=tenant_id,
        source="api-gateway",
        stage="ai_service.completed",
        status="ok",
        metadata={"path": path},
    )
    return data


async def run_text_query(request: InternalAIQueryRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/query", request.model_dump(), trace_id=trace_id)


async def run_audio_overview(request: InternalAudioOverviewRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/audio-overview", request.model_dump(), trace_id=trace_id)


async def run_video_overview(request: InternalVideoOverviewRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/video-overview", request.model_dump(), trace_id=trace_id)


async def run_study_tool(request: InternalStudyToolGenerateRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/study-tool", request.model_dump(), trace_id=trace_id)


async def run_teacher_assessment(request: InternalTeacherAssessmentRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/teacher-assessment", request.model_dump(), trace_id=trace_id)


async def run_url_ingestion(request: InternalIngestURLRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/url-ingest", request.model_dump(), trace_id=trace_id)


async def run_teacher_document_ingestion(request: InternalTeacherDocumentIngestRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/teacher-document-ingest", request.model_dump(), trace_id=trace_id)


async def run_teacher_youtube_ingestion(request: InternalTeacherYoutubeIngestRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await _post_to_ai_service("/internal/ai/teacher-youtube-ingest", request.model_dump(), trace_id=trace_id)
