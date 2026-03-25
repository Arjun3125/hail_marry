from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from database import get_db

from src.domains.platform.schemas.feature_flags import FeatureFlagResponse, FeatureFlagToggleRequest
from src.domains.platform.services.feature_flags import get_all_feature_flags, toggle_feature_flag, apply_system_profile

router = APIRouter(prefix="/features", tags=["Feature Flags"])

@router.get("", response_model=List[FeatureFlagResponse])
def get_features(db: Session = Depends(get_db)):
    """
    Retrieve all feature flags categorized as AI or Non-AI.
    """
    return get_all_feature_flags(db)

@router.post("/{feature_id}/toggle", response_model=FeatureFlagResponse)
def toggle_feature(
    feature_id: str,
    payload: FeatureFlagToggleRequest,
    db: Session = Depends(get_db)
):
    """
    return toggle_feature_flag(db, feature_id, payload.enabled)

@router.post("/profile/{profile_name}")
def apply_profile(profile_name: str, db: Session = Depends(get_db)):
    """
    Apply predefined system modes ("ai_tutor", "ai_helper", "full_erp")
    """
    if profile_name not in ["ai_tutor", "ai_helper", "full_erp"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=400, detail="Invalid profile name")
    
    return apply_system_profile(db, profile_name)
