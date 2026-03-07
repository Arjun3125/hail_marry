"""VidyaOS backend FastAPI application entry point."""
import os
import subprocess
import sys
from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import PlainTextResponse
from contextlib import asynccontextmanager

# ==============================================================================
# 0. INDESTRUCTIBLE DATABASE MIGRATIONS
# Must run BEFORE any routes or models are imported to prevent schema caching errors
# ==============================================================================
try:
    if not os.environ.get("TESTING"):
        print("Running automatic database migrations...", flush=True)
        backend_dir = os.path.dirname(os.path.abspath(__file__))
        subprocess.run(
            [sys.executable, "-m", "alembic", "upgrade", "head"], 
            check=True,
            cwd=backend_dir
        )
except Exception as e:
    print(f"Failed to run database migrations: {e}", flush=True)
    # RAW SQL FALLBACK - Railway Proof
    try:
        from sqlalchemy import text
        from database import engine
        print("Running raw fallback migration for users.hashed_password...", flush=True)
        with engine.begin() as conn:
            conn.execute(text("ALTER TABLE users ADD COLUMN IF NOT EXISTS hashed_password VARCHAR(255);"))
    except Exception as raw_e:
        print(f"Fallback migration failed: {raw_e}", flush=True)

# ==============================================================================
# 1. NORMAL APPLICATION IMPORTS
# ==============================================================================
from config import settings
from database import engine
from middleware.observability import ObservabilityMiddleware
from middleware.tenant import TenantMiddleware
from middleware.rate_limit import RateLimitMiddleware
from middleware.csrf import CSRFMiddleware
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
from routes import demo_management as demo_mgmt_routes
from routes import enterprise as enterprise_routes
from routes import superadmin as superadmin_routes
from services.alerting import get_active_alerts
from services.metrics_registry import export_prometheus_text
from services.startup_checks import collect_dependency_status, enforce_startup_dependencies
from services.structured_logging import configure_structured_logging
from services.telemetry import configure_telemetry, instrument_sqlalchemy_engine

configure_structured_logging(service_name="vidyaos-api")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not os.environ.get("TESTING"):
        enforce_startup_dependencies("api")
    yield

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
app.add_middleware(
    CORSMiddleware,
    allow_origins=_allowed_origins,
    allow_origin_regex=_vercel_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(ObservabilityMiddleware, service_name="vidyaos-api")


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
app.include_router(demo_mgmt_routes.router)
app.include_router(enterprise_routes.router)
app.include_router(superadmin_routes.router)


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
