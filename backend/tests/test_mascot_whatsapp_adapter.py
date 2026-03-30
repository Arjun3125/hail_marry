from contextlib import asynccontextmanager
from unittest.mock import AsyncMock

import pytest


@asynccontextmanager
async def _fake_async_session():
    yield object()


@pytest.mark.asyncio
async def test_run_whatsapp_agent_delegates_to_mascot(monkeypatch):
    from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

    mascot_mock = AsyncMock(
        return_value=type(
            "MascotResponse",
            (),
            {
                "reply_text": "Generated flashcards for photosynthesis.",
                "intent": "study_tool",
                "actions": [type("Action", (), {"kind": "study_tool", "payload": {"tool": "flashcards"}})()],
                "requires_confirmation": False,
                "confirmation_id": None,
                "notebook_id": "notebook-1",
            },
        )()
    )

    monkeypatch.setattr("database.AsyncSessionLocal", lambda: _fake_async_session())
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.handle_mascot_message", mascot_mock)

    result = await run_whatsapp_agent(
        message="mala flashcards pahije photosynthesis var",
        user_id="user-1",
        tenant_id="tenant-1",
        role="student",
        notebook_id="notebook-1",
        conversation_history=[{"role": "user", "content": "Hi"}],
    )

    assert result["response"] == "Generated flashcards for photosynthesis."
    assert result["intent"] == "study_tool"
    assert result["tool_name"] == "flashcards"
    assert result["notebook_id"] == "notebook-1"
    mascot_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_whatsapp_agent_formats_confirmation_prompt(monkeypatch):
    from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

    mascot_mock = AsyncMock(
        return_value=type(
            "MascotResponse",
            (),
            {
                "reply_text": "Please confirm before I archive that notebook.",
                "intent": "notebook_update",
                "actions": [type("Action", (), {"kind": "notebook_update", "payload": {"operation": "archive"}})()],
                "requires_confirmation": True,
                "confirmation_id": "mascot-confirm-123",
                "notebook_id": "notebook-1",
            },
        )()
    )

    monkeypatch.setattr("database.AsyncSessionLocal", lambda: _fake_async_session())
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.handle_mascot_message", mascot_mock)

    result = await run_whatsapp_agent(
        message="Delete Biology notebook",
        user_id="user-1",
        tenant_id="tenant-1",
        role="student",
        session_id="ws-1",
        pending_confirmation_id=None,
    )

    assert "reply *confirm* to continue" in result["response"].lower()
    assert result["requires_confirmation"] is True
    assert result["confirmation_id"] == "mascot-confirm-123"
    assert result["notebook_id"] == "notebook-1"


@pytest.mark.asyncio
async def test_run_whatsapp_agent_executes_pending_confirmation(monkeypatch):
    from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

    confirm_mock = AsyncMock(
        return_value=type(
            "MascotResponse",
            (),
            {
                "reply_text": "Archived notebook 'Biology'.",
                "intent": "confirm",
                "actions": [type("Action", (), {"kind": "confirm", "payload": {}})()],
                "requires_confirmation": False,
                "confirmation_id": None,
                "notebook_id": None,
            },
        )()
    )

    monkeypatch.setattr("database.AsyncSessionLocal", lambda: _fake_async_session())
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.execute_pending_confirmation", confirm_mock)

    result = await run_whatsapp_agent(
        message="confirm",
        user_id="user-1",
        tenant_id="tenant-1",
        role="student",
        session_id="ws-1",
        pending_confirmation_id="mascot-confirm-123",
    )

    assert result["response"] == "Archived notebook 'Biology'."
    assert result["intent"] == "confirm"
    assert result["confirmation_cleared"] is True
    confirm_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_run_whatsapp_agent_cancels_pending_confirmation(monkeypatch):
    from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

    confirm_mock = AsyncMock(
        return_value=type(
            "MascotResponse",
            (),
            {
                "reply_text": "Cancelled. I did not make any changes.",
                "intent": "confirm",
                "actions": [type("Action", (), {"kind": "confirm", "payload": {}})()],
                "requires_confirmation": False,
                "confirmation_id": None,
                "notebook_id": None,
            },
        )()
    )

    monkeypatch.setattr("database.AsyncSessionLocal", lambda: _fake_async_session())
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.execute_pending_confirmation", confirm_mock)

    result = await run_whatsapp_agent(
        message="cancel",
        user_id="user-1",
        tenant_id="tenant-1",
        role="student",
        session_id="ws-1",
        pending_confirmation_id="mascot-confirm-123",
    )

    assert result["response"] == "Cancelled. I did not make any changes."
    assert result["confirmation_cleared"] is True
    confirm_mock.assert_awaited_once()
    assert confirm_mock.await_args.kwargs["approved"] is False


@pytest.mark.asyncio
async def test_run_whatsapp_agent_keeps_normal_queries_when_pending_confirmation_exists(monkeypatch):
    from src.interfaces.whatsapp_bot.agent import run_whatsapp_agent

    mascot_mock = AsyncMock(
        return_value=type(
            "MascotResponse",
            (),
            {
                "reply_text": "Photosynthesis uses sunlight to make glucose.",
                "intent": "query",
                "actions": [type("Action", (), {"kind": "query", "payload": {"mode": "qa"}})()],
                "requires_confirmation": False,
                "confirmation_id": None,
                "notebook_id": "notebook-1",
            },
        )()
    )
    confirm_mock = AsyncMock()

    monkeypatch.setattr("database.AsyncSessionLocal", lambda: _fake_async_session())
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.handle_mascot_message", mascot_mock)
    monkeypatch.setattr("src.domains.platform.services.mascot_orchestrator.execute_pending_confirmation", confirm_mock)

    result = await run_whatsapp_agent(
        message="Explain photosynthesis",
        user_id="user-1",
        tenant_id="tenant-1",
        role="student",
        notebook_id="notebook-1",
        session_id="ws-1",
        pending_confirmation_id="mascot-confirm-123",
    )

    assert result["response"] == "Photosynthesis uses sunlight to make glucose."
    mascot_mock.assert_awaited_once()
    confirm_mock.assert_not_awaited()
