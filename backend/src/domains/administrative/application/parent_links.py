"""Application helpers for admin parent-link workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.domains.academic.models.parent_link import ParentLink
from src.domains.identity.models.user import User
from src.domains.platform.models.audit import AuditLog


def build_admin_parent_links_response(
    *,
    db: Session,
    tenant_id,
) -> list[dict]:
    links = db.query(ParentLink).filter(
        ParentLink.tenant_id == tenant_id,
    ).order_by(desc(ParentLink.created_at)).all()

    parent_ids = list({link.parent_id for link in links})
    child_ids = list({link.child_id for link in links})
    users = []
    if parent_ids or child_ids:
        users = db.query(User).filter(
            User.tenant_id == tenant_id,
            User.id.in_(parent_ids + child_ids),
        ).all()
    name_by_id = {user.id: user.full_name or user.email for user in users}

    return [
        {
            "id": str(link.id),
            "parent_id": str(link.parent_id),
            "parent_name": name_by_id.get(link.parent_id, "Unknown"),
            "child_id": str(link.child_id),
            "child_name": name_by_id.get(link.child_id, "Unknown"),
            "created_at": str(link.created_at),
        }
        for link in links
    ]


def create_admin_parent_link(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    parent_id: str,
    child_id: str,
    parse_uuid_fn,
) -> dict:
    parent_uuid = parse_uuid_fn(parent_id, "parent_id")
    child_uuid = parse_uuid_fn(child_id, "child_id")

    parent = db.query(User).filter(
        User.id == parent_uuid,
        User.tenant_id == tenant_id,
        User.role == "parent",
    ).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent user not found")

    child = db.query(User).filter(
        User.id == child_uuid,
        User.tenant_id == tenant_id,
        User.role == "student",
    ).first()
    if not child:
        raise HTTPException(status_code=404, detail="Student user not found")

    existing = db.query(ParentLink).filter(
        ParentLink.tenant_id == tenant_id,
        ParentLink.parent_id == parent_uuid,
        ParentLink.child_id == child_uuid,
    ).first()
    if existing:
        return {"success": True, "id": str(existing.id), "already_exists": True}

    link = ParentLink(
        tenant_id=tenant_id,
        parent_id=parent_uuid,
        child_id=child_uuid,
    )
    db.add(link)
    if hasattr(db, "flush"):
        db.flush()
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="parent.linked",
            entity_type="parent_link",
            entity_id=link.id,
            metadata_={"parent_id": str(parent_uuid), "child_id": str(child_uuid)},
        )
    )
    db.commit()
    if hasattr(db, "refresh"):
        db.refresh(link)
    return {"success": True, "id": str(link.id)}


def delete_admin_parent_link(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    link_id: str,
    parse_uuid_fn,
) -> dict:
    link_uuid = parse_uuid_fn(link_id, "link_id")
    link = db.query(ParentLink).filter(
        ParentLink.id == link_uuid,
        ParentLink.tenant_id == tenant_id,
    ).first()
    if not link:
        raise HTTPException(status_code=404, detail="Parent link not found")

    db.delete(link)
    db.add(
        AuditLog(
            tenant_id=tenant_id,
            user_id=actor_user_id,
            action="parent.unlinked",
            entity_type="parent_link",
            entity_id=link_uuid,
        )
    )
    db.commit()
    return {"success": True}
