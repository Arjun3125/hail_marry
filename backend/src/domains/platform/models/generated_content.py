"""GeneratedContent model for storing AI-generated artifacts like quizzes and mind maps."""
import uuid

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB, UUID

from database import Base


class GeneratedContent(Base):
    """Stores AI-generated content like quizzes, flashcards, and visual artifacts."""

    __tablename__ = "generated_content"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    notebook_id = Column(UUID(as_uuid=True), ForeignKey("notebooks.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    type = Column(String(50), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    content = Column(JSONB, nullable=False)
    source_query = Column(Text, nullable=True)
    parent_conversation_id = Column(UUID(as_uuid=True), ForeignKey("ai_queries.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(DateTime(timezone=True), server_default=text("CURRENT_TIMESTAMP"))
    is_archived = Column(Boolean, nullable=False, default=False)
