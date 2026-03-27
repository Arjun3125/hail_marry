"""AI query log with trace support."""
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func, Boolean
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class AIQuery(Base):
    __tablename__ = "ai_queries"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=True, index=True)
    query_text = Column(Text, nullable=False)
    mode = Column(String(50), nullable=False, default="qa")
    response_text = Column(Text, nullable=True)
    token_usage = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    trace_id = Column(String(64), nullable=True)
    citation_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    # History management fields
    title = Column(String(200), nullable=True)
    is_pinned = Column(Boolean, default=False)
    folder_id = Column(UUID(as_uuid=True), ForeignKey("ai_folders.id"), nullable=True)
    deleted_at = Column(DateTime(timezone=True), nullable=True)


class AIFolder(Base):
    __tablename__ = "ai_folders"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    color = Column(String(20), default="blue")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
