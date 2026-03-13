"""SMTP email utility for system notifications and digests."""
from __future__ import annotations

import logging
import smtplib
import ssl
from email.message import EmailMessage

from config import settings

logger = logging.getLogger(__name__)


def send_email(*, to_address: str, subject: str, html_body: str, text_body: str | None = None) -> None:
    """Send an email using SMTP settings."""
    if not settings.email.enabled:
        raise RuntimeError("Email sending is disabled. Set EMAIL_ENABLED=true to enable.")

    if not settings.email.host:
        raise RuntimeError("SMTP_HOST is required when email is enabled.")

    message = EmailMessage()
    from_header = settings.email.from_email
    if settings.email.from_name:
        from_header = f"{settings.email.from_name} <{settings.email.from_email}>"
    message["From"] = from_header
    message["To"] = to_address
    message["Subject"] = subject

    if text_body:
        message.set_content(text_body)
        message.add_alternative(html_body, subtype="html")
    else:
        message.set_content("This email requires an HTML-capable client.")
        message.add_alternative(html_body, subtype="html")

    context = ssl.create_default_context()
    with smtplib.SMTP(settings.email.host, settings.email.port, timeout=15) as server:
        if settings.email.use_tls:
            server.starttls(context=context)
        if settings.email.username:
            server.login(settings.email.username, settings.email.password or "")
        server.send_message(message)

    logger.info("Email sent to %s", to_address)
