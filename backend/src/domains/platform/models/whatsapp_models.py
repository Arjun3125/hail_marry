"""WhatsApp conversational access — database models.

Tables:
- phone_user_link: Maps a WhatsApp phone number to a VidyaOS User (tenant-scoped).
- whatsapp_sessions: Active conversation sessions (Redis is primary; Postgres is durable backup).
- whatsapp_messages: Audit log of all inbound and outbound WhatsApp messages.
"""
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database import Base


class PhoneUserLink(Base):
    """Links a WhatsApp phone number (E.164) to a VidyaOS ERP user account."""
    __tablename__ = "phone_user_link"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False, index=True)  # e.g. "919876543210"
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False, index=True)
    verified = Column(Boolean, nullable=False, default=False, server_default="false")
    verified_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    __table_args__ = (
        # One phone number per tenant (a parent could have accounts in two schools)
        {"sqlite_autoincrement": True},
    )


class WhatsAppSession(Base):
    """Active WhatsApp conversation session (Redis is the hot store; this is the durable backup)."""
    __tablename__ = "whatsapp_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False, unique=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    role = Column(String(20), nullable=False)  # student, teacher, parent, admin
    active_child_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    session_data = Column(JSONB, nullable=False, default=dict)  # conversation_history, context
    last_activity = Column(DateTime(timezone=True), server_default=func.now())
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class WhatsAppMessage(Base):
    """Audit log entry for every WhatsApp message (inbound and outbound)."""
    __tablename__ = "whatsapp_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    phone = Column(String(20), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    direction = Column(String(10), nullable=False)  # 'inbound' | 'outbound'
    message_type = Column(String(20), nullable=False, default="text")  # text, list, image, audio, document
    content = Column(Text, nullable=False)
    wa_message_id = Column(String(100), nullable=True)  # Meta's message ID (for dedup)
    intent = Column(String(50), nullable=True)  # classified intent
    tool_called = Column(String(100), nullable=True)  # ERP tool invoked
    latency_ms = Column(Integer, nullable=True)  # response time
    status = Column(String(20), default="delivered")  # sent, delivered, read, failed
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
