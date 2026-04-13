"""Mascot conversation agent using LangGraph."""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional, TypedDict
from uuid import UUID

from langgraph.graph import END, StateGraph

from src.infrastructure.llm.providers import get_llm_provider

from .context_assembler import assemble_context
from .elicitation_scheduler import get_next_elicitation, record_elicitation_asked
from .memory_manager import increment_interaction_count, update_memory
from .profile_manager import save_signal
from .prompt_builder import build_mascot_system_prompt
from .signal_extractor import detect_emotional_state, extract_signals_from_text
from ..models.conversation import MascotConversationTurn
from ..models.mascot_memory import MascotMemoryUpdate

logger = logging.getLogger(__name__)


class MascotAgentState(TypedDict):
    """State for the mascot conversation agent."""

    # Input
    student_message: str
    student_id: str
    tenant_id: str
    student_name: str
    session_id: str
    turn_number: int
    conversation_history: List[Dict[str, str]]  # [{"role": "student"|"mascot", "content": str}]

    # Assembled context (filled by load_context node)
    mascot_context: Optional[Dict[str, Any]]  # MascotContext serialized to dict
    system_prompt: Optional[str]
    elicitation_question: Optional[Dict[str, Any]]

    # Signal extraction (filled by extract_signals node)
    detected_emotional_state: Optional[str]
    extracted_signals: Optional[List[Dict[str, Any]]]

    # Response (filled by generate_response node)
    mascot_response: Optional[str]
    is_elicitation_turn: bool  # True if this turn includes an elicitation question

    # Output
    final_response: Optional[str]


async def load_context_node(state: MascotAgentState) -> Dict[str, Any]:
    """
    Load context, build system prompt, and determine elicitation question.
    """
    try:
        from src.bootstrap.app_factory import get_db_session

        db = next(get_db_session())
        student_id = UUID(state["student_id"])
        tenant_id = UUID(state["tenant_id"])

        # Assemble context
        mascot_context = assemble_context(db, student_id, tenant_id, state["student_name"])

        # Build system prompt
        system_prompt = build_mascot_system_prompt(mascot_context)

        # Get elicitation question
        from ..models.personality_profile import StudentPersonalityProfile
        profile = db.query(StudentPersonalityProfile).filter(
            StudentPersonalityProfile.student_id == student_id,
            StudentPersonalityProfile.tenant_id == tenant_id
        ).first()

        elicitation_question = None
        if profile:
            elicitation_question = get_next_elicitation(
                db, student_id, tenant_id,
                mascot_context.total_interactions, profile
            )

        return {
            "mascot_context": mascot_context.__dict__,
            "system_prompt": system_prompt,
            "elicitation_question": elicitation_question,
        }
    except Exception as e:
        logger.exception(f"Failed to load context for student {state['student_id']}: {e}")
        # Return safe defaults
        return {
            "mascot_context": None,
            "system_prompt": "You are a helpful study companion.",
            "elicitation_question": None,
        }


async def extract_signals_node(state: MascotAgentState) -> Dict[str, Any]:
    """
    Extract signals and detect emotional state from the student message.
    """
    try:
        signals = extract_signals_from_text(state["student_message"])
        emotional_state = detect_emotional_state(state["student_message"])

        return {
            "detected_emotional_state": emotional_state,
            "extracted_signals": [s.__dict__ for s in signals],
        }
    except Exception as e:
        logger.exception(f"Failed to extract signals: {e}")
        return {
            "detected_emotional_state": "neutral",
            "extracted_signals": [],
        }


async def generate_response_node(state: MascotAgentState) -> Dict[str, Any]:
    """
    Generate the mascot response using the LLM.
    """
    try:
        provider = get_llm_provider()

        # Build messages
        messages = [{"role": "system", "content": state["system_prompt"]}]
        messages.extend(state["conversation_history"][-8:])  # Last 8 turns
        messages.append({"role": "user", "content": state["student_message"]})

        # Add elicitation question if appropriate
        elicitation_text = ""
        is_elicitation_turn = False
        if (state["elicitation_question"] and
            state["turn_number"] % 5 == 0):  # Every 5th turn
            elicitation_text = f"\n\n{state['elicitation_question']['text']}"
            is_elicitation_turn = True

        # Generate response
        full_prompt = "\n".join([msg["content"] for msg in messages]) + elicitation_text
        response = await provider.generate(full_prompt)

        return {
            "mascot_response": response,
            "is_elicitation_turn": is_elicitation_turn,
        }
    except Exception as e:
        logger.exception(f"Failed to generate response: {e}")
        return {
            "mascot_response": "I'm here to help you study! What would you like to work on today?",
            "is_elicitation_turn": False,
        }


async def persist_and_format_node(state: MascotAgentState) -> Dict[str, Any]:
    """
    Save conversation turn, signals, and update memory.
    """
    try:
        from src.bootstrap.app_factory import get_db_session

        db = next(get_db_session())
        student_id = UUID(state["student_id"])
        tenant_id = UUID(state["tenant_id"])
        session_id = UUID(state["session_id"])

        # Save conversation turn
        turn = MascotConversationTurn(
            student_id=student_id,
            tenant_id=tenant_id,
            session_id=session_id,
            turn_number=state["turn_number"],
            student_message=state["student_message"],
            mascot_response=state["mascot_response"],
            emotional_state=state["detected_emotional_state"],
            elicitation_question_key=state["elicitation_question"]["key"] if state["elicitation_question"] else None,
        )
        db.add(turn)

        # Save signals
        if state["extracted_signals"]:
            for signal_dict in state["extracted_signals"]:
                from ..models.signals import ExtractedSignal
                signal = ExtractedSignal(**signal_dict)
                save_signal(db, student_id, tenant_id, signal, "whatsapp")

        # Update memory
        increment_interaction_count(db, student_id, tenant_id)

        if state["elicitation_question"] and state["is_elicitation_turn"]:
            record_elicitation_asked(db, student_id, tenant_id, state["elicitation_question"])

        # Update emotional state in memory
        update_data = MascotMemoryUpdate(last_emotional_state=state["detected_emotional_state"])
        update_memory(db, student_id, tenant_id, update_data)

        db.commit()

    except Exception as e:
        logger.exception(f"Failed to persist conversation data: {e}")
        # Don't fail the response

    return {"final_response": state["mascot_response"]}


def build_mascot_agent_graph() -> StateGraph:
    """Build the mascot agent LangGraph."""
    graph = StateGraph(MascotAgentState)
    graph.add_node("load_context", load_context_node)
    graph.add_node("extract_signals", extract_signals_node)
    graph.add_node("generate_response", generate_response_node)
    graph.add_node("persist_and_format", persist_and_format_node)

    graph.set_entry_point("load_context")
    graph.add_edge("load_context", "extract_signals")
    graph.add_edge("extract_signals", "generate_response")
    graph.add_edge("generate_response", "persist_and_format")
    graph.add_edge("persist_and_format", END)

    return graph.compile()


mascot_agent_app = build_mascot_agent_graph()


async def run_mascot_agent(student_message: str, student_id: str,
                            tenant_id: str, student_name: str,
                            session_id: str, turn_number: int,
                            conversation_history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Entry point for the mascot agent.
    Returns dict with 'response' key.
    """
    initial_state: MascotAgentState = {
        "student_message": student_message,
        "student_id": student_id,
        "tenant_id": tenant_id,
        "student_name": student_name,
        "session_id": session_id,
        "turn_number": turn_number,
        "conversation_history": conversation_history,
        "mascot_context": None,
        "system_prompt": None,
        "elicitation_question": None,
        "detected_emotional_state": None,
        "extracted_signals": None,
        "mascot_response": None,
        "is_elicitation_turn": False,
        "final_response": None,
    }

    result = await mascot_agent_app.ainvoke(initial_state)
    return {"response": result.get("final_response", ""), "response_type": "text"}
