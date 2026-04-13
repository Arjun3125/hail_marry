"""FastAPI app factory extracted from the legacy monolithic entrypoint."""
from __future__ import annotations

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.responses import PlainTextResponse

from middleware.captcha import CaptchaMiddleware
from middleware.csrf import CSRFMiddleware
from middleware.observability import ObservabilityMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.tenant import TenantMiddleware
from src.bootstrap.container import build_runtime_container
from src.bootstrap.logging import configure_application_logging
from src.bootstrap.settings import (
    get_allowed_origins,
    get_vercel_origin_regex,
    should_enforce_security_middleware,
)
from src.bootstrap.startup import create_lifespan, initialize_demo_mode
from src.domains.platform.services.metrics_registry import export_prometheus_text
from src.domains.platform.services.sentry_config import configure_sentry
from src.domains.platform.services.startup_checks import collect_dependency_status
from src.domains.platform.services.telemetry import configure_telemetry, instrument_sqlalchemy_engine
from src.domains.platform.services.traceability import (
    TraceabilityError,
    build_http_error_response,
    build_unhandled_error_response,
    get_error_descriptor,
)
from src.interfaces.http.academic.router import router as academic_router
from src.interfaces.http.administrative.router import router as administrative_router
from src.interfaces.http.ai.router import router as ai_engine_router
from src.interfaces.http.demo.router import router as demo_router
from src.interfaces.http.identity.router import router as identity_router
from src.interfaces.http.platform.router import router as platform_router
from src.interfaces.whatsapp.router import router as whatsapp_router
from database import get_db


def get_db_session():
    yield from get_db()


from src.domains.mascot.routes.mascot_routes import router as mascot_router


def create_app() -> FastAPI:
    configure_application_logging(service_name="vidyaos-api")
    container = build_runtime_container()
    settings = container.settings
    app = FastAPI(
        title=settings.app.name,
        version=settings.app.version,
        description="AI Infrastructure for Educational Institutions",
        docs_url="/docs" if settings.app.debug else None,
        redoc_url="/redoc" if settings.app.debug else None,
        lifespan=create_lifespan(container),
    )
    configure_telemetry(service_name="vidyaos-api", app=app)
    instrument_sqlalchemy_engine(container.engine)
    _register_middleware(app)
    _register_exception_handlers(app)
    _register_system_routes(app)
    _register_routers(app)
    configure_sentry(service_name="vidyaos-api", app=app)
    initialize_demo_mode(container)
    return app


def _register_middleware(app: FastAPI) -> None:
    allowed_origins = get_allowed_origins()
    vercel_origin_regex = get_vercel_origin_regex()

    if should_enforce_security_middleware():
        app.add_middleware(RateLimitMiddleware)
    app.add_middleware(TenantMiddleware)
    if should_enforce_security_middleware():
        app.add_middleware(CSRFMiddleware, allowed_origins=allowed_origins)
    if should_enforce_security_middleware():
        app.add_middleware(CaptchaMiddleware)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allowed_origins,
        allow_origin_regex=vercel_origin_regex,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(ObservabilityMiddleware, service_name="vidyaos-api")


def _register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(TraceabilityError)
    async def traceability_exception_handler(request: Request, exc: TraceabilityError):
        descriptor = get_error_descriptor(exc.key)
        http_exc = HTTPException(
            status_code=exc.status_code or descriptor.default_status_code,
            detail=exc.detail or descriptor.default_message,
        )
        payload, status_code, headers = build_http_error_response(
            request,
            http_exc,
            override_key=exc.key,
        )
        return JSONResponse(status_code=status_code, content=payload, headers=headers)

    @app.exception_handler(HTTPException)
    async def http_exception_handler(request: Request, exc: HTTPException):
        payload, status_code, headers = build_http_error_response(request, exc)
        return JSONResponse(status_code=status_code, content=payload, headers=headers)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(request: Request, exc: Exception):
        payload, status_code, headers = build_unhandled_error_response(request, exc)
        return JSONResponse(status_code=status_code, content=payload, headers=headers)


def _register_system_routes(app: FastAPI) -> None:
    from config import settings

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "version": settings.app.version}

    @app.get("/ready")
    async def readiness_check():
        status = collect_dependency_status("api")
        if not status["ready"]:
            raise HTTPException(status_code=503, detail=status)
        return status

    @app.get("/metrics", response_class=PlainTextResponse)
    async def metrics_export(x_metrics_token: str | None = Header(default=None)):
        expected = settings.observability.metrics_token.strip()
        if expected and x_metrics_token != expected:
            raise HTTPException(status_code=401, detail="Unauthorized metrics request.")
        return export_prometheus_text(alerts=[])


def _register_routers(app: FastAPI) -> None:
    app.include_router(identity_router)
    app.include_router(academic_router)
    app.include_router(administrative_router)
    app.include_router(ai_engine_router)
    app.include_router(platform_router)
    app.include_router(demo_router)
    app.include_router(whatsapp_router)
    app.include_router(mascot_router, prefix="/api/mascot", tags=["mascot"])
