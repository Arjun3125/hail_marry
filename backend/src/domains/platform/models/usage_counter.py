"""Persistent usage counters for quotas, governance, and cost tracking."""
import uuid

from sqlalchemy import Column, Date, DateTime, Float, ForeignKey, Integer, String, text
from sqlalchemy.dialects.postgresql import UUID

from database import Base


class UsageCounter(Base):
    __tablename__ = "usage_counters"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    scope = Column(String(16), nullable=False, index=True, default="user", server_default="user")
    metric = Column(String(64), nullable=False, index=True)
    bucket_type = Column(String(16), nullable=False, index=True)
    bucket_start = Column(Date, nullable=False, index=True)
    count = Column(Integer, nullable=False, default=0, server_default="0")
    token_total = Column(Integer, nullable=False, default=0, server_default="0")
    cache_hits = Column(Integer, nullable=False, default=0, server_default="0")
    estimated_cost_units = Column(Float, nullable=False, default=0.0, server_default="0")
    last_model = Column(String(128), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
