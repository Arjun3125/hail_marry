"""Notification WebSocket + REST endpoints."""
from __future__ import annotations

import asyncio
import json
import logging

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session

from auth.dependencies import require_role
from auth.jwt import decode_access_token
from database import get_db
from models.user import User
from services.notifications import (
    add_notification,
    get_notifications,
    mark_read,
    subscribe,
    unsubscribe,
)

router = APIRouter(prefix="/api/notifications", tags=["Notifications"])
logger = logging.getLogger(__name__)


@router.websocket("/ws")
async def websocket_notifications(websocket: WebSocket, token: str = ""):
    """WebSocket endpoint for real-time notification push.
    Connect with: ws://host/api/notifications/ws?token=<jwt>
    """
    payload = decode_access_token(token)
    if not payload or not payload.get("user_id"):
        await websocket.close(code=4001, reason="Invalid token")
        return

    user_id = payload["user_id"]
    await websocket.accept()
    queue = subscribe(user_id)

    try:
        while True:
            try:
                notification = await asyncio.wait_for(queue.get(), timeout=30.0)
                await websocket.send_json(notification)
            except asyncio.TimeoutError:
                # Send keepalive ping
                await websocket.send_json({"type": "ping"})
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error for user %s", user_id)
    finally:
        unsubscribe(user_id, queue)


@router.get("")
async def list_notifications(
    unread_only: bool = False,
    current_user: User = Depends(require_role("student", "teacher", "parent", "admin")),
):
    """Get notifications for the current user."""
    return get_notifications(str(current_user.id), unread_only=unread_only)


@router.post("/{notification_id}/read")
async def mark_notification_read(
    notification_id: str,
    current_user: User = Depends(require_role("student", "teacher", "parent", "admin")),
):
    """Mark a notification as read."""
    found = mark_read(str(current_user.id), notification_id)
    if not found:
        raise HTTPException(status_code=404, detail="Notification not found")
    return {"success": True}
