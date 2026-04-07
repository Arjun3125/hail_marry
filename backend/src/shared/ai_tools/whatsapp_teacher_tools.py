"""LLM-callable WhatsApp tools for teachers.

These tools allow the Teacher WhatsApp Assistant to perform administrative
actions via natural language, such as marking attendance for a class
("Mark everyone present except Rohan") or parsing bulk homework grades.
"""
from __future__ import annotations

import logging
from datetime import datetime, timezone
from uuid import UUID

from langchain_core.tools import StructuredTool

from database import SessionLocal
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.services.attendance_notifier import notify_parents_bulk_absence
from src.domains.identity.models.user import User
from src.domains.platform.services.background_runtime import submit_async_job

logger = logging.getLogger(__name__)


def _normalize_name(value: str) -> str:
    return " ".join((value or "").lower().split())


def mark_batch_attendance(
    tenant_id: str,
    user_id: str,
    class_name: str,
    absent_student_names: list[str],
) -> str:
    """Mark attendance for a class. Defaults all to 'present', except listed names.
    
    Args:
        tenant_id: School tenant ID
        user_id: The teacher's user ID
        class_name: E.g., "Class 10 A"
        absent_student_names: List of names identified as absent.
    """
    db = SessionLocal()
    try:
        # 1. Fuzzy match students in this "class" 
        # (Assuming basic string matching for demo purposes)
        students = db.query(User).filter(
            User.tenant_id == UUID(tenant_id),
            User.role == "student"
        ).all()
        student_name_entries = [
            (_normalize_name(s.full_name), s)
            for s in students
            if s.full_name
        ]
        token_index: dict[str, list[int]] = {}
        for index, (normalized_name, _student) in enumerate(student_name_entries):
            for token in dict.fromkeys(normalized_name.split()):
                token_index.setdefault(token, []).append(index)

        absent_ids = []
        absent_records = []
        today = datetime.now(timezone.utc).date()
        today_date = today.strftime("%Y-%m-%d")

        for name in absent_student_names:
            name_lower = _normalize_name(name)
            candidate_indexes: list[int] = []
            seen_indexes: set[int] = set()
            for token in name_lower.split():
                for index in token_index.get(token, []):
                    if index not in seen_indexes:
                        seen_indexes.add(index)
                        candidate_indexes.append(index)
            if not candidate_indexes:
                candidate_indexes = list(range(len(student_name_entries)))
            for index in candidate_indexes:
                normalized_full_name, s = student_name_entries[index]
                if name_lower and name_lower in normalized_full_name:
                    absent_ids.append(s.id)
                    absent_records.append({
                        "student_id": str(s.id),
                        "class_name": class_name,
                        "date": today_date,
                        "status": "absent"
                    })
                    break
        student_ids = [s.id for s in students]
        if student_ids:
            try:
                existing_rows = db.query(Attendance).filter(
                    Attendance.student_id.in_(student_ids),
                    Attendance.date == today,
                ).all()
            except TypeError:
                existing_rows = []
        else:
            existing_rows = []
        existing_by_student = {row.student_id: row for row in existing_rows}

        # 2. Update DB
        for s in students:
            status = "absent" if s.id in absent_ids else "present"
            existing = existing_by_student.get(s.id)
            if not existing:
                att = Attendance(
                    tenant_id=UUID(tenant_id),
                    student_id=s.id,
                    date=today,
                    status=status
                )
                db.add(att)
            else:
                existing.status = status
                
        db.commit()
        
        # 3. Fire parent notifications
        if absent_records:
            try:
                submit_async_job(
                    "parent-attendance-notifications",
                    notify_parents_bulk_absence,
                    tenant_id=tenant_id,
                    absences=absent_records,
                )
            except Exception:
                logger.exception("Failed to enqueue parent attendance notifications")
                
        return f"✅ Attendance marked for {class_name}. {len(absent_ids)} students marked absent."
        
    except Exception as e:
        logger.exception("Failed to mark attendance via WhatsApp")
        return f"❌ Failed to mark attendance: {str(e)}"
    finally:
        db.close()


mark_attendance_tool = StructuredTool.from_function(
    func=mark_batch_attendance,
    name="mark_batch_attendance",
    description="Mark attendance for a class. Requires the class name and a list of absent student names."
)

TEACHER_ACTION_TOOLS = [
    mark_attendance_tool,
]
