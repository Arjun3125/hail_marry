"""System-wide traceability helpers for structured failure codes and diagnostics."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
import logging
from typing import Any

from fastapi import HTTPException
from starlette.requests import Request

from database import SessionLocal
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.services.metrics_registry import observe_traceability_error
from src.domains.platform.services.trace_backend import record_trace_event

logger = logging.getLogger("traceability")


@dataclass(frozen=True)
class ErrorDescriptor:
    key: str
    module: str
    category: str
    sequence: str
    subsystem: str
    title: str
    default_message: str
    severity: str = "error"
    default_status_code: int = 500

    @property
    def error_code(self) -> str:
        return f"{self.module}-{self.category}-{self.sequence}"


class TraceabilityError(Exception):
    def __init__(
        self,
        key: str,
        *,
        detail: str | None = None,
        status_code: int | None = None,
        metadata: dict[str, Any] | None = None,
        cause: Exception | None = None,
    ) -> None:
        self.key = key
        self.detail = detail
        self.status_code = status_code
        self.metadata = metadata or {}
        self.cause = cause
        descriptor = get_error_descriptor(key)
        super().__init__(detail or descriptor.default_message)


ERROR_TAXONOMY: dict[str, ErrorDescriptor] = {
    "whatsapp.connection": ErrorDescriptor("whatsapp.connection", "WA", "CONN", "001", "whatsapp", "WhatsApp connection failure", "WhatsApp integration failed.", severity="critical", default_status_code=503),
    "whatsapp.webhook": ErrorDescriptor("whatsapp.webhook", "WA", "WEB", "002", "whatsapp", "WhatsApp webhook failure", "WhatsApp webhook handling failed.", severity="critical", default_status_code=502),
    "ocr.read": ErrorDescriptor("ocr.read", "OCR", "READ", "002", "ocr", "OCR extraction failure", "OCR processing failed.", severity="warning", default_status_code=500),
    "file.upload": ErrorDescriptor("file.upload", "FILE", "UPL", "003", "upload", "File upload failure", "File upload failed.", severity="warning", default_status_code=400),
    "rag.retrieval": ErrorDescriptor("rag.retrieval", "RAG", "RET", "003", "rag", "RAG retrieval failure", "RAG retrieval failed.", severity="critical", default_status_code=502),
    "llm.generation": ErrorDescriptor("llm.generation", "LLM", "GEN", "004", "llm", "LLM generation failure", "AI generation failed.", severity="critical", default_status_code=502),
    "flowchart.generation": ErrorDescriptor("flowchart.generation", "FLOW", "GEN", "005", "flowchart", "Flowchart generation failure", "Flowchart generation failed.", severity="warning", default_status_code=422),
    "api.call": ErrorDescriptor("api.call", "API", "CALL", "006", "api", "External API failure", "External API call failed.", severity="critical", default_status_code=502),
    "vector.database": ErrorDescriptor("vector.database", "DB", "VEC", "007", "vector_db", "Vector database failure", "Vector database operation failed.", severity="critical", default_status_code=503),
    "ui.action": ErrorDescriptor("ui.action", "UI", "ACT", "008", "ui", "UI action failure", "The requested action failed.", severity="warning", default_status_code=500),
    "quiz.generation": ErrorDescriptor("quiz.generation", "QUIZ", "GEN", "009", "quiz", "Quiz generation failure", "Quiz generation failed.", severity="warning", default_status_code=422),
    "flashcards.generation": ErrorDescriptor("flashcards.generation", "CARD", "GEN", "010", "flashcards", "Flashcard generation failure", "Flashcard generation failed.", severity="warning", default_status_code=422),
    "mindmap.generation": ErrorDescriptor("mindmap.generation", "MIND", "GEN", "011", "mindmap", "Mind map generation failure", "Mind map generation failed.", severity="warning", default_status_code=422),
    "concept_map.generation": ErrorDescriptor("concept_map.generation", "CMAP", "GEN", "012", "concept_map", "Concept map generation failure", "Concept map generation failed.", severity="warning", default_status_code=422),
    "cache.operation": ErrorDescriptor("cache.operation", "CACHE", "OPS", "013", "cache", "Cache failure", "Cache operation failed.", severity="warning", default_status_code=503),
    "job.execution": ErrorDescriptor("job.execution", "JOB", "EXEC", "014", "background_jobs", "Background job failure", "Background job execution failed.", severity="critical", default_status_code=500),
    "embedding.generation": ErrorDescriptor("embedding.generation", "EMB", "GEN", "015", "embedding", "Embedding generation failure", "Embedding generation failed.", severity="critical", default_status_code=502),
    "chunking.document": ErrorDescriptor("chunking.document", "ING", "CHNK", "016", "ingestion", "Document chunking failure", "Document chunking failed.", severity="warning", default_status_code=500),
    "api.validation": ErrorDescriptor("api.validation", "API", "VAL", "017", "api", "Validation failure", "Please check your input and try again.", severity="warning", default_status_code=422),
    "api.auth": ErrorDescriptor("api.auth", "API", "AUTH", "018", "auth", "Authorization failure", "Authentication or authorization failed.", severity="warning", default_status_code=401),
    "api.server": ErrorDescriptor("api.server", "API", "SRV", "019", "api", "Unhandled server failure", "Something went wrong while processing the request.", severity="critical", default_status_code=500),
}

FALLBACK_DESCRIPTOR = ERROR_TAXONOMY["api.server"]
ERROR_KEYWORD_TO_KEY: dict[str, str] = {
    "ocr processing failed": "ocr.read",
    "no readable": "ocr.read",
    "ocr": "ocr.read",
    "flowchart": "flowchart.generation",
    "quiz output": "quiz.generation",
    "quiz generation": "quiz.generation",
    "flashcards output": "flashcards.generation",
    "flashcard generation": "flashcards.generation",
    "mind map output": "mindmap.generation",
    "mind map generation": "mindmap.generation",
    "mindmap": "mindmap.generation",
    "concept map output": "concept_map.generation",
    "concept map generation": "concept_map.generation",
    "vector": "vector.database",
    "faiss": "vector.database",
    "qdrant": "vector.database",
    "embedding search": "vector.database",
    "retrieval": "rag.retrieval",
    "grounded context": "rag.retrieval",
    "study materials found": "rag.retrieval",
    "ollama": "llm.generation",
    "ai runtime": "llm.generation",
    "timed out": "llm.generation",
    "generation failed": "llm.generation",
    "webhook": "whatsapp.webhook",
    "whatsapp": "whatsapp.connection",
    "upload": "file.upload",
    "embedding": "embedding.generation",
    "chunk": "chunking.document",
    "cache": "cache.operation",
    "redis": "cache.operation",
    "job": "job.execution",
    "worker": "job.execution",
}


def get_error_descriptor(key: str | None) -> ErrorDescriptor:
    if not key:
        return FALLBACK_DESCRIPTOR
    return ERROR_TAXONOMY.get(key, FALLBACK_DESCRIPTOR)


def _normalize_message(detail: Any) -> str:
    if isinstance(detail, dict):
        value = detail.get("detail")
        if isinstance(value, str) and value.strip():
            return value.strip()
        if isinstance(detail.get("message"), str) and str(detail["message"]).strip():
            return str(detail["message"]).strip()
        return "Request failed."
    if isinstance(detail, str) and detail.strip():
        return detail.strip()
    return "Request failed."


def classify_error_key(*, path: str, status_code: int, detail: Any = None) -> str:
    message = _normalize_message(detail).lower()
    lowered_path = path.lower()

    for keyword, key in ERROR_KEYWORD_TO_KEY.items():
        if keyword in message:
            return key

    if lowered_path.startswith("/api/whatsapp"):
        return "whatsapp.connection"
    if lowered_path.startswith("/api/ai"):
        if status_code in {503, 504, 502}:
            return "llm.generation"
        return "rag.retrieval"
    if lowered_path.startswith("/api/student/upload") or lowered_path.startswith("/api/teacher/upload"):
        return "file.upload"
    if lowered_path.startswith("/api/") and status_code in {400, 422}:
        return "api.validation"
    if lowered_path.startswith("/api/") and status_code in {401, 403}:
        return "api.auth"
    return "api.server"


def _serialize_exception(exc: Exception | None) -> str | None:
    if exc is None:
        return None
    return f"{exc.__class__.__name__}: {exc}"


def _record_traceability_audit(
    *,
    trace_id: str | None,
    tenant_id: str | None,
    user_id: str | None,
    descriptor: ErrorDescriptor,
    detail: str,
    status_code: int,
    path: str,
    method: str,
    metadata: dict[str, Any] | None = None,
) -> None:
    observe_traceability_error(descriptor.error_code, subsystem=descriptor.subsystem, severity=descriptor.severity)
    record_trace_event(
        trace_id=trace_id,
        tenant_id=tenant_id,
        user_id=user_id,
        source="traceability",
        stage="error.recorded",
        status="error",
        detail=detail,
        metadata={
            "error_code": descriptor.error_code,
            "subsystem": descriptor.subsystem,
            "path": path,
            "method": method,
            "status_code": status_code,
            **(metadata or {}),
        },
    )
    if not tenant_id:
        return
    db = SessionLocal()
    try:
        db.add(
            AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action="trace.error",
                entity_type="trace_error",
                entity_id=None,
                metadata_={
                    "trace_id": trace_id,
                    "error_code": descriptor.error_code,
                    "subsystem": descriptor.subsystem,
                    "category": descriptor.category,
                    "severity": descriptor.severity,
                    "title": descriptor.title,
                    "detail": detail,
                    "status_code": status_code,
                    "path": path,
                    "method": method,
                    **(metadata or {}),
                },
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    finally:
        db.close()


def build_error_payload(
    *,
    descriptor: ErrorDescriptor,
    detail: str,
    trace_id: str | None,
    status_code: int,
) -> dict[str, Any]:
    return {
        "detail": detail,
        "error_code": descriptor.error_code,
        "subsystem": descriptor.subsystem,
        "error_title": descriptor.title,
        "severity": descriptor.severity,
        "trace_id": trace_id,
        "status_code": status_code,
        "support_message": f"Please contact support with error code {descriptor.error_code}.",
    }


def build_http_error_response(request: Request, exc: HTTPException, *, override_key: str | None = None) -> tuple[dict[str, Any], int, dict[str, str]]:
    status_code = int(exc.status_code)
    key = override_key or classify_error_key(path=request.url.path, status_code=status_code, detail=exc.detail)
    descriptor = get_error_descriptor(key)
    detail = _normalize_message(exc.detail) or descriptor.default_message
    payload = build_error_payload(
        descriptor=descriptor,
        detail=detail,
        trace_id=getattr(request.state, "trace_id", None),
        status_code=status_code,
    )
    extra_metadata = {}
    if isinstance(exc.detail, dict):
        extra_metadata["raw_detail"] = exc.detail
    _record_traceability_audit(
        trace_id=getattr(request.state, "trace_id", None),
        tenant_id=getattr(request.state, "tenant_id", None),
        user_id=getattr(request.state, "user_id", None),
        descriptor=descriptor,
        detail=detail,
        status_code=status_code,
        path=request.url.path,
        method=request.method,
        metadata=extra_metadata,
    )
    logger.warning(
        "traceable_http_error",
        extra={
            "event": "traceability.http_error",
            "trace_id": getattr(request.state, "trace_id", None),
            "tenant_id": getattr(request.state, "tenant_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "path": request.url.path,
            "method": request.method,
            "status_code": status_code,
            "error_code": descriptor.error_code,
            "subsystem": descriptor.subsystem,
            "error_category": descriptor.category,
        },
    )
    return payload, status_code, {"X-Trace-Id": getattr(request.state, "trace_id", ""), "X-Error-Code": descriptor.error_code}


def build_unhandled_error_response(request: Request, exc: Exception) -> tuple[dict[str, Any], int, dict[str, str]]:
    key = classify_error_key(path=request.url.path, status_code=500, detail=str(exc))
    descriptor = get_error_descriptor(key)
    status_code = descriptor.default_status_code
    detail = descriptor.default_message
    payload = build_error_payload(
        descriptor=descriptor,
        detail=detail,
        trace_id=getattr(request.state, "trace_id", None),
        status_code=status_code,
    )
    _record_traceability_audit(
        trace_id=getattr(request.state, "trace_id", None),
        tenant_id=getattr(request.state, "tenant_id", None),
        user_id=getattr(request.state, "user_id", None),
        descriptor=descriptor,
        detail=str(exc),
        status_code=status_code,
        path=request.url.path,
        method=request.method,
        metadata={"exception": _serialize_exception(exc)},
    )
    logger.error(
        "traceable_unhandled_error",
        extra={
            "event": "traceability.unhandled_error",
            "trace_id": getattr(request.state, "trace_id", None),
            "tenant_id": getattr(request.state, "tenant_id", None),
            "user_id": getattr(request.state, "user_id", None),
            "path": request.url.path,
            "method": request.method,
            "status_code": status_code,
            "error_code": descriptor.error_code,
            "subsystem": descriptor.subsystem,
            "error_category": descriptor.category,
        },
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return payload, status_code, {"X-Trace-Id": getattr(request.state, "trace_id", ""), "X-Error-Code": descriptor.error_code}


def build_traceability_summary(*, tenant_id: Any, days: int = 7, limit: int = 50, db_session: Any | None = None) -> dict[str, Any]:
    since = datetime.now(timezone.utc) - timedelta(days=max(days, 1))
    db = db_session or SessionLocal()
    try:
        rows = (
            db.query(AuditLog)
            .filter(
                AuditLog.tenant_id == tenant_id,
                AuditLog.entity_type == "trace_error",
                AuditLog.created_at >= since,
            )
            .order_by(AuditLog.created_at.desc())
            .limit(max(limit, 1) * 4)
            .all()
        )
        by_code: dict[str, dict[str, Any]] = {}
        by_subsystem: dict[str, int] = {}
        recent_errors: list[dict[str, Any]] = []
        for row in rows:
            metadata = row.metadata_ or {}
            error_code = str(metadata.get("error_code") or "UNKNOWN")
            subsystem = str(metadata.get("subsystem") or "unknown")
            severity = str(metadata.get("severity") or "error")
            bucket = by_code.setdefault(
                error_code,
                {
                    "error_code": error_code,
                    "title": metadata.get("title") or error_code,
                    "subsystem": subsystem,
                    "severity": severity,
                    "count": 0,
                    "latest_at": str(row.created_at),
                },
            )
            bucket["count"] += 1
            bucket["latest_at"] = max(str(row.created_at), str(bucket["latest_at"]))
            by_subsystem[subsystem] = by_subsystem.get(subsystem, 0) + 1
            if len(recent_errors) < limit:
                recent_errors.append(
                    {
                        "created_at": str(row.created_at),
                        "error_code": error_code,
                        "subsystem": subsystem,
                        "severity": severity,
                        "detail": metadata.get("detail"),
                        "path": metadata.get("path"),
                        "method": metadata.get("method"),
                        "status_code": metadata.get("status_code"),
                        "trace_id": metadata.get("trace_id"),
                    }
                )

        grouped_errors = sorted(by_code.values(), key=lambda item: (-int(item["count"]), str(item["error_code"])))
        subsystem_totals = [
            {"subsystem": subsystem, "count": count}
            for subsystem, count in sorted(by_subsystem.items(), key=lambda item: (-item[1], item[0]))
        ]
        return {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "period_days": max(days, 1),
            "total_errors": sum(int(item["count"]) for item in grouped_errors),
            "grouped_errors": grouped_errors,
            "subsystem_totals": subsystem_totals,
            "recent_errors": recent_errors,
        }
    finally:
        if db_session is None:
            db.close()
