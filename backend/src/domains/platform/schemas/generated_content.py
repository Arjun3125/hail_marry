"""Schemas for generated content API endpoints."""
from datetime import datetime
from typing import Optional, Any
from uuid import UUID

from pydantic import BaseModel, Field


class GeneratedContentBase(BaseModel):
    """Base generated content schema."""
    type: str = Field(..., pattern="^(quiz|flashcards|mindmap|flowchart|concept_map)$")
    title: Optional[str] = Field(None, max_length=255)
    content: dict  # JSON structure based on type
    source_query: Optional[str] = None


class GeneratedContentCreate(GeneratedContentBase):
    """Schema for creating generated content."""
    notebook_id: UUID
    parent_conversation_id: Optional[UUID] = None


class GeneratedContentUpdate(BaseModel):
    """Schema for updating generated content."""
    title: Optional[str] = Field(None, max_length=255)
    content: Optional[dict] = None
    is_archived: Optional[bool] = None


class GeneratedContentResponse(GeneratedContentBase):
    """Schema for generated content API responses."""
    id: UUID
    notebook_id: UUID
    user_id: UUID
    parent_conversation_id: Optional[UUID] = None
    created_at: datetime
    updated_at: datetime
    is_archived: bool
    
    class Config:
        from_attributes = True


class GeneratedContentListResponse(BaseModel):
    """Schema for list of generated content."""
    items: list[GeneratedContentResponse]
    total: int


class GeneratedContentFilter(BaseModel):
    """Filter parameters for listing generated content."""
    type: Optional[str] = None
    is_archived: Optional[bool] = False
    limit: int = Field(default=50, ge=1, le=100)
    offset: int = Field(default=0, ge=0)
