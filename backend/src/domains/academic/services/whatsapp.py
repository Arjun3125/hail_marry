"""WhatsApp Business API integration for parent notifications.

Uses the official WhatsApp Business Cloud API (Meta).
Set WHATSAPP_TOKEN and WHATSAPP_PHONE_NUMBER_ID in your environment.

Usage:
    from src.domains.academic.services.whatsapp import send_whatsapp_message, send_attendance_alert, send_weekly_digest
"""
try:
    import httpx
except ModuleNotFoundError:  # Lightweight test environments
    class _HTTPStatusError(Exception):
        def __init__(self, *args, response=None, **kwargs) -> None:
            super().__init__(*args)
            self.response = response

    class _HTTPXStub:
        AsyncClient = None
        HTTPStatusError = _HTTPStatusError

    httpx = _HTTPXStub()
import os
import logging
from typing import Any


from httpx import Response


from constants import attendance_emoji

logger: logging.Logger = logging.getLogger(__name__)

WHATSAPP_API_URL = "https://graph.facebook.com/v18.0"
WHATSAPP_TOKEN: str = os.getenv("WHATSAPP_TOKEN", "")
WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_NUMBER_ID", "")


async def send_whatsapp_message(to_phone: str, message: str) -> dict[str, Any]:
    """Send a plain-text WhatsApp message to a phone number.

    Args:
        to_phone: recipient phone with country code (e.g. "919876543210")
        message: text body to send

    Returns:
        WhatsApp API response dict, or error dict on failure.
    """
    if not WHATSAPP_TOKEN or not WHATSAPP_PHONE_ID:
        logger.warning("WhatsApp credentials not configured. Message not sent.")
        return {"success": False, "error": "WhatsApp not configured"}

    url: str = f"{WHATSAPP_API_URL}/{WHATSAPP_PHONE_ID}/messages"
    headers: dict[str, str] = {
        "Authorization": f"Bearer {WHATSAPP_TOKEN}",
        "Content-Type": "application/json",
    }
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone,
        "type": "text",
        "text": {"body": message},
    }

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            resp: Response = await client.post(url, json=payload, headers=headers)
            resp.raise_for_status()
            return {"success": True, "data": resp.json()}
    except (httpx.HTTPStatusError, _HTTPStatusError) as e:
        logger.error("WhatsApp API error: %s — %s", e.response.status_code, e.response.text)
        return {"success": False, "error": str(e)}
    except Exception as e:
        logger.error("WhatsApp send failed: %s", str(e))
        return {"success": False, "error": str(e)}


async def send_attendance_alert(
    to_phone: str,
    student_name: str,
    date_str: str,
    status: str,
    school_name: str = "VidyaOS School",
) -> dict:
    """Send an attendance alert to a parent via WhatsApp."""
    if status == "absent":
        msg: str = (
            f"🔴 Attendance Alert — {school_name}\n\n"
            f"Dear Parent,\n"
            f"Your child *{student_name}* was marked *absent* on {date_str}.\n\n"
            f"If this was planned, please ignore this message. "
            f"Otherwise, please contact the school.\n\n"
            f"— VidyaOS"
        )
    else:
        msg: str = (
            f"✅ Attendance Update — {school_name}\n\n"
            f"Your child *{student_name}* was marked *{status}* on {date_str}.\n\n"
            f"— VidyaOS"
        )
    return await send_whatsapp_message(to_phone, msg)


async def send_weekly_digest(
    to_phone: str,
    student_name: str,
    attendance_pct: int,
    avg_marks: int,
    top_subject: str,
    weak_subject: str,
    school_name: str = "VidyaOS School",
) -> dict:
    """Send a weekly performance digest to a parent via WhatsApp."""
    msg: str = (
        f"📊 Weekly Report — {school_name}\n\n"
        f"Student: *{student_name}*\n"
        f"──────────────\n"
        f"📅 Attendance: *{attendance_pct}%*\n"
        f"📈 Avg Marks: *{avg_marks}%*\n"
        f"⭐ Best Subject: *{top_subject}*\n"
        f"⚠️ Needs Work: *{weak_subject}*\n\n"
        f"Keep encouraging your child!\n"
        f"— VidyaOS"
    )
    return await send_whatsapp_message(to_phone, msg)


async def send_exam_result(
    to_phone: str,
    student_name: str,
    exam_name: str,
    marks_obtained: int,
    max_marks: int,
    school_name: str = "VidyaOS School",
) -> dict:
    """Send an exam result notification to a parent via WhatsApp."""
    pct: int = round(marks_obtained / max_marks * 100) if max_marks > 0 else 0
    emoji: str = attendance_emoji(pct)
    msg: str = (
        f"{emoji} Exam Result — {school_name}\n\n"
        f"Student: *{student_name}*\n"
        f"Exam: *{exam_name}*\n"
        f"Score: *{marks_obtained}/{max_marks}* ({pct}%)\n\n"
        f"— VidyaOS"
    )
    return await send_whatsapp_message(to_phone, msg)
