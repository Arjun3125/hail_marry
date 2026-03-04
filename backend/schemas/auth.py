"""Auth-related Pydantic schemas."""
from pydantic import BaseModel
from uuid import UUID
from typing import Optional


class GoogleLoginRequest(BaseModel):
    token: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: UUID
    tenant_id: UUID
    email: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class UserCreateRequest(BaseModel):
    email: str
    full_name: str
    role: str = "student"
    tenant_id: UUID
