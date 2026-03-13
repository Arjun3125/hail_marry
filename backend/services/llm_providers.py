"""Pluggable LLM provider registry — Ollama (self-hosted), OpenAI, Anthropic.

Usage:
    provider = ProviderRegistry.get()  # uses DEFAULT_LLM_PROVIDER
    result = await provider.chat_completion(messages, model="llama3")
"""
import os
from abc import ABC, abstractmethod
from typing import Any, Optional

import httpx

from constants import DEFAULT_LLM_PROVIDER, OLLAMA_BASE_URL, SUPPORTED_LLM_PROVIDERS


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""

    name: str = "base"

    @abstractmethod
    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> dict[str, Any]:
        """Send a chat completion request and return OpenAI-format response."""
        ...

    @abstractmethod
    async def list_models(self) -> list[dict]:
        """List available models from this provider."""
        ...


class OllamaProvider(LLMProvider):
    """Self-hosted Ollama provider — no API key needed."""

    name = "ollama"

    def __init__(self):
        self.base_url = os.getenv("OLLAMA_BASE_URL", OLLAMA_BASE_URL)

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "llama3",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> dict[str, Any]:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,  # Non-streaming for now
            "options": {"temperature": temperature, "num_predict": max_tokens},
        }
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(f"{self.base_url}/api/chat", json=payload)
            resp.raise_for_status()
            data = resp.json()

        return self._to_openai_format(data, model)

    async def list_models(self) -> list[dict]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/api/tags")
            resp.raise_for_status()
            data = resp.json()

        return [
            {"id": m["name"], "object": "model", "owned_by": "ollama"}
            for m in data.get("models", [])
        ]

    @staticmethod
    def _to_openai_format(ollama_resp: dict, model: str) -> dict:
        message = ollama_resp.get("message", {})
        return {
            "id": f"chatcmpl-ollama-{id(ollama_resp)}",
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": message.get("content", "")},
                    "finish_reason": "stop",
                }
            ],
            "usage": {
                "prompt_tokens": ollama_resp.get("prompt_eval_count", 0),
                "completion_tokens": ollama_resp.get("eval_count", 0),
                "total_tokens": ollama_resp.get("prompt_eval_count", 0)
                + ollama_resp.get("eval_count", 0),
            },
        }


class OpenAIProvider(LLMProvider):
    """OpenAI API provider — requires OPENAI_API_KEY env var."""

    name = "openai"

    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY", "")
        self.base_url = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> dict[str, Any]:
        headers = {"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/chat/completions", json=payload, headers=headers)
            resp.raise_for_status()
            return resp.json()

    async def list_models(self) -> list[dict]:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(f"{self.base_url}/models", headers=headers)
            resp.raise_for_status()
            data = resp.json()
        return data.get("data", [])


class AnthropicProvider(LLMProvider):
    """Anthropic Claude API provider — requires ANTHROPIC_API_KEY env var."""

    name = "anthropic"

    def __init__(self):
        self.api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self.base_url = "https://api.anthropic.com/v1"

    async def chat_completion(
        self,
        messages: list[dict],
        model: str = "claude-3-haiku-20240307",
        temperature: float = 0.7,
        max_tokens: int = 2048,
        stream: bool = False,
    ) -> dict[str, Any]:
        headers = {
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
            "Content-Type": "application/json",
        }
        # Convert OpenAI format to Anthropic format
        system_msg = ""
        user_messages = []
        for m in messages:
            if m["role"] == "system":
                system_msg = m["content"]
            else:
                user_messages.append(m)

        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "messages": user_messages,
        }
        if system_msg:
            payload["system"] = system_msg

        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{self.base_url}/messages", json=payload, headers=headers)
            resp.raise_for_status()
            data = resp.json()

        # Convert Anthropic response to OpenAI format
        content = ""
        for block in data.get("content", []):
            if block.get("type") == "text":
                content += block.get("text", "")

        return {
            "id": data.get("id", ""),
            "object": "chat.completion",
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": content},
                    "finish_reason": data.get("stop_reason", "stop"),
                }
            ],
            "usage": {
                "prompt_tokens": data.get("usage", {}).get("input_tokens", 0),
                "completion_tokens": data.get("usage", {}).get("output_tokens", 0),
                "total_tokens": data.get("usage", {}).get("input_tokens", 0)
                + data.get("usage", {}).get("output_tokens", 0),
            },
        }

    async def list_models(self) -> list[dict]:
        return [
            {"id": "claude-3-haiku-20240307", "object": "model", "owned_by": "anthropic"},
            {"id": "claude-3-sonnet-20240229", "object": "model", "owned_by": "anthropic"},
            {"id": "claude-3-opus-20240229", "object": "model", "owned_by": "anthropic"},
        ]


# ── Provider Registry ──

_PROVIDERS: dict[str, type[LLMProvider]] = {
    "ollama": OllamaProvider,
    "openai": OpenAIProvider,
    "anthropic": AnthropicProvider,
}

_instances: dict[str, LLMProvider] = {}


class ProviderRegistry:
    """Singleton registry for LLM providers."""

    @staticmethod
    def get(name: Optional[str] = None) -> LLMProvider:
        """Get a provider instance by name. Defaults to configured provider."""
        provider_name = name or os.getenv("LLM_PROVIDER", DEFAULT_LLM_PROVIDER)
        if provider_name not in _PROVIDERS:
            raise ValueError(f"Unknown LLM provider: {provider_name}. Supported: {SUPPORTED_LLM_PROVIDERS}")
        if provider_name not in _instances:
            _instances[provider_name] = _PROVIDERS[provider_name]()
        return _instances[provider_name]

    @staticmethod
    def register(name: str, provider_class: type[LLMProvider]):
        """Register a custom 3rd-party provider."""
        _PROVIDERS[name] = provider_class

    @staticmethod
    def list_providers() -> list[str]:
        return list(_PROVIDERS.keys())
