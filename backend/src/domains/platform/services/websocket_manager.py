"""WebSocket connection management and real-time event broadcasting."""
import asyncio
import logging
from datetime import datetime
from typing import Any, Dict, Optional, Set
from uuid import UUID

from fastapi import WebSocket
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasts events to connected clients.
    
    Features:
    - Connection pooling per tenant and user role
    - Efficient broadcasting to specific users/roles/tenants
    - Connection state tracking
    - Automatic cleanup on disconnect
    - Message queue (optional future feature)
    """

    def __init__(self):
        # Active connections: {tenant_id: {user_id: {connection_id: websocket}}}
        self.active_connections: Dict[str, Dict[str, Dict[str, WebSocket]]] = {}
        # Connection metadata: {connection_id: {"user_id": UUID, "tenant_id": UUID, "role": str, "connected_at": datetime}}
        self.connection_metadata: Dict[str, Dict[str, Any]] = {}
        # Lock for thread-safe operations
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket, tenant_id: UUID, user_id: UUID, role: str) -> str:
        """Register a new WebSocket connection.
        
        Args:
            websocket: FastAPI WebSocket connection
            tenant_id: Tenant ID for multi-tenancy
            user_id: User ID of the connected client
            role: User role (teacher, student, parent, admin)
            
        Returns:
            connection_id (UUID string)
        """
        await websocket.accept()
        connection_id = str(UUID(int=abs(hash((tenant_id, user_id, datetime.now().timestamp())))) if False else UUID(int=abs(hash((tenant_id, user_id, datetime.now().timestamp())))))
        
        # Use proper UUID generation
        import uuid
        connection_id = str(uuid.uuid4())
        
        async with self._lock:
            tenant_str = str(tenant_id)
            user_str = str(user_id)
            
            if tenant_str not in self.active_connections:
                self.active_connections[tenant_str] = {}
            if user_str not in self.active_connections[tenant_str]:
                self.active_connections[tenant_str][user_str] = {}
                
            self.active_connections[tenant_str][user_str][connection_id] = websocket
            self.connection_metadata[connection_id] = {
                "user_id": str(user_id),
                "tenant_id": str(tenant_id),
                "role": role,
                "connected_at": datetime.utcnow().isoformat(),
            }
        
        logger.info(f"WebSocket connected: {connection_id} (user={user_id}, tenant={tenant_id}, role={role})")
        return connection_id

    async def disconnect(self, connection_id: str) -> None:
        """Unregister a WebSocket connection.
        
        Args:
            connection_id: Connection ID to disconnect
        """
        async with self._lock:
            if connection_id not in self.connection_metadata:
                return
                
            metadata = self.connection_metadata[connection_id]
            tenant_str = metadata["tenant_id"]
            user_str = metadata["user_id"]
            
            if tenant_str in self.active_connections:
                if user_str in self.active_connections[tenant_str]:
                    self.active_connections[tenant_str][user_str].pop(connection_id, None)
                    
                    # Cleanup empty dicts
                    if not self.active_connections[tenant_str][user_str]:
                        del self.active_connections[tenant_str][user_str]
                    if not self.active_connections[tenant_str]:
                        del self.active_connections[tenant_str]
            
            del self.connection_metadata[connection_id]
        
        logger.info(f"WebSocket disconnected: {connection_id}")

    async def broadcast_to_user(
        self, tenant_id: UUID, user_id: UUID, event_type: str, data: Dict[str, Any]
    ) -> int:
        """Send an event to a specific user's all connections.
        
        Args:
            tenant_id: Tenant ID
            user_id: User ID to send to
            event_type: Type of event (e.g., "attendance.updated", "assignment.created")
            data: Event payload
            
        Returns:
            Number of messages sent
        """
        tenant_str = str(tenant_id)
        user_str = str(user_id)
        sent_count = 0
        
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        async with self._lock:
            if tenant_str in self.active_connections:
                if user_str in self.active_connections[tenant_str]:
                    connections = list(self.active_connections[tenant_str][user_str].values())
        
        for websocket in connections:
            try:
                await websocket.send_json(payload)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to send message to user {user_id}: {str(e)}")
        
        return sent_count

    async def broadcast_to_role(
        self, tenant_id: UUID, role: str, event_type: str, data: Dict[str, Any]
    ) -> int:
        """Send an event to all connected users with a specific role.
        
        Args:
            tenant_id: Tenant ID
            role: User role to send to (teacher, student, parent, admin)
            event_type: Type of event
            data: Event payload
            
        Returns:
            Number of messages sent
        """
        tenant_str = str(tenant_id)
        sent_count = 0
        
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        # Collect all matching connections
        matching_connections = []
        async with self._lock:
            if tenant_str in self.active_connections:
                for user_connections in self.active_connections[tenant_str].values():
                    for connection_id, websocket in user_connections.items():
                        if self.connection_metadata[connection_id]["role"] == role:
                            matching_connections.append(websocket)
        
        for websocket in matching_connections:
            try:
                await websocket.send_json(payload)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to broadcast to role {role}: {str(e)}")
        
        return sent_count

    async def broadcast_to_tenant(
        self, tenant_id: UUID, event_type: str, data: Dict[str, Any]
    ) -> int:
        """Send an event to all connected users in a tenant.
        
        Args:
            tenant_id: Tenant ID
            event_type: Type of event
            data: Event payload
            
        Returns:
            Number of messages sent
        """
        tenant_str = str(tenant_id)
        sent_count = 0
        
        payload = {
            "event": event_type,
            "timestamp": datetime.utcnow().isoformat(),
            "data": data,
        }
        
        # Collect all matching connections
        matching_connections = []
        async with self._lock:
            if tenant_str in self.active_connections:
                for user_connections in self.active_connections[tenant_str].values():
                    for websocket in user_connections.values():
                        matching_connections.append(websocket)
        
        for websocket in matching_connections:
            try:
                await websocket.send_json(payload)
                sent_count += 1
            except Exception as e:
                logger.warning(f"Failed to broadcast to tenant {tenant_id}: {str(e)}")
        
        return sent_count

    async def broadcast_to_class(
        self, tenant_id: UUID, class_id: UUID, event_type: str, data: Dict[str, Any], db: Session
    ) -> int:
        """Send an event to all connected users in a class (teachers and enrolled students).
        
        Args:
            tenant_id: Tenant ID
            class_id: Class ID
            event_type: Type of event
            data: Event payload
            db: Database session for querying enrollments
            
        Returns:
            Number of messages sent
        """
        from src.domains.academic.models.core import Enrollment, Class
        
        # Query enrolled students and teacher
        class_record = db.query(Class).filter(Class.id == class_id).first()
        if not class_record:
            return 0
        
        # Collect teacher and student IDs
        target_user_ids = {class_record.teacher_id}
        enrollments = db.query(Enrollment).filter(Enrollment.class_id == class_id).all()
        for enrollment in enrollments:
            target_user_ids.add(enrollment.student_id)
        
        # Broadcast to each user
        sent_count = 0
        for user_id in target_user_ids:
            count = await self.broadcast_to_user(tenant_id, user_id, event_type, data)
            sent_count += count
        
        return sent_count

    def get_connection_count(self, tenant_id: Optional[UUID] = None) -> int:
        """Get count of active connections.
        
        Args:
            tenant_id: If specified, only count for this tenant; otherwise count all
            
        Returns:
            Number of active connections
        """
        if tenant_id:
            tenant_str = str(tenant_id)
            if tenant_str not in self.active_connections:
                return 0
            return sum(
                len(connections) for connections in self.active_connections[tenant_str].values()
            )
        
        total = 0
        for tenant_connections in self.active_connections.values():
            for user_connections in tenant_connections.values():
                total += len(user_connections)
        return total

    def get_connected_users(self, tenant_id: UUID) -> Set[str]:
        """Get set of connected user IDs for a tenant.
        
        Args:
            tenant_id: Tenant ID
            
        Returns:
            Set of user IDs (as strings)
        """
        tenant_str = str(tenant_id)
        if tenant_str not in self.active_connections:
            return set()
        return set(self.active_connections[tenant_str].keys())


# Global connection manager instance
manager = ConnectionManager()


# Event helper functions
async def emit_attendance_event(
    tenant_id: UUID, class_id: UUID, student_id: UUID, status: str, db: Session
) -> int:
    """Emit attendance update event to class.
    
    Args:
        tenant_id: Tenant ID
        class_id: Class ID
        student_id: Student ID
        status: Attendance status (present, absent, late)
        db: Database session
        
    Returns:
        Number of messages sent
    """
    return await manager.broadcast_to_class(
        tenant_id=tenant_id,
        class_id=class_id,
        event_type="attendance.updated",
        data={
            "student_id": str(student_id),
            "class_id": str(class_id),
            "status": status,
            "timestamp": datetime.utcnow().isoformat(),
        },
        db=db,
    )


async def emit_assignment_event(
    tenant_id: UUID, class_id: UUID, assignment_id: UUID, event_type: str, db: Session
) -> int:
    """Emit assignment event.
    
    Args:
        tenant_id: Tenant ID
        class_id: Class ID
        assignment_id: Assignment ID
        event_type: "assignment.created" or "assignment.updated"
        db: Database session
        
    Returns:
        Number of messages sent
    """
    return await manager.broadcast_to_class(
        tenant_id=tenant_id,
        class_id=class_id,
        event_type=event_type,
        data={
            "assignment_id": str(assignment_id),
            "class_id": str(class_id),
            "timestamp": datetime.utcnow().isoformat(),
        },
        db=db,
    )


async def emit_marks_event(
    tenant_id: UUID, user_id: UUID, exam_id: UUID, score: int, max_score: int
) -> int:
    """Emit marks/exam result event to student and parents.
    
    Args:
        tenant_id: Tenant ID
        user_id: Student ID
        exam_id: Exam ID
        score: Student's score
        max_score: Maximum possible score
        
    Returns:
        Number of messages sent
    """
    return await manager.broadcast_to_user(
        tenant_id=tenant_id,
        user_id=user_id,
        event_type="exam.results.updated",
        data={
            "exam_id": str(exam_id),
            "score": score,
            "max_score": max_score,
            "percentage": round((score / max_score * 100), 2) if max_score > 0 else 0,
            "timestamp": datetime.utcnow().isoformat(),
        },
    )
