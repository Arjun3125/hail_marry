"""Observability middleware for structured logs, request traces, and metrics."""
from __future__ import annotations

import logging
import time
import uuid

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request

from services.metrics_registry import observe_http_request
from services.trace_backend import record_trace_event

logger = logging.getLogger("observability")


class ObservabilityMiddleware(BaseHTTPMiddleware):
    def __init__(self, app, service_name: str):
        super().__init__(app)
        self.service_name = service_name

    @staticmethod
    def _should_trace(path: str) -> bool:
        return path.startswith("/api/ai") or path.startswith("/api/admin/ai-jobs") or path.startswith("/internal/ai")

    async def dispatch(self, request: Request, call_next):
        trace_id = request.headers.get("X-Trace-Id") or uuid.uuid4().hex[:16]
        request.state.trace_id = trace_id
        start = time.perf_counter()

        if self._should_trace(request.url.path):
            record_trace_event(
                trace_id=trace_id,
                tenant_id=getattr(request.state, "tenant_id", None),
                user_id=getattr(request.state, "user_id", None),
                source=self.service_name,
                stage="request.started",
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                },
            )

        try:
            response = await call_next(request)
            status_code = response.status_code
            return response
        except Exception:
            duration_ms = round((time.perf_counter() - start) * 1000, 2)
            observe_http_request(self.service_name, request.method, request.url.path, 500, duration_ms)
            logger.exception(
                "request_failed",
                extra={
                    "event": "request.failed",
                    "trace_id": trace_id,
                    "path": request.url.path,
                    "method": request.method,
                    "duration_ms": duration_ms,
                    "tenant_id": getattr(request.state, "tenant_id", None),
                    "user_id": getattr(request.state, "user_id", None),
                    "status_code": 500,
                },
            )
            if self._should_trace(request.url.path):
                record_trace_event(
                    trace_id=trace_id,
                    tenant_id=getattr(request.state, "tenant_id", None),
                    user_id=getattr(request.state, "user_id", None),
                    source=self.service_name,
                    stage="request.failed",
                    status="error",
                    detail="Unhandled exception",
                    metadata={"path": request.url.path, "method": request.method, "duration_ms": duration_ms},
                )
            raise

        duration_ms = round((time.perf_counter() - start) * 1000, 2)
        response.headers["X-Trace-Id"] = trace_id
        observe_http_request(self.service_name, request.method, request.url.path, status_code, duration_ms)
        logger.info(
            "request_completed",
            extra={
                "event": "request.completed",
                "trace_id": trace_id,
                "path": request.url.path,
                "method": request.method,
                "duration_ms": duration_ms,
                "tenant_id": getattr(request.state, "tenant_id", None),
                "user_id": getattr(request.state, "user_id", None),
                "status_code": status_code,
            },
        )
        if self._should_trace(request.url.path):
            record_trace_event(
                trace_id=trace_id,
                tenant_id=getattr(request.state, "tenant_id", None),
                user_id=getattr(request.state, "user_id", None),
                source=self.service_name,
                stage="request.completed",
                status="ok" if status_code < 400 else "error",
                metadata={
                    "path": request.url.path,
                    "method": request.method,
                    "status_code": status_code,
                    "duration_ms": duration_ms,
                },
            )
        return response
