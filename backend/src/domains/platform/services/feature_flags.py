import json
from pathlib import Path
from typing import List, Optional
from uuid import uuid4
from sqlalchemy.orm import Session
from fastapi import HTTPException, status, Depends
from config import settings
from src.domains.platform.models.feature_flag import FeatureFlag
from database import get_db

CATALOG_PATH = Path(__file__).parent.parent.parent.parent.parent / "features_catalog.json"

def init_feature_flags(db: Session):
    """
    Reads the features_catalog.json and upserts the features into the database.
    Does not overwrite the 'enabled' state of existing features.
    """
    if not CATALOG_PATH.exists():
        print("⚠️ features_catalog.json not found. Skipping feature flag initialization.")
        return
    
    with open(CATALOG_PATH, "r", encoding="utf-8") as f:
        catalog = json.load(f)
        
    for item in catalog:
        existing = db.query(FeatureFlag).filter(FeatureFlag.feature_id == item["feature_id"]).first()
        if existing:
            # Update metadata but not the 'enabled' state
            existing.name = item["name"]
            existing.description = item.get("description", "")
            existing.category = item["category"]
            existing.module = item.get("module", "Platform Operations")
            existing.ai_intensity = item.get("ai_intensity", "No AI")
        else:
            # Create new feature flag
            new_flag = FeatureFlag(
                id=uuid4(),
                feature_id=item["feature_id"],
                name=item["name"],
                description=item.get("description", ""),
                category=item["category"],
                module=item.get("module", "Platform Operations"),
                ai_intensity=item.get("ai_intensity", "No AI"),
                enabled=item.get("enabled", True)
            )
            db.add(new_flag)
    db.commit()

def get_all_feature_flags(db: Session) -> List[FeatureFlag]:
    return db.query(FeatureFlag).all()


def _bootstrap_feature_flags_if_empty(db: Session) -> None:
    """
    Self-heal empty demo/local databases where the table exists but the catalog
    was never populated.
    """
    existing = db.query(FeatureFlag.id).limit(1).first()
    if existing is None:
        init_feature_flags(db)

def toggle_feature_flag(db: Session, feature_id: str, enabled: bool) -> FeatureFlag:
    flag = db.query(FeatureFlag).filter(FeatureFlag.feature_id == feature_id).first()
    if not flag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Feature '{feature_id}' not found."
        )
    flag.enabled = enabled
    db.commit()
    db.refresh(flag)
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
            # Enable Heavy AI & Learning, disable purely administrative ERP.
            if flag.ai_intensity == "Heavy AI" or flag.module == "Learning Management":
                flag.enabled = True
            elif flag.module in ["Finance", "Admissions", "Student Management", "Platform Operations"] and flag.ai_intensity == "No AI":
                flag.enabled = False
                
        elif profile == "ai_helper":
            # Enable Medium/Low AI + Core Administrative ERP.
            if flag.ai_intensity in ["Medium AI", "Low AI", "No AI"]:
                flag.enabled = True
            elif flag.ai_intensity == "Heavy AI":
                flag.enabled = False
                
        elif profile == "full_erp":
            # Enable core administrative ERP features. Disable generative AI chat/orchestration.
            if flag.ai_intensity == "No AI" or flag.ai_intensity == "Low AI":
                flag.enabled = True
            elif flag.ai_intensity in ["Heavy AI", "Medium AI"]:
                flag.enabled = False
                
        if initial_state != flag.enabled:
            updated_count += 1
            
    db.commit()
    return {"success": True, "profile": profile, "features_updated": updated_count}

# --- Dependency Generator for Runtime Enforcement ---
def require_feature(feature_id: str):
    """
    FastAPI dependency that blocks the request if the feature is disabled.
    Usage: @app.get('/route', dependencies=[Depends(require_feature('ai_chat'))])
    """
    def dependency(db: Session = Depends(get_db)):
        _bootstrap_feature_flags_if_empty(db)
        flag = db.query(FeatureFlag).filter(FeatureFlag.feature_id == feature_id).first()
        if not flag:
            print(f"⚠️ Feature {feature_id} guard checked but not found in DB.")
            if settings.app.demo_mode:
                print(f"⚠️ Allowing missing feature {feature_id} in DEMO_MODE.")
                return True
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_id}' is conditionally disabled."
            )
        if not flag.enabled:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Feature '{feature_id}' is currently disabled by the administrator."
            )
        return True
    return dependency
