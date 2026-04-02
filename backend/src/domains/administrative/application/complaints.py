"""Application helpers for admin complaint workflows."""

from __future__ import annotations

from datetime import datetime

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.domains.administrative.models.complaint import Complaint
from src.domains.identity.models.user import User


def build_admin_complaints_response(
    *,
    db: Session,
    tenant_id,
) -> list[dict]:
    complaints = db.query(Complaint, User.full_name).join(User, Complaint.student_id == User.id).filter(
        Complaint.tenant_id == tenant_id,
    ).order_by(desc(Complaint.created_at)).all()
    return [
        {
            "id": str(complaint.id),
            "student": name,
            "category": complaint.category,
            "description": complaint.description,
            "status": complaint.status,
            "resolution_note": complaint.resolution_note,
            "date": str(complaint.created_at.date()),
        }
        for complaint, name in complaints
    ]


def update_admin_complaint(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    complaint_id: str,
    status: str,
    resolution_note: str,
    parse_uuid_fn,
    allowed_statuses: set[str],
) -> dict:
    complaint_uuid = parse_uuid_fn(complaint_id, "complaint_id")
    complaint = db.query(Complaint).filter(Complaint.id == complaint_uuid, Complaint.tenant_id == tenant_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid complaint status")

    complaint.status = status
    complaint.resolution_note = resolution_note
    if status == "resolved":
        complaint.resolved_by = actor_user_id
        complaint.resolved_at = datetime.utcnow()
    db.commit()

    return {
        "complaint": complaint,
        "webhook_payload": {
            "complaint_id": str(complaint.id),
            "status": complaint.status,
            "resolved_by": str(complaint.resolved_by) if complaint.resolved_by else None,
        },
    }
