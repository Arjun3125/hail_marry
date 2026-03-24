"""Dedicated observability persistence models."""
import uuid
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from database import Base

class TraceEventRecord(Base):
    __tablename__ = "trace_event_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    trace_id = Column(String(255), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    source = Column(String(100), nullable=False, index=True)
    stage = Column(String(100), nullable=False, index=True)
    status = Column(String(50), nullable=True, index=True)
    detail = Column(Text, nullable=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)

class ObservabilityAlertRecord(Base):
    __tablename__ = "observability_alert_records"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    alert_code = Column(String(100), nullable=False, index=True)
    severity = Column(String(30), nullable=False, index=True)
    status = Column(String(30), nullable=False, default="active", index=True)
    message = Column(Text, nullable=False)
    first_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    last_seen_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
    last_dispatched_at = Column(DateTime(timezone=True), nullable=True)
    delivery_count = Column(Integer, nullable=False, default=0)
    occurrence_count = Column(Integer, nullable=False, default=1)
    active = Column(Boolean, nullable=False, default=True, server_default="true", index=True)
    trace_id = Column(String(255), nullable=True, index=True)
    latest_payload = Column(JSONB, nullable=True)
    latest_metrics = Column(JSONB, nullable=True)

class ObservabilityAlertEvent(Base):
    __tablename__ = "observability_alert_events"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    alert_record_id = Column(UUID(as_uuid=True), ForeignKey("observability_alert_records.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    event_type = Column(String(50), nullable=False, index=True)
    detail = Column(Text, nullable=True)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
