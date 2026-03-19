"""Persistent AI job and event history."""
import uuid

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database import Base


class AIJob(Base):
    __tablename__ = "ai_jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    job_type = Column(String(100), nullable=False, index=True)
    status = Column(String(30), nullable=False, index=True)
    trace_id = Column(String(255), nullable=True, index=True)
    priority = Column(Integer, nullable=True)
    attempts = Column(Integer, nullable=False, default=0)
    max_retries = Column(Integer, nullable=False, default=0)
    worker_id = Column(String(255), nullable=True)
    error = Column(Text, nullable=True)
    request_payload = Column(JSONB, nullable=True)
    result_payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now(), onupdate=func.now())
    started_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)


class AIJobEvent(Base):
    __tablename__ = "ai_job_events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    ai_job_id = Column(UUID(as_uuid=True), ForeignKey("ai_jobs.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    stage = Column(String(100), nullable=False, index=True)
    source = Column(String(100), nullable=False)
    detail = Column(Text, nullable=True)
    event_timestamp = Column(DateTime(timezone=True), nullable=False)
    payload = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
