"""HTTP route for mascot chat API."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.bootstrap.app_factory import get_db_session
from src.domains.identity.models.user import User
from src.domains.mascot.services.mascot_agent import run_mascot_agent
from auth.dependencies import get_current_user

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_elicitation_turn: bool


@router.post("/chat", response_model=ChatResponse)
async def chat_with_mascot(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Chat with the mascot. Student only."""
    if current_user.role != "student":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Student access required")

    session_id = request.session_id or str(uuid.uuid4())

    # Get conversation history (simplified - would need proper history management)
    conversation_history = []  # TODO: Implement proper conversation history retrieval

    # Get student name
    student_name = current_user.full_name or "Student"

    result = await run_mascot_agent(
        student_message=request.message,
        student_id=str(current_user.id),
        tenant_id=str(current_user.tenant_id),
        student_name=student_name,
        session_id=session_id,
        turn_number=len(conversation_history) + 1,
        conversation_history=conversation_history,
    )

    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        is_elicitation_turn=False,  # TODO: Implement elicitation turn detection
    )
