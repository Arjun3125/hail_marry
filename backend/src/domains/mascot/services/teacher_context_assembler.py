"""Teacher-specific context assembler for Mascot conversations."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.timetable import Timetable
from src.domains.identity.models.user import User

logger = logging.getLogger(__name__)


@dataclass
class TeacherContext:
    """Context snapshot for teacher Mascot conversations."""

    teacher_name: str
    user_id: str
    tenant_id: str

    todays_classes: list[dict] = field(default_factory=list)   # [{class_id, class_name, subject_id, start_time}]
    absent_count_today: int = 0
    absent_students: list[str] = field(default_factory=list)   # first 5 names
    pending_review_count: int = 0                               # ungraded submissions
    weakest_class_topic: Optional[str] = None
    consecutive_absentees: list[str] = field(default_factory=list)  # absent 2+ days

    def to_prompt_context(self) -> str:
        classes_text = ", ".join(
            f"{c.get('class_name', '?')} ({c.get('start_time', '?')})"
            for c in self.todays_classes[:3]
        ) or "None scheduled"
        absentees = ", ".join(self.absent_students[:5]) or "None"
        consecutive = ", ".join(self.consecutive_absentees[:3]) or "None"
        return "\n".join([
            f"TEACHER: {self.teacher_name}",
            f"TODAY'S CLASSES: {classes_text}",
            f"ABSENT TODAY: {self.absent_count_today} students — {absentees}",
            f"CONSECUTIVE ABSENTEES (2+ days): {consecutive}",
            f"PENDING REVIEWS: {self.pending_review_count} ungraded submissions",
            f"WEAKEST CLASS TOPIC: {self.weakest_class_topic or 'Unknown'}",
        ])


def assemble_teacher_context(
    db: Session, user_id: UUID, tenant_id: UUID, teacher_name: str
) -> TeacherContext:
    """
    Build TeacherContext. Each DB query is wrapped in try/except — never raises.
    """
    ctx = TeacherContext(
        teacher_name=teacher_name,
        user_id=str(user_id),
        tenant_id=str(tenant_id),
    )

    today = date.today()
    day_of_week = today.weekday()  # 0=Mon … 6=Sun

    # Today's classes from timetable
    try:
        from src.domains.academic.models.core import Class as AcademicClass
        rows = (
            db.query(Timetable, AcademicClass)
            .join(AcademicClass, Timetable.class_id == AcademicClass.id)
            .filter(
                Timetable.teacher_id == user_id,
                Timetable.tenant_id == tenant_id,
                Timetable.day_of_week == day_of_week,
            )
            .all()
        )
        ctx.todays_classes = [
            {
                "class_id": str(tt.class_id),
                "class_name": cls.name if cls else "Unknown",
                "subject_id": str(tt.subject_id),
                "start_time": tt.start_time.strftime("%H:%M") if tt.start_time else "TBD",
            }
            for tt, cls in rows
        ]
    except Exception as e:
        logger.warning("TeacherContext: failed to load timetable for %s: %s", user_id, e)

    # Absent students today across teacher's classes
    try:
        class_ids = [UUID(c["class_id"]) for c in ctx.todays_classes]
        if class_ids:
            absent_rows = (
                db.query(Attendance, User)
                .join(User, Attendance.student_id == User.id)
                .filter(
                    Attendance.tenant_id == tenant_id,
                    Attendance.class_id.in_(class_ids),
                    Attendance.date == today,
                    Attendance.status == "absent",
                )
                .limit(20)
                .all()
            )
            ctx.absent_count_today = len(absent_rows)
            ctx.absent_students = [u.full_name or u.email for _, u in absent_rows[:5]]
    except Exception as e:
        logger.warning("TeacherContext: failed to load absent students for %s: %s", user_id, e)

    # Consecutive absentees (absent yesterday AND today)
    try:
        yesterday = today - timedelta(days=1)
        class_ids = [UUID(c["class_id"]) for c in ctx.todays_classes]
        if class_ids:
            absent_today_ids = set(
                row.student_id
                for row in db.query(Attendance).filter(
                    Attendance.tenant_id == tenant_id,
                    Attendance.class_id.in_(class_ids),
                    Attendance.date == today,
                    Attendance.status == "absent",
                ).all()
            )
            absent_yesterday_ids = set(
                row.student_id
                for row in db.query(Attendance).filter(
                    Attendance.tenant_id == tenant_id,
                    Attendance.class_id.in_(class_ids),
                    Attendance.date == yesterday,
                    Attendance.status == "absent",
                ).all()
            )
            consecutive_ids = absent_today_ids & absent_yesterday_ids
            if consecutive_ids:
                users = db.query(User).filter(User.id.in_(consecutive_ids)).limit(5).all()
                ctx.consecutive_absentees = [u.full_name or u.email for u in users]
    except Exception as e:
        logger.warning("TeacherContext: failed to load consecutive absentees for %s: %s", user_id, e)

    # Pending reviews — assignments created by this teacher with ungraded submissions
    try:
        teacher_assignment_ids = [
            row.id
            for row in db.query(Assignment).filter(
                Assignment.tenant_id == tenant_id,
                Assignment.created_by == user_id,
            ).all()
        ]
        if teacher_assignment_ids:
            ctx.pending_review_count = (
                db.query(AssignmentSubmission)
                .filter(
                    AssignmentSubmission.tenant_id == tenant_id,
                    AssignmentSubmission.assignment_id.in_(teacher_assignment_ids),
                    AssignmentSubmission.grade.is_(None),
                )
                .count()
            )
    except Exception as e:
        logger.warning("TeacherContext: failed to load pending reviews for %s: %s", user_id, e)

    # weakest_class_topic: not populated in this phase — requires doubt heatmap
    # or per-class mark averages which are computed by background jobs (Sub-project 3).

    return ctx
