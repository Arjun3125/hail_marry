"""Parent weekly digest email generation."""
from __future__ import annotations

import logging
from datetime import date, timedelta
from typing import Any, Tuple, List
from uuid import UUID

from sqlalchemy.engine.row import Row
from sqlalchemy.orm import Session
from sqlalchemy import case, func
from sqlalchemy.sql.schema import Column

from src.domains.identity.models.user import User
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Exam, Mark
from src.domains.platform.models.ai import AIQuery
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.core import Enrollment
from src.domains.platform.services.emailer import send_email

logger: logging.Logger = logging.getLogger(__name__)


def _get_child_ids(db: Session, parent_id: UUID, tenant_id: UUID) -> list[UUID]:
    """Get all children linked to a parent."""
    links: List[ParentLink] = db.query(ParentLink).filter(
        ParentLink.parent_id == parent_id,
        ParentLink.tenant_id == tenant_id,
    ).all()
    return [link.student_id for link in links]


def generate_digest(
    db: Session,
    *,
    parent_id: UUID,
    tenant_id: UUID,
    days: int = 7,
) -> dict[str, Any]:
    """Generate a weekly digest for a parent covering attendance, marks, and AI usage."""
    child_ids: list[UUID] = _get_child_ids(db, parent_id, tenant_id)
    if not child_ids:
        return {"children": [], "period_days": days, "message": "No linked children found."}

    since: date = date.today() - timedelta(days=days)
    children_data = []
    children: List[User] = db.query(User).filter(User.id.in_(child_ids)).all()
    children_by_id: dict[Column[UUID], User] = {child.id: child for child in children}
    attendance_rows: List[Row[Tuple[UUID, int, Any]]] = db.query(
        Attendance.student_id,
        func.count(Attendance.student_id),
        func.sum(case((Attendance.status == "present", 1), else_=0)),
    ).filter(
        Attendance.tenant_id == tenant_id,
        Attendance.student_id.in_(child_ids),
        Attendance.date >= since,
    ).group_by(Attendance.student_id).all()
    attendance_by_child: dict[Any, dict[str, int]] = {
        student_id: {
            "total_days": int(total or 0),
            "present_days": int(present or 0),
        }
        for student_id, total, present in attendance_rows
    }
    enrolled_child_ids: set[Column[UUID]] = {
        enrollment.student_id
        for enrollment in db.query(Enrollment).filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.student_id.in_(child_ids),
        ).all()
    }
    mark_rows: List[Row[Tuple[Mark, Exam]]] = db.query(Mark, Exam).join(
        Exam,
        Mark.exam_id == Exam.id,
    ).filter(
        Mark.tenant_id == tenant_id,
        Mark.student_id.in_(child_ids),
    ).order_by(Mark.student_id.asc(), Mark.id.desc()).all()
    recent_marks_by_child: dict[UUID, list[dict[str, Any]]] = {}
    for mark, exam in mark_rows:
        if mark.student_id not in enrolled_child_ids:
            continue
        entries: list[dict[str, Any]] = recent_marks_by_child.setdefault(mark.student_id, [])
        if len(entries) >= 10:
            continue
        entries.append({
            "exam": exam.name,
            "marks_obtained": mark.marks_obtained,
            "max_marks": exam.max_marks,
            "percentage": round(marks_obtained / exam.max_marks * 100) if (marks_obtained := mark.marks_obtained) and exam.max_marks > 0 else 0,
        })
    ai_usage_rows: List[Row[Tuple[UUID, int]]] = db.query(
        AIQuery.user_id,
        func.count(AIQuery.id),
    ).filter(
        AIQuery.tenant_id == tenant_id,
        AIQuery.user_id.in_(child_ids),
    ).group_by(AIQuery.user_id).all()
    ai_sessions_by_child: dict[Any, int] = {user_id: int(count or 0) for user_id, count in ai_usage_rows}

    for child_id in child_ids:
        child: User | None = children_by_id.get(child_id)
        if not child:
            continue

        attendance: dict[str, int] = attendance_by_child.get(child_id, {"total_days": 0, "present_days": 0})
        total_att: int = attendance["total_days"]
        present_att: int = attendance["present_days"]
        attendance_pct: int | None = round(present_att / total_att * 100) if total_att > 0 else None

        children_data.append({
            "student_id": str(child_id),
            "student_name": child.full_name,
            "attendance": {
                "total_days": total_att,
                "present_days": present_att,
                "percentage": attendance_pct,
            },
            "recent_marks": recent_marks_by_child.get(child_id, []),
            "ai_study_sessions": ai_sessions_by_child.get(child_id, 0),
        })

    return {
        "period_days": days,
        "generated_date": str(date.today()),
        "children": children_data,
    }


def render_digest_html(digest: dict[str, Any]) -> str:
    """Render digest data as a simple HTML email body."""
    parts: list[str] = [
        "<html><body style='font-family:sans-serif;max-width:600px;margin:auto;'>",
        f"<h2>📋 Weekly Digest — {digest.get('generated_date', '')}</h2>",
    ]
    for child in digest.get("children", []):
        parts.append(f"<h3>{child['student_name']}</h3>")
        att = child.get("attendance", {})
        if att.get("percentage") is not None:
            parts.append(f"<p><strong>Attendance:</strong> {att['percentage']}% ({att['present_days']}/{att['total_days']} days)</p>")
        else:
            parts.append("<p><strong>Attendance:</strong> No records this week</p>")

        marks = child.get("recent_marks", [])
        if marks:
            parts.append("<p><strong>Recent Marks:</strong></p><ul>")
            for m in marks[:5]:
                parts.append(f"<li>{m['exam']}: {m['marks_obtained']}/{m['max_marks']} ({m['percentage']}%)</li>")
            parts.append("</ul>")

        parts.append(f"<p><strong>AI Study Sessions:</strong> {child.get('ai_study_sessions', 0)}</p>")
        parts.append("<hr/>")

    parts.append("<p style='color:#888;font-size:12px;'>Sent by VidyaOS</p></body></html>")
    return "".join(parts)


def send_parent_digest(db: Session, parent: User, days: int = 7) -> bool:
    """Send the weekly digest email to a parent. Returns True if sent."""
    if not parent.email:
        return False

    digest: dict[str, Any] = generate_digest(
        db,
        parent_id=parent.id,
        tenant_id=parent.tenant_id,
        days=days,
    )
    if not digest.get("children"):
        return False

    subject: str = f"VidyaOS Weekly Digest — {digest.get('generated_date', '')}".strip()
    html_body: str = render_digest_html(digest)
    send_email(
        to_address=parent.email,
        subject=subject,
        html_body=html_body,
    )
    return True


def send_weekly_digests(db: Session, days: int = 7) -> dict[str, int]:
    """Send weekly digests to all parents across tenants."""
    sent = 0
    skipped = 0

    parents: List[User] = db.query(User).filter(User.role == "parent").all()
    for parent in parents:
        try:
            if send_parent_digest(db, parent, days=days):
                sent += 1
            else:
                skipped += 1
        except Exception as exc:
            skipped += 1
            logger.warning("Digest send failed for parent %s: %s", parent.id, exc)

    return {"sent": sent, "skipped": skipped}
