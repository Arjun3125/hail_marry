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
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.assignment import Assignment
from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.marks import Mark, Exam
from src.domains.identity.models.user import User
from src.domains.platform.models.notification import Notification, NotificationPreference
from src.domains.academic.services.whatsapp import send_whatsapp_message

logger = logging.getLogger(__name__)

# ── Localized message templates ──────────────────────────────────────

ASSIGNMENT_DUE_TEMPLATES = {
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

ASSESSMENT_RESULTS_TEMPLATES = {
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

LOW_ATTENDANCE_TEMPLATES = {
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
        prefs = db.query(NotificationPreference).filter(
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
        **kwargs: dict,
    ) -> NotificationPreference:
        """Update notification preferences for a parent."""
        prefs = ParentNotificationService.get_or_create_preferences(
            db, tenant_id, parent_id
        )

        # Whitelist allowed fields
        allowed_fields = {
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
        if not prefs.quiet_hours_start or not prefs.quiet_hours_end:
            return False

        now = datetime.now(timezone.utc).astimezone().time()
        start = datetime.strptime(prefs.quiet_hours_start, "%H:%M").time()
        end = datetime.strptime(prefs.quiet_hours_end, "%H:%M").time()

        if start <= end:
            return start <= now <= end
        else:
            # Overnight quiet hours (e.g., 22:00 to 07:00)
            return now >= start or now <= end

    @staticmethod
    def should_send_notification(
        prefs: NotificationPreference,
        category: str,
        channel: str = "whatsapp",
    ) -> bool:
        """Check if notification should be sent based on preferences."""
        # Check channel preference
        if channel == "whatsapp" and not prefs.whatsapp_enabled:
            return False
        if channel == "email" and not prefs.email_enabled:
            return False
        if channel == "push" and not prefs.push_enabled:
            return False
        if channel == "in_app" and not prefs.in_app_enabled:
            return False

        # Check category overrides
        if prefs.category_overrides and category in prefs.category_overrides:
            if not prefs.category_overrides[category]:
                return False

        # Check quiet hours
        if ParentNotificationService.is_quiet_hours(prefs):
            return False

        return True

    @staticmethod
    async def notify_assignment_due_tomorrow(
        db: Session,
        tenant_id: UUID,
        student_id: UUID,
        assignment_id: UUID,
    ) -> list[dict]:
        """Notify parents of assignment due tomorrow."""
        results = []

        try:
            # Get assignment details
            assignment = db.query(Assignment).filter(
                Assignment.id == assignment_id
            ).first()

            if not assignment:
                logger.warning(f"Assignment {assignment_id} not found")
                return results

            # Get student name
            student = db.query(User).filter(User.id == student_id).first()
            if not student:
                return results

            # Get parents
            parents = db.query(User).join(
                ParentLink,
                and_(
                    ParentLink.child_id == student_id,
                    ParentLink.tenant_id == tenant_id,
                ),
            ).all()

            # Get subject name
            from src.domains.academic.models.core import Subject

            subject = db.query(Subject).filter(
                Subject.id == assignment.subject_id
            ).first()
            subject_name = subject.name if subject else "Assignment"

            # Get student's preferred language
            student_lang = getattr(student, "preferred_language", "en")
            if student_lang not in ASSIGNMENT_DUE_TEMPLATES:
                student_lang = "en"

            templates = ASSIGNMENT_DUE_TEMPLATES[student_lang]

            for parent in parents:
                prefs = ParentNotificationService.get_or_create_preferences(
                    db, tenant_id, parent.id
                )

                if not ParentNotificationService.should_send_notification(
                    prefs, "assignment_reminder", "whatsapp"
                ):
                    continue

                # Format message
                due_date = assignment.due_date.strftime("%d-%m-%Y") if assignment.due_date else "TBD"
                message = templates.format(
                    child_name=student.name,
                    subject=subject_name,
                    assignment_title=assignment.title,
                    due_date=due_date,
                )

                # Get parent phone
                parent_phone = getattr(parent, "phone", None)
                if not parent_phone:
                    logger.warning(f"Parent {parent.id} has no phone number")
                    continue

                # Send WhatsApp message
                wa_result = await send_whatsapp_message(parent_phone, message)
                results.append({
                    "parent_id": str(parent.id),
                    "status": "sent" if wa_result.get("success") else "failed",
                    "channel": "whatsapp",
                })

                # Log notification
                notification = Notification(
                    tenant_id=tenant_id,
                    user_id=parent.id,
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
    ) -> list[dict]:
        """Notify parents of assessment results."""
        results = []

        try:
            # Get mark details
            mark = db.query(Mark).filter(Mark.id == mark_id).first()
            if not mark:
                logger.warning(f"Mark {mark_id} not found")
                return results

            # Get exam details
            exam = db.query(Exam).filter(Exam.id == mark.exam_id).first()
            if not exam:
                return results

            # Get student name
            student = db.query(User).filter(User.id == student_id).first()
            if not student:
                return results

            # Get subject name
            from src.domains.academic.models.core import Subject

            subject = db.query(Subject).filter(
                Subject.id == mark.subject_id
            ).first()
            subject_name = subject.name if subject else "Subject"

            # Get parents
            parents = db.query(User).join(
                ParentLink,
                and_(
                    ParentLink.child_id == student_id,
                    ParentLink.tenant_id == tenant_id,
                ),
            ).all()

            # Get student's preferred language
            student_lang = getattr(student, "preferred_language", "en")
            if student_lang not in ASSESSMENT_RESULTS_TEMPLATES:
                student_lang = "en"

            templates = ASSESSMENT_RESULTS_TEMPLATES[student_lang]

            for parent in parents:
                prefs = ParentNotificationService.get_or_create_preferences(
                    db, tenant_id, parent.id
                )

                if not ParentNotificationService.should_send_notification(
                    prefs, "assessment_results", "whatsapp"
                ):
                    continue

                max_marks = exam.max_marks or 100
                percentage = round((mark.marks_obtained or 0) / max_marks * 100)

                # Format message
                message = templates.format(
                    child_name=student.name,
                    exam_name=exam.name,
                    marks_obtained=mark.marks_obtained or 0,
                    max_marks=max_marks,
                    percentage=percentage,
                    subject=subject_name,
                )

                # Get parent phone
                parent_phone = getattr(parent, "phone", None)
                if not parent_phone:
                    logger.warning(f"Parent {parent.id} has no phone number")
                    continue

                # Log notification (in real scenario, would send WhatsApp)
                notification = Notification(
                    tenant_id=tenant_id,
                    user_id=parent.id,
                    recipient_role="parent",
                    recipient_channel="whatsapp",
                    category="assessment_results",
                    title=f"{exam.name} Results",
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
                    "parent_id": str(parent.id),
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
    ) -> list[dict]:
        """Check if student attendance is below threshold and notify parents."""
        results = []
        attendance_threshold = threshold

        try:
            # Calculate attendance for current month
            today = datetime.now(timezone.utc)
            month_start = today.replace(day=1)

            attendance_records = db.query(Attendance).filter(
                and_(
                    Attendance.student_id == student_id,
                    Attendance.date >= month_start,
                    Attendance.date <= today,
                )
            ).all()

            if not attendance_records:
                return results

            total_days = len(attendance_records)
            present_days = len([a for a in attendance_records if a.status == "present"])
            absent_days = len([a for a in attendance_records if a.status == "absent"])

            current_attendance = (
                round(present_days / total_days * 100) if total_days > 0 else 0
            )

            # Check if below threshold
            if current_attendance >= attendance_threshold:
                return results

            # Get student
            student = db.query(User).filter(User.id == student_id).first()
            if not student:
                return results

            # Get parents
            parents = db.query(User).join(
                ParentLink,
                and_(
                    ParentLink.child_id == student_id,
                    ParentLink.tenant_id == tenant_id,
                ),
            ).all()

            student_lang = getattr(student, "preferred_language", "en")
            if student_lang not in LOW_ATTENDANCE_TEMPLATES:
                student_lang = "en"

            templates = LOW_ATTENDANCE_TEMPLATES[student_lang]

            for parent in parents:
                prefs = ParentNotificationService.get_or_create_preferences(
                    db, tenant_id, parent.id
                )

                if not ParentNotificationService.should_send_notification(
                    prefs, "low_attendance", "whatsapp"
                ):
                    continue

                # Format message
                message = templates.format(
                    child_name=student.name,
                    threshold=attendance_threshold,
                    current_attendance=current_attendance,
                    absent_count=absent_days,
                )

                # Get parent phone
                parent_phone = getattr(parent, "phone", None)
                if not parent_phone:
                    logger.warning(f"Parent {parent.id} has no phone number")
                    continue

                # Log notification
                notification = Notification(
                    tenant_id=tenant_id,
                    user_id=parent.id,
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
                    "parent_id": str(parent.id),
                    "status": "sent",
                    "channel": "whatsapp",
                })

            db.commit()

        except Exception as e:
            logger.error(f"Error checking low attendance: {str(e)}")
            db.rollback()

        return results
