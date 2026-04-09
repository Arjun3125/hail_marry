"""Application helpers for admin complaint workflows."""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta

from fastapi import HTTPException
from sqlalchemy import desc
from sqlalchemy.orm import Session

from src.domains.administrative.models.complaint import Complaint
from src.domains.identity.models.user import User


def _ensure_tz(value: datetime | date | None) -> datetime | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return datetime.combine(value, datetime.min.time(), tzinfo=UTC)
    if value.tzinfo is None:
        return value.replace(tzinfo=UTC)
    return value.astimezone(UTC)


def _shift_month(value: datetime, delta: int) -> datetime:
    month_index = value.month - 1 + delta
    year = value.year + month_index // 12
    month = month_index % 12 + 1
    return value.replace(year=year, month=month, day=1)


def _month_windows(now: datetime | None = None) -> list[dict]:
    current = _ensure_tz(now or datetime.now(UTC))
    assert current is not None
    first_of_month = current.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    windows = []
    for offset in range(-5, 1):
        start = _shift_month(first_of_month, offset)
        windows.append({"key": start.strftime("%Y-%m"), "month": start.strftime("%b")})
    return windows


def _month_key(value: datetime | date | None) -> str | None:
    normalized = _ensure_tz(value)
    if normalized is None:
        return None
    return normalized.strftime("%Y-%m")


def build_admin_complaints_response(
    *,
    db: Session,
    tenant_id,
) -> dict:
    complaints = db.query(Complaint, User.full_name).join(User, Complaint.student_id == User.id).filter(
        Complaint.tenant_id == tenant_id,
    ).order_by(desc(Complaint.created_at)).all()
    items = [
        {
            "id": str(complaint.id),
            "student": name,
            "category": complaint.category,
            "description": complaint.description,
            "status": complaint.status,
            "resolution_note": complaint.resolution_note,
            "date": str(complaint.created_at.date()),
        }
        for complaint, name in complaints
    ]
    status_counts = {
        "open": 0,
        "in_review": 0,
        "resolved": 0,
    }
    categories: dict[str, int] = {}
    monthly = {
        window["key"]: {
            "month": window["month"],
            "total": 0,
            "resolved": 0,
        }
        for window in _month_windows()
    }
    resolved_last_30d = 0
    last_30_days = datetime.now(UTC) - timedelta(days=30)
    for complaint, _name in complaints:
        status = complaint.status or "open"
        if status in status_counts:
            status_counts[status] += 1
        category = complaint.category or "General"
        categories[category] = categories.get(category, 0) + 1
        month_key = _month_key(complaint.created_at)
        if month_key in monthly:
            monthly[month_key]["total"] += 1
        resolved_key = _month_key(complaint.resolved_at)
        if resolved_key in monthly:
            monthly[resolved_key]["resolved"] += 1
        resolved_at = _ensure_tz(complaint.resolved_at)
        if resolved_at and resolved_at >= last_30_days:
            resolved_last_30d += 1
    total = len(complaints)
    return {
        "items": items,
        "summary": {
            "total": total,
            "open": status_counts["open"],
            "in_review": status_counts["in_review"],
            "resolved": status_counts["resolved"],
            "resolved_last_30d": resolved_last_30d,
            "resolution_rate_pct": round((status_counts["resolved"] / total * 100) if total else 100),
        },
        "monthly_activity": [monthly[window["key"]] for window in _month_windows()],
        "categories": [
            {"category": category, "count": count}
            for category, count in sorted(categories.items(), key=lambda item: (-item[1], item[0]))
        ],
    }


def update_admin_complaint(
    *,
    db: Session,
    tenant_id,
    actor_user_id,
    complaint_id: str,
    status: str,
    resolution_note: str,
    parse_uuid_fn,
    allowed_statuses: set[str],
) -> dict:
    complaint_uuid = parse_uuid_fn(complaint_id, "complaint_id")
    complaint = db.query(Complaint).filter(Complaint.id == complaint_uuid, Complaint.tenant_id == tenant_id).first()
    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")
    if status not in allowed_statuses:
        raise HTTPException(status_code=400, detail="Invalid complaint status")

    complaint.status = status
    complaint.resolution_note = resolution_note
    if status == "resolved":
        complaint.resolved_by = actor_user_id
        complaint.resolved_at = datetime.utcnow()
    db.commit()

    return {
        "complaint": complaint,
        "webhook_payload": {
            "complaint_id": str(complaint.id),
            "status": complaint.status,
            "resolved_by": str(complaint.resolved_by) if complaint.resolved_by else None,
        },
    }
