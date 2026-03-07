"""Dedicated AI service entrypoint for extracted AI workflows."""
from __future__ import annotations

import logging
import secrets

from fastapi import Depends, FastAPI, Header, HTTPException
from starlette.responses import PlainTextResponse

from ai.workflows import (
    execute_audio_overview,
    execute_text_query,
    execute_video_overview,
)
from ai.discovery_workflows import execute_url_ingestion
from ai.ingestion_workflows import execute_teacher_document_ingestion, execute_teacher_youtube_ingestion
from ai.study_tools import execute_study_tool
from ai.teacher_workflows import execute_teacher_assessment
from config import settings
from database import engine
from middleware.observability import ObservabilityMiddleware
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
from services.metrics_registry import export_prometheus_text
from services.startup_checks import collect_dependency_status, enforce_startup_dependencies
from services.structured_logging import configure_structured_logging
from services.telemetry import configure_telemetry, instrument_sqlalchemy_engine
from services.trace_backend import record_trace_event

configure_structured_logging(service_name="vidyaos-ai-service")

app = FastAPI(
    title=f"{settings.app.name} AI Service",
    version=settings.app.version,
    description="Dedicated AI execution service for grounded generation workflows.",
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
)
configure_telemetry(service_name="vidyaos-ai-service", app=app)
instrument_sqlalchemy_engine(engine)
logger = logging.getLogger("ai-service")
app.add_middleware(ObservabilityMiddleware, service_name="vidyaos-ai-service")


def require_ai_service_key(x_ai_service_key: str | None = Header(default=None)) -> None:
    expected = settings.ai_service.api_key.strip()
    if not expected:
        return
    if not x_ai_service_key or not secrets.compare_digest(x_ai_service_key, expected):
        raise HTTPException(status_code=401, detail="Unauthorized AI service request.")


@app.get("/health")
async def ai_service_health() -> dict[str, str]:
    return {"status": "healthy", "service": "ai-service", "version": settings.app.version}


@app.on_event("startup")
async def ai_service_startup_dependency_checks():
    enforce_startup_dependencies("ai-service")


@app.get("/ready")
async def ai_service_ready():
    status = collect_dependency_status("ai-service")
    if not status["ready"]:
        raise HTTPException(status_code=503, detail=status)
    return status


@app.get("/metrics", response_class=PlainTextResponse)
async def ai_service_metrics(x_metrics_token: str | None = Header(default=None)):
    expected = settings.observability.metrics_token.strip()
    if expected and x_metrics_token != expected:
        raise HTTPException(status_code=401, detail="Unauthorized metrics request.")
    return export_prometheus_text()


@app.post("/internal/ai/query", dependencies=[Depends(require_ai_service_key)])
async def internal_ai_query(request: InternalAIQueryRequest, x_trace_id: str | None = Header(default=None)) -> dict:
    logger.info("AI service handling query trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="query.started",
    )
    payload = await execute_text_query(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="query.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/audio-overview", dependencies=[Depends(require_ai_service_key)])
async def internal_audio_overview(request: InternalAudioOverviewRequest, x_trace_id: str | None = Header(default=None)) -> dict:
    logger.info("AI service handling audio_overview trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="audio_overview.started",
    )
    payload = await execute_audio_overview(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="audio_overview.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/video-overview", dependencies=[Depends(require_ai_service_key)])
async def internal_video_overview(request: InternalVideoOverviewRequest, x_trace_id: str | None = Header(default=None)) -> dict:
    logger.info("AI service handling video_overview trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="video_overview.started",
    )
    payload = await execute_video_overview(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="video_overview.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/study-tool", dependencies=[Depends(require_ai_service_key)])
async def internal_study_tool(request: InternalStudyToolGenerateRequest, x_trace_id: str | None = Header(default=None)) -> dict:
    logger.info("AI service handling study_tool trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="study_tool.started",
    )
    payload = await execute_study_tool(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="study_tool.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/teacher-assessment", dependencies=[Depends(require_ai_service_key)])
async def internal_teacher_assessment(
    request: InternalTeacherAssessmentRequest,
    x_trace_id: str | None = Header(default=None),
) -> dict:
    logger.info("AI service handling teacher_assessment trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="teacher_assessment.started",
    )
    payload = await execute_teacher_assessment(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="teacher_assessment.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/url-ingest", dependencies=[Depends(require_ai_service_key)])
async def internal_url_ingest(
    request: InternalIngestURLRequest,
    x_trace_id: str | None = Header(default=None),
) -> dict:
    logger.info("AI service handling url_ingest trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="url_ingest.started",
    )
    payload = await execute_url_ingestion(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="url_ingest.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/teacher-document-ingest", dependencies=[Depends(require_ai_service_key)])
async def internal_teacher_document_ingest(
    request: InternalTeacherDocumentIngestRequest,
    x_trace_id: str | None = Header(default=None),
) -> dict:
    logger.info("AI service handling teacher_document_ingest trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="teacher_document_ingest.started",
    )
    payload = await execute_teacher_document_ingestion(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="teacher_document_ingest.completed",
        status="ok",
    )
    return payload


@app.post("/internal/ai/teacher-youtube-ingest", dependencies=[Depends(require_ai_service_key)])
async def internal_teacher_youtube_ingest(
    request: InternalTeacherYoutubeIngestRequest,
    x_trace_id: str | None = Header(default=None),
) -> dict:
    logger.info("AI service handling teacher_youtube_ingest trace_id=%s", x_trace_id or "-")
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="teacher_youtube_ingest.started",
    )
    payload = await execute_teacher_youtube_ingestion(request)
    if x_trace_id:
        payload["trace_id"] = x_trace_id
    record_trace_event(
        trace_id=x_trace_id,
        tenant_id=request.tenant_id,
        source="ai-service",
        stage="teacher_youtube_ingest.completed",
        status="ok",
    )
    return payload
