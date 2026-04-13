from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db

from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
from auth.dependencies import get_current_user, require_role
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.services.branding_extractor import extract_brand_palette

router = APIRouter(prefix="/api/branding", tags=["Branding"])

class BrandingUpdateRequest(BaseModel):
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    font_family: str | None = None
    theme_style: str | None = None
    logo_url: str | None = None


def _record_branding_audit_log(db: Session, current_user: User, metadata: dict) -> None:
    db.add(
        AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action="branding.updated",
            entity_type="tenant",
            entity_id=current_user.tenant_id,
            metadata_=metadata,
        )
    )
    db.commit()

@router.post("/extract")
async def extract_logo_colors(
    file: UploadFile = File(...),
    current_user: User = Depends(require_role("admin")),
):
    """
    Accepts an uploaded image logo and automatically extracts the brand palette.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    content: bytes = await file.read()
    palette = extract_brand_palette(content)
    
    return {
        "success": True,
        "suggested_palette": palette
    }

@router.patch("/save")
async def save_tenant_branding(
    request: BrandingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role("admin")),
):
    """
    Saves the custom branding configuration to the current user's Tenant.
    """
    tenant: Tenant | None = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    updates: dict[str, str] = {}

    if request.primary_color:
        tenant.primary_color = request.primary_color
        updates["primary_color"] = request.primary_color
    if request.secondary_color:
        tenant.secondary_color = request.secondary_color
        updates["secondary_color"] = request.secondary_color
    if request.accent_color:
        tenant.accent_color = request.accent_color
        updates["accent_color"] = request.accent_color
    if request.font_family:
        tenant.font_family = request.font_family
        updates["font_family"] = request.font_family
    if request.theme_style:
        tenant.theme_style = request.theme_style
        updates["theme_style"] = request.theme_style
    if request.logo_url:
        tenant.logo_url = request.logo_url
        updates["logo_url"] = request.logo_url

    db.commit()
    _record_branding_audit_log(db, current_user, updates)
    return {"success": True, "message": "Branding updated successfully."}

@router.get("/config")
async def get_tenant_branding(
    # This might be accessed publicly if passed a domain/tenant_id, but keeping simple for now.
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, str | None]:
    tenant: Tenant | None = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")
        
    return {
        "primary_color": tenant.primary_color,
        "secondary_color": tenant.secondary_color,
        "accent_color": tenant.accent_color,
        "font_family": tenant.font_family,
        "theme_style": tenant.theme_style,
        "logo_url": tenant.logo_url,
        "name": tenant.name
    }
