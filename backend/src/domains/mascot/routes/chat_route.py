"""HTTP route for mascot chat API."""

from __future__ import annotations

import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db as get_db_session
from src.domains.identity.models.user import User
from src.domains.mascot.models.conversation import MascotConversationTurn
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

    # Load recent turns for this session (last 8 exchanges = 16 rows max)
    session_uuid = uuid.UUID(session_id)
    recent_turns = (
        db.query(MascotConversationTurn)
        .filter(
            MascotConversationTurn.student_id == current_user.id,
            MascotConversationTurn.session_id == session_uuid,
        )
        .order_by(MascotConversationTurn.turn_number.asc())
        .limit(16)
        .all()
    )
    conversation_history: list[dict] = []
    for turn in recent_turns:
        if turn.student_message:
            conversation_history.append({"role": "student", "content": turn.student_message})
        if turn.mascot_response:
            conversation_history.append({"role": "mascot", "content": turn.mascot_response})

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

    # Persist this turn for future context
    turn_number = len(recent_turns) + 1
    new_turn = MascotConversationTurn(
        student_id=current_user.id,
        tenant_id=current_user.tenant_id,
        session_id=session_uuid,
        turn_number=turn_number,
        student_message=request.message,
        mascot_response=result["response"],
    )
    db.add(new_turn)
    db.commit()

    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        is_elicitation_turn=bool(result.get("is_elicitation_turn", False)),
    )
