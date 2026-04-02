"""Application helpers for admin AI review workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.domains.identity.models.user import User
from src.domains.platform.models.ai import AIQuery


def build_ai_review_list_response(
    *,
    db: Session,
    tenant_id,
    load_review_history_fn,
    review_status_from_action_fn,
) -> list[dict]:
    recent = db.query(AIQuery, User.full_name).join(User, AIQuery.user_id == User.id).filter(
        AIQuery.tenant_id == tenant_id,
    ).order_by(desc(AIQuery.created_at)).limit(20).all()
    query_ids = [query.id for query, _ in recent]
    _, latest_map = load_review_history_fn(
        db,
        tenant_id=tenant_id,
        query_ids=query_ids,
    )
    return [
        {
            **({
                "review_status": review_status_from_action_fn(latest_map.get(str(query.id), {}).get("action")),
                "review_note": latest_map.get(str(query.id), {}).get("note"),
                "reviewed_at": latest_map.get(str(query.id), {}).get("created_at"),
                "reviewed_by": latest_map.get(str(query.id), {}).get("reviewed_by"),
            }),
            "id": str(query.id),
            "user": name,
            "query": query.query_text,
            "response": query.response_text[:500],
            "mode": query.mode,
            "citations": query.citation_count,
            "response_time_ms": query.response_time_ms,
            "trace_id": query.trace_id,
            "created_at": str(query.created_at),
        }
        for query, name in recent
    ]


def build_ai_review_detail_response(
    *,
    db: Session,
    tenant_id,
    review_id: str,
    parse_uuid_fn,
    load_review_history_fn,
    review_status_from_action_fn,
) -> dict:
    review_uuid = parse_uuid_fn(review_id, "review_id")
    row = db.query(AIQuery, User.full_name).join(User, AIQuery.user_id == User.id).filter(
        AIQuery.tenant_id == tenant_id,
        AIQuery.id == review_uuid,
    ).first()
    if not row:
        raise HTTPException(status_code=404, detail="AI review item not found")

    query, name = row
    history_map, latest_map = load_review_history_fn(
        db,
        tenant_id=tenant_id,
        query_ids=[query.id],
    )
    latest = latest_map.get(str(query.id), {})
    return {
        "id": str(query.id),
        "user": name,
        "query": query.query_text,
        "response": query.response_text,
        "mode": query.mode,
        "citations": query.citation_count,
        "response_time_ms": query.response_time_ms,
        "trace_id": query.trace_id,
        "created_at": str(query.created_at),
        "token_usage": query.token_usage,
        "review_status": review_status_from_action_fn(latest.get("action")),
        "review_note": latest.get("note"),
        "reviewed_at": latest.get("created_at"),
        "reviewed_by": latest.get("reviewed_by"),
        "review_history": history_map.get(str(query.id), []),
    }
