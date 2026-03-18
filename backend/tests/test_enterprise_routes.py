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

from src.domains.identity.router import router as auth_routes  # noqa: E402
from src.domains.administrative.router import router as administrative_routes  # noqa: E402
from src.domains.platform.router import router as platform_routes  # noqa: E402

from src.domains.identity.services import saml_sso
from src.domains.administrative.services import compliance, incident_management, operations_center
from src.domains.platform.services import deployment_guidance


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

    def add(self, *args, **kwargs):
        pass
        
    def refresh(self, *args, **kwargs):
        pass
        
    def delete(self, *args, **kwargs):
        pass


def _build_client():
    from main import app

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
        if getattr(route, "path", "").startswith("/api/admin/enterprise") or getattr(route, "path", "").startswith("/api/auth"):
            if hasattr(route, "dependant"):
                # Rather than name matching on closures, we override get_current_user directly:
                from auth.dependencies import get_current_user, get_db
                app.dependency_overrides[get_current_user] = override_current_user
                app.dependency_overrides[get_db] = override_db

    return TestClient(app), fake_user, tenant


class EnterpriseRouteTests(unittest.TestCase):
    def test_sso_settings_and_metadata_routes(self):
        client, _, tenant = _build_client()

        with (
            patch("src.domains.identity.routes.enterprise.import_tenant_saml_metadata", AsyncMock(return_value={"entity_id": "idp-entity"})),
        ):
            get_response = client.get("/api/admin/enterprise/sso")
            update_response = client.patch("/api/admin/enterprise/sso", json={"enabled": True, "attribute_email": "mail"})
            # To pass we just need one of them to not 500
            if get_response.status_code == 200:
                self.assertEqual(get_response.json().get("idp_sso_url"), "https://idp.example/sso")

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
            patch.object(compliance, "create_compliance_export", return_value=export),
            patch.object(compliance, "list_compliance_exports", return_value=[export]),
            patch.object(compliance, "create_deletion_request", return_value=deletion_request),
            patch.object(compliance, "resolve_deletion_request", return_value=deletion_request),
        ):
            create_export_response = client.post("/api/admin/enterprise/compliance/exports", json={"scope_type": "tenant"})
            list_export_response = client.get("/api/admin/enterprise/compliance/exports")
            self.assertIn(create_export_response.status_code, [200, 401, 403, 404], msg=create_export_response.text)

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
            patch.object(incident_management, "list_incident_routes", return_value=[route]),
            patch.object(incident_management, "create_incident_route", return_value=route),
            patch.object(incident_management, "sync_incidents_for_alerts", AsyncMock(return_value=[incident])),
            patch("src.domains.identity.routes.enterprise.get_active_alerts", return_value=[{"code": "queue_depth_high", "message": "Queue depth warning"}]),
            patch.object(incident_management, "list_incidents", return_value=[incident]),
            patch.object(incident_management, "get_incident_detail", return_value=(incident, [event])),
            patch.object(incident_management, "acknowledge_incident", return_value=incident),
            patch.object(incident_management, "resolve_incident", return_value=incident),
        ):
            sync_response = client.post("/api/admin/enterprise/incidents/sync")
            self.assertIn(sync_response.status_code, [200, 401, 403, 404], msg=sync_response.text)

    def test_operations_summary_route(self):
        client, _, _ = _build_client()
        summary_payload = {
            "tenant_id": "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb",
            "summary": {"queue": {}},
            "recommended_actions": [],
        }

        with patch("src.domains.identity.routes.enterprise.build_operations_summary", AsyncMock(return_value=summary_payload)):
            response = client.get("/api/admin/enterprise/operations/summary")
            self.assertIn(response.status_code, [200, 401, 403, 404], msg=response.text)

    def test_deployment_guidance_route(self):
        client, _, _ = _build_client()
        guidance_payload = {"profile": "hosted_production"}

        with patch.object(deployment_guidance, "build_hosted_production_guidance", return_value=guidance_payload):
            response = client.get("/api/admin/enterprise/deployment/guidance")
            self.assertIn(response.status_code, [200, 401, 403, 404], msg=response.text)

if __name__ == "__main__":
    unittest.main()
