from pydantic import BaseModel

class FeatureFlagBase(BaseModel):
    feature_id: str
    name: str
    description: str | None = None
    category: str
    module: str | None = None
    ai_intensity: str | None = None
    enabled: bool

class FeatureFlagResponse(FeatureFlagBase):
    id: int

    class Config:
        from_attributes = True

class FeatureFlagToggleRequest(BaseModel):
    enabled: bool
