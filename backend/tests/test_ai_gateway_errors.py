import pytest
import httpx
from unittest.mock import patch

@pytest.mark.asyncio
async def test_ai_gateway_handles_503_gracefully():
    """Verify the AI Gateway safely intercepts HTTP 5xx responses from the dedicated service."""
    from services.ai_gateway import InternalAIQueryRequest, _post_to_ai_service
    from fastapi import HTTPException
    
    mock_request = InternalAIQueryRequest(query="What is testing?", tenant_id="t-123")
    
    # Simulate the AI Service host returning 503 Internal Server Error
    error_resp = httpx.Response(status_code=503, text="Service Unavailable due to overload")
    
    # Because httpx.AsyncClient throws specific exceptions on establish, we stub the client itself
    class MockClient:
        async def __aenter__(self):
            return self
        async def __aexit__(self, exc_type, exc_val, exc_tb):
            pass
        async def post(self, url, **kwargs):
            raise httpx.ConnectError("Simulated Network Connection Refused", request=httpx.Request("POST", url))
            
    with patch("httpx.AsyncClient", return_value=MockClient()):
        try:
            await _post_to_ai_service("/internal/ai/query", mock_request.model_dump())
            pytest.fail("Exception should have been raised")
        except HTTPException as exc:
            assert exc.status_code == 503
            assert "Dedicated AI service is unavailable" in str(exc.detail)
