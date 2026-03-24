"""Compliance export and deletion-tracking models."""
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from database import Base

class ComplianceExport(Base):
    __tablename__ = "compliance_exports"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    export_type = Column(String(50), nullable=False, default="tenant_bundle")
    scope_type = Column(String(50), nullable=False, default="tenant")
    scope_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    format = Column(String(20), nullable=False, default="zip")
    status = Column(String(30), nullable=False, default="pending")
    file_path = Column(Text, nullable=True)
    file_size = Column(Integer, nullable=True)
    checksum = Column(String(128), nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class DeletionRequest(Base):
    __tablename__ = "deletion_requests"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    requested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    target_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    status = Column(String(30), nullable=False, default="requested")
    reason = Column(Text, nullable=True)
    resolution_note = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    resolved_at = Column(DateTime(timezone=True), nullable=True)
