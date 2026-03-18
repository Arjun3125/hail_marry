"""Notification store with durable DB persistence and WebSocket push support."""
from __future__ import annotations

import asyncio
import logging
import os
import time
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID, uuid4

from sqlalchemy import desc

from database import SessionLocal
from models.notification import Notification

logger = logging.getLogger(__name__)

# ── In-memory store (optional fallback) ───────────────────────────────────────
_notifications: dict[str, list[dict[str, Any]]] = defaultdict(list)
_subscribers: dict[str, list[asyncio.Queue]] = defaultdict(list)

NOTIFICATION_TTL = 7 * 24 * 3600  # 7 days
MAX_PER_USER = 200
USE_MEMORY_STORE = os.getenv("NOTIFICATIONS_BACKEND", "db").lower() == "memory"


def _parse_uuid(value: str) -> UUID:
    return UUID(str(value))


def _serialize_notification(row: Notification) -> dict[str, Any]:
    created_at = row.created_at
    created_ts = created_at.timestamp() if created_at else time.time()
    return {
        "id": str(row.id),
        "user_id": str(row.user_id),
        "title": row.title,
        "body": row.body,
        "category": row.category,
        "data": row.data or {},
        "read": bool(row.read),
        "created_at": created_ts,
    }


def _trim_memory_notifications(user_id: str) -> None:
    cutoff = time.time() - NOTIFICATION_TTL
    _notifications[user_id] = [
        n for n in _notifications[user_id]
        if n["created_at"] > cutoff
    ][-MAX_PER_USER:]


def _add_memory_notification(
    user_id: str,
    *,
    title: str,
    body: str,
    category: str,
    data: dict[str, Any] | None,
) -> dict[str, Any]:
    notification = {
        "id": uuid4().hex,
        "user_id": user_id,
        "title": title,
        "body": body,
        "category": category,
        "data": data or {},
        "read": False,
        "created_at": time.time(),
    }
    _notifications[user_id].append(notification)
    _trim_memory_notifications(user_id)
    return notification


def _push_to_subscribers(user_id: str, notification: dict[str, Any]) -> None:
    for queue in _subscribers.get(user_id, []):
        try:
            queue.put_nowait(notification)
        except asyncio.QueueFull:
            pass


def _cleanup_db(db, user_uuid: UUID) -> None:
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=NOTIFICATION_TTL)
    db.query(Notification).filter(
        Notification.user_id == user_uuid,
        Notification.created_at < cutoff,
    ).delete(synchronize_session=False)

    if MAX_PER_USER:
        stale_ids = db.query(Notification.id).filter(
            Notification.user_id == user_uuid
        ).order_by(Notification.created_at.desc()).offset(MAX_PER_USER).all()
        if stale_ids:
            db.query(Notification).filter(
                Notification.id.in_([row.id for row in stale_ids])
            ).delete(synchronize_session=False)


def add_notification(
    user_id: str,
    *,
    title: str,
    body: str,
    category: str = "info",
    data: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Create a notification and push to any connected WebSocket subscribers."""
    if USE_MEMORY_STORE:
        notification = _add_memory_notification(
            user_id,
            title=title,
            body=body,
            category=category,
            data=data,
        )
        _push_to_subscribers(user_id, notification)
        return notification

    try:
        user_uuid = _parse_uuid(user_id)
        db = SessionLocal()
        try:
            row = Notification(
                user_id=user_uuid,
                title=title,
                body=body,
                category=category,
                data=data or {},
                read=False,
                created_at=datetime.now(timezone.utc),
            )
            db.add(row)
            db.commit()
            db.refresh(row)
            _cleanup_db(db, user_uuid)
            db.commit()
            notification = _serialize_notification(row)
        finally:
            db.close()
    except Exception:
        logger.exception("Falling back to in-memory notifications for user %s", user_id)
        notification = _add_memory_notification(
            user_id,
            title=title,
            body=body,
            category=category,
            data=data,
        )

    _push_to_subscribers(user_id, notification)
    return notification


def get_notifications(user_id: str, *, unread_only: bool = False) -> list[dict[str, Any]]:
    """Retrieve notifications for a user, newest first."""
    if USE_MEMORY_STORE:
        items = _notifications.get(user_id, [])
        if unread_only:
            items = [n for n in items if not n["read"]]
        return sorted(items, key=lambda n: n["created_at"], reverse=True)

    try:
        user_uuid = _parse_uuid(user_id)
        db = SessionLocal()
        try:
            query = db.query(Notification).filter(Notification.user_id == user_uuid)
            if unread_only:
                query = query.filter(Notification.read.is_(False))
            rows = query.order_by(desc(Notification.created_at)).limit(MAX_PER_USER).all()
            return [_serialize_notification(row) for row in rows]
        finally:
            db.close()
    except Exception:
        logger.exception("Falling back to in-memory notifications for user %s", user_id)
        items = _notifications.get(user_id, [])
        if unread_only:
            items = [n for n in items if not n["read"]]
        return sorted(items, key=lambda n: n["created_at"], reverse=True)


def mark_read(user_id: str, notification_id: str) -> bool:
    """Mark a notification as read. Returns True if found."""
    if USE_MEMORY_STORE:
        for n in _notifications.get(user_id, []):
            if n["id"] == notification_id:
                n["read"] = True
                return True
        return False

    try:
        user_uuid = _parse_uuid(user_id)
        notification_uuid = _parse_uuid(notification_id)
        db = SessionLocal()
        try:
            updated = db.query(Notification).filter(
                Notification.user_id == user_uuid,
                Notification.id == notification_uuid,
            ).update({"read": True})
            db.commit()
            return bool(updated)
        finally:
            db.close()
    except Exception:
        logger.exception("Falling back to in-memory notification read for user %s", user_id)
        for n in _notifications.get(user_id, []):
            if n["id"] == notification_id:
                n["read"] = True
                return True
        return False


def subscribe(user_id: str) -> asyncio.Queue:
    """Register a WebSocket subscriber queue for real-time push."""
    queue: asyncio.Queue = asyncio.Queue(maxsize=50)
    _subscribers[user_id].append(queue)
    return queue


def unsubscribe(user_id: str, queue: asyncio.Queue) -> None:
    """Remove a subscriber queue."""
    subs = _subscribers.get(user_id, [])
    if queue in subs:
        subs.remove(queue)
