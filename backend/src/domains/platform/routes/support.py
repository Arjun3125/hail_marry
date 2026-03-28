"""Support and documentation assistance routes."""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from auth.dependencies import get_current_user
from src.domains.identity.models.user import User
from src.domains.platform.services.docs_chatbot import (
    generate_support_response_async,
    get_docs_categories,
    get_faqs_by_category,
)

router = APIRouter(prefix="/api/support", tags=["Support"])


class DocsChatRequest(BaseModel):
    query: str


@router.post("/docs-chat")
async def docs_chat(
    request: DocsChatRequest,
    current_user: User = Depends(get_current_user),
):
    """Answer support questions using FAQ-based docs chatbot."""
    _ = current_user
    query = request.query.strip()
    if not query:
        raise HTTPException(status_code=400, detail="query is required")
    return await generate_support_response_async(query)


@router.get("/docs-chat/categories")
async def docs_chat_categories(current_user: User = Depends(get_current_user)):
    _ = current_user
    return {"categories": get_docs_categories()}


@router.get("/docs-chat/faqs/{category}")
async def docs_chat_faqs(category: str, current_user: User = Depends(get_current_user)):
    _ = current_user
    return {"category": category, "faqs": get_faqs_by_category(category)}
