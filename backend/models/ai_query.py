"""AI query log with trace support."""
import uuid
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class AIQuery(Base):
    __tablename__ = "ai_queries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    mode = Column(String(50), nullable=False, default="qa")  # qa, study_guide, quiz, concept_map, weak_topic
    response_text = Column(Text, nullable=True)
    token_usage = Column(Integer, nullable=True)
    response_time_ms = Column(Integer, nullable=True)
    trace_id = Column(String(64), nullable=True)
    citation_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
