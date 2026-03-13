"""Tests for OpenAI-compatible API and LLM provider registry."""
import pytest
from constants import DEFAULT_LLM_PROVIDER, SUPPORTED_LLM_PROVIDERS, OLLAMA_BASE_URL


def test_default_provider_is_ollama():
    assert DEFAULT_LLM_PROVIDER == "ollama"


def test_supported_providers():
    assert "ollama" in SUPPORTED_LLM_PROVIDERS
    assert "openai" in SUPPORTED_LLM_PROVIDERS
    assert "anthropic" in SUPPORTED_LLM_PROVIDERS


def test_ollama_base_url():
    assert OLLAMA_BASE_URL == "http://localhost:11434"


def test_provider_registry_list():
    from services.llm_providers import ProviderRegistry
    providers = ProviderRegistry.list_providers()
    assert "ollama" in providers
    assert "openai" in providers
    assert "anthropic" in providers


def test_provider_registry_get_ollama():
    from services.llm_providers import ProviderRegistry
    provider = ProviderRegistry.get("ollama")
    assert provider.name == "ollama"


def test_provider_registry_get_openai():
    from services.llm_providers import ProviderRegistry
    provider = ProviderRegistry.get("openai")
    assert provider.name == "openai"


def test_provider_registry_get_anthropic():
    from services.llm_providers import ProviderRegistry
    provider = ProviderRegistry.get("anthropic")
    assert provider.name == "anthropic"


def test_provider_registry_unknown_raises():
    from services.llm_providers import ProviderRegistry
    with pytest.raises(ValueError, match="Unknown LLM provider"):
        ProviderRegistry.get("unknown_provider")


def test_ollama_to_openai_format():
    from services.llm_providers import OllamaProvider
    ollama_resp = {
        "message": {"role": "assistant", "content": "Hello World"},
        "prompt_eval_count": 10,
        "eval_count": 5,
    }
    result = OllamaProvider._to_openai_format(ollama_resp, "llama3")
    assert result["object"] == "chat.completion"
    assert result["model"] == "llama3"
    assert len(result["choices"]) == 1
    assert result["choices"][0]["message"]["content"] == "Hello World"
    assert result["usage"]["total_tokens"] == 15


def test_register_custom_provider():
    from services.llm_providers import ProviderRegistry, LLMProvider

    class CustomProvider(LLMProvider):
        name = "custom"
        async def chat_completion(self, messages, model="", temperature=0.7, max_tokens=2048, stream=False):
            return {"choices": [{"message": {"content": "custom"}}]}
        async def list_models(self):
            return [{"id": "custom-model"}]

    ProviderRegistry.register("custom", CustomProvider)
    assert "custom" in ProviderRegistry.list_providers()
