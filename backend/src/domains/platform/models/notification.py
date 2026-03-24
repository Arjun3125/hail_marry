"""User notification model for durable storage."""
import uuid
from sqlalchemy import Column, String, Text, Boolean, DateTime, ForeignKey, func
from sqlalchemy.dialects.postgresql import UUID, JSONB
from database import Base

class Notification(Base):
    __tablename__ = "notifications"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    body = Column(Text, nullable=False)
    category = Column(String(50), nullable=False, default="info")
    data = Column(JSONB, nullable=True)
    read = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)
