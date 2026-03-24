"""Compliance export and deletion workflow helpers."""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID
from zipfile import ZIP_DEFLATED, ZipFile

from fastapi import HTTPException
from sqlalchemy.orm import Session

from config import settings
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.audit import AuditLog
from src.domains.administrative.models.compliance import ComplianceExport, DeletionRequest
from src.domains.administrative.models.incident import Incident, IncidentEvent
from src.domains.identity.models.user import User


EXPORT_DIR = Path(settings.storage.compliance_export_dir).resolve()
EXPORT_DIR.mkdir(parents=True, exist_ok=True)


def _serialize_user(user: User) -> dict:
    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "is_active": user.is_active,
        "created_at": str(user.created_at),
        "last_login": str(user.last_login) if user.last_login else None,
    }


def _serialize_audit(log: AuditLog) -> dict:
    return {
        "id": str(log.id),
        "action": log.action,
        "entity_type": log.entity_type,
        "entity_id": str(log.entity_id) if log.entity_id else None,
        "metadata": log.metadata_,
        "created_at": str(log.created_at),
    }


def _serialize_ai_query(query: AIQuery) -> dict:
    return {
        "id": str(query.id),
        "user_id": str(query.user_id),
        "mode": query.mode,
        "query": query.query,
        "response": query.response,
        "trace_id": query.trace_id,
        "token_usage": query.token_usage,
        "citation_count": query.citation_count,
        "created_at": str(query.created_at),
    }


def _serialize_incident(incident: Incident) -> dict:
    return {
        "id": str(incident.id),
        "alert_code": incident.alert_code,
        "severity": incident.severity,
        "status": incident.status,
        "title": incident.title,
        "summary": incident.summary,
        "trace_id": incident.trace_id,
        "created_at": str(incident.created_at),
        "updated_at": str(incident.updated_at),
    }


def _serialize_incident_event(event: IncidentEvent) -> dict:
    return {
        "id": str(event.id),
        "incident_id": str(event.incident_id),
        "actor_user_id": str(event.actor_user_id) if event.actor_user_id else None,
        "event_type": event.event_type,
        "detail": event.detail,
        "payload": event.payload,
        "created_at": str(event.created_at),
    }


def create_compliance_export(
    db: Session,
    *,
    tenant_id: UUID,
    requested_by: UUID,
    scope_type: str = "tenant",
    scope_user_id: UUID | None = None,
) -> ComplianceExport:
    export = ComplianceExport(
        tenant_id=tenant_id,
        requested_by=requested_by,
        export_type="tenant_bundle" if scope_type == "tenant" else "user_bundle",
        scope_type=scope_type,
        scope_user_id=scope_user_id,
        format="zip",
        status="processing",
    )
    db.add(export)
    db.commit()
    db.refresh(export)

    user_filter = [User.tenant_id == tenant_id]
    ai_filter = [AIQuery.tenant_id == tenant_id]
    audit_filter = [AuditLog.tenant_id == tenant_id]
    incident_filter = [Incident.tenant_id == tenant_id]
    incident_event_filter = [IncidentEvent.tenant_id == tenant_id]

    if scope_type == "user":
        if not scope_user_id:
            raise HTTPException(status_code=400, detail="scope_user_id is required for user export.")
        user_filter.append(User.id == scope_user_id)
        ai_filter.append(AIQuery.user_id == scope_user_id)
        audit_filter.append(AuditLog.user_id == scope_user_id)
        incident_event_filter.append(IncidentEvent.actor_user_id == scope_user_id)

    users = [_serialize_user(user) for user in db.query(User).filter(*user_filter).all()]
    ai_queries = [_serialize_ai_query(query) for query in db.query(AIQuery).filter(*ai_filter).all()]
    audits = [_serialize_audit(log) for log in db.query(AuditLog).filter(*audit_filter).all()]
    incidents = [_serialize_incident(incident) for incident in db.query(Incident).filter(*incident_filter).all()]
    incident_events = [_serialize_incident_event(event) for event in db.query(IncidentEvent).filter(*incident_event_filter).all()]

    manifest = {
        "export_id": str(export.id),
        "scope_type": scope_type,
        "scope_user_id": str(scope_user_id) if scope_user_id else None,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "counts": {
            "users": len(users),
            "ai_queries": len(ai_queries),
            "audit_logs": len(audits),
            "incidents": len(incidents),
            "incident_events": len(incident_events),
        },
    }

    file_path = EXPORT_DIR / f"{export.id}.zip"
    with ZipFile(file_path, "w", compression=ZIP_DEFLATED) as archive:
        archive.writestr("manifest.json", json.dumps(manifest, indent=2))
        archive.writestr("users.json", json.dumps(users, indent=2))
        archive.writestr("ai_queries.json", json.dumps(ai_queries, indent=2))
        archive.writestr("audit_logs.json", json.dumps(audits, indent=2))
        archive.writestr("incidents.json", json.dumps(incidents, indent=2))
        archive.writestr("incident_events.json", json.dumps(incident_events, indent=2))

    payload = file_path.read_bytes()
    export.file_path = str(file_path)
    export.file_size = len(payload)
    export.checksum = hashlib.sha256(payload).hexdigest()
    export.status = "completed"
    export.completed_at = datetime.now(timezone.utc)
    export.metadata_ = manifest
    db.commit()
    db.refresh(export)
    return export


def list_compliance_exports(db: Session, tenant_id: UUID) -> list[ComplianceExport]:
    return db.query(ComplianceExport).filter(ComplianceExport.tenant_id == tenant_id).order_by(ComplianceExport.created_at.desc()).all()


def create_deletion_request(
    db: Session,
    *,
    tenant_id: UUID,
    requested_by: UUID,
    target_user_id: UUID | None,
    reason: str,
) -> DeletionRequest:
    request = DeletionRequest(
        tenant_id=tenant_id,
        requested_by=requested_by,
        target_user_id=target_user_id,
        reason=reason,
        status="requested",
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def resolve_deletion_request(
    db: Session,
    *,
    tenant_id: UUID,
    request_id: UUID,
    note: str,
) -> DeletionRequest:
    request = db.query(DeletionRequest).filter(
        DeletionRequest.id == request_id,
        DeletionRequest.tenant_id == tenant_id,
    ).first()
    if not request:
        raise HTTPException(status_code=404, detail="Deletion request not found")
    request.status = "resolved"
    request.resolution_note = note
    request.resolved_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(request)
    return request
