"""Auth-related Pydantic schemas."""
from pydantic import BaseModel, ConfigDict
from uuid import UUID
from typing import Optional

class StrictBaseModel(BaseModel):
    model_config = ConfigDict(extra="forbid")

class GoogleLoginRequest(StrictBaseModel):
    token: str

class TokenResponse(StrictBaseModel):
    access_token: str
    token_type: str = "bearer"

class UserResponse(StrictBaseModel):
    model_config = ConfigDict(from_attributes=True)

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
