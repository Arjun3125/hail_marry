"""Admin-specific context assembler for Mascot conversations."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from uuid import UUID

from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


@dataclass
class AdminContext:
    """Context snapshot for admin Mascot conversations."""

    admin_name: str
    user_id: str
    tenant_id: str

    total_students: int = 0
    present_today: int = 0
    absent_today: int = 0
    attendance_pct: float = 0.0
    open_alerts: int = 0
    alert_summaries: list[str] = field(default_factory=list)  # first 3 alert titles
    queue_pending: int = 0
    fee_defaulters_count: int = 0

    def to_prompt_context(self) -> str:
        alerts_text = "; ".join(self.alert_summaries[:3]) or "None"
        return "\n".join([
            f"ADMIN: {self.admin_name}",
            f"STUDENTS: {self.total_students} total | Present: {self.present_today} | Absent: {self.absent_today}",
            f"ATTENDANCE: {self.attendance_pct:.1f}%",
            f"OPEN ALERTS: {self.open_alerts} — {alerts_text}",
            f"AI QUEUE PENDING: {self.queue_pending}",
            f"FEE DEFAULTERS: {self.fee_defaulters_count}",
        ])


def assemble_admin_context(
    db: Session, user_id: UUID, tenant_id: UUID, admin_name: str
) -> AdminContext:
    """
    Build AdminContext. Each DB query is wrapped in try/except — never raises.
    """
    ctx = AdminContext(
        admin_name=admin_name,
        user_id=str(user_id),
        tenant_id=str(tenant_id),
    )

    today = date.today()

    # Total enrolled students
    try:
        from src.domains.academic.models.core import Enrollment
        ctx.total_students = (
            db.query(Enrollment)
            .filter(Enrollment.tenant_id == tenant_id)
            .count()
        )
    except Exception as e:
        logger.warning("AdminContext: failed to load enrollment count for %s: %s", tenant_id, e)

    # Today's attendance counts
    try:
        from src.domains.academic.models.attendance import Attendance
        today_rows = (
            db.query(Attendance)
            .filter(Attendance.tenant_id == tenant_id, Attendance.date == today)
            .all()
        )
        ctx.present_today = sum(1 for r in today_rows if r.status != "absent")
        ctx.absent_today = sum(1 for r in today_rows if r.status == "absent")
        total = ctx.present_today + ctx.absent_today
        ctx.attendance_pct = (ctx.present_today / total * 100) if total > 0 else 0.0
    except Exception as e:
        logger.warning("AdminContext: failed to load attendance counts for %s: %s", tenant_id, e)

    # Open incidents / alerts
    try:
        from src.domains.administrative.models.incident import Incident
        alert_rows = (
            db.query(Incident)
            .filter(Incident.tenant_id == tenant_id, Incident.status == "open")
            .order_by(Incident.created_at.desc())
            .limit(3)
            .all()
        )
        ctx.open_alerts = (
            db.query(Incident)
            .filter(Incident.tenant_id == tenant_id, Incident.status == "open")
            .count()
        )
        ctx.alert_summaries = [r.title for r in alert_rows]
    except Exception as e:
        logger.warning("AdminContext: failed to load alerts for %s: %s", tenant_id, e)

    # AI job queue — pending or running jobs
    try:
        from src.domains.platform.models.ai_job import AIJob
        ctx.queue_pending = (
            db.query(AIJob)
            .filter(
                AIJob.tenant_id == tenant_id,
                AIJob.status.in_(["pending", "running"]),
            )
            .count()
        )
    except Exception as e:
        logger.warning("AdminContext: failed to load AI queue for %s: %s", tenant_id, e)

    # Fee defaulters — students with overdue invoices
    try:
        from src.domains.administrative.models.fee import FeeInvoice
        from sqlalchemy import func as sqlfunc
        ctx.fee_defaulters_count = (
            db.query(sqlfunc.count(sqlfunc.distinct(FeeInvoice.student_id)))
            .filter(
                FeeInvoice.tenant_id == tenant_id,
                FeeInvoice.status == "overdue",
            )
            .scalar() or 0
        )
    except Exception as e:
        logger.warning("AdminContext: failed to load fee defaulters for %s: %s", tenant_id, e)

    return ctx
