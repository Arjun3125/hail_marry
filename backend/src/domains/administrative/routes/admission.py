"""Admission API routes — application submission, listing, status updates, bulk enrollment."""
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from auth.dependencies import require_role
from database import get_db
from src.domains.administrative.models.admission import AdmissionApplication
from src.domains.administrative.services.admission import (
    bulk_enroll,
    get_admission_stats,
    list_applications,
    submit_application,
    update_status,
)

router = APIRouter(prefix="/api/admission", tags=["Admission"])


# ── Request schemas ──

class ApplyRequest(BaseModel):
    tenant_id: str
    student_name: str
    parent_email: str
    parent_phone: Optional[str] = None
    applied_class_name: Optional[str] = None
    notes: Optional[str] = None


class UpdateStatusRequest(BaseModel):
    status: str
    notes: Optional[str] = None


class BulkEnrollRequest(BaseModel):
    application_ids: list[str]


# ── Endpoints ──

@router.post("/apply")
def apply_for_admission(body: ApplyRequest, db: Session = Depends(get_db)):
    """Submit an admission application. Public endpoint (rate-limited)."""
    if not body.student_name.strip():
        raise HTTPException(status_code=400, detail="Student name is required")
    if not body.parent_email.strip():
        raise HTTPException(status_code=400, detail="Parent email is required")

    try:
        tenant_uuid = UUID(body.tenant_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid tenant_id")

    app = submit_application(
        db,
        tenant_id=tenant_uuid,
        student_name=body.student_name.strip(),
        parent_email=body.parent_email.strip(),
        parent_phone=body.parent_phone,
        applied_class_name=body.applied_class_name,
    )
    return {
        "status": "submitted",
        "application_id": str(app.id),
        "application_status": app.status,
    }


@router.get("/applications")
def get_applications(
    status: Optional[str] = Query(None),
    class_name: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """List admission applications with optional filters. Admin only."""
    apps, total = list_applications(db, user.tenant_id, status, class_name, limit, offset)
    return {
        "applications": [
            {
                "id": str(a.id),
                "student_name": a.student_name,
                "parent_email": a.parent_email,
                "parent_phone": a.parent_phone,
                "applied_class": a.applied_class_name,
                "status": a.status,
                "applied_at": a.applied_at.isoformat() if a.applied_at else None,
                "reviewed_at": a.reviewed_at.isoformat() if a.reviewed_at else None,
            }
            for a in apps
        ],
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/applications/{application_id}")
def get_application_detail(
    application_id: str,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Get single application detail. Admin only."""
    try:
        app_uuid = UUID(application_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid application_id")

    app = db.query(AdmissionApplication).filter(
        AdmissionApplication.id == app_uuid,
        AdmissionApplication.tenant_id == user.tenant_id,
    ).first()
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")

    return {
        "id": str(app.id),
        "student_name": app.student_name,
        "parent_email": app.parent_email,
        "parent_phone": app.parent_phone,
        "applied_class": app.applied_class_name,
        "status": app.status,
        "documents": app.documents,
        "notes": app.notes,
        "applied_at": app.applied_at.isoformat() if app.applied_at else None,
        "reviewed_by": str(app.reviewed_by) if app.reviewed_by else None,
        "reviewed_at": app.reviewed_at.isoformat() if app.reviewed_at else None,
    }


@router.patch("/applications/{application_id}/status")
def update_application_status(
    application_id: str,
    body: UpdateStatusRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Update application status. Admin only."""
    try:
        app_uuid = UUID(application_id)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail="Invalid application_id")

    try:
        app = update_status(db, app_uuid, body.status, user.id, body.notes)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc))

    return {"status": app.status, "application_id": str(app.id)}


@router.post("/bulk-enroll")
def bulk_enroll_students(
    body: BulkEnrollRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Enroll accepted applicants as students. Admin only."""
    if not body.application_ids:
        raise HTTPException(status_code=400, detail="No application IDs provided")

    uuids = []
    for aid in body.application_ids:
        try:
            uuids.append(UUID(aid))
        except (TypeError, ValueError):
            raise HTTPException(status_code=400, detail=f"Invalid ID: {aid}")

    result = bulk_enroll(db, user.tenant_id, uuids, user.id)
    return result


@router.get("/stats")
def admission_stats(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Get admission dashboard statistics. Admin only."""
    stats = get_admission_stats(db, user.tenant_id)
    return {"stats": stats}
