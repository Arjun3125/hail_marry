"""Health and metrics app for the AI worker process."""
from __future__ import annotations

from fastapi import FastAPI, HTTPException
from starlette.responses import PlainTextResponse

from config import settings
from src.domains.platform.services.metrics_registry import export_prometheus_text
from src.domains.platform.services.worker_runtime import snapshot_worker_state

app = FastAPI(title="VidyaOS Worker Health", version=settings.app.version)


def _worker_metrics_text() -> str:
    state = snapshot_worker_state()
    lines = [
        "# HELP vidyaos_worker_up Worker process health status",
        "# TYPE vidyaos_worker_up gauge",
        f"vidyaos_worker_up {1 if not state.get('heartbeat_stale') else 0}",
        "# HELP vidyaos_worker_ready Worker readiness based on dependencies and heartbeat freshness",
        "# TYPE vidyaos_worker_ready gauge",
        f"vidyaos_worker_ready {1 if state.get('ready') else 0}",
        "# HELP vidyaos_worker_jobs_processed_total Total successfully processed jobs",
        "# TYPE vidyaos_worker_jobs_processed_total counter",
        f"vidyaos_worker_jobs_processed_total {state.get('jobs_processed_total', 0)}",
        "# HELP vidyaos_worker_jobs_failed_total Total failed jobs seen by the worker",
        "# TYPE vidyaos_worker_jobs_failed_total counter",
        f"vidyaos_worker_jobs_failed_total {state.get('jobs_failed_total', 0)}",
    ]
    return "\n".join(lines) + "\n"


@app.get("/health")
async def worker_health():
    state = snapshot_worker_state()
    return {
        "status": "healthy" if not state.get("heartbeat_stale") else "degraded",
        "worker": state,
    }


@app.get("/ready")
async def worker_ready():
    state = snapshot_worker_state()
    if not state.get("ready"):
        raise HTTPException(status_code=503, detail=state)
    return {"ready": True, "worker": state}


@app.get("/metrics", response_class=PlainTextResponse)
async def worker_metrics():
    return export_prometheus_text() + _worker_metrics_text()
