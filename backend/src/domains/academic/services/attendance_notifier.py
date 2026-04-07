"""Automated Attendance Workflows — parent notification on absence.

This module provides the automated trigger that fires when a teacher
marks a student absent. It:
1. Looks up the student's linked parent(s) via the ParentLink model
2. Sends a localized WhatsApp notification to each parent
3. Supports both individual and bulk attendance marking
4. Tracks notification delivery in the audit trail

Indian context: Parents in Tier 2-3 cities rely heavily on WhatsApp
for school communication. An absence alert at 9:30 AM (after roll
call) is the #1 most-requested notification by Indian parents.
"""
from __future__ import annotations

import logging
from uuid import UUID

from database import SessionLocal
from src.domains.academic.models.parent_link import ParentLink
from src.domains.identity.models.user import User

logger = logging.getLogger(__name__)

# ── Localized message templates ──────────────────────────────────────
ABSENCE_TEMPLATES = {
    "en": (
        "📋 Attendance Alert\n\n"
        "Your child *{child_name}* was marked *absent* today ({date}) "
        "in class *{class_name}*.\n\n"
        "If this is incorrect, please contact the school office."
    ),
    "hi": (
        "📋 उपस्थिति सूचना\n\n"
        "आपके बच्चे *{child_name}* को आज ({date}) "
        "कक्षा *{class_name}* में *अनुपस्थित* चिह्नित किया गया है।\n\n"
        "अगर यह गलत है, तो कृपया स्कूल कार्यालय से संपर्क करें।"
    ),
}

LATE_TEMPLATES = {
    "en": (
        "⏰ Late Arrival Alert\n\n"
        "Your child *{child_name}* arrived *late* today ({date}) "
        "for class *{class_name}*."
    ),
    "hi": (
        "⏰ देरी सूचना\n\n"
        "आपके बच्चे *{child_name}* आज ({date}) "
        "कक्षा *{class_name}* में *देर* से पहुँचे।"
    ),
}

STREAK_ALERT_TEMPLATES = {
    "en": (
        "⚠️ Attendance Concern\n\n"
        "Your child *{child_name}* has been absent for "
        "*{streak_days} consecutive days*.\n\n"
        "The school counselor may reach out. "
        "Please contact us if you need support."
    ),
    "hi": (
        "⚠️ उपस्थिति चिंता\n\n"
        "आपके बच्चे *{child_name}* *{streak_days} लगातार दिन* "
        "अनुपस्थित रहे हैं।\n\n"
        "स्कूल काउंसलर संपर्क कर सकते हैं। "
        "कृपया सहायता के लिए हमसे संपर्क करें।"
    ),
}


async def notify_parents_on_absence(
    *,
    tenant_id: str,
    student_id: str,
    class_name: str,
    date_str: str,
    status: str = "absent",
    consecutive_absent_days: int = 0,
) -> list[dict]:
    """Send attendance notification to all linked parents of a student.

    Args:
        tenant_id: School tenant ID
        student_id: The student whose attendance changed
        class_name: Human-readable class name ("Class 10 A")
        date_str: Date of attendance ("2026-04-06")
        status: "absent" or "late"
        consecutive_absent_days: If >2, triggers a streak concern alert

    Returns:
        List of dispatch results per parent
    """
    db = SessionLocal()
    results = []

    try:
        # 1. Look up the student
        student = db.query(User).filter(User.id == UUID(student_id)).first()
        if not student:
            logger.warning("Student %s not found for attendance notification", student_id)
            return []

        child_name = student.full_name or student.email or "your child"
        locale = student.preferred_locale or "en"

        # 2. Find all linked parents
        parent_links = db.query(ParentLink).filter(
            ParentLink.child_id == UUID(student_id),
            ParentLink.tenant_id == UUID(tenant_id),
        ).all()

        if not parent_links:
            logger.info("No parent links for student %s — skipping notification", student_id)
            return []

        # 3. Select the right template
        if consecutive_absent_days >= 3:
            templates = STREAK_ALERT_TEMPLATES
            category = "behavior_alert"
        elif status == "late":
            templates = LATE_TEMPLATES
            category = "attendance"
        else:
            templates = ABSENCE_TEMPLATES
            category = "attendance"

        title = {
            "attendance": "Attendance Alert",
            "behavior_alert": "Attendance Concern",
        }.get(category, "School Update")

        # 4. Dispatch to each parent
        from src.domains.platform.services.notification_dispatch import dispatch_notification

        for link in parent_links:
            parent = db.query(User).filter(User.id == link.parent_id).first()
            if not parent:
                continue

            parent_locale = parent.preferred_locale or locale
            parent_body = templates.get(parent_locale, templates["en"]).format(
                child_name=child_name,
                date=date_str,
                class_name=class_name,
                streak_days=consecutive_absent_days,
            )

            result = await dispatch_notification(
                tenant_id=tenant_id,
                recipient_id=str(link.parent_id),
                recipient_role="parent",
                category=category,
                title=title,
                body=parent_body,
                body_locale=parent_locale,
                data={
                    "student_id": student_id,
                    "date": date_str,
                    "status": status,
                    "class_name": class_name,
                },
                triggered_by="system",
                related_entity_type="attendance",
                related_entity_id=student_id,
                preferred_channel="whatsapp",  # WhatsApp-first for Indian parents
            )
            results.extend(result)

        logger.info(
            "Attendance notification dispatched for student %s to %d parent(s)",
            student_id, len(parent_links),
        )

    except Exception:
        logger.exception("Failed to send attendance notification for student %s", student_id)
    finally:
        db.close()

    return results


async def notify_parents_bulk_absence(
    *,
    tenant_id: str,
    absences: list[dict],
) -> int:
    """Bulk-dispatch attendance notifications for multiple students.

    Args:
        tenant_id: School tenant ID
        absences: List of dicts with keys: student_id, class_name, date, status

    Returns:
        Number of notifications dispatched
    """
    total_sent = 0
    for entry in absences:
        results = await notify_parents_on_absence(
            tenant_id=tenant_id,
            student_id=entry["student_id"],
            class_name=entry.get("class_name", ""),
            date_str=entry.get("date", ""),
            status=entry.get("status", "absent"),
            consecutive_absent_days=entry.get("consecutive_absent_days", 0),
        )
        total_sent += len([r for r in results if r.get("status") in ("sent", "delivered")])

    return total_sent
