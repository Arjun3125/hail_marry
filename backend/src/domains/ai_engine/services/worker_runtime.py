"""Shared worker runtime state for health/readiness and metrics exposure."""
from __future__ import annotations

import threading
from datetime import datetime, timezone
from typing import Any

from config import settings

_lock = threading.Lock()
_state: dict[str, Any] = {
    "status": "starting",
    "worker_id": None,
    "started_at": None,
    "last_heartbeat": None,
    "last_job_id": None,
    "last_success_at": None,
    "last_error": None,
    "jobs_processed_total": 0,
    "jobs_failed_total": 0,
    "dependency_status": {},
}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def mark_worker_started(worker_id: str, dependency_status: dict[str, Any]) -> None:
    with _lock:
        _state.update({
            "status": "idle",
            "worker_id": worker_id,
            "started_at": _now_iso(),
            "last_heartbeat": _now_iso(),
            "dependency_status": dependency_status,
        })


def mark_worker_heartbeat(status: str = "idle", job_id: str | None = None) -> None:
    with _lock:
        _state["status"] = status
        _state["last_heartbeat"] = _now_iso()
        if job_id:
            _state["last_job_id"] = job_id


def mark_worker_success(job_id: str) -> None:
    with _lock:
        _state["status"] = "idle"
        _state["last_heartbeat"] = _now_iso()
        _state["last_success_at"] = _now_iso()
        _state["last_job_id"] = job_id
        _state["jobs_processed_total"] += 1
        _state["last_error"] = None


def mark_worker_failure(job_id: str | None, error: str) -> None:
    with _lock:
        _state["status"] = "idle"
        _state["last_heartbeat"] = _now_iso()
        _state["last_job_id"] = job_id
        _state["jobs_failed_total"] += 1
        _state["last_error"] = error


def update_dependency_status(status: dict[str, Any]) -> None:
    with _lock:
        _state["dependency_status"] = status


def snapshot_worker_state() -> dict[str, Any]:
    with _lock:
        snapshot = dict(_state)

    last_heartbeat = snapshot.get("last_heartbeat")
    stale = False
    if last_heartbeat:
        heartbeat_dt = datetime.fromisoformat(last_heartbeat)
        stale = (datetime.now(timezone.utc) - heartbeat_dt).total_seconds() > settings.worker_health.heartbeat_stale_seconds
    snapshot["heartbeat_stale"] = stale
    snapshot["ready"] = bool(snapshot.get("dependency_status", {}).get("ready")) and not stale
    return snapshot
