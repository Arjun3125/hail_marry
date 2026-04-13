"""Timetable and scheduling models."""
import uuid
import sqlalchemy
from datetime import time
from sqlalchemy.dialects import postgresql
from database import Base

class Timetable(Base):
    __tablename__ = "timetable"
    id: sqlalchemy.Column[uuid.UUID] = sqlalchemy.Column(postgresql.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id: sqlalchemy.Column[uuid.UUID] = sqlalchemy.Column(postgresql.UUID(as_uuid=True), sqlalchemy.ForeignKey("tenants.id"), nullable=False, index=True)
    class_id: sqlalchemy.Column[uuid.UUID] = sqlalchemy.Column(postgresql.UUID(as_uuid=True), sqlalchemy.ForeignKey("classes.id"), nullable=False)
    subject_id: sqlalchemy.Column[uuid.UUID] = sqlalchemy.Column(postgresql.UUID(as_uuid=True), sqlalchemy.ForeignKey("subjects.id"), nullable=False)
    teacher_id: sqlalchemy.Column[uuid.UUID] = sqlalchemy.Column(postgresql.UUID(as_uuid=True), sqlalchemy.ForeignKey("users.id"), nullable=False)
    day_of_week: sqlalchemy.Column[int] = sqlalchemy.Column(sqlalchemy.Integer, nullable=False)  # 0-6 (Mon-Sun)
    start_time: sqlalchemy.Column[time] = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    end_time: sqlalchemy.Column[time] = sqlalchemy.Column(sqlalchemy.Time, nullable=False)
    room_number: sqlalchemy.Column[str] = sqlalchemy.Column(sqlalchemy.String(50), nullable=True)
