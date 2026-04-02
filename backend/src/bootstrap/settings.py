"""Bootstrap helpers for environment-aware runtime settings."""
from __future__ import annotations

import os

from config import settings

DEMO_ORIGINS = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://localhost:3002",
    "http://localhost:3006",
    "http://localhost:3008",
    "http://localhost:4000",
    "http://localhost:4005",
    "http://localhost:7125",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:3001",
    "http://127.0.0.1:3006",
    "http://127.0.0.1:3008",
    "http://127.0.0.1:4000",
    "http://127.0.0.1:4005",
    "http://127.0.0.1:7125",
    "http://127.0.0.1:8080",
]


def should_enforce_security_middleware() -> bool:
    return not settings.app.demo_mode or os.environ.get("TESTING") == "true"


def get_allowed_origins() -> list[str]:
    origins = settings.app.cors_origins + (DEMO_ORIGINS if settings.app.demo_mode else [])
    return list(dict.fromkeys(origins))


def get_vercel_origin_regex() -> str | None:
    return r"^https://.*\.vercel\.app$" if settings.app.debug else None

