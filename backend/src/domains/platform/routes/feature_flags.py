from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import Column
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from database import get_db
from src.domains.identity.models.user import User
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.models.feature_flag import FeatureFlag
from src.domains.platform.schemas.feature_flags import FeatureFlagResponse, FeatureFlagToggleRequest
from src.domains.platform.services.feature_flags import get_all_feature_flags, toggle_feature_flag, apply_system_profile

router = APIRouter(prefix="/api/features", tags=["Feature Flags"])


def _record_audit_log(
    db: Session,
    current_user: User,
    *,
    action: str,
    entity_type: str,
    metadata: dict,
) -> None:
    db.add(
        AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=action,
            entity_type=entity_type,
            metadata_=metadata,
        )
    )
    db.commit()


@router.get("", response_model=List[FeatureFlagResponse])
def get_features(
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> List[FeatureFlag]:
    """
    Retrieve all feature flags categorized as AI or Non-AI.
    """
    _: User = current_user
    return get_all_feature_flags(db)


@router.post("/{feature_id}/toggle", response_model=FeatureFlagResponse)
def toggle_feature(
    feature_id: str,
    payload: FeatureFlagToggleRequest,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
) -> FeatureFlag:
    """
    Toggle a specific platform feature flag on or off.
    """
    feature: FeatureFlag | None = db.query(FeatureFlag).filter(FeatureFlag.feature_id == feature_id).first()
    if not feature:
        raise HTTPException(status_code=404, detail=f"Feature '{feature_id}' not found.")

    previous_enabled: Column[bool] = feature.enabled
    updated: FeatureFlag = toggle_feature_flag(db, feature_id, payload.enabled)
    _record_audit_log(
        db,
        current_user,
        action="feature_flag.toggled",
        entity_type="feature_flag",
        metadata={
            "feature_id": feature_id,
            "old_enabled": previous_enabled,
            "new_enabled": updated.enabled,
        },
    )
    db.refresh(updated)
    return updated


@router.post("/profile/{profile_name}")
def apply_profile(
    profile_name: str,
    current_user: User = Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """
    Apply predefined system modes ("ai_tutor", "ai_helper", "full_erp")
    """
    if profile_name not in ["ai_tutor", "ai_helper", "full_erp"]:
        raise HTTPException(status_code=400, detail="Invalid profile name")

    result = apply_system_profile(db, profile_name)
    _record_audit_log(
        db,
        current_user,
        action="feature_profile.applied",
        entity_type="tenant",
        metadata={
            "profile_name": profile_name,
            "features_updated": result.get("features_updated", 0),
        },
    )
    return result
