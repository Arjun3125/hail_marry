"""Incident routing, escalation, and lifecycle helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.orm import Session

from config import settings
from models.incident import Incident, IncidentEvent, IncidentRoute


def list_incident_routes(db: Session, tenant_id: UUID) -> list[IncidentRoute]:
    return db.query(IncidentRoute).filter(IncidentRoute.tenant_id == tenant_id).order_by(IncidentRoute.created_at.desc()).all()


def create_incident_route(
    db: Session,
    *,
    tenant_id: UUID,
    name: str,
    channel_type: str,
    target: str,
    secret: str | None,
    severity_filter: str,
    escalation_channel_type: str | None,
    escalation_target: str | None,
    escalation_after_minutes: int | None,
) -> IncidentRoute:
    route = IncidentRoute(
        tenant_id=tenant_id,
        name=name,
        channel_type=channel_type,
        target=target,
        secret=secret,
        severity_filter=severity_filter,
        escalation_channel_type=escalation_channel_type,
        escalation_target=escalation_target,
        escalation_after_minutes=escalation_after_minutes or settings.incidents.default_escalation_minutes,
    )
    db.add(route)
    db.commit()
    db.refresh(route)
    return route


def _record_incident_event(
    db: Session,
    *,
    tenant_id: UUID,
    incident_id: UUID,
    actor_user_id: UUID | None,
    event_type: str,
    detail: str | None = None,
    payload: dict[str, Any] | None = None,
) -> None:
    db.add(
        IncidentEvent(
            tenant_id=tenant_id,
            incident_id=incident_id,
            actor_user_id=actor_user_id,
            event_type=event_type,
            detail=detail,
            payload=payload,
        )
    )
    db.commit()


async def _deliver_incident(route: IncidentRoute, incident: Incident, *, escalated: bool = False) -> bool:
    payload = {
        "incident_id": str(incident.id),
        "alert_code": incident.alert_code,
        "severity": incident.severity,
        "status": incident.status,
        "title": incident.title,
        "summary": incident.summary,
        "trace_id": incident.trace_id,
        "escalated": escalated,
    }
    headers = {"Content-Type": "application/json"}
    target = route.escalation_target if escalated and route.escalation_target else route.target
    channel_type = route.escalation_channel_type if escalated and route.escalation_channel_type else route.channel_type

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            if channel_type == "slack_webhook":
                response = await client.post(target, json={"text": f"[{incident.severity}] {incident.title}: {incident.summary}"})
            elif channel_type == "pagerduty_events":
                response = await client.post(
                    "https://events.pagerduty.com/v2/enqueue",
                    json={
                        "routing_key": route.secret or target,
                        "event_action": "trigger",
                        "payload": {
                            "summary": incident.summary,
                            "severity": "critical" if incident.severity == "critical" else "warning",
                            "source": "vidyaos",
                            "custom_details": payload,
                        },
                    },
                )
            elif channel_type == "opsgenie":
                headers["Authorization"] = f"GenieKey {route.secret or ''}"
                response = await client.post(
                    "https://api.opsgenie.com/v2/alerts",
                    headers=headers,
                    json={
                        "message": incident.title,
                        "description": incident.summary,
                        "details": payload,
                    },
                )
            else:
                response = await client.post(target, json=payload, headers=headers)
        return 200 <= response.status_code < 300
    except Exception:
        return False


async def sync_incidents_for_alerts(db: Session, tenant_id: UUID, alerts: list[dict[str, Any]]) -> list[Incident]:
    incidents: list[Incident] = []
    if not settings.incidents.auto_create_from_alerts:
        return incidents

    routes = list_incident_routes(db, tenant_id)
    now = datetime.now(timezone.utc)

    for alert in alerts:
        incident = db.query(Incident).filter(
            Incident.tenant_id == tenant_id,
            Incident.alert_code == alert["code"],
            Incident.status.in_(["open", "acknowledged"]),
        ).order_by(Incident.created_at.desc()).first()

        if not incident:
            incident = Incident(
                tenant_id=tenant_id,
                alert_code=alert["code"],
                severity=alert.get("severity", "warning"),
                status="open",
                title=alert["code"].replace("_", " ").title(),
                summary=alert.get("message", alert["code"]),
                trace_id=alert.get("trace_id"),
                source_payload=alert,
                last_notified_at=now,
            )
            db.add(incident)
            db.commit()
            db.refresh(incident)
            _record_incident_event(
                db,
                tenant_id=tenant_id,
                incident_id=incident.id,
                actor_user_id=None,
                event_type="created",
                detail=incident.summary,
                payload=alert,
            )
            for route in routes:
                if route.severity_filter not in ("all", incident.severity):
                    continue
                delivered = await _deliver_incident(route, incident, escalated=False)
                _record_incident_event(
                    db,
                    tenant_id=tenant_id,
                    incident_id=incident.id,
                    actor_user_id=None,
                    event_type="notification_sent" if delivered else "notification_failed",
                    detail=route.channel_type,
                    payload={"route_id": str(route.id), "target": route.target},
                )
        else:
            incident.summary = alert.get("message", incident.summary)
            incident.severity = alert.get("severity", incident.severity)
            incident.source_payload = alert
            db.commit()

            if incident.status != "resolved" and incident.acknowledged_at is None:
                for route in routes:
                    if route.severity_filter not in ("all", incident.severity):
                        continue
                    threshold = route.escalation_after_minutes or settings.incidents.default_escalation_minutes
                    if incident.last_notified_at and incident.last_notified_at > now - timedelta(minutes=threshold):
                        continue
                    delivered = await _deliver_incident(route, incident, escalated=True)
                    incident.last_notified_at = now
                    db.commit()
                    _record_incident_event(
                        db,
                        tenant_id=tenant_id,
                        incident_id=incident.id,
                        actor_user_id=None,
                        event_type="escalated" if delivered else "escalation_failed",
                        detail=route.channel_type,
                        payload={"route_id": str(route.id)},
                    )
        incidents.append(incident)
    return incidents


def list_incidents(db: Session, tenant_id: UUID) -> list[Incident]:
    return db.query(Incident).filter(Incident.tenant_id == tenant_id).order_by(Incident.created_at.desc()).all()


def get_incident_detail(db: Session, tenant_id: UUID, incident_id: UUID) -> tuple[Incident, list[IncidentEvent]]:
    incident = db.query(Incident).filter(Incident.id == incident_id, Incident.tenant_id == tenant_id).first()
    if not incident:
        raise ValueError("Incident not found")
    events = db.query(IncidentEvent).filter(
        IncidentEvent.incident_id == incident_id,
        IncidentEvent.tenant_id == tenant_id,
    ).order_by(IncidentEvent.created_at.asc()).all()
    return incident, events


def acknowledge_incident(db: Session, tenant_id: UUID, incident_id: UUID, actor_user_id: UUID) -> Incident:
    incident, _ = get_incident_detail(db, tenant_id, incident_id)
    incident.status = "acknowledged"
    incident.acknowledged_by = actor_user_id
    incident.acknowledged_at = datetime.now(timezone.utc)
    db.commit()
    _record_incident_event(
        db,
        tenant_id=tenant_id,
        incident_id=incident.id,
        actor_user_id=actor_user_id,
        event_type="acknowledged",
        detail="Incident acknowledged",
    )
    return incident


def resolve_incident(db: Session, tenant_id: UUID, incident_id: UUID, actor_user_id: UUID, note: str) -> Incident:
    incident, _ = get_incident_detail(db, tenant_id, incident_id)
    incident.status = "resolved"
    incident.resolved_by = actor_user_id
    incident.resolved_at = datetime.now(timezone.utc)
    db.commit()
    _record_incident_event(
        db,
        tenant_id=tenant_id,
        incident_id=incident.id,
        actor_user_id=actor_user_id,
        event_type="resolved",
        detail=note or "Incident resolved",
    )
    return incident
