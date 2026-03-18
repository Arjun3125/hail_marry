"""Tests for the AI Gateway service.

The old `_post_to_ai_service` helper has been removed since we now call AI
workflows directly (monolith). These tests verify the gateway routes requests
to the correct underlying workflow function and surfaces errors cleanly.
"""
import pytest
from unittest.mock import AsyncMock, patch

from src.domains.ai_engine.services.ai_gateway import run_text_query, run_audio_overview
from src.domains.ai_engine.schemas.ai_runtime import InternalAIQueryRequest, InternalAudioOverviewRequest


@pytest.mark.asyncio
async def test_run_text_query_raises_when_workflow_fails():
    """Verify the AI Gateway surfaces errors from the underlying workflow."""
    from fastapi import HTTPException

    mock_request = InternalAIQueryRequest(query="What is testing?", tenant_id="t-123")

    with patch(
        "src.domains.ai_engine.services.ai_gateway.execute_text_query",
        new_callable=AsyncMock,
        side_effect=RuntimeError("Workflow execution failed"),
    ):
        with pytest.raises(RuntimeError, match="Workflow execution failed"):
            await run_text_query(mock_request)


@pytest.mark.asyncio
async def test_run_text_query_returns_dict_on_success():
    """Verify gateway returns a dict when the workflow succeeds."""
    mock_request = InternalAIQueryRequest(query="What is testing?", tenant_id="t-123")
    expected = {"answer": "Testing is important.", "sources": []}

    with patch(
        "src.domains.ai_engine.services.ai_gateway.execute_text_query",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        result = await run_text_query(mock_request)

    assert result["answer"] == "Testing is important."


@pytest.mark.asyncio
async def test_run_audio_overview_returns_audio_payload():
    """Verify gateway passes through the audio overview workflow result."""
    mock_request = InternalAudioOverviewRequest(
        topic="Photosynthesis",
        format="brief",
        language="english",
        tenant_id="t-123",
    )
    expected = {"title": "Photosynthesis", "dialogue": [], "duration_estimate": "3 minutes"}

    with patch(
        "src.domains.ai_engine.services.ai_gateway.execute_audio_overview",
        new_callable=AsyncMock,
        return_value=expected,
    ):
        result = await run_audio_overview(mock_request)

    assert result["title"] == "Photosynthesis"
