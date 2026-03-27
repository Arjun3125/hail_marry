"""GeneratedContent model for storing AI-generated artifacts like quizzes, flashcards, mind maps."""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from sqlmodel import Field, SQLModel
from sqlalchemy.dialects.postgresql import JSONB


class GeneratedContent(SQLModel, table=True):
    """Stores AI-generated content like quizzes, flashcards, mind maps within a notebook."""
    
    __tablename__ = "generated_content"
    
    id: Optional[UUID] = Field(default=None, primary_key=True)
    notebook_id: UUID = Field(foreign_key="notebooks.id", index=True)
    user_id: UUID = Field(foreign_key="users.id", index=True)
    type: str = Field(max_length=50, index=True)  # 'quiz', 'flashcards', 'mindmap', 'flowchart', 'concept_map'
    title: Optional[str] = Field(max_length=255, default=None)
    content: dict = Field(sa_type=JSONB)  # Structured content based on type
    source_query: Optional[str] = None
    parent_conversation_id: Optional[UUID] = Field(foreign_key="ai_history.id", default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    is_archived: bool = Field(default=False)
