"""HTTP route for mascot chat API."""

from __future__ import annotations

import logging
import uuid
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db as get_db_session
from src.domains.identity.models.user import User
from src.domains.mascot.models.conversation import MascotConversationTurn
from src.domains.mascot.services.mascot_agent import run_mascot_agent
from auth.dependencies import get_current_user

logger = logging.getLogger(__name__)

router = APIRouter()


class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None


class ChatResponse(BaseModel):
    response: str
    session_id: str
    is_elicitation_turn: bool


class GreetingResponse(BaseModel):
    greeting: str
    chips: List[str]
    has_urgent: bool


@router.post("/chat", response_model=ChatResponse)
async def chat_with_mascot(
    request: ChatRequest,
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """Chat with the mascot. All roles allowed."""
    session_id = request.session_id or str(uuid.uuid4())

    try:
        session_uuid = uuid.UUID(session_id)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid session_id: must be a valid UUID",
        )

    # Load recent turns — student_id column stores the user id regardless of role
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
            conversation_history.append({"role": "user", "content": turn.student_message})
        if turn.mascot_response:
            conversation_history.append({"role": "assistant", "content": turn.mascot_response})

    user_name = current_user.full_name or "there"

    result = await run_mascot_agent(
        student_message=request.message,
        student_id=str(current_user.id),
        tenant_id=str(current_user.tenant_id),
        student_name=user_name,
        session_id=session_id,
        turn_number=len(conversation_history) + 1,
        conversation_history=conversation_history,
        role=current_user.role,
    )

    turn_number = len(recent_turns) + 1
    new_turn = MascotConversationTurn(
        student_id=current_user.id,
        tenant_id=current_user.tenant_id,
        session_id=session_uuid,
        turn_number=turn_number,
        student_message=request.message,
        mascot_response=result["response"],
    )
    try:
        db.add(new_turn)
        db.commit()
    except Exception:
        db.rollback()
        logger.exception("Failed to persist mascot turn for session %s", session_id)

    return ChatResponse(
        response=result["response"],
        session_id=session_id,
        is_elicitation_turn=bool(result.get("is_elicitation_turn", False)),
    )


@router.get("/greeting", response_model=GreetingResponse)
async def get_mascot_greeting(
    db: Session = Depends(get_db_session),
    current_user: User = Depends(get_current_user),
):
    """
    Returns a role-aware proactive greeting, 3 action chips, and an urgency flag.
    All roles allowed. LLM failure falls back to a static greeting.
    """
    from src.domains.mascot.services.context_assembler import assemble_context_for_role
    from uuid import UUID

    user_name = current_user.full_name or "there"
    role = current_user.role

    try:
        context = assemble_context_for_role(
            db,
            UUID(str(current_user.id)),
            UUID(str(current_user.tenant_id)),
            user_name,
            role,
        )
    except Exception:
        logger.exception("Failed to assemble context for greeting, using fallback")
        context = None

    greeting = await _generate_greeting(context, role, user_name)
    chips = _build_chips(context, role)
    has_urgent = _check_urgency(context, role)

    return GreetingResponse(greeting=greeting, chips=chips, has_urgent=has_urgent)


async def _generate_greeting(context, role: str, user_name: str = "there") -> str:
    """Single LLM call to generate a warm one-sentence greeting. Falls back on error."""
    fallback = f"Good morning {user_name}! Ready to help. 🦉"
    if context is None:
        return fallback
    try:
        from src.infrastructure.llm.providers import get_llm_provider
        provider = get_llm_provider()
        ctx_text = context.to_prompt_context()
        system = (
            f"You are VidyaOS Mascot. Write exactly ONE warm sentence greeting for "
            f"{role} {user_name}. Use Hinglish. Use ONLY these facts:\n{ctx_text}\n"
            f"Max 20 words. No bullet points. Just the sentence."
        )
        response = await provider.generate(system)
        return response.strip() if response else fallback
    except Exception:
        logger.exception("Greeting LLM call failed, using fallback")
        return fallback


def _build_chips(context, role: str) -> list[str]:
    """Build up to 3 action chip labels from context. Deterministic — no LLM."""
    chips: list[str] = []
    if context is None:
        return ["Ask a question", "View my data", "Help me out"]

    if role == "student":
        ws = getattr(context, "weakest_subject", None)
        if ws:
            chips.append(f"Revise {ws}")
        if getattr(context, "topics_due_for_review", None):
            chips.append("My reviews")
        chips.append("My homework")

    elif role == "teacher":
        if getattr(context, "absent_count_today", 0) > 0:
            chips.append("View attendance")
        if getattr(context, "pending_review_count", 0) > 0:
            chips.append("Grade papers")
        chips.append("My schedule")

    elif role == "parent":
        child = getattr(context, "child_name", "child")
        if getattr(context, "attendance_today", "Unknown") == "Absent":
            chips.append(f"Why was {child} absent?")
        ws = getattr(context, "weak_subjects", [])
        if ws:
            chips.append(f"{child}'s {ws[0]} marks")
        chips.append("Fee status")

    elif role == "admin":
        if getattr(context, "open_alerts", 0) > 0:
            chips.append("View alerts")
        if getattr(context, "fee_defaulters_count", 0) > 0:
            chips.append("Fee pending list")
        chips.append("AI queue status")

    return chips[:3]


def _check_urgency(context, role: str) -> bool:
    """Return True if there's something urgent for the role. Deterministic."""
    if context is None:
        return False
    if role == "student":
        ws = getattr(context, "weakest_subject", None)
        score = getattr(context, "overall_score_pct", None)
        return ws is not None and score is not None and score < 60
    if role == "teacher":
        return (
            getattr(context, "absent_count_today", 0) > 0
            or getattr(context, "pending_review_count", 0) > 0
        )
    if role == "parent":
        return (
            getattr(context, "attendance_today", "Unknown") == "Absent"
            or len(getattr(context, "weak_subjects", [])) > 0
            or getattr(context, "fee_due", False)
        )
    if role == "admin":
        return (
            getattr(context, "open_alerts", 0) > 0
            or getattr(context, "queue_pending", 0) > 5
        )
    return False
