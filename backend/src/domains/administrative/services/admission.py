"""Admission workflow service — application CRUD, status transitions, bulk enrollment."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from constants import ADMISSION_STATUS_TRANSITIONS, ADMISSION_STATUSES
from src.domains.administrative.models.admission import AdmissionApplication
from src.domains.academic.models.core import Class, Enrollment
from src.domains.platform.models.audit import AuditLog
from src.domains.identity.models.user import User


def submit_application(
    db: Session,
    tenant_id: UUID,
    student_name: str,
    parent_email: str,
    parent_phone: Optional[str] = None,
    applied_class_name: Optional[str] = None,
    applied_class_id: Optional[UUID] = None,
    documents: Optional[list] = None,
    notes: Optional[str] = None,
) -> AdmissionApplication:
    """Create a new admission application."""
    # Resolve class name if class_id is provided
    if applied_class_id and not applied_class_name:
        cls = db.query(Class).filter(Class.id == applied_class_id).first()
        if cls:
            applied_class_name = cls.name

    app = AdmissionApplication(
        tenant_id=tenant_id,
        student_name=student_name,
        parent_email=parent_email,
        parent_phone=parent_phone,
        applied_class_id=applied_class_id,
        applied_class_name=applied_class_name,
        documents=documents,
        notes=notes,
        status="pending",
    )
    db.add(app)
    db.commit()
    db.refresh(app)
    return app


def list_applications(
    db: Session,
    tenant_id: UUID,
    status_filter: Optional[str] = None,
    class_filter: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[AdmissionApplication], int]:
    """List admission applications with optional filters. Returns (apps, total_count)."""
    query = db.query(AdmissionApplication).filter(AdmissionApplication.tenant_id == tenant_id)

    if status_filter and status_filter in ADMISSION_STATUSES:
        query = query.filter(AdmissionApplication.status == status_filter)
    if class_filter:
        query = query.filter(AdmissionApplication.applied_class_name == class_filter)

    total = query.count()
    apps = query.order_by(AdmissionApplication.applied_at.desc()).offset(offset).limit(limit).all()
    return apps, total


def update_status(
    db: Session,
    application_id: UUID,
    new_status: str,
    reviewed_by: UUID,
    notes: Optional[str] = None,
) -> AdmissionApplication:
    """Update application status with validation and audit logging."""
    app = db.query(AdmissionApplication).filter(AdmissionApplication.id == application_id).first()
    if not app:
        raise ValueError("Application not found")

    # Validate status transition
    allowed = ADMISSION_STATUS_TRANSITIONS.get(app.status, set())
    if new_status not in allowed:
        raise ValueError(f"Cannot transition from '{app.status}' to '{new_status}'. Allowed: {allowed}")

    old_status = app.status
    app.status = new_status
    app.reviewed_by = reviewed_by
    app.reviewed_at = datetime.now(timezone.utc)
    if notes:
        app.notes = notes

    # Audit log
    audit = AuditLog(
        tenant_id=app.tenant_id,
        user_id=reviewed_by,
        action=f"admission.status.{new_status}",
        entity_type="admission_application",
        entity_id=str(app.id),
        metadata={"old_status": old_status, "new_status": new_status},
    )
    db.add(audit)
    db.commit()
    db.refresh(app)
    return app


def bulk_enroll(
    db: Session,
    tenant_id: UUID,
    application_ids: list[UUID],
    enrolled_by: UUID,
) -> dict:
    """Convert accepted applications into enrolled students."""
    enrolled = 0
    errors = []

    for app_id in application_ids:
        app = db.query(AdmissionApplication).filter(
            AdmissionApplication.id == app_id,
            AdmissionApplication.tenant_id == tenant_id,
        ).first()

        if not app:
            errors.append(f"{app_id}: not found")
            continue
        if app.status != "accepted":
            errors.append(f"{app_id}: status is '{app.status}', must be 'accepted'")
            continue

        # Check for existing student with same email
        existing = db.query(User).filter(
            User.email == app.parent_email,
            User.tenant_id == tenant_id,
        ).first()

        if existing:
            errors.append(f"{app_id}: email '{app.parent_email}' already exists")
            continue

        # Create student user
        student = User(
            tenant_id=tenant_id,
            email=app.parent_email,
            full_name=app.student_name,
            role="student",
            is_active=True,
        )
        db.add(student)
        db.flush()

        # Create enrollment if class specified
        if app.applied_class_id:
            enrollment = Enrollment(
                student_id=student.id,
                class_id=app.applied_class_id,
                tenant_id=tenant_id,
            )
            db.add(enrollment)

        # Update application status
        app.status = "enrolled"
        app.reviewed_by = enrolled_by
        app.reviewed_at = datetime.now(timezone.utc)
        enrolled += 1

    db.commit()
    return {"enrolled": enrolled, "errors": errors}


def get_admission_stats(db: Session, tenant_id: UUID) -> dict:
    """Get admission application counts by status."""
    from sqlalchemy import func

    results = (
        db.query(AdmissionApplication.status, func.count(AdmissionApplication.id))
        .filter(AdmissionApplication.tenant_id == tenant_id)
        .group_by(AdmissionApplication.status)
        .all()
    )
    stats = {status: 0 for status in ADMISSION_STATUSES}
    for status, count in results:
        stats[status] = count
    stats["total"] = sum(stats.values())
    return stats
