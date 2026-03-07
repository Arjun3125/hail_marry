"""Common Pydantic schemas used across routes."""
from pydantic import BaseModel, ConfigDict

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")
from typing import Optional, Generic, TypeVar, List
from uuid import UUID

T = TypeVar("T")


class PaginationParams(StrictBaseModel):
    page: int = 1
    per_page: int = 20


class PaginatedResponse(StrictBaseModel, Generic[T]):
    items: List[T]
    total: int
    page: int
    per_page: int
    total_pages: int


class MessageResponse(StrictBaseModel):
    message: str
    success: bool = True


class TenantResponse(StrictBaseModel):
    id: UUID
    name: str
    plan_tier: str
    max_students: int
    ai_daily_limit: int

    class Config:
        from_attributes = True
