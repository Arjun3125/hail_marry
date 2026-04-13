"""Parent-student relationship link model."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING
from sqlalchemy import Column, String, ForeignKey, DateTime, func, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from database import Base

if TYPE_CHECKING:
    from src.domains.identity.models.user import User

class ParentLink(Base):
    __tablename__ = "parent_links"
    id: Column[uuid.UUID] = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    parent_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    child_id: Column[uuid.UUID] = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    relationship_type: Column[str] = Column(String(50), default="parent")
    created_at: Column[datetime] = Column(DateTime(timezone=True), server_default=func.now())
    parent: User = relationship("User", foreign_keys=[parent_id], lazy="select")
    child: User = relationship("User", foreign_keys=[child_id], lazy="select")

    __table_args__ = (
        UniqueConstraint("tenant_id", "parent_id", "child_id", name="uq_parent_child_per_tenant"),
    )
