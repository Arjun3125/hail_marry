"""OpenTelemetry configuration and helpers with graceful fallback if packages are unavailable."""
from __future__ import annotations

import logging
from typing import Any

from config import settings

logger = logging.getLogger("telemetry")

_TELEMETRY_CONFIGURED = False
_HTTPX_INSTRUMENTED = False
_SQLALCHEMY_INSTRUMENTED_ENGINES: set[int] = set()


def _load_otel():
    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.propagate import get_global_textmap
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.sdk.trace.sampling import TraceIdRatioBased
        return {
            "trace": trace,
            "OTLPSpanExporter": OTLPSpanExporter,
            "FastAPIInstrumentor": FastAPIInstrumentor,
            "HTTPXClientInstrumentor": HTTPXClientInstrumentor,
            "SQLAlchemyInstrumentor": SQLAlchemyInstrumentor,
            "get_global_textmap": get_global_textmap,
            "Resource": Resource,
            "TracerProvider": TracerProvider,
            "BatchSpanProcessor": BatchSpanProcessor,
            "TraceIdRatioBased": TraceIdRatioBased,
        }
    except Exception as exc:
        logger.warning("OpenTelemetry packages unavailable: %s", exc)
        return None


def configure_telemetry(service_name: str, app: Any | None = None) -> None:
    global _TELEMETRY_CONFIGURED, _HTTPX_INSTRUMENTED

    if not settings.observability.enabled or not settings.observability.tracing_enabled:
        return

    otel = _load_otel()
    if not otel:
        return

    trace = otel["trace"]
    if not _TELEMETRY_CONFIGURED:
        resource = otel["Resource"].create({
            "service.name": service_name,
            "service.version": settings.app.version,
        })
        provider = otel["TracerProvider"](
            resource=resource,
            sampler=otel["TraceIdRatioBased"](settings.observability.trace_sample_ratio),
        )
        if settings.observability.otlp_endpoint:
            exporter = otel["OTLPSpanExporter"](
                endpoint=settings.observability.otlp_endpoint,
            )
            provider.add_span_processor(otel["BatchSpanProcessor"](exporter))
        trace.set_tracer_provider(provider)
        _TELEMETRY_CONFIGURED = True

    if app is not None:
        otel["FastAPIInstrumentor"].instrument_app(app)

    if not _HTTPX_INSTRUMENTED:
        otel["HTTPXClientInstrumentor"].instrument()
        _HTTPX_INSTRUMENTED = True


def instrument_sqlalchemy_engine(engine: Any) -> None:
    if not settings.observability.enabled or not settings.observability.tracing_enabled:
        return

    otel = _load_otel()
    if not otel:
        return

    engine_id = id(engine)
    if engine_id in _SQLALCHEMY_INSTRUMENTED_ENGINES:
        return

    otel["SQLAlchemyInstrumentor"].instrument(engine=engine)
    _SQLALCHEMY_INSTRUMENTED_ENGINES.add(engine_id)


def get_current_traceparent() -> str | None:
    otel = _load_otel()
    if not otel:
        return None

    carrier: dict[str, str] = {}
    otel["get_global_textmap"]().inject(carrier)
    return carrier.get("traceparent")


def extract_context_from_traceparent(traceparent: str | None):
    otel = _load_otel()
    if not otel or not traceparent:
        return None
    return otel["get_global_textmap"]().extract({"traceparent": traceparent})


def get_tracer(name: str):
    otel = _load_otel()
    if not otel:
        return None
    return otel["trace"].get_tracer(name)
