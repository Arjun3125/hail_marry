"""Enterprise administration APIs for SSO, vector backend, compliance, and incidents."""
from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from config import settings
from database import get_db
from models.compliance import ComplianceExport, DeletionRequest
from models.incident import Incident, IncidentEvent
from models.tenant import Tenant
from models.user import User
from services.alerting import get_active_alerts
from services.compliance import (
    create_compliance_export,
    create_deletion_request,
    list_compliance_exports,
    resolve_deletion_request,
)
from services.incident_management import (
    acknowledge_incident,
    create_incident_route,
    get_incident_detail,
    list_incident_routes,
    list_incidents,
    resolve_incident,
    sync_incidents_for_alerts,
)
from services.deployment_guidance import build_hosted_production_guidance
from services.operations_center import build_operations_summary
from services.saml_sso import import_tenant_saml_metadata

router = APIRouter(prefix="/api/admin/enterprise", tags=["Enterprise"])


def _uuid_str(value: UUID | None) -> str | None:
    return str(value) if value else None


class SAMLSettingsUpdate(BaseModel):
    enabled: bool = False
    entity_id: str | None = None
    metadata_url: str | None = None
    attribute_email: str = "email"
    attribute_name: str = "full_name"


class SAMLMetadataImportRequest(BaseModel):
    metadata_url: str | None = None
    metadata_xml: str | None = None


class VectorBackendSettingsResponse(BaseModel):
    provider: str
    qdrant_url: str
    collection_prefix: str


class ComplianceExportCreate(BaseModel):
    scope_type: str = Field(default="tenant")
    scope_user_id: str | None = None


class DeletionRequestCreate(BaseModel):
    target_user_id: str | None = None
    reason: str = ""


class DeletionRequestResolve(BaseModel):
    note: str = ""


class IncidentRouteCreate(BaseModel):
    name: str
    channel_type: str
    target: str
    secret: str | None = None
    severity_filter: str = "all"
    escalation_channel_type: str | None = None
    escalation_target: str | None = None
    escalation_after_minutes: int | None = None


class IncidentAction(BaseModel):
    note: str = ""


def _serialize_export(export: ComplianceExport) -> dict:
    return {
        "id": str(export.id),
        "tenant_id": str(export.tenant_id),
        "requested_by": _uuid_str(export.requested_by),
        "export_type": export.export_type,
        "scope_type": export.scope_type,
        "scope_user_id": _uuid_str(export.scope_user_id),
        "format": export.format,
        "status": export.status,
        "file_path": export.file_path,
        "file_size": export.file_size,
        "checksum": export.checksum,
        "metadata": export.metadata_,
        "created_at": str(export.created_at),
        "completed_at": str(export.completed_at) if export.completed_at else None,
    }


def _serialize_deletion_request(request: DeletionRequest) -> dict:
    return {
        "id": str(request.id),
        "tenant_id": str(request.tenant_id),
        "requested_by": _uuid_str(request.requested_by),
        "target_user_id": _uuid_str(request.target_user_id),
        "status": request.status,
        "reason": request.reason,
        "resolution_note": request.resolution_note,
        "metadata": request.metadata_,
        "created_at": str(request.created_at),
        "resolved_at": str(request.resolved_at) if request.resolved_at else None,
    }


def _serialize_incident(incident: Incident, events: list[IncidentEvent] | None = None) -> dict:
    payload = {
        "id": str(incident.id),
        "alert_code": incident.alert_code,
        "severity": incident.severity,
        "status": incident.status,
        "title": incident.title,
        "summary": incident.summary,
        "trace_id": incident.trace_id,
        "created_at": str(incident.created_at),
        "updated_at": str(incident.updated_at),
        "acknowledged_at": str(incident.acknowledged_at) if incident.acknowledged_at else None,
        "resolved_at": str(incident.resolved_at) if incident.resolved_at else None,
        "source_payload": incident.source_payload,
    }
    if events is not None:
        payload["events"] = [{
            "id": str(event.id),
            "event_type": event.event_type,
            "detail": event.detail,
            "payload": event.payload,
            "created_at": str(event.created_at),
            "actor_user_id": _uuid_str(event.actor_user_id),
        } for event in events]
    return payload


@router.get("/sso")
async def get_sso_settings(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {
        "enabled": tenant.saml_enabled,
        "entity_id": tenant.saml_entity_id,
        "metadata_url": tenant.saml_metadata_url,
        "idp_entity_id": tenant.saml_idp_entity_id,
        "idp_sso_url": tenant.saml_idp_sso_url,
        "idp_slo_url": tenant.saml_idp_slo_url,
        "attribute_email": tenant.saml_attribute_email,
        "attribute_name": tenant.saml_attribute_name,
    }


@router.patch("/sso")
async def update_sso_settings(
    data: SAMLSettingsUpdate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    tenant.saml_enabled = data.enabled
    tenant.saml_entity_id = data.entity_id or tenant.saml_entity_id
    tenant.saml_metadata_url = data.metadata_url
    tenant.saml_attribute_email = data.attribute_email
    tenant.saml_attribute_name = data.attribute_name
    db.commit()
    return {"success": True}


@router.post("/sso/import-metadata")
async def import_sso_metadata(
    data: SAMLMetadataImportRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    parsed = await import_tenant_saml_metadata(tenant, metadata_url=data.metadata_url, metadata_xml=data.metadata_xml)
    db.commit()
    return parsed


@router.get("/vector-backend", response_model=VectorBackendSettingsResponse)
async def vector_backend_settings(current_user: User = Depends(require_role("admin"))):
    return {
        "provider": settings.vector_backend.provider,
        "qdrant_url": settings.vector_backend.qdrant_url,
        "collection_prefix": settings.vector_backend.collection_prefix,
    }


@router.get("/compliance/settings")
async def get_compliance_settings(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    return {
        "data_retention_days": tenant.data_retention_days,
        "export_retention_days": tenant.export_retention_days,
    }


@router.patch("/compliance/settings")
async def update_compliance_settings(
    data: dict,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
    if "data_retention_days" in data:
        tenant.data_retention_days = max(int(data["data_retention_days"]), 1)
    if "export_retention_days" in data:
        tenant.export_retention_days = max(int(data["export_retention_days"]), 1)
    db.commit()
    return {"success": True}


@router.get("/compliance/exports")
async def compliance_exports(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return [_serialize_export(export) for export in list_compliance_exports(db, current_user.tenant_id)]


@router.post("/compliance/exports")
async def create_export(
    data: ComplianceExportCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    scope_user_id = UUID(data.scope_user_id) if data.scope_user_id else None
    export = create_compliance_export(
        db,
        tenant_id=current_user.tenant_id,
        requested_by=current_user.id,
        scope_type=data.scope_type,
        scope_user_id=scope_user_id,
    )
    return _serialize_export(export)


@router.get("/compliance/deletion-requests")
async def list_deletion_requests(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    requests = db.query(DeletionRequest).filter(DeletionRequest.tenant_id == current_user.tenant_id).order_by(DeletionRequest.created_at.desc()).all()
    return [_serialize_deletion_request(item) for item in requests]


@router.post("/compliance/deletion-requests")
async def request_deletion(
    data: DeletionRequestCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    target_user_id = UUID(data.target_user_id) if data.target_user_id else None
    request = create_deletion_request(
        db,
        tenant_id=current_user.tenant_id,
        requested_by=current_user.id,
        target_user_id=target_user_id,
        reason=data.reason,
    )
    return _serialize_deletion_request(request)


@router.post("/compliance/deletion-requests/{request_id}/resolve")
async def resolve_deletion(
    request_id: str,
    data: DeletionRequestResolve,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    request = resolve_deletion_request(
        db,
        tenant_id=current_user.tenant_id,
        request_id=UUID(request_id),
        note=data.note,
    )
    return _serialize_deletion_request(request)


@router.get("/incidents/routes")
async def incident_routes(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return [{
        "id": str(route.id),
        "name": route.name,
        "channel_type": route.channel_type,
        "target": route.target,
        "severity_filter": route.severity_filter,
        "escalation_channel_type": route.escalation_channel_type,
        "escalation_target": route.escalation_target,
        "escalation_after_minutes": route.escalation_after_minutes,
        "is_active": route.is_active,
        "created_at": str(route.created_at),
    } for route in list_incident_routes(db, current_user.tenant_id)]


@router.post("/incidents/routes")
async def add_incident_route(
    data: IncidentRouteCreate,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    route = create_incident_route(
        db,
        tenant_id=current_user.tenant_id,
        name=data.name,
        channel_type=data.channel_type,
        target=data.target,
        secret=data.secret,
        severity_filter=data.severity_filter,
        escalation_channel_type=data.escalation_channel_type,
        escalation_target=data.escalation_target,
        escalation_after_minutes=data.escalation_after_minutes,
    )
    return {"id": str(route.id), "success": True}


@router.post("/incidents/sync")
async def sync_incidents(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    alerts = get_active_alerts(str(current_user.tenant_id))
    incidents = await sync_incidents_for_alerts(db, current_user.tenant_id, alerts)
    return [_serialize_incident(incident) for incident in incidents]


@router.get("/incidents")
async def incidents(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    return [_serialize_incident(incident) for incident in list_incidents(db, current_user.tenant_id)]


@router.get("/incidents/{incident_id}")
async def incident_detail(
    incident_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    try:
        incident, events = get_incident_detail(db, current_user.tenant_id, UUID(incident_id))
    except ValueError:
        raise HTTPException(status_code=404, detail="Incident not found")
    return _serialize_incident(incident, events)


@router.post("/incidents/{incident_id}/acknowledge")
async def acknowledge(
    incident_id: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    incident = acknowledge_incident(db, current_user.tenant_id, UUID(incident_id), current_user.id)
    return _serialize_incident(incident)


@router.post("/incidents/{incident_id}/resolve")
async def resolve(
    incident_id: str,
    data: IncidentAction,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    incident = resolve_incident(db, current_user.tenant_id, UUID(incident_id), current_user.id, data.note)
    return _serialize_incident(incident)


@router.get("/operations/summary")
async def operations_summary(
    current_user: User = Depends(require_role("admin")),
):
    """Single-pane operations summary for queue, alerts, and AI runtime health."""
    return await build_operations_summary(str(current_user.tenant_id))


@router.get("/deployment/guidance")
async def deployment_guidance(
    current_user: User = Depends(require_role("admin")),
):
    """Show required vs optional hosted production configuration keys."""
    _ = current_user
    return build_hosted_production_guidance()
