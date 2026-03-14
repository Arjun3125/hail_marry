"""Deployment guidance helpers to reduce configuration complexity."""
from __future__ import annotations

import os
from typing import Any


HOSTED_PRODUCTION_REQUIRED = [
    "DATABASE_URL",
    "REDIS_URL",
    "JWT_SECRET",
    "AI_SERVICE_URL",
]

HOSTED_PRODUCTION_OPTIONAL = [
    "AI_SERVICE_URLS",
    "AI_SERVICE_KEY",
    "OLLAMA_BASE_URL",
    "OLLAMA_BASE_URLS",
    "SENTRY_DSN",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "QDRANT_URL",
    "GRAFANA_URL",
    "SLACK_WEBHOOK_URL",
]


def _status_for_var(name: str) -> dict[str, Any]:
    value = os.getenv(name)
    is_set = bool(value and value.strip())
    return {
        "name": name,
        "configured": is_set,
        "value_preview": "***set***" if is_set else None,
    }


def build_hosted_production_guidance() -> dict[str, Any]:
    required = [_status_for_var(name) for name in HOSTED_PRODUCTION_REQUIRED]
    optional = [_status_for_var(name) for name in HOSTED_PRODUCTION_OPTIONAL]

    missing_required = [item["name"] for item in required if not item["configured"]]

    return {
        "profile": "hosted_production",
        "summary": {
            "required_total": len(required),
            "required_configured": sum(1 for item in required if item["configured"]),
            "optional_total": len(optional),
            "optional_configured": sum(1 for item in optional if item["configured"]),
            "ready": len(missing_required) == 0,
            "missing_required": missing_required,
        },
        "required": required,
        "optional": optional,
        "notes": [
            "Set required keys first to get a runnable hosted baseline.",
            "Optional keys unlock reliability, observability, and advanced integrations.",
            "Prefer AI_SERVICE_URLS + OLLAMA_BASE_URLS for multi-node resilience.",
        ],
    }
