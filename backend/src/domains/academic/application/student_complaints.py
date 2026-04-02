"""Application helpers for student complaint workflows."""

from __future__ import annotations

from sqlalchemy.orm import Session

from src.domains.administrative.models.complaint import Complaint


def list_student_complaints(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> list[dict[str, str]]:
    complaints = (
        db.query(Complaint)
        .filter(
            Complaint.tenant_id == tenant_id,
            Complaint.student_id == student_id,
        )
        .order_by(Complaint.created_at.desc())
        .all()
    )

    return [
        {
            "id": str(complaint.id),
            "category": complaint.category,
            "description": complaint.description,
            "status": complaint.status,
            "date": str(complaint.created_at.date()),
        }
        for complaint in complaints
    ]


def create_student_complaint(
    *,
    db: Session,
    tenant_id,
    student_id,
    category: str,
    description: str,
) -> dict[str, object]:
    complaint = Complaint(
        tenant_id=tenant_id,
        student_id=student_id,
        category=category,
        description=description.strip(),
    )
    db.add(complaint)
    db.commit()
    return {"success": True, "message": "Complaint submitted"}
