from __future__ import annotations

from fastapi.testclient import TestClient

from src.domains.platform.services import startup_checks
from src.domains.platform.services.worker_runtime import mark_worker_heartbeat, mark_worker_started, update_dependency_status
from worker_health_app import app as worker_health_app


def test_collect_dependency_status_shapes_response(monkeypatch):
    monkeypatch.setattr(
        startup_checks,
        "_service_checks",
        lambda service_name: {
            "database": (True, "ok"),
            "redis": (False, "unavailable"),
        },
    )

    status = startup_checks.collect_dependency_status("api")

    assert status["service"] == "api"
    assert status["ready"] is False
    assert status["checks"]["database"] == {"ok": True, "detail": "ok"}
    assert status["checks"]["redis"] == {"ok": False, "detail": "unavailable"}


def test_enforce_startup_dependencies_raises_when_strict(monkeypatch):
    monkeypatch.setattr(
        startup_checks,
        "_service_checks",
        lambda service_name: {"database": (False, "down")},
    )
    original_enabled = startup_checks.settings.startup_checks.enabled
    original_strict = startup_checks.settings.startup_checks.strict
    startup_checks.settings.startup_checks.enabled = True
    startup_checks.settings.startup_checks.strict = True

    try:
        try:
            startup_checks.enforce_startup_dependencies("worker")
            assert False, "expected RuntimeError"
        except RuntimeError as exc:
            assert "worker" in str(exc)
    finally:
        startup_checks.settings.startup_checks.enabled = original_enabled
        startup_checks.settings.startup_checks.strict = original_strict


def test_worker_health_endpoints_surface_readiness():
    mark_worker_started("test-worker", {"ready": True, "checks": {}})
    mark_worker_heartbeat(status="idle")
    update_dependency_status({"ready": True, "checks": {}})

    with TestClient(worker_health_app) as client:
        health = client.get("/health")
        ready = client.get("/ready")

    assert health.status_code == 200
    assert health.json()["worker"]["ready"] is True
    assert ready.status_code == 200
    assert ready.json()["ready"] is True


def test_worker_ready_returns_503_when_dependencies_fail():
    mark_worker_started("test-worker", {"ready": False, "checks": {"redis": {"ok": False}}})
    update_dependency_status({"ready": False, "checks": {"redis": {"ok": False}}})

    with TestClient(worker_health_app) as client:
        response = client.get("/ready")

    assert response.status_code == 503
    assert response.json()["detail"]["ready"] is False
