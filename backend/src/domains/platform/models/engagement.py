"""Engagement and motivation models."""
import uuid
from sqlalchemy import Column, Date, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from database import Base

class LoginStreak(Base):
    __tablename__ = "login_streaks"
    id = Column(PG_UUID(as_uuid=True), primary_key=True, server_default="gen_random_uuid()")
    tenant_id = Column(PG_UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False)
    user_id = Column(PG_UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True)
    current_streak = Column(Integer, default=0, nullable=False)
    longest_streak = Column(Integer, default=0, nullable=False)
    total_sessions = Column(Integer, default=0, nullable=False)
    last_login_date = Column(Date, nullable=True)
