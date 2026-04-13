"""Parent event-based notifications service.

Emits WhatsApp notifications for key events:
- Assignment due tomorrow
- Student absent (already handled by attendance_notifier)
- Assessment results
- Low attendance warning

Respects parent notification preferences (quiet hours, channel toggles).
"""
from __future__ import annotations

import logging
from datetime import datetime, time, timezone
from typing import Any, List, Optional, cast
from uuid import UUID

import importlib
from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.domains.academic.models.core import Subject
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.assignment import Assignment
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Exam, Mark
from src.domains.identity.models.user import User
from src.domains.platform.models.notification import Notification, NotificationPreference

whatsapp = cast(Any, importlib.import_module("src.domains.academic.services.whatsapp"))

logger: logging.Logger = logging.getLogger(__name__)

# ── Localized message templates ──────────────────────────────────────

ASSIGNMENT_DUE_TEMPLATES: dict[str, str] = {
    "en": (
        "📝 *{child_name}* has an assignment due tomorrow!\n"
        "Subject: *{subject}*\n"
        "Title: {assignment_title}\n"
        "Due: {due_date}\n\n"
        "Pls ensure timely submission. — VidyaOS"
    ),
    "hi": (
        "📝 *{child_name}* का कल असाइनमेंट है!\n"
        "विषय: *{subject}*\n"
        "शीर्षक: {assignment_title}\n"
        "समय सीमा: {due_date}\n\n"
        "समय पर जमा करने को कहें। — VidyaOS"
    ),
}

ASSESSMENT_RESULTS_TEMPLATES: dict[str, str] = {
    "en": (
        "✅ Exam results ready!\n"
        "*{child_name}* scored {marks_obtained}/{max_marks} ({percentage}%)\n"
        "Exam: {exam_name}\n"
        "Subject: {subject}\n\n"
        "View full report in VidyaOS app."
    ),
    "hi": (
        "✅ परीक्षा परिणाम तैयार!\n"
        "*{child_name}* को {marks_obtained}/{max_marks} ({percentage}%) मिले\n"
        "परीक्षा: {exam_name}\n"
        "विषय: {subject}\n\n"
        "VidyaOS ऐप में पूरी रिपोर्ट देखें।"
    ),
}

LOW_ATTENDANCE_TEMPLATES: dict[str, str] = {
    "en": (
        "⚠️ Attendance Alert!\n"
        "*{child_name}* attendance: {current_attendance}%\n"
        "Threshold: {threshold}% | Absent: {absent_count} days\n\n"
        "Pls ensure regular attendance. — VidyaOS"
    ),
    "hi": (
        "⚠️ उपस्थिति चेतावनी!\n"
        "*{child_name}* की उपस्थिति: {current_attendance}%\n"
        "सीमा: {threshold}% | अनुपस्थिति: {absent_count} दिन\n\n"
        "नियमित उपस्थिति सुनिश्चित करें। — VidyaOS"
    ),
}


class ParentNotificationService:
    """Service for managing parent event notifications."""

    @staticmethod
    def get_or_create_preferences(
        db: Session, tenant_id: UUID, parent_id: UUID
    ) -> NotificationPreference:
        """Get or create notification preferences for a parent."""
        prefs: NotificationPreference | None = db.query(NotificationPreference).filter(
            and_(
                NotificationPreference.tenant_id == tenant_id,
                NotificationPreference.user_id == parent_id,
            )
        ).first()

        if not prefs:
            prefs = NotificationPreference(
                tenant_id=tenant_id,
                user_id=parent_id,
                whatsapp_enabled=True,
                email_enabled=True,
                push_enabled=True,
            )
            db.add(prefs)
            db.commit()
            db.refresh(prefs)

        return prefs

    @staticmethod
    def update_preferences(
        db: Session,
        tenant_id: UUID,
        parent_id: UUID,
        **kwargs: Any,
    ) -> NotificationPreference:
        """Update notification preferences for a parent."""
        prefs: NotificationPreference = ParentNotificationService.get_or_create_preferences(
            db, tenant_id, parent_id
        )

        # Whitelist allowed fields
        allowed_fields: set[str] = {
            "whatsapp_enabled",
            "sms_enabled",
            "email_enabled",
            "push_enabled",
            "in_app_enabled",
            "quiet_hours_start",
            "quiet_hours_end",
            "category_overrides",
        }

        for key, value in kwargs.items():
            if key in allowed_fields:
                setattr(prefs, key, value)

        db.commit()
        db.refresh(prefs)
        return prefs

    @staticmethod
    def is_quiet_hours(prefs: NotificationPreference) -> bool:
        """Check if current time is in quiet hours."""
        quiet_start = cast(Optional[str], getattr(prefs, "quiet_hours_start", None))
        quiet_end = cast(Optional[str], getattr(prefs, "quiet_hours_end", None))

        if not quiet_start or not quiet_end:
            return False

        now: time = datetime.now(timezone.utc).astimezone().time()
        start: time = datetime.strptime(quiet_start, "%H:%M").time()
        end: time = datetime.strptime(quiet_end, "%H:%M").time()

        if start <= end:
            return start <= now <= end
        return now >= start or now <= end

    @staticmethod
    def should_send_notification(
        prefs: NotificationPreference,
        category: str,
        channel: str = "whatsapp",
    ) -> bool:
        """Check if notification should be sent based on preferences."""
        whatsapp_enabled = bool(
            cast(Optional[bool], getattr(prefs, "whatsapp_enabled", False))
        )
        email_enabled = bool(
            cast(Optional[bool], getattr(prefs, "email_enabled", False))
        )
        push_enabled = bool(
            cast(Optional[bool], getattr(prefs, "push_enabled", False))
        )
        in_app_enabled = bool(
            cast(Optional[bool], getattr(prefs, "in_app_enabled", False))
        )

        if channel == "whatsapp" and not whatsapp_enabled:
            return False
        if channel == "email" and not email_enabled:
            return False
        if channel == "push" and not push_enabled:
            return False
        if channel == "in_app" and not in_app_enabled:
            return False

        category_overrides = cast(
            Optional[dict[str, bool]],
            getattr(prefs, "category_overrides", None),
        )
        if category_overrides and category in category_overrides:
            if not category_overrides[category]:
                return False

        if ParentNotificationService.is_quiet_hours(prefs):
            return False

        return True

    @staticmethod
    async def notify_assignment_due_tomorrow(
        db: Session,
        tenant_id: UUID,
        student_id: UUID,
        assignment_id: UUID,
    ) -> list[dict[str, Any]]:
        """Notify parents of assignment due tomorrow."""
        results: list[dict[str, Any]] = []

        try:
            # Get assignment details
            assignment: Assignment | None = db.query(Assignment).filter(
                Assignment.id == assignment_id
            ).first()

            if not assignment:
                logger.warning(f"Assignment {assignment_id} not found")
                return results

            # Get student name
            student: User | None = db.query(User).filter(User.id == student_id).first()
            if not student:
                return results

            # Get parents
            parents: List[User] = db.query(User).join(
                ParentLink,
                and_(
                    ParentLink.child_id == student_id,
                    ParentLink.tenant_id == tenant_id,
                ),
            ).all()

            subject: Subject | None = db.query(Subject).filter(
                Subject.id == getattr(assignment, "subject_id", None)
            ).first()
            subject_name: str = cast(str, getattr(subject, "name", "Assignment"))

            student_lang: str = cast(str, getattr(student, "preferred_language", "en"))
            if student_lang not in ASSIGNMENT_DUE_TEMPLATES:
                student_lang = "en"
            templates = ASSIGNMENT_DUE_TEMPLATES[student_lang]

            student_name = cast(str, getattr(student, "name", "Student"))
            assignment_title = cast(str, getattr(assignment, "title", ""))
            due_date_value = getattr(assignment, "due_date", None)
            due_date = (
                due_date_value.strftime("%d-%m-%Y") if due_date_value else "TBD"
            )

            for parent in parents:
                parent_id = getattr(parent, "id", None)
                if not isinstance(parent_id, UUID):
                    continue

                prefs: NotificationPreference = ParentNotificationService.get_or_create_preferences(
                    db, tenant_id, parent_id
                )
                if not ParentNotificationService.should_send_notification(
                    prefs, "assignment_reminder", "whatsapp"
                ):
                    continue

                message = templates.format(
                    child_name=student_name,
                    subject=subject_name,
                    assignment_title=assignment_title,
                    due_date=due_date,
                )

                parent_phone = cast(Optional[str], getattr(parent, "phone", None))
                if not parent_phone:
                    logger.warning(f"Parent {parent_id} has no phone number")
                    continue

                wa_sender: Any = whatsapp.send_whatsapp_message
                wa_result = cast(
                    dict[str, Any],
                    await wa_sender(parent_phone, message),
                )
                results.append({
                    "parent_id": str(parent_id),
                    "status": "sent" if wa_result.get("success") else "failed",
                    "channel": "whatsapp",
                })

                notification = Notification(
                    tenant_id=tenant_id,
                    user_id=parent_id,
                    recipient_role="parent",
                    recipient_channel="whatsapp",
                    category="assignment_reminder",
                    title="Assignment Due Tomorrow",
                    body=message,
                    body_locale=student_lang,
                    triggered_by="system",
                    related_entity_type="assignment",
                    related_entity_id=assignment_id,
                    status="sent" if wa_result.get("success") else "failed",
                    sent_at=datetime.now(timezone.utc),
                )
                db.add(notification)

            db.commit()

        except Exception as e:
            logger.error(f"Error notifying assignment due: {str(e)}")
            db.rollback()

        return results

    @staticmethod
    def notify_assessment_results(
        db: Session,
        tenant_id: UUID,
        student_id: UUID,
        mark_id: UUID,
    ) -> list[dict[str, Any]]:
        """Notify parents of assessment results."""
        results: list[dict[str, Any]] = []

        try:
            mark: Mark | None = db.query(Mark).filter(Mark.id == mark_id).first()
            if not mark:
                logger.warning(f"Mark {mark_id} not found")
                return results

            exam: Exam | None = db.query(Exam).filter(
                Exam.id == getattr(mark, "exam_id", None)
            ).first()
            if not exam:
                return results

            student: User | None = db.query(User).filter(User.id == student_id).first()
            if not student:
                return results

            subject: Subject | None = db.query(Subject).filter(
                Subject.id == getattr(mark, "subject_id", None)
            ).first()
            subject_name: str = cast(str, getattr(subject, "name", "Subject"))

            parents: List[User] = db.query(User).join(
                ParentLink,
                and_(
                    ParentLink.child_id == student_id,
                    ParentLink.tenant_id == tenant_id,
                ),
            ).all()

            student_lang = cast(str, getattr(student, "preferred_language", "en"))
            if student_lang not in ASSESSMENT_RESULTS_TEMPLATES:
                student_lang = "en"
            templates = ASSESSMENT_RESULTS_TEMPLATES[student_lang]

            student_name = cast(str, getattr(student, "name", "Student"))
            exam_name = cast(str, getattr(exam, "name", "Exam"))
            max_marks = int(cast(Optional[int], getattr(exam, "max_marks", 100)) or 100)
            marks_obtained = int(cast(Optional[int], getattr(mark, "marks_obtained", 0)) or 0)
            percentage = round((marks_obtained / max_marks) * 100) if max_marks else 0

            for parent in parents:
                parent_id = getattr(parent, "id", None)
                if not isinstance(parent_id, UUID):
                    continue

                prefs: NotificationPreference = ParentNotificationService.get_or_create_preferences(
                    db, tenant_id, parent_id
                )
                if not ParentNotificationService.should_send_notification(
                    prefs, "assessment_results", "whatsapp"
                ):
                    continue

                message = templates.format(
                    child_name=student_name,
                    exam_name=exam_name,
                    marks_obtained=marks_obtained,
                    max_marks=max_marks,
                    percentage=percentage,
                    subject=subject_name,
                )

                parent_phone = cast(Optional[str], getattr(parent, "phone", None))
                if not parent_phone:
                    logger.warning(f"Parent {parent_id} has no phone number")
                    continue

                notification = Notification(
                    tenant_id=tenant_id,
                    user_id=parent_id,
                    recipient_role="parent",
                    recipient_channel="whatsapp",
                    category="assessment_results",
                    title=f"{exam_name} Results",
                    body=message,
                    body_locale=student_lang,
                    triggered_by="system",
                    related_entity_type="mark",
                    related_entity_id=mark_id,
                    status="sent",
                    sent_at=datetime.now(timezone.utc),
                )
                db.add(notification)
                results.append({
                    "parent_id": str(parent_id),
                    "status": "sent",
                    "channel": "whatsapp",
                })

            db.commit()

        except Exception as e:
            logger.error(f"Error notifying assessment results: {str(e)}")
            db.rollback()

        return results

    @staticmethod
    def check_and_notify_low_attendance(
        db: Session,
        tenant_id: UUID,
        student_id: UUID,
        threshold: int = 75,
    ) -> list[dict[str, Any]]:
        """Check if student attendance is below threshold and notify parents."""
        results: list[dict[str, Any]] = []
        attendance_threshold = threshold

        try:
            today: datetime = datetime.now(timezone.utc)
            month_start: datetime = today.replace(day=1)

            attendance_date_column: Any = getattr(Attendance, "date")
            attendance_records: List[Attendance] = db.query(Attendance).filter(
                and_(
                    Attendance.student_id == student_id,
                    attendance_date_column >= month_start,
                    attendance_date_column <= today,
                )
            ).all()

            if not attendance_records:
                return results

            total_days = len(attendance_records)
            present_days = sum(
                1
                for a in attendance_records
                if cast(str, getattr(a, "status", "")) == "present"
            )
            absent_days = sum(
                1
                for a in attendance_records
                if cast(str, getattr(a, "status", "")) == "absent"
            )

            current_attendance = (
                round(present_days / total_days * 100) if total_days > 0 else 0
            )

            if current_attendance >= attendance_threshold:
                return results

            student: User | None = db.query(User).filter(User.id == student_id).first()
            if not student:
                return results

            parents: List[User] = db.query(User).join(
                ParentLink,
                and_(
                    ParentLink.child_id == student_id,
                    ParentLink.tenant_id == tenant_id,
                ),
            ).all()

            student_lang = cast(str, getattr(student, "preferred_language", "en"))
            if student_lang not in LOW_ATTENDANCE_TEMPLATES:
                student_lang = "en"
            templates = LOW_ATTENDANCE_TEMPLATES[student_lang]
            student_name = cast(str, getattr(student, "name", "Student"))

            for parent in parents:
                parent_id = getattr(parent, "id", None)
                if not isinstance(parent_id, UUID):
                    continue

                prefs: NotificationPreference = ParentNotificationService.get_or_create_preferences(
                    db, tenant_id, parent_id
                )
                if not ParentNotificationService.should_send_notification(
                    prefs, "low_attendance", "whatsapp"
                ):
                    continue

                message = templates.format(
                    child_name=student_name,
                    threshold=attendance_threshold,
                    current_attendance=current_attendance,
                    absent_count=absent_days,
                )

                parent_phone = cast(Optional[str], getattr(parent, "phone", None))
                if not parent_phone:
                    logger.warning(f"Parent {parent_id} has no phone number")
                    continue

                notification = Notification(
                    tenant_id=tenant_id,
                    user_id=parent_id,
                    recipient_role="parent",
                    recipient_channel="whatsapp",
                    category="low_attendance",
                    title="Attendance Below Threshold",
                    body=message,
                    body_locale=student_lang,
                    triggered_by="system",
                    related_entity_type="attendance",
                    status="sent",
                    sent_at=datetime.now(timezone.utc),
                )
                db.add(notification)
                results.append({
                    "parent_id": str(parent_id),
                    "status": "sent",
                    "channel": "whatsapp",
                })

            db.commit()

        except Exception as e:
            logger.error(f"Error checking low attendance: {str(e)}")
            db.rollback()

        return results
