"""Parent-specific context assembler for Mascot conversations."""
from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import date
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Mark, Exam
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.parent_link import ParentLink
from src.domains.administrative.models.fee import FeeInvoice
from src.domains.identity.models.user import User

logger = logging.getLogger(__name__)


@dataclass
class ParentContext:
    """Context snapshot for parent Mascot conversations."""

    parent_name: str
    user_id: str
    tenant_id: str

    child_name: str = "your child"
    child_id: Optional[str] = None
    attendance_today: str = "Unknown"          # "Present" | "Absent" | "Unknown"
    attendance_pct: Optional[float] = None
    latest_marks: list[dict] = field(default_factory=list)   # [{subject_name, marks_obtained, max_marks}]
    weak_subjects: list[str] = field(default_factory=list)   # below 60%
    pending_homework_count: int = 0
    fee_due: bool = False
    fee_amount: Optional[float] = None
    next_ptm_date: Optional[str] = None

    def to_prompt_context(self) -> str:
        marks_text = ", ".join(
            f"{m.get('subject_name', '?')} {m.get('marks_obtained', '?')}/{m.get('max_marks', '?')}"
            for m in self.latest_marks[:3]
        ) or "No marks available"
        weak_text = ", ".join(self.weak_subjects) or "None"
        fee_text = f"Due ₹{self.fee_amount:.0f}" if self.fee_due and self.fee_amount else ("Due" if self.fee_due else "Paid/NA")
        return "\n".join([
            f"PARENT: {self.parent_name}",
            f"CHILD: {self.child_name} (id: {self.child_id or 'unknown'})",
            f"ATTENDANCE TODAY: {self.attendance_today}",
            f"ATTENDANCE %: {self.attendance_pct:.1f}%" if self.attendance_pct is not None else "ATTENDANCE %: Unknown",
            f"LATEST MARKS: {marks_text}",
            f"WEAK SUBJECTS: {weak_text}",
            f"PENDING HOMEWORK: {self.pending_homework_count}",
            f"FEE STATUS: {fee_text}",
        ])


def assemble_parent_context(
    db: Session, user_id: UUID, tenant_id: UUID, parent_name: str
) -> ParentContext:
    """
    Build ParentContext. Each DB query is wrapped in try/except — never raises.
    """
    ctx = ParentContext(
        parent_name=parent_name,
        user_id=str(user_id),
        tenant_id=str(tenant_id),
    )

    today = date.today()

    # Linked child
    child_id: Optional[UUID] = None
    try:
        link = (
            db.query(ParentLink)
            .filter(ParentLink.parent_id == user_id, ParentLink.tenant_id == tenant_id)
            .first()
        )
        if link:
            child_id = link.child_id
            ctx.child_id = str(child_id)
            child_user = db.query(User).filter(User.id == child_id).first()
            if child_user:
                ctx.child_name = child_user.full_name or child_user.email
    except Exception as e:
        logger.warning("ParentContext: failed to load parent link for %s: %s", user_id, e)

    if child_id is None:
        return ctx

    # Today's attendance
    try:
        att = (
            db.query(Attendance)
            .filter(
                Attendance.student_id == child_id,
                Attendance.tenant_id == tenant_id,
                Attendance.date == today,
            )
            .first()
        )
        if att:
            ctx.attendance_today = "Absent" if att.status == "absent" else "Present"
    except Exception as e:
        logger.warning("ParentContext: failed to load attendance for %s: %s", child_id, e)

    # Attendance percentage from student profile
    try:
        from src.domains.academic.models.student_profile import StudentProfile
        profile = (
            db.query(StudentProfile)
            .filter(StudentProfile.user_id == child_id, StudentProfile.tenant_id == tenant_id)
            .first()
        )
        if profile:
            ctx.attendance_pct = profile.attendance_pct
    except Exception as e:
        logger.warning("ParentContext: failed to load student profile for %s: %s", child_id, e)

    # Latest marks (join Mark → Exam for subject/max info)
    try:
        mark_rows = (
            db.query(Mark, Exam)
            .join(Exam, Mark.exam_id == Exam.id)
            .filter(Mark.student_id == child_id, Mark.tenant_id == tenant_id)
            .order_by(Exam.exam_date.desc())
            .limit(5)
            .all()
        )
        marks_list = []
        weak = []
        for mark, exam in mark_rows:
            pct = (mark.marks_obtained / exam.max_marks * 100) if exam.max_marks else 0
            marks_list.append({
                "subject_name": exam.name,
                "marks_obtained": mark.marks_obtained,
                "max_marks": exam.max_marks,
            })
            if pct < 60:
                weak.append(exam.name)
        ctx.latest_marks = marks_list
        ctx.weak_subjects = weak
    except Exception as e:
        logger.warning("ParentContext: failed to load marks for %s: %s", child_id, e)

    # Pending homework — unsubmitted assignments for child's class
    try:
        from src.domains.academic.models.core import Enrollment
        enrollment = (
            db.query(Enrollment)
            .filter(Enrollment.student_id == child_id, Enrollment.tenant_id == tenant_id)
            .first()
        )
        if enrollment:
            submitted_ids = {
                row.assignment_id
                for row in db.query(AssignmentSubmission).filter(
                    AssignmentSubmission.student_id == child_id,
                    AssignmentSubmission.tenant_id == tenant_id,
                ).all()
            }
            from src.domains.academic.models.core import Subject
            subject_ids = [
                s.id
                for s in db.query(Subject).filter(Subject.class_id == enrollment.class_id).all()
            ]
            if subject_ids:
                all_assignments = db.query(Assignment).filter(
                    Assignment.tenant_id == tenant_id,
                    Assignment.subject_id.in_(subject_ids),
                ).all()
                ctx.pending_homework_count = sum(
                    1 for a in all_assignments if a.id not in submitted_ids
                )
    except Exception as e:
        logger.warning("ParentContext: failed to load homework for %s: %s", child_id, e)

    # Fee status
    try:
        unpaid = (
            db.query(FeeInvoice)
            .filter(
                FeeInvoice.student_id == child_id,
                FeeInvoice.tenant_id == tenant_id,
                FeeInvoice.status.in_(["pending", "overdue"]),
            )
            .all()
        )
        if unpaid:
            ctx.fee_due = True
            ctx.fee_amount = sum(
                (inv.amount_due - inv.amount_paid) for inv in unpaid
            )
    except Exception as e:
        logger.warning("ParentContext: failed to load fee status for %s: %s", child_id, e)

    return ctx
