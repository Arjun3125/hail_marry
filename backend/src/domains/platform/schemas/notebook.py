"""Schemas for notebook API endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class NotebookBase(BaseModel):
    """Base notebook schema."""
    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    color: str = Field(default="#6366f1", max_length=7)
    icon: str = Field(default="Book", max_length=50)


class NotebookCreate(NotebookBase):
    """Schema for creating a notebook."""
    pass


class NotebookUpdate(BaseModel):
    """Schema for updating a notebook."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    subject: Optional[str] = Field(None, max_length=100)
    color: Optional[str] = Field(None, max_length=7)
    icon: Optional[str] = Field(None, max_length=50)
    is_active: Optional[bool] = None


class NotebookResponse(NotebookBase):
    """Schema for notebook API responses."""
    id: UUID
    user_id: UUID
    created_at: datetime
    updated_at: datetime
    is_active: bool
    
    class Config:
        from_attributes = True


class NotebookListResponse(BaseModel):
    """Schema for list of notebooks."""
    items: list[NotebookResponse]
    total: int


class NotebookStats(BaseModel):
    """Schema for notebook statistics."""
    document_count: int
    question_count: int
    quiz_count: int
    flashcard_count: int
    mindmap_count: int
    total_study_time: int  # in minutes
    last_accessed: Optional[datetime] = None


class NotebookExport(BaseModel):
    """Schema for notebook export."""
    notebook: NotebookResponse
    documents: list[dict]
    ai_history: list[dict]
    generated_content: list[dict]
    stats: NotebookStats
    exported_at: datetime


class BulkNotebookOperation(BaseModel):
    """Schema for bulk notebook operations."""
    notebook_ids: list[UUID]
    operation: str  # 'archive', 'delete', 'export'


class BulkOperationResult(BaseModel):
    """Schema for bulk operation results."""
    success: list[UUID]
    failed: list[dict]  # {id: UUID, error: str}
    total_processed: int
