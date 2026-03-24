"""Parent-student relationship link model."""
import uuid
from sqlalchemy import Column, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from database import Base

class ParentLink(Base):
    __tablename__ = "parent_links"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    parent_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    child_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    relationship_type = Column(String(50), default="parent")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        UniqueConstraint("parent_id", "child_id", name="uq_parent_child"),
    )
