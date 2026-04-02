"""Application helpers for student dashboard workflows."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.academic.models.assignment import Assignment, AssignmentSubmission
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.core import Enrollment, Subject
from src.domains.academic.models.marks import Mark
from src.domains.academic.models.timetable import Timetable
from src.domains.identity.models.tenant import Tenant
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.document import Document


def build_student_dashboard_response(
    *,
    db: Session,
    tenant_id,
    user_id,
) -> dict:
    total_att = db.query(Attendance).filter(
        Attendance.tenant_id == tenant_id,
        Attendance.student_id == user_id,
    ).count()
    present_att = db.query(Attendance).filter(
        Attendance.tenant_id == tenant_id,
        Attendance.student_id == user_id,
        Attendance.status == "present",
    ).count()
    attendance_pct = round((present_att / total_att * 100) if total_att > 0 else 0)

    avg_marks_row = db.query(func.avg(Mark.marks_obtained)).filter(
        Mark.tenant_id == tenant_id,
        Mark.student_id == user_id,
    ).scalar()
    avg_marks = round(float(avg_marks_row)) if avg_marks_row else 0

    enrollment = db.query(Enrollment).filter(
        Enrollment.tenant_id == tenant_id,
        Enrollment.student_id == user_id,
    ).first()
    pending_assignments = 0
    if enrollment:
        subject_ids = [
            subject.id
            for subject in db.query(Subject).filter(
                Subject.tenant_id == tenant_id,
                Subject.class_id == enrollment.class_id,
            ).all()
        ]
        total_assignments = db.query(Assignment).filter(
            Assignment.tenant_id == tenant_id,
            Assignment.subject_id.in_(subject_ids),
        ).count()
        submitted = db.query(AssignmentSubmission).filter(
            AssignmentSubmission.tenant_id == tenant_id,
            AssignmentSubmission.student_id == user_id,
        ).count()
        pending_assignments = max(0, total_assignments - submitted)

    ai_today = db.query(AIQuery).filter(
        AIQuery.tenant_id == tenant_id,
        AIQuery.user_id == user_id,
        func.date(AIQuery.created_at) == date.today(),
    ).count()
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    ai_limit = tenant.ai_daily_limit if tenant else 50

    today_dow = datetime.now().weekday()
    upcoming = []
    if enrollment:
        slots = db.query(Timetable).filter(
            Timetable.tenant_id == tenant_id,
            Timetable.class_id == enrollment.class_id,
            Timetable.day_of_week == today_dow,
        ).order_by(Timetable.start_time).all()
        for slot in slots:
            subject = db.query(Subject).filter(
                Subject.id == slot.subject_id,
                Subject.tenant_id == tenant_id,
            ).first()
            upcoming.append(
                {
                    "subject": subject.name if subject else "Unknown",
                    "time": slot.start_time.strftime("%I:%M %p"),
                }
            )

    my_docs = db.query(Document).filter(
        Document.tenant_id == tenant_id,
        Document.uploaded_by == user_id,
    ).count()

    return {
        "attendance_pct": attendance_pct,
        "avg_marks": avg_marks,
        "pending_assignments": pending_assignments,
        "ai_queries_today": ai_today,
        "ai_queries_limit": ai_limit,
        "upcoming_classes": upcoming,
        "my_uploads": my_docs,
        "ai_insight": (
            f"Your average is {avg_marks}%. Focus on weak areas to improve."
            if avg_marks < 80
            else None
        ),
    }
