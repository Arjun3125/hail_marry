"""Application helpers for admin tenant settings workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from src.domains.identity.models.tenant import Tenant
from src.domains.platform.models.audit import AuditLog


def build_admin_settings_response(
    *,
    db: Session,
    tenant_id,
) -> dict:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    return {
        "name": tenant.name if tenant else "",
        "plan_tier": tenant.plan_tier if tenant else "basic",
        "max_students": tenant.max_students if tenant else 50,
        "ai_daily_limit": tenant.ai_daily_limit if tenant else 50,
        "domain": tenant.domain if tenant else "",
    }


def update_admin_settings(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    ai_daily_limit: int | None,
    name: str | None,
) -> dict:
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        raise HTTPException(status_code=404, detail="Tenant not found")

    if ai_daily_limit is not None:
        tenant.ai_daily_limit = ai_daily_limit
    if name:
        tenant.name = name

    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="settings.updated",
            entity_type="tenant",
            entity_id=tenant.id,
        )
    )
    db.commit()
    return {"success": True}
