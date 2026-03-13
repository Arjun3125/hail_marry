"""SMS utility for operational notifications."""
from __future__ import annotations

import logging
from typing import Any

import httpx

from config import settings

logger = logging.getLogger(__name__)


def send_sms(*, to_number: str, message: str) -> dict[str, Any]:
    if not settings.sms.enabled:
        return {"sent": False, "skipped": True, "reason": "sms_disabled"}

    provider = (settings.sms.provider or "twilio").lower()
    if provider != "twilio":
        return {"sent": False, "error": f"Unsupported SMS provider '{provider}'"}

    if not settings.sms.account_sid or not settings.sms.auth_token or not settings.sms.from_number:
        return {"sent": False, "error": "SMS provider credentials are missing"}

    url = f"https://api.twilio.com/2010-04-01/Accounts/{settings.sms.account_sid}/Messages.json"
    payload = {
        "To": to_number,
        "From": settings.sms.from_number,
        "Body": message,
    }

    try:
        with httpx.Client(timeout=10) as client:
            response = client.post(url, data=payload, auth=(settings.sms.account_sid, settings.sms.auth_token))
            response.raise_for_status()
            data = response.json()
    except Exception as exc:
        logger.exception("SMS dispatch failed to %s", to_number)
        return {"sent": False, "error": str(exc)}

    return {
        "sent": True,
        "provider": provider,
        "sid": data.get("sid"),
    }
