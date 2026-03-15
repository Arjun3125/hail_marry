import pytest
import httpx
import asyncio

from services.llm_providers import OllamaProvider


class _MockResponse:
    def __init__(self, status_code=200, json_payload=None, text=""):
        self.status_code = status_code
        self._json_payload = json_payload or {}
        self.text = text
        self.request = httpx.Request("POST", "http://test")

    def raise_for_status(self):
        if self.status_code >= 400:
            raise httpx.HTTPStatusError(
                "error",
                request=self.request,
                response=httpx.Response(
                    status_code=self.status_code,
                    text=self.text,
                    request=self.request,
                ),
            )

    def json(self):
        return self._json_payload


def test_ollama_provider_fails_over_to_next_endpoint(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URLS", "http://ollama-1:11434,http://ollama-2:11434")
    provider = OllamaProvider()

    calls = []

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, json):
            calls.append(url)
            if "ollama-1" in url:
                raise httpx.ConnectError("down", request=httpx.Request("POST", url))
            return _MockResponse(
                status_code=200,
                json_payload={
                    "message": {"content": "ok"},
                    "prompt_eval_count": 5,
                    "eval_count": 7,
                },
            )

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: MockClient())

    result = asyncio.run(provider.chat_completion(messages=[{"role": "user", "content": "hi"}]))

    assert result["choices"][0]["message"]["content"] == "ok"
    assert calls == [
        "http://ollama-1:11434/api/chat",
        "http://ollama-2:11434/api/chat",
    ]


def test_ollama_provider_non_retryable_status_does_not_failover(monkeypatch):
    monkeypatch.setenv("OLLAMA_BASE_URLS", "http://ollama-1:11434,http://ollama-2:11434")
    provider = OllamaProvider()

    calls = []

    class MockClient:
        async def __aenter__(self):
            return self

        async def __aexit__(self, exc_type, exc_val, exc_tb):
            return False

        async def post(self, url, json):
            calls.append(url)
            return _MockResponse(status_code=400, text="bad request")

    monkeypatch.setattr(httpx, "AsyncClient", lambda timeout: MockClient())

    with pytest.raises(httpx.HTTPStatusError) as exc_info:
        asyncio.run(provider.chat_completion(messages=[{"role": "user", "content": "hi"}]))

    assert exc_info.value.response.status_code == 400
    assert calls == ["http://ollama-1:11434/api/chat"]
