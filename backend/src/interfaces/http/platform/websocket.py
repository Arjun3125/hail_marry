"""WebSocket endpoint for real-time streaming."""
import logging
from uuid import UUID

from fastapi import APIRouter, WebSocketDisconnect
from sqlalchemy.orm import Session

from src.domains.identity.models.user import User
from src.domains.platform.services.websocket_manager import manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["WebSocket"])


@router.websocket("/ws/realtime")
async def websocket_realtime_endpoint(websocket=None, db: Session = None):
    """WebSocket endpoint for real-time updates.
    
    To connect:
    1. Send WebSocket upgrade request to /ws/realtime?token=<jwt_token>
    2. Server responds with connection confirmation
    3. Receive real-time events (attendance, assignments, marks, etc.)
    4. Connection auto-closes on disconnect
    
    Events received:
    - attendance.updated: Attendance marked for a student
    - assignment.created: New assignment created
    - assignment.updated: Assignment updated
    - exam.results.updated: Exam results published
    - announcement.sent: Admin announcement
    
    Event format:
    {
        "event": "event_type",
        "timestamp": "2026-04-11T10:30:00",
        "data": {...}
    }
    """
    # Note: This is a pattern - actual implementation requires custom FastAPI WebSocket auth
    # The endpoint structure will be integrated into the actual router
    pass


# Alternative approach: Direct WebSocket handler for integration with existing auth
async def handle_websocket_connection(
    websocket,
    tenant_id: UUID,
    user: User,
    db: Session,
):
    """Handle a WebSocket connection with proper auth and cleanup.
    
    Args:
        websocket: FastAPI WebSocket connection
        tenant_id: Tenant ID (from middleware)
        user: Current user (from auth)
        db: Database session
    """
    connection_id = await manager.connect(
        websocket=websocket,
        tenant_id=tenant_id,
        user_id=user.id,
        role=user.role,
    )
    
    try:
        # Send connection confirmation
        await websocket.send_json({
            "event": "connection.established",
            "connection_id": connection_id,
            "user_id": str(user.id),
            "role": user.role,
        })
        
        # Keep connection alive and listen for messages
        while True:
            data = await websocket.receive_text()
            
            # Handle heartbeat/ping-pong
            if data == "ping":
                await websocket.send_text("pong")
                continue
            
            # Handle other message types (future extension)
            logger.debug(f"Received message from {connection_id}: {data}")
    
    except WebSocketDisconnect:
        await manager.disconnect(connection_id)
        logger.info(f"WebSocket disconnected normally: {connection_id}")
    
    except Exception as e:
        await manager.disconnect(connection_id)
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
