"""Application-level WhatsApp analytics helpers."""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import func as sqlfunc
from sqlalchemy.orm import Session

from src.domains.platform.models.whatsapp_models import WhatsAppMessage


def build_whatsapp_usage_snapshot(current_user, db: Session, days: int) -> dict:
    since = datetime.now(timezone.utc) - timedelta(days=days)
    base_query = db.query(WhatsAppMessage).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
    )

    total_messages = base_query.count()
    inbound = base_query.filter(WhatsAppMessage.direction == "inbound").count()
    outbound = base_query.filter(WhatsAppMessage.direction == "outbound").count()
    unique_users = db.query(sqlfunc.count(sqlfunc.distinct(WhatsAppMessage.phone))).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
    ).scalar()
    top_intents = db.query(
        WhatsAppMessage.intent,
        sqlfunc.count(WhatsAppMessage.id).label("count"),
    ).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
        WhatsAppMessage.intent.isnot(None),
    ).group_by(WhatsAppMessage.intent).order_by(
        sqlfunc.count(WhatsAppMessage.id).desc()
    ).limit(10).all()
    avg_latency = db.query(sqlfunc.avg(WhatsAppMessage.latency_ms)).filter(
        WhatsAppMessage.tenant_id == current_user.tenant_id,
        WhatsAppMessage.created_at >= since,
        WhatsAppMessage.latency_ms.isnot(None),
    ).scalar()

    return {
        "period_days": days,
        "total_messages": total_messages,
        "inbound": inbound,
        "outbound": outbound,
        "unique_users": unique_users or 0,
        "avg_latency_ms": round(avg_latency) if avg_latency else None,
        "top_intents": [{"intent": item[0], "count": item[1]} for item in top_intents],
    }

