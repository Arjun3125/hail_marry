"""VidyaOS backend FastAPI application entry point."""
import os
import subprocess
import sys
import asyncio
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from contextlib import asynccontextmanager

# ==============================================================================
# 1. NORMAL APPLICATION IMPORTS
# ==============================================================================
from config import settings
from database import engine
from middleware.observability import ObservabilityMiddleware
from middleware.tenant import TenantMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.csrf import CSRFMiddleware
from middleware.captcha import CaptchaMiddleware
from routes import auth as auth_routes
from routes import demo as demo_routes
from routes import students as student_routes
from routes import parent as parent_routes
from routes import teacher as teacher_routes
from routes import admin as admin_routes
from routes import ai as ai_routes
from routes import ai_jobs as ai_job_routes
from routes import audio as audio_routes
from routes import video as video_routes
from routes import discovery as discovery_routes
from routes import documents as document_routes
from routes import demo_management as demo_mgmt_routes
from routes import enterprise as enterprise_routes
from routes import superadmin as superadmin_routes
from routes import billing as billing_routes
from routes import i18n as i18n_routes
from routes import onboarding as onboarding_routes
from routes import admission as admission_routes
from routes import fees as fee_routes
from routes import openai_compat as openai_compat_routes
from routes import support as support_routes
from services.alerting import get_active_alerts
from services.metrics_registry import export_prometheus_text
from services.startup_checks import collect_dependency_status, enforce_startup_dependencies
from services.structured_logging import configure_structured_logging
from services.sentry_config import configure_sentry
from services.telemetry import configure_telemetry, instrument_sqlalchemy_engine
from services.runtime_scheduler import run_doc_watch_loop, run_digest_loop

configure_structured_logging(service_name="vidyaos-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("TESTING"):
        enforce_startup_dependencies("api")
    stop_event = asyncio.Event()
    tasks: list[asyncio.Task] = []
    if not os.environ.get("TESTING"):
        if settings.doc_watch.enabled:
            tasks.append(asyncio.create_task(run_doc_watch_loop(stop_event)))
        if settings.digest_email.enabled:
            tasks.append(asyncio.create_task(run_digest_loop(stop_event)))
    yield
    stop_event.set()
    for task in tasks:
        task.cancel()
    if tasks:
        await asyncio.gather(*tasks, return_exceptions=True)

app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="AI Infrastructure for Educational Institutions",
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
    lifespan=lifespan,
)
configure_telemetry(service_name="vidyaos-api", app=app)
instrument_sqlalchemy_engine(engine)

_demo_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
]
_allowed_origins = settings.app.cors_origins + (_demo_origins if settings.app.demo_mode else [])
_allowed_origins = list(dict.fromkeys(_allowed_origins))
_vercel_origin_regex = r"^https://.*\.vercel\.app$" if settings.app.debug else None

# Order matters: last added executes first.
if not settings.app.demo_mode or os.environ.get("TESTING") == "true":
    app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantMiddleware)
if not settings.app.demo_mode or os.environ.get("TESTING") == "true":
    app.add_middleware(CSRFMiddleware, allowed_origins=_allowed_origins)
if not settings.app.demo_mode or os.environ.get("TESTING") == "true":
    app.add_middleware(CaptchaMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=_vercel_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ObservabilityMiddleware, service_name="vidyaos-api")
configure_sentry(service_name="vidyaos-api", app=app)


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

    alerts = []
    return export_prometheus_text(alerts=alerts)


app.include_router(auth_routes.router)
app.include_router(demo_routes.router)
app.include_router(student_routes.router)
app.include_router(parent_routes.router)
app.include_router(teacher_routes.router)
app.include_router(admin_routes.router)
app.include_router(ai_routes.router)
app.include_router(ai_job_routes.router)
app.include_router(audio_routes.router)
app.include_router(video_routes.router)
app.include_router(discovery_routes.router)
app.include_router(document_routes.router)
app.include_router(demo_mgmt_routes.router)
app.include_router(enterprise_routes.router)
app.include_router(superadmin_routes.router)
app.include_router(billing_routes.router)
app.include_router(i18n_routes.router)
app.include_router(onboarding_routes.router)
app.include_router(admission_routes.router)
app.include_router(fee_routes.router)
app.include_router(openai_compat_routes.router)
app.include_router(support_routes.router)

from routes import library as library_routes
from routes import invitations as invitation_routes
app.include_router(library_routes.router)
app.include_router(invitation_routes.router)

# ── Enhancement: Real-time notifications ──
from routes import notifications as notification_routes
app.include_router(notification_routes.router)


# ── Auto-seed in DEMO_MODE ──
if settings.app.demo_mode:
    import models  # noqa — register all models so create_all creates all tables
    from database import Base, engine
    Base.metadata.create_all(bind=engine)
    try:
        from database import SessionLocal
        _db = SessionLocal()
        from models.user import User
        if _db.query(User).count() == 0:
            from demo_seed import seed_demo_data
            seed_demo_data(_db)
        _db.close()
    except Exception as e:
        print(f"⚠️ Demo seed check: {e}")
