"""Superadmin endpoints for global operations like creating new Tenants."""
import os
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from src.domains.identity.models.tenant import Tenant
from src.domains.identity.models.user import User

try:
    from auth.auth import pwd_context
except ImportError:
    import sys
    _bcrypt_rounds: int = 4 if "pytest" in sys.modules else 12
    from passlib.context import CryptContext
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__rounds=_bcrypt_rounds)

router = APIRouter(prefix="/api/superadmin", tags=["Superadmin"])


class TenantCreateRequest(BaseModel):
    name: str
    domain: str
    admin_email: str
    admin_name: str
    admin_password: str
    superadmin_secret: str
    plan_tier: str = "pro"


@router.post("/tenant", status_code=status.HTTP_201_CREATED)
async def create_tenant(request: TenantCreateRequest, db: Session = Depends(get_db)):
    """
    Creates a new Tenant (School/Institute) and its first Admin user.
    Protected by SUPERADMIN_SECRET environment variable.
    """
    secret: str | None = os.getenv("SUPERADMIN_SECRET")
    if not secret:
        # If no secret is configured, we disallow tenant creation for security
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SUPERADMIN_SECRET is not configured on the server",
        )
    
    if request.superadmin_secret != secret:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid superadmin secret",
        )

    # Check if tenant or admin already exists
    existing_tenant: Tenant | None = db.query(Tenant).filter(Tenant.domain == request.domain.strip()).first()
    if existing_tenant:
        raise HTTPException(status_code=400, detail="Tenant with this domain already exists")

    existing_user: User | None = db.query(User).filter(User.email == request.admin_email.strip()).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="User with this email already exists")

    # Create Tenant
    tenant = Tenant(
        name=request.name.strip(),
        domain=request.domain.strip(),
        plan_tier=request.plan_tier,
        is_active=1
    )
    db.add(tenant)
    db.flush()

    # Create Admin
    hashed_pw = pwd_context.hash(request.admin_password)
    admin_user = User(
        tenant_id=tenant.id,
        email=request.admin_email.strip(),
        full_name=request.admin_name.strip(),
        role="admin",
        hashed_password=hashed_pw,
        is_active=True
    )
    db.add(admin_user)
    db.commit()
    db.refresh(tenant)
    db.refresh(admin_user)

    return {
        "success": True,
        "tenant_id": str(tenant.id),
        "admin_id": str(admin_user.id),
        "message": f"Tenant '{tenant.name}' and Admin account created safely."
    }
