"""Auth-related Pydantic schemas."""
from typing import Optional
from uuid import UUID

from pydantic import BaseModel


class StrictBaseModel(BaseModel):
    class Config:
        extra = "forbid"


class GoogleLoginRequest(StrictBaseModel):
    token: str


class TokenResponse(StrictBaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(StrictBaseModel):
    class Config:
        extra = "forbid"
        orm_mode = True
        from_attributes = True

    id: UUID
    tenant_id: UUID
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool


class UserCreateRequest(StrictBaseModel):
    email: str
    full_name: str
    role: str = "student"
    tenant_id: UUID
