"""WhatsApp NLP intent router and lightweight study assistant integration."""
import json
import logging
import os
import uuid
from tempfile import NamedTemporaryFile
from typing import Literal, Optional

import httpx
from langchain_core.prompts import PromptTemplate
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from config import settings
from src.domains.identity.models.user import User
from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest, InternalStudyToolGenerateRequest
from src.domains.platform.services.ai_gateway import run_study_tool, run_text_query
from src.infrastructure.vector_store.ingestion import ingest_document
from src.infrastructure.llm.cache import invalidate_tenant_cache

logger = logging.getLogger(__name__)


def get_fast_llm():
    """Compatibility helper for the legacy WhatsApp intent router."""
    provider = (settings.llm.provider or "ollama").lower()
    if provider == "openai":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            api_key=settings.llm.openai_api_key,
        )
    if provider == "groq":
        from langchain_groq import ChatGroq

        return ChatGroq(
            model=settings.llm.model,
            temperature=settings.llm.temperature,
            api_key=settings.llm.groq_api_key,
        )

    from langchain_ollama import ChatOllama

    return ChatOllama(
        model=settings.llm.model,
        temperature=settings.llm.temperature,
        base_url=settings.llm.url,
    )


class WhatsAppIntent(BaseModel):
    action: Literal["query", "quiz", "flashcards", "mindmap", "flowchart", "concept_map", "video_overview", "audio_overview"] = Field(
        description="The recognized user intent action."
    )
    extracted_topic: str = Field(
        description="The main topic of study extracted from the message."
    )


INTENT_TEMPLATE = """You are an intent router for a WhatsApp AI Study Assistant.
The user speaks English, Hindi, Marathi, or a mix of these (Hinglish, etc).
Extract their core intent and map it to an exact action.
Valid actions: query, quiz, flashcards, mindmap, flowchart, concept_map.
If they just ask a question, use 'query'. If they ask to make a quiz, use 'quiz'.

User message: "{message}"

Map this to the appropriate structured intent:
"""


def format_whatsapp_response(result: dict, intent: str) -> str:
    """Format structured backend results into plain WhatsApp-friendly markdown."""
    text = ""

    if intent == "query":
        text += result.get("answer", "")
    elif intent == "quiz":
        text += "*Generated Quiz*\n\n"
        try:
            quiz_data = json.loads(result.get("tool_data", "{}"))
            for i, question in enumerate(quiz_data.get("questions", []), start=1):
                text += f"*{i}. {question.get('q')}*\n"
                for j, option in enumerate(question.get("options", [])):
                    text += f"   {chr(65 + j)}. {option}\n"
                text += "\n"
        except Exception:
            text += "Failed to parse quiz format"
    elif intent == "flashcards":
        text += "*Flashcards*\n\n"
        try:
            flashcard_data = json.loads(result.get("tool_data", "{}"))
            for card in flashcard_data.get("cards", []):
                text += f"- *Q:* {card.get('front')}\n  *A:* {card.get('back')}\n\n"
        except Exception:
            text += "Failed to parse flashcards"
    elif intent in ["mindmap", "flowchart", "concept_map"]:
        text += (
            f"*{intent.title().replace('_', ' ')} Generated!*\n\n"
            "Please visit the VidyaOS dashboard web interface to view this saved visual diagram."
        )
    else:
        text += str(result)

    citations = result.get("citations", [])
    if citations:
        text += "\n\n_Sources:_\n"
        for citation in citations:
            text += f"- {citation.get('source', 'Document')}\n"

    return text.strip()


async def _download_whatsapp_media(media_id: str) -> tuple[bytes, str]:
    """Resolve a Meta media id to bytes plus content type."""
    if not settings.whatsapp.token:
        raise ValueError("WHATSAPP_TOKEN is required to download inbound media.")

    headers = {"Authorization": f"Bearer {settings.whatsapp.token}"}
    media_meta_url = f"{settings.whatsapp.api_url}/{media_id}"

    async with httpx.AsyncClient(timeout=30, follow_redirects=True) as client:
        meta_response = await client.get(media_meta_url, headers=headers)
        meta_response.raise_for_status()
        media_url = meta_response.json().get("url")
        if not media_url:
            raise ValueError("WhatsApp media lookup did not return a download URL.")

        media_response = await client.get(media_url, headers=headers)
        media_response.raise_for_status()
        return media_response.content, media_response.headers.get("Content-Type", "")


def _infer_media_suffix(content_type: str) -> str:
    normalized = (content_type or "").lower()
    if "pdf" in normalized:
        return ".pdf"
    if "png" in normalized:
        return ".png"
    if "jpeg" in normalized or "jpg" in normalized:
        return ".jpg"
    if "webp" in normalized:
        return ".webp"
    if "mp3" in normalized or "mpeg" in normalized:
        return ".mp3"
    if "mp4" in normalized:
        return ".mp4"
    return ".bin"


async def _ingest_media_upload(user: User, media_id: str) -> str:
    content, content_type = await _download_whatsapp_media(media_id)
    tmp_path = None
    try:
        with NamedTemporaryFile(delete=False, suffix=_infer_media_suffix(content_type)) as tmp:
            tmp.write(content)
            tmp_path = tmp.name

        ingest_document(
            file_path=tmp_path,
            document_id=str(uuid.uuid4()),
            tenant_id=str(user.tenant_id),
            subject_id=None,
            notebook_id=None,
        )
        invalidate_tenant_cache(str(user.tenant_id))
        return "Received your document. It has been added to your knowledge base."
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


async def handle_whatsapp_intent(user: User, body: str, media_id: Optional[str], db: Session) -> str:
    """Classify a WhatsApp message and trigger the corresponding study workflow."""
    del db  # Reserved for future legacy router compatibility paths.

    if media_id:
        try:
            return await _ingest_media_upload(user, media_id)
        except Exception as exc:
            logger.error("WhatsApp media ingestion failed: %s", exc)
            return f"Failed to ingest document. Error: {exc}"

    if not body:
        return "Please send a message, question, or study material to get started."

    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(WhatsAppIntent)
    prompt = PromptTemplate.from_template(INTENT_TEMPLATE)
    chain = prompt | structured_llm

    try:
        intent_result: WhatsAppIntent = chain.invoke({"message": body})
        logger.info(
            "[WhatsApp] Detected intent: %s for topic: %s",
            intent_result.action,
            intent_result.extracted_topic,
        )
    except Exception as exc:
        logger.error("WhatsApp intent parsing failed: %s", exc)
        intent_result = WhatsAppIntent(action="query", extracted_topic=body)

    if intent_result.action == "query":
        request = InternalAIQueryRequest(
            tenant_id=str(user.tenant_id),
            query=intent_result.extracted_topic,
            mode="qa",
            notebook_id=None,
        )
        result = await run_text_query(request)
        return format_whatsapp_response(result, intent_result.action)

    if intent_result.action in ["quiz", "flashcards", "mindmap", "flowchart", "concept_map"]:
        request = InternalStudyToolGenerateRequest(
            tenant_id=str(user.tenant_id),
            tool=intent_result.action,
            topic=intent_result.extracted_topic,
            subject_id=None,
        )
        result = await run_study_tool(request)
        return format_whatsapp_response(result, intent_result.action)

    return "I wasn't sure how to handle that request. Please try a question or ask for quiz/flashcards."
