"""Notebook model for subject-based organization."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlmodel import Field, SQLModel


class Notebook(SQLModel, table=True):
    """A notebook represents a subject-based workspace for study materials."""
    
    __tablename__ = "notebooks"
    
    id: Optional[UUID] = Field(default=None, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    name: str = Field(max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(max_length=100, default=None)
    color: str = Field(max_length=7, default="#6366f1")
    icon: str = Field(max_length=50, default="Book")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_active: bool = Field(default=True, index=True)
