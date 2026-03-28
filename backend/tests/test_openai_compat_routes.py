def test_openai_compat_requires_configured_api_key(client, monkeypatch):
    from src.interfaces.rest_api.ai.routes import openai_compat

    monkeypatch.setattr(openai_compat.settings.ai_service, "compat_api_keys", [])
    monkeypatch.setattr(openai_compat.settings.ai_service, "api_key", "")

    response = client.get("/v1/models")

    assert response.status_code == 503
    assert response.json()["detail"] == "OpenAI-compatible API is not configured with any access keys."


def test_openai_compat_rejects_invalid_api_key(client, monkeypatch):
    from src.interfaces.rest_api.ai.routes import openai_compat

    monkeypatch.setattr(openai_compat.settings.ai_service, "compat_api_keys", ["compat-test-key"])
    monkeypatch.setattr(openai_compat.settings.ai_service, "api_key", "")

    response = client.get("/v1/models", headers={"Authorization": "Bearer wrong-key"})

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid API key."


def test_openai_compat_accepts_valid_bearer_token(client, monkeypatch):
    from src.interfaces.rest_api.ai.routes import openai_compat

    class FakeProvider:
        name = "fake"

        async def chat_completion(self, **_kwargs):
            return {
                "object": "chat.completion",
                "model": "llama3",
                "choices": [{"message": {"role": "assistant", "content": "secured"}}],
            }

    monkeypatch.setattr(openai_compat.settings.ai_service, "compat_api_keys", ["compat-test-key"])
    monkeypatch.setattr(openai_compat.settings.ai_service, "api_key", "")
    monkeypatch.setattr(openai_compat.ProviderRegistry, "get", staticmethod(lambda provider=None: FakeProvider()))

    response = client.post(
        "/v1/chat/completions",
        headers={"Authorization": "Bearer compat-test-key"},
        json={
            "model": "llama3",
            "messages": [{"role": "user", "content": "hello"}],
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["choices"][0]["message"]["content"] == "secured"
    assert payload["id"].startswith("chatcmpl-")
    assert "created" in payload


def test_openai_compat_accepts_x_api_key_header(client, monkeypatch):
    from src.interfaces.rest_api.ai.routes import openai_compat

    class FakeProvider:
        name = "fake"

        async def list_models(self):
            return [{"id": "llama3", "object": "model"}]

    monkeypatch.setattr(openai_compat.settings.ai_service, "compat_api_keys", ["compat-test-key"])
    monkeypatch.setattr(openai_compat.settings.ai_service, "api_key", "")
    monkeypatch.setattr(openai_compat.ProviderRegistry, "get", staticmethod(lambda provider=None: FakeProvider()))

    response = client.get("/v1/models", headers={"X-API-Key": "compat-test-key"})

    assert response.status_code == 200
    payload = response.json()
    assert payload["object"] == "list"
    assert payload["data"][0]["id"] == "llama3"
