import json
from pathlib import Path
from typing import List

from fastapi import Depends, HTTPException, status
from sqlalchemy import inspect
from sqlalchemy.orm import Session

from config import settings
from database import get_db
from src.domains.platform.models.feature_flag import FeatureFlag

CATALOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "features_catalog.json"


def _ensure_feature_flags_table(db: Session) -> None:
    """Create the feature_flags table on local/test databases when migrations have not run yet."""
    bind = db.get_bind()
    if bind is None:
        return
    inspector = inspect(bind)
    if "feature_flags" not in inspector.get_table_names():
        FeatureFlag.__table__.create(bind=bind, checkfirst=True)


def init_feature_flags(db: Session) -> None:
    """
    Reads the features catalog and upserts features into the database.
    Existing enabled states are preserved.
    """
    _ensure_feature_flags_table(db)

    if not CATALOG_PATH.exists():
        print("Warning: features_catalog.json not found. Skipping feature flag initialization.")
        return

    with open(CATALOG_PATH, "r", encoding="utf-8") as handle:
        catalog = json.load(handle)

    for item in catalog:
        existing = db.query(FeatureFlag).filter(FeatureFlag.feature_id == item["feature_id"]).first()
        if existing:
            existing.name = item["name"]
            existing.description = item.get("description", "")
            existing.category = item["category"]
            existing.module = item.get("module", "Platform Operations")
            existing.ai_intensity = item.get("ai_intensity", "No AI")
            continue

        db.add(
            FeatureFlag(
                feature_id=item["feature_id"],
                name=item["name"],
                description=item.get("description", ""),
                category=item["category"],
                module=item.get("module", "Platform Operations"),
                ai_intensity=item.get("ai_intensity", "No AI"),
                enabled=item.get("enabled", True),
            )
        )

    db.commit()


def get_all_feature_flags(db: Session) -> List[FeatureFlag]:
    return db.query(FeatureFlag).all()


def _bootstrap_feature_flags_if_empty(db: Session) -> None:
    """Self-heal empty demo/local databases where the table exists but the catalog was never populated."""
    _ensure_feature_flags_table(db)
    existing = db.query(FeatureFlag.id).limit(1).first()
    if existing is None:
        init_feature_flags(db)


def toggle_feature_flag(db: Session, feature_id: str, enabled: bool) -> FeatureFlag:
    flag = db.query(FeatureFlag).filter(FeatureFlag.feature_id == feature_id).first()
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_id}' not found.",
        )
    flag.enabled = enabled
    db.commit()
    db.refresh(flag)
    return flag


def apply_system_profile(db: Session, profile: str) -> dict:
    """
    Applies a predefined AI/ERP configuration mode.
    Valid profiles: "ai_tutor", "ai_helper", "full_erp".
    """
    flags = db.query(FeatureFlag).all()
    updated_count = 0

    for flag in flags:
        initial_state = flag.enabled

        if profile == "ai_tutor":
            if flag.ai_intensity == "Heavy AI" or flag.module == "Learning Management":
                flag.enabled = True
            elif flag.module in ["Finance", "Admissions", "Student Management", "Platform Operations"] and flag.ai_intensity == "No AI":
                flag.enabled = False

        elif profile == "ai_helper":
            if flag.ai_intensity in ["Medium AI", "Low AI", "No AI"]:
                flag.enabled = True
            elif flag.ai_intensity == "Heavy AI":
                flag.enabled = False

        elif profile == "full_erp":
            if flag.ai_intensity == "No AI" or flag.ai_intensity == "Low AI":
                flag.enabled = True
            elif flag.ai_intensity in ["Heavy AI", "Medium AI"]:
                flag.enabled = False

        if initial_state != flag.enabled:
            updated_count += 1

    db.commit()
    return {"success": True, "profile": profile, "features_updated": updated_count}


def require_feature(feature_id: str):
    """
    FastAPI dependency that blocks the request if the feature is disabled.
    Usage: Depends(require_feature("ai_chat"))
    """

    def dependency(db: Session = Depends(get_db)):
        _bootstrap_feature_flags_if_empty(db)
        flag = db.query(FeatureFlag).filter(FeatureFlag.feature_id == feature_id).first()
        if not flag:
            print(f"Warning: feature guard checked but missing: {feature_id}")
            if settings.app.demo_mode:
                print(f"Warning: allowing missing feature in demo mode: {feature_id}")
                return True
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_id}' is conditionally disabled.",
            )
        if not flag.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_id}' is currently disabled by the administrator.",
            )
        return True

    return dependency
