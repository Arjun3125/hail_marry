import uuid

from auth.dependencies import get_current_user


def _make_user(*, role: str = "admin"):
    return type(
        "TestUser",
        (),
        {
            "id": uuid.uuid4(),
            "tenant_id": uuid.uuid4(),
            "role": role,
            "is_active": True,
        },
    )()


def test_fee_routes_reject_malformed_identifiers_with_400(client, monkeypatch):
    import src.domains.administrative.routes.fees as fee_routes

    client.app.dependency_overrides[get_current_user] = lambda: _make_user(role="admin")
    monkeypatch.setattr(
        fee_routes,
        "create_fee_structure",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("service should not run")),
    )
    monkeypatch.setattr(
        fee_routes,
        "generate_invoices",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("service should not run")),
    )
    monkeypatch.setattr(
        fee_routes,
        "list_invoices",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("service should not run")),
    )
    monkeypatch.setattr(
        fee_routes,
        "record_payment",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("service should not run")),
    )
    monkeypatch.setattr(
        fee_routes,
        "get_student_ledger",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("service should not run")),
    )

    try:
        create_structure_response = client.post(
            "/api/fees/structures",
            json={
                "fee_type": "tuition",
                "amount": 5000,
                "frequency": "monthly",
                "class_id": "not-a-uuid",
            },
        )
        assert create_structure_response.status_code == 400
        assert create_structure_response.json()["detail"] == "Invalid class_id"

        generate_invoices_response = client.post(
            "/api/fees/generate-invoices",
            json={"fee_structure_id": "not-a-uuid", "due_date": "2026-04-06T10:00:00"},
        )
        assert generate_invoices_response.status_code == 400
        assert generate_invoices_response.json()["detail"] == "Invalid fee_structure_id"

        invoice_list_response = client.get("/api/fees/invoices?student_id=not-a-uuid")
        assert invoice_list_response.status_code == 400
        assert invoice_list_response.json()["detail"] == "Invalid student_id"

        payment_response = client.post(
            "/api/fees/payments",
            json={
                "invoice_id": "not-a-uuid",
                "amount": 2500,
                "payment_method": "cash",
            },
        )
        assert payment_response.status_code == 400
        assert payment_response.json()["detail"] == "Invalid invoice_id"

        ledger_response = client.get("/api/fees/student/not-a-uuid/ledger")
        assert ledger_response.status_code == 400
        assert ledger_response.json()["detail"] == "Invalid student_id"
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_personalization_student_endpoints_reject_non_student_roles(client):
    client.app.dependency_overrides[get_current_user] = lambda: _make_user(role="admin")

    try:
        recommendations_response = client.get("/api/personalization/recommendations")
        assert recommendations_response.status_code == 403
        assert "not authorized" in recommendations_response.text.lower()

        profile_response = client.get("/api/personalization/profile")
        assert profile_response.status_code == 403

        remediation_response = client.get("/api/personalization/remediation")
        assert remediation_response.status_code == 403

        study_path_response = client.get("/api/personalization/study-path?topic=Photosynthesis")
        assert study_path_response.status_code == 403

        complete_step_response = client.post(
            "/api/personalization/study-path/demo-plan/steps/demo-step/complete"
        )
        assert complete_step_response.status_code == 403

        event_response = client.post(
            "/api/personalization/events",
            json={"event_type": "recommendation_click"},
        )
        assert event_response.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_ai_discovery_endpoints_reject_non_teacher_roles(client):
    client.app.dependency_overrides[get_current_user] = lambda: _make_user(role="student")

    try:
        discover_response = client.post(
            "/api/ai/discover-sources",
            json={"query": "quadratic equations"},
        )
        assert discover_response.status_code == 403
        assert "not authorized" in discover_response.text.lower()

        ingest_response = client.post(
            "/api/ai/ingest-url",
            json={"url": "https://example.com/lesson"},
        )
        assert ingest_response.status_code == 403
        assert "not authorized" in ingest_response.text.lower()
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_whatsapp_admin_endpoints_reject_non_admin_roles(client):
    client.app.dependency_overrides[get_current_user] = lambda: _make_user(role="teacher")

    try:
        send_response = client.post(
            "/api/whatsapp/send",
            json={"phone": "+919999999999", "message": "hello"},
        )
        assert send_response.status_code == 403
        assert "not authorized" in send_response.text.lower()

        sessions_response = client.get("/api/whatsapp/sessions")
        assert sessions_response.status_code == 403

        analytics_response = client.get("/api/whatsapp/analytics")
        assert analytics_response.status_code == 403

        tool_catalog_response = client.get("/api/whatsapp/tools/catalog")
        assert tool_catalog_response.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)


def test_mascot_admin_release_gate_endpoints_reject_non_admin_roles(client):
    client.app.dependency_overrides[get_current_user] = lambda: _make_user(role="teacher")

    try:
        snapshot_response = client.get("/api/mascot/release-gate-snapshot?days=7")
        assert snapshot_response.status_code == 403
        assert "not authorized" in snapshot_response.text.lower()

        evidence_response = client.get("/api/mascot/release-gate-evidence?days=7")
        assert evidence_response.status_code == 403

        packet_response = client.get("/api/mascot/staging-packet?days=7")
        assert packet_response.status_code == 403
    finally:
        client.app.dependency_overrides.pop(get_current_user, None)
