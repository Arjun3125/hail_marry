"""Audit log model with JSONB metadata (from SaaS Starter Kit pattern)."""
import uuid
from sqlalchemy import Column, String, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base

class AuditLog(Base):
    __tablename__ = "audit_logs"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    action = Column(String(255), nullable=False)  # e.g. user.created, role.changed
    entity_type = Column(String(100), nullable=True)  # user, document, complaint
    entity_id = Column(UUID(as_uuid=True), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)  # Additional context
    ip_address = Column(String(45), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
