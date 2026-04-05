"""Common Pydantic schemas used across routes."""
from pydantic import BaseModel, ConfigDict
from typing import Optional, Generic, TypeVar, List
from uuid import UUID

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


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
    logo_url: Optional[str] = None
    primary_color: Optional[str] = None
    secondary_color: Optional[str] = None
    accent_color: Optional[str] = None
    font_family: Optional[str] = None
    theme_style: Optional[str] = None

    class Config:
        from_attributes = True
