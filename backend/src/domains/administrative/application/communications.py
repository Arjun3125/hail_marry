"""Application helpers for admin communication and document delivery workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.parent_link import ParentLink
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User


def build_admin_report_card_payload(
    *,
    db: Session,
    tenant_id,
    student_id: str,
    parse_uuid_fn,
    generate_report_card_pdf_fn,
) -> dict:
    student_uuid = parse_uuid_fn(student_id, "student_id")
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    school_name = tenant.name if tenant and hasattr(tenant, "name") else "VidyaOS School"

    try:
        pdf_bytes = generate_report_card_pdf_fn(
            db,
            student_id=str(student_uuid),
            tenant_id=str(tenant_id),
            school_name=school_name,
        )
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    return {
        "content": pdf_bytes,
        "filename": f"report_card_{student_id}.pdf",
    }


async def send_admin_whatsapp_digest_bulk(
    *,
    db: Session,
    tenant_id,
    phone_numbers: list[str] | None,
    send_weekly_digest_fn,
) -> dict:
    links = db.query(ParentLink).filter(
        ParentLink.tenant_id == tenant_id,
    ).all()

    allowed_numbers = set(phone_numbers or [])
    sent = 0
    errors: list[str] = []
    for link in links:
        parent = db.query(User).filter(User.id == link.parent_id).first()
        child = db.query(User).filter(User.id == link.child_id).first()
        if not parent or not child:
            continue

        phone = parent.email.split("@")[0] if parent.email else None
        if not phone:
            continue
        if allowed_numbers and phone not in allowed_numbers:
            continue

        total_att = db.query(Attendance).filter(
            Attendance.tenant_id == tenant_id,
            Attendance.student_id == child.id,
        ).count()
        present_att = db.query(Attendance).filter(
            Attendance.tenant_id == tenant_id,
            Attendance.student_id == child.id,
            Attendance.status == "present",
        ).count()
        att_pct = round(present_att / total_att * 100) if total_att > 0 else 0

        result = await send_weekly_digest_fn(
            to_phone=phone,
            student_name=child.full_name or child.email,
            attendance_pct=att_pct,
            avg_marks=0,
            top_subject="N/A",
            weak_subject="N/A",
        )
        if result.get("success"):
            sent += 1
        else:
            errors.append(f"{parent.email}: {result.get('error', 'Unknown')}")

    return {"success": True, "sent": sent, "errors": errors}
