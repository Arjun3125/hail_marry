
from fastapi import HTTPException

from src.domains.platform.models.audit import AuditLog
from src.domains.platform.services.metrics_registry import reset_metrics_registry
from src.domains.platform.services.traceability import build_traceability_summary, classify_error_key


def _install_traceability_test_routes(app):
    existing_paths = {route.path for route in app.routes}
    if "/api/student/traceability-ocr-test" not in existing_paths:
        @app.get("/api/student/traceability-ocr-test")
        async def _traceability_ocr_test():
            raise HTTPException(status_code=500, detail="OCR processing failed. Please upload a clearer, higher-contrast image or a PDF.")

    existing_paths = {route.path for route in app.routes}
    if "/api/ai/traceability-llm-test" not in existing_paths:
        @app.get("/api/ai/traceability-llm-test")
        async def _traceability_llm_test():
            raise RuntimeError("Ollama connect timed out")


def test_classify_error_key_maps_subsystems():
    assert classify_error_key(path="/api/whatsapp/webhook", status_code=503, detail="Meta webhook unavailable") == "whatsapp.webhook"
    assert classify_error_key(path="/api/student/tools", status_code=422, detail="Flowchart output must be a JSON object") == "flowchart.generation"
    assert classify_error_key(path="/api/student/tools", status_code=422, detail="Quiz output must be a JSON array") == "quiz.generation"
    assert classify_error_key(path="/api/ai/query", status_code=503, detail="Cannot connect to AI runtime (Ollama).") == "llm.generation"


def test_http_exception_response_contains_error_code(client):
    _install_traceability_test_routes(client.app)
    reset_metrics_registry()

    response = client.get("/api/student/traceability-ocr-test")

    assert response.status_code == 500
    payload = response.json()
    assert payload["error_code"] == "OCR-READ-002"
    assert payload["subsystem"] == "ocr"
    assert "OCR processing failed" in payload["detail"]
    assert response.headers["X-Error-Code"] == "OCR-READ-002"
    assert response.headers["X-Trace-Id"]


def test_unhandled_ai_exception_response_contains_error_code(client):
    from fastapi.testclient import TestClient

    _install_traceability_test_routes(client.app)
    reset_metrics_registry()

    with TestClient(client.app, raise_server_exceptions=False) as test_client:
        response = test_client.get("/api/ai/traceability-llm-test")

    assert response.status_code == 502
    payload = response.json()
    assert payload["error_code"] == "LLM-GEN-004"
    assert payload["subsystem"] == "llm"
    assert payload["detail"] == "AI generation failed."
    assert response.headers["X-Error-Code"] == "LLM-GEN-004"


def test_build_traceability_summary_aggregates_errors(db_session, active_tenant):
    first_code = "OCR-READ-002"
    second_code = "LLM-GEN-004"
    for index, code in enumerate([first_code, first_code, second_code], start=1):
        db_session.add(
            AuditLog(
                tenant_id=active_tenant.id,
                user_id=None,
                action="trace.error",
                entity_type="trace_error",
                entity_id=None,
                metadata_={
                    "trace_id": f"trace-{index}",
                    "error_code": code,
                    "subsystem": "ocr" if code == first_code else "llm",
                    "severity": "warning" if code == first_code else "critical",
                    "title": code,
                    "detail": "failure",
                    "path": "/api/test",
                    "method": "GET",
                    "status_code": 500,
                },
            )
        )
    db_session.commit()

    summary = build_traceability_summary(tenant_id=active_tenant.id, days=7, db_session=db_session)

    assert summary["total_errors"] == 3
    assert summary["grouped_errors"][0]["error_code"] == first_code
    assert summary["grouped_errors"][0]["count"] == 2
    assert any(item["subsystem"] == "llm" for item in summary["subsystem_totals"])
    assert len(summary["recent_errors"]) == 3
