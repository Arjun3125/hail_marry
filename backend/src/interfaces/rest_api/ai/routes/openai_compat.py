"""OpenAI-compatible API — /v1/chat/completions and /v1/models endpoints.

Allows external tools (LangChain, AutoGen, etc.) to connect to VidyaOS
as if it were an OpenAI API, routing to the configured LLM provider
(Ollama self-hosted by default, or any 3rd-party provider).
"""
import hmac
import time
import uuid

from fastapi import APIRouter, Depends, Header, HTTPException, status
from pydantic import BaseModel
from typing import Optional

from config import settings
from src.domains.platform.services.llm_providers import ProviderRegistry

router = APIRouter(prefix="/v1", tags=["OpenAI-Compatible API"])


# ── Request / Response schemas (OpenAI format) ──

class ChatMessage(BaseModel):
    role: str
    content: str


class ChatCompletionRequest(BaseModel):
    model: str = "llama3"
    messages: list[ChatMessage]
    temperature: float = 0.7
    max_tokens: int = 2048
    stream: bool = False
    provider: Optional[str] = None  # override: "ollama", "openai", "anthropic"


# ── Auth helper ──

def _extract_auth_token(authorization: str, x_api_key: str) -> str:
    if authorization:
        if not authorization.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authorization header must use Bearer auth",
            )
        token = authorization[7:].strip()
        if not token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Empty bearer token",
            )
        return token

    if x_api_key:
        token = x_api_key.strip()
        if token:
            return token

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Missing API key. Provide Authorization: Bearer <key> or X-API-Key.",
    )


def _validate_api_key(
    authorization: str = Header(default=""),
    x_api_key: str = Header(default="", alias="X-API-Key"),
):
    valid_keys = settings.ai_service.resolved_compat_api_keys()
    if not valid_keys:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="OpenAI-compatible API is not configured with any access keys.",
        )

    token = _extract_auth_token(authorization, x_api_key)
    if not any(hmac.compare_digest(token, key) for key in valid_keys):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid API key.",
        )

    return token


# ── Endpoints ──

@router.post("/chat/completions")
async def chat_completions(
    body: ChatCompletionRequest,
    auth: str = Depends(_validate_api_key),
):
    """OpenAI-compatible chat completion endpoint.

    Routes to the configured LLM provider (default: Ollama self-hosted).
    Use the `provider` field to override per-request.
    """
    try:
        provider = ProviderRegistry.get(body.provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    messages = [{"role": m.role, "content": m.content} for m in body.messages]

    try:
        result = await provider.chat_completion(
            messages=messages,
            model=body.model,
            temperature=body.temperature,
            max_tokens=body.max_tokens,
            stream=body.stream,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"LLM provider '{provider.name}' error: {str(exc)}",
        )

    # Ensure response has required fields
    if "created" not in result:
        result["created"] = int(time.time())
    if "id" not in result:
        result["id"] = f"chatcmpl-{uuid.uuid4().hex[:12]}"

    return result


@router.get("/models")
async def list_models(
    auth: str = Depends(_validate_api_key),
    provider: Optional[str] = None,
):
    """List available models from the active LLM provider."""
    try:
        p = ProviderRegistry.get(provider)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    try:
        models = await p.list_models()
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail=f"Failed to list models from '{p.name}': {str(exc)}",
        )

    return {"object": "list", "data": models}


@router.get("/providers")
async def list_providers():
    """List all registered LLM providers."""
    return {
        "providers": ProviderRegistry.list_providers(),
        "active": ProviderRegistry.get().name,
    }
