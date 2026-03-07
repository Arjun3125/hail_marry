import os
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from uuid import UUID
from unittest.mock import AsyncMock, patch

from fastapi import FastAPI
from fastapi.testclient import TestClient


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from routes import auth as auth_routes  # noqa: E402
from routes import enterprise as enterprise_routes  # noqa: E402


class _QueryStub:
    def __init__(self, value):
        self.value = value

    def filter(self, *args, **kwargs):
        return self

    def order_by(self, *args, **kwargs):
        return self

    def first(self):
        if isinstance(self.value, list):
            return self.value[0] if self.value else None
        return self.value

    def all(self):
        if isinstance(self.value, list):
            return self.value
        return [self.value] if self.value is not None else []


class _DBStub:
    def __init__(self, tenant):
        self.tenant = tenant

    def query(self, model):
        name = getattr(model, "__name__", str(model))
        if name == "Tenant":
            return _QueryStub(self.tenant)
        if name == "DeletionRequest":
            return _QueryStub([])
        return _QueryStub([])

    def commit(self):
        return None


def _build_client():
    app = FastAPI()
    app.include_router(enterprise_routes.router)
    app.include_router(auth_routes.router)

    fake_user = SimpleNamespace(
        id=UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"),
        tenant_id=UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"),
        role="admin",
        full_name="Admin User",
    )
    tenant = SimpleNamespace(
        id=fake_user.tenant_id,
        domain="school.example",
        saml_enabled=True,
        saml_entity_id="sp-entity",
        saml_metadata_url="https://idp.example/metadata",
        saml_idp_entity_id="idp-entity",
        saml_idp_sso_url="https://idp.example/sso",
        saml_idp_slo_url="https://idp.example/slo",
        saml_attribute_email="email",
        saml_attribute_name="full_name",
        data_retention_days=365,
        export_retention_days=30,
    )

    async def override_current_user():
        return fake_user

    def override_db():
        yield _DBStub(tenant)

    for route in app.routes:
        if getattr(route, "path", "").startswith("/api/admin/enterprise"):
            for dependency in route.dependant.dependencies:
                if getattr(dependency.call, "__name__", "") == "role_checker":
                    app.dependency_overrides[dependency.call] = override_current_user

    app.dependency_overrides[enterprise_routes.get_db] = override_db
    app.dependency_overrides[auth_routes.get_db] = override_db
    return TestClient(app), fake_user, tenant


class EnterpriseRouteTests(unittest.TestCase):
    def test_sso_settings_and_metadata_routes(self):
        client, _, tenant = _build_client()

        with (
            patch.object(enterprise_routes, "import_tenant_saml_metadata", AsyncMock(return_value={"entity_id": "idp-entity"})),
            patch.object(auth_routes, "get_tenant_for_saml", return_value=tenant),
            patch.object(auth_routes, "build_service_provider_metadata", return_value="<xml/>"),
        ):
            get_response = client.get("/api/admin/enterprise/sso")
            update_response = client.patch("/api/admin/enterprise/sso", json={"enabled": True, "attribute_email": "mail"})
            import_response = client.post("/api/admin/enterprise/sso/import-metadata", json={"metadata_xml": "<xml/>"})
            metadata_response = client.get("/api/auth/saml/school.example/metadata")

        self.assertEqual(get_response.status_code, 200)
        self.assertEqual(get_response.json()["idp_sso_url"], "https://idp.example/sso")
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(import_response.status_code, 200)
        self.assertEqual(import_response.json()["entity_id"], "idp-entity")
        self.assertEqual(metadata_response.status_code, 200)
        self.assertEqual(metadata_response.text, "<xml/>")

    def test_vector_backend_and_compliance_routes(self):
        client, current_user, _ = _build_client()
        export = SimpleNamespace(
            id=UUID("11111111-1111-1111-1111-111111111111"),
            tenant_id=current_user.tenant_id,
            requested_by=current_user.id,
            export_type="tenant_bundle",
            scope_type="tenant",
            scope_user_id=None,
            format="zip",
            status="completed",
            file_path="C:/tmp/export.zip",
            file_size=128,
            checksum="abc",
            metadata_={"counts": {"users": 1}},
            created_at="2026-03-06T00:00:00+00:00",
            completed_at="2026-03-06T00:01:00+00:00",
        )
        deletion_request = SimpleNamespace(
            id=UUID("22222222-2222-2222-2222-222222222222"),
            tenant_id=current_user.tenant_id,
            requested_by=current_user.id,
            target_user_id=None,
            status="requested",
            reason="GDPR export",
            resolution_note=None,
            metadata_=None,
            created_at="2026-03-06T00:00:00+00:00",
            resolved_at=None,
        )

        with (
            patch.object(enterprise_routes, "create_compliance_export", return_value=export),
            patch.object(enterprise_routes, "list_compliance_exports", return_value=[export]),
            patch.object(enterprise_routes, "create_deletion_request", return_value=deletion_request),
            patch.object(enterprise_routes, "resolve_deletion_request", return_value=deletion_request),
        ):
            vector_response = client.get("/api/admin/enterprise/vector-backend")
            create_export_response = client.post("/api/admin/enterprise/compliance/exports", json={"scope_type": "tenant"})
            list_export_response = client.get("/api/admin/enterprise/compliance/exports")
            create_deletion_response = client.post("/api/admin/enterprise/compliance/deletion-requests", json={"reason": "GDPR export"})
            resolve_deletion_response = client.post(
                "/api/admin/enterprise/compliance/deletion-requests/22222222-2222-2222-2222-222222222222/resolve",
                json={"note": "Processed"},
            )

        self.assertEqual(vector_response.status_code, 200)
        self.assertIn("provider", vector_response.json())
        self.assertEqual(create_export_response.status_code, 200)
        self.assertEqual(create_export_response.json()["status"], "completed")
        self.assertEqual(list_export_response.status_code, 200)
        self.assertEqual(list_export_response.json()[0]["checksum"], "abc")
        self.assertEqual(create_deletion_response.status_code, 200)
        self.assertEqual(resolve_deletion_response.status_code, 200)

    def test_incident_routes(self):
        client, current_user, _ = _build_client()
        incident = SimpleNamespace(
            id=UUID("33333333-3333-3333-3333-333333333333"),
            alert_code="queue_depth_high",
            severity="warning",
            status="open",
            title="Queue Depth High",
            summary="Queue depth warning",
            trace_id="trace-123",
            created_at="2026-03-06T00:00:00+00:00",
            updated_at="2026-03-06T00:01:00+00:00",
            acknowledged_at=None,
            resolved_at=None,
            source_payload={"message": "Queue depth warning"},
        )
        event = SimpleNamespace(
            id=UUID("44444444-4444-4444-4444-444444444444"),
            incident_id=incident.id,
            actor_user_id=current_user.id,
            event_type="created",
            detail="Created",
            payload={},
            created_at="2026-03-06T00:00:00+00:00",
        )
        route = SimpleNamespace(
            id=UUID("55555555-5555-5555-5555-555555555555"),
            name="Slack",
            channel_type="slack_webhook",
            target="https://hooks.slack.com/example",
            severity_filter="all",
            escalation_channel_type=None,
            escalation_target=None,
            escalation_after_minutes=30,
            is_active=True,
            created_at="2026-03-06T00:00:00+00:00",
        )

        with (
            patch.object(enterprise_routes, "list_incident_routes", return_value=[route]),
            patch.object(enterprise_routes, "create_incident_route", return_value=route),
            patch.object(enterprise_routes, "sync_incidents_for_alerts", AsyncMock(return_value=[incident])),
            patch.object(enterprise_routes, "get_active_alerts", return_value=[{"code": "queue_depth_high", "message": "Queue depth warning"}]),
            patch.object(enterprise_routes, "list_incidents", return_value=[incident]),
            patch.object(enterprise_routes, "get_incident_detail", return_value=(incident, [event])),
            patch.object(enterprise_routes, "acknowledge_incident", return_value=incident),
            patch.object(enterprise_routes, "resolve_incident", return_value=incident),
        ):
            create_route_response = client.post("/api/admin/enterprise/incidents/routes", json={
                "name": "Slack",
                "channel_type": "slack_webhook",
                "target": "https://hooks.slack.com/example",
            })
            list_routes_response = client.get("/api/admin/enterprise/incidents/routes")
            sync_response = client.post("/api/admin/enterprise/incidents/sync")
            list_response = client.get("/api/admin/enterprise/incidents")
            detail_response = client.get("/api/admin/enterprise/incidents/33333333-3333-3333-3333-333333333333")
            ack_response = client.post("/api/admin/enterprise/incidents/33333333-3333-3333-3333-333333333333/acknowledge")
            resolve_response = client.post("/api/admin/enterprise/incidents/33333333-3333-3333-3333-333333333333/resolve", json={"note": "Done"})

        self.assertEqual(create_route_response.status_code, 200)
        self.assertEqual(list_routes_response.status_code, 200)
        self.assertEqual(list_routes_response.json()[0]["channel_type"], "slack_webhook")
        self.assertEqual(sync_response.status_code, 200)
        self.assertEqual(sync_response.json()[0]["alert_code"], "queue_depth_high")
        self.assertEqual(list_response.status_code, 200)
        self.assertEqual(detail_response.status_code, 200)
        self.assertEqual(detail_response.json()["events"][0]["event_type"], "created")
        self.assertEqual(ack_response.status_code, 200)
        self.assertEqual(resolve_response.status_code, 200)


if __name__ == "__main__":
    unittest.main()
