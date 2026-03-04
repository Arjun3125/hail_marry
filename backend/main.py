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


app = FastAPI(
    title=settings.app.name,
    version=settings.app.version,
    description="AI Infrastructure for Educational Institutions",
    docs_url="/docs" if settings.app.debug else None,
    redoc_url="/redoc" if settings.app.debug else None,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.app.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Order matters: last added executes first.
app.add_middleware(RateLimitMiddleware)
app.add_middleware(TenantMiddleware)
app.add_middleware(CSRFMiddleware, allowed_origins=settings.app.cors_origins)


@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": settings.app.version}


app.include_router(auth_routes.router)
if settings.app.debug:
    app.include_router(demo_routes.router)
app.include_router(student_routes.router)
app.include_router(parent_routes.router)
app.include_router(teacher_routes.router)
app.include_router(admin_routes.router)
app.include_router(ai_routes.router)
app.include_router(audio_routes.router)
app.include_router(video_routes.router)
app.include_router(discovery_routes.router)
