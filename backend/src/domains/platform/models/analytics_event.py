"""Warehouse-friendly analytics event records."""
import uuid

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database import Base


class AnalyticsEvent(Base):
    __tablename__ = "analytics_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    event_name = Column(String(100), nullable=False, index=True)
    event_family = Column(String(50), nullable=True, index=True)
    surface = Column(String(50), nullable=True, index=True)
    target = Column(String(100), nullable=True, index=True)
    channel = Column(String(30), nullable=True, index=True)
    value = Column(Float, nullable=False, default=1.0)
    event_date = Column(Date, nullable=False, server_default=func.current_date(), index=True)
    metadata_ = Column("metadata", JSONB, nullable=True)
    occurred_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), index=True)
