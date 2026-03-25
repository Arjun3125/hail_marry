from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import get_db

from src.domains.identity.models.user import User
from src.domains.identity.models.tenant import Tenant
from auth.dependencies import get_current_user
from src.domains.platform.services.branding_extractor import extract_brand_palette

router = APIRouter(prefix="/branding", tags=["Branding"])

class BrandingUpdateRequest(BaseModel):
    primary_color: str | None = None
    secondary_color: str | None = None
    accent_color: str | None = None
    font_family: str | None = None
    theme_style: str | None = None
    logo_url: str | None = None

@router.post("/extract")
async def extract_logo_colors(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
):
    """
    Accepts an uploaded image logo and automatically extracts the brand palette.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage branding.")

    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image.")

    content = await file.read()
    palette = extract_brand_palette(content)
    
    return {
        "success": True,
        "suggested_palette": palette
    }

@router.patch("/save")
async def save_tenant_branding(
    request: BrandingUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Saves the custom branding configuration to the current user's Tenant.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only admins can manage branding.")

    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found.")

    if request.primary_color:
        tenant.primary_color = request.primary_color
    if request.secondary_color:
        tenant.secondary_color = request.secondary_color
    if request.accent_color:
        tenant.accent_color = request.accent_color
    if request.font_family:
        tenant.font_family = request.font_family
    if request.theme_style:
        tenant.theme_style = request.theme_style
    if request.logo_url:
        tenant.logo_url = request.logo_url

    db.commit()
    return {"success": True, "message": "Branding updated successfully."}

@router.get("/config")
async def get_tenant_branding(
    # This might be accessed publicly if passed a domain/tenant_id, but keeping simple for now.
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant = db.query(Tenant).filter(Tenant.id == user.tenant_id).first()
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
