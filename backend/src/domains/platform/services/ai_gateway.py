"""Gateway for executing AI workflows natively within the monolith."""
from __future__ import annotations

from typing import Any

from src.domains.platform.schemas.ai_runtime import (
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalIngestURLRequest,
    InternalStudyToolGenerateRequest,
    InternalTeacherAssessmentRequest,
    InternalTeacherDocumentIngestRequest,
    InternalTeacherYoutubeIngestRequest,
    InternalVideoOverviewRequest,
)

from src.domains.platform.services.trace_backend import record_trace_event

from src.interfaces.rest_api.ai.workflows import (
    execute_audio_overview,
    execute_text_query,
    execute_video_overview,
)
from src.interfaces.rest_api.ai.discovery_workflows import execute_url_ingestion
from src.interfaces.rest_api.ai.ingestion_workflows import execute_teacher_document_ingestion, execute_teacher_youtube_ingestion
from src.shared.ai_tools.study_tools import execute_study_tool
from src.interfaces.rest_api.ai.teacher_workflows import execute_teacher_assessment


async def run_text_query(request: InternalAIQueryRequest, trace_id: str | None = None) -> dict[str, Any]:
    record_trace_event(trace_id=trace_id, tenant_id=request.tenant_id, source="ai-gateway", stage="query.started")
    payload = await execute_text_query(request)
    if trace_id:
        payload["trace_id"] = trace_id
    record_trace_event(trace_id=trace_id, tenant_id=request.tenant_id, source="ai-gateway", stage="query.completed", status="ok")
    return payload


async def run_audio_overview(request: InternalAudioOverviewRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_audio_overview(request)


async def run_video_overview(request: InternalVideoOverviewRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_video_overview(request)


async def run_study_tool(request: InternalStudyToolGenerateRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_study_tool(request)


async def run_teacher_assessment(request: InternalTeacherAssessmentRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_teacher_assessment(request)


async def run_url_ingestion(request: InternalIngestURLRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_url_ingestion(request)


async def run_teacher_document_ingestion(request: InternalTeacherDocumentIngestRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_teacher_document_ingestion(request)


async def run_teacher_youtube_ingestion(request: InternalTeacherYoutubeIngestRequest, trace_id: str | None = None) -> dict[str, Any]:
    return await execute_teacher_youtube_ingestion(request)
