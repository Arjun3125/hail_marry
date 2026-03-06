"""AIaaS backend FastAPI application entry point."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
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
from routes import audio as audio_routes
from routes import video as video_routes
from routes import discovery as discovery_routes
from routes import demo_management as demo_mgmt_routes


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="AI Infrastructure for Educational Institutions",
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
)

_demo_origins = ["http://localhost:3000", "http://localhost:3001", "http://localhost:3002", "http://127.0.0.1:3000", "http://127.0.0.1:3001"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_demo_origins if settings.app.demo_mode else settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Order matters: last added executes first.
if not settings.app.demo_mode:
    app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantMiddleware)
if not settings.app.demo_mode:
    app.add_middleware(CSRFMiddleware, allowed_origins=settings.app.cors_origins)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app.version}


app.include_router(auth_routes.router)
app.include_router(demo_routes.router)
app.include_router(student_routes.router)
app.include_router(parent_routes.router)
app.include_router(teacher_routes.router)
app.include_router(admin_routes.router)
app.include_router(ai_routes.router)
app.include_router(audio_routes.router)
app.include_router(video_routes.router)
app.include_router(discovery_routes.router)
app.include_router(demo_mgmt_routes.router)


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
