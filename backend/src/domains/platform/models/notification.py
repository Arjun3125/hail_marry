"""Notification Event Bus — centralized outbound communication system.

All outbound messages (WhatsApp, SMS, Email, Push) are funneled through
a single Notification table. This provides:
- Full audit trail for parent communication (regulatory compliance)
- Unified retry/delivery tracking across channels
- Teacher smart inbox for viewing all sent/received communications
- Deduplication to prevent spam during automated workflows
"""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base


class Notification(Base):
    """A single outbound notification across any channel.

    Channels: whatsapp, sms, email, push, in_app
    Categories: attendance, homework, test_reminder, fee_reminder, report,
                behavior_alert, announcement, custom
    """
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)

    # ── Targeting ────────────────────────────────────────────────────
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    recipient_role = Column(String(20), nullable=True)            # parent, student, teacher, admin
    recipient_channel = Column(String(20), nullable=True, default="in_app")  # whatsapp, sms, email, push, in_app

    # ── Content ──────────────────────────────────────────────────────
    category = Column(String(50), nullable=False, default="info", index=True)
    title = Column(String(300), nullable=False)
    body = Column(Text, nullable=False)
    body_locale = Column(String(10), default="en")                # Language of the notification body
    data = Column(JSONB, nullable=True)                           # Structured payload for rich notifications

    # ── Delivery tracking ────────────────────────────────────────────
    read = Column(Boolean, nullable=False, default=False)
    status = Column(String(20), nullable=False, default="pending")  # pending, sent, delivered, failed, read
    sent_at = Column(DateTime(timezone=True), nullable=True)
    delivered_at = Column(DateTime(timezone=True), nullable=True)
    read_at = Column(DateTime(timezone=True), nullable=True)
    retry_count = Column(Integer, default=0)
    error_message = Column(Text, nullable=True)

    # ── Source context (who/what triggered this notification) ─────────
    triggered_by = Column(String(50), nullable=True)               # system, teacher, admin, automation
    triggered_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    related_entity_type = Column(String(50), nullable=True)        # attendance, assignment, invoice, etc.
    related_entity_id = Column(UUID(as_uuid=True), nullable=True)

    # ── Deduplication ────────────────────────────────────────────────
    idempotency_key = Column(String(200), nullable=True, unique=True, index=True)

    # ── Metadata ─────────────────────────────────────────────────────
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class NotificationPreference(Base):
    """Per-user notification channel preferences.

    Parents might prefer WhatsApp over email. Students might disable
    push notifications during exam week. Teachers want everything in-app.
    """
    __tablename__ = "notification_preferences"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)

    whatsapp_enabled = Column(Boolean, default=True)
    sms_enabled = Column(Boolean, default=False)
    email_enabled = Column(Boolean, default=True)
    push_enabled = Column(Boolean, default=True)
    in_app_enabled = Column(Boolean, default=True)

    # Category-level overrides: {"fee_reminder": false, "attendance": true}
    category_overrides = Column(JSONB, nullable=True)

    # Push notification device tokens (iOS/Android FCM tokens)
    device_tokens = Column(JSONB, nullable=True)  # Stored as JSON array of tokens
    
    quiet_hours_start = Column(String(5), nullable=True)  # "22:00" (IST)
    quiet_hours_end = Column(String(5), nullable=True)    # "07:00" (IST)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
