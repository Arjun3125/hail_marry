"""WhatsApp NLP Intent router and Agent integration."""
import json
import logging
from typing import Optional, Literal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from langchain_core.prompts import PromptTemplate
from src.infrastructure.llm.client import get_fast_llm
from src.domains.identity.models.user import User
from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest, InternalStudyToolGenerateRequest
from src.domains.platform.services.ai_gateway import run_text_query, run_study_tool

logger = logging.getLogger(__name__)

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
    """Format structured backend results into nice WhatsApp markdown."""
    text = ""
    
    if intent == "query":
        text += result.get("answer", "")
    elif intent == "quiz":
        text += "*Generated Quiz*\n\n"
        try:
            quiz_data = json.loads(result.get("tool_data", "{}"))
            for i, q in enumerate(quiz_data.get("questions", [])):
                text += f"*{i+1}. {q.get('q')}*\n"
                for j, opt in enumerate(q.get("options", [])):
                    letter = chr(65 + j)
                    text += f"   {letter}. {opt}\n"
                text += "\n"
        except:
            text += "Failed to parse quiz format"
    elif intent == "flashcards":
        text += "*Flashcards*\n\n"
        try:
            fc_data = json.loads(result.get("tool_data", "{}"))
            for i, card in enumerate(fc_data.get("cards", [])):
                text += f"• *Q:* {card.get('front')}\n  *A:* {card.get('back')}\n\n"
        except:
            text += "Failed to parse flashcards"
    elif intent in ["mindmap", "flowchart", "concept_map"]:
        text += f"*{intent.title().replace('_', ' ')} Generated!*\n\nPlease visit the VidyaOS dashboard web interface to view this rich SVG visual diagram. Generating visuals within WhatsApp directly is currently unsupported rendering-wise, but your diagram is saved in your library!"
    else:
        text += str(result)
        
    # Append Citations if present
    citations = result.get("citations", [])
    if citations:
        text += "\n\n_Sources:_\n"
        for c in citations:
            text += f"- {c.get('source', 'Document')}\n"
            
    return text.strip()


async def handle_whatsapp_intent(user: User, body: str, media_url: Optional[str], db: Session) -> str:
    """Classifies WhatsApp message and triggers correct orchestrator workflow."""
    
    # 1. Check for Media Upload Phase 6 (Data Upload via WhatsApp)
    if media_url:
        import httpx
        from tempfile import NamedTemporaryFile
        from config import settings
        from src.infrastructure.vector_store.ingestion import ingest_document
        import os
        import uuid
        
        try:
            # Twilio media urls require Basic Auth
            auth = (settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
            async with httpx.AsyncClient() as client:
                res = await client.get(media_url, auth=auth, follow_redirects=True)
                res.raise_for_status()
                
            # Determine extension from content-type or fallback
            content_type = res.headers.get("Content-Type", "")
            ext = ".pdf" if "pdf" in content_type else (".jpg" if "jpeg" in content_type else ".txt")
            
            with NamedTemporaryFile(delete=False, suffix=ext) as tmp:
                tmp.write(res.content)
                tmp_path = tmp.name
                
            doc_id = str(uuid.uuid4())
            try:
                # Add to RAG Knowledge Base
                ingest_document(
                    file_path=tmp_path,
                    document_id=doc_id,
                    tenant_id=str(user.tenant_id),
                    subject_id=None,
                    notebook_id=None
                )
            finally:
                os.unlink(tmp_path)
                
            return "Received your document! It has been securely added to your RAG knowledge base. What would you like to explore?"
        except Exception as e:
            logger.error(f"Media ingestion failed: {e}")
            return f"Failed to ingest document. Error: {str(e)}"
        
    if not body:
        return "Please send a message, question, or study material to get started!"

    # 2. Extract Intent using Fast LLM Phase 3 (LLM Interpretation)
    llm = get_fast_llm()
    structured_llm = llm.with_structured_output(WhatsAppIntent)
    
    prompt = PromptTemplate.from_template(INTENT_TEMPLATE)
    chain = prompt | structured_llm
    
    try:
        intent_result: WhatsAppIntent = chain.invoke({"message": body})
        logger.info(f"[WhatsApp] Detected intent: {intent_result.action} for topic: {intent_result.extracted_topic}")
    except Exception as e:
        logger.error(f"Intent parsing failed: {e}")
        # Fallback to standard query
        intent_result = WhatsAppIntent(action="query", extracted_topic=body)

    # 3. Route to Orchesterator (Phase 4: Agentic Tool Orchestration & Phase 7 RAG)
    if intent_result.action == "query":
        # Phase 5: Q&A Assistant
        req = InternalAIQueryRequest(
            tenant_id=str(user.tenant_id),
            user_id=str(user.id),
            query=intent_result.extracted_topic,
            mode="qa",
            notebook_id=None
        )
        res = await run_text_query(req)
        return format_whatsapp_response(res, intent_result.action)
        
    elif intent_result.action in ["quiz", "flashcards", "mindmap", "flowchart", "concept_map"]:
        # Phase 5: Specific Application Study Tools
        req = InternalStudyToolGenerateRequest(
            tenant_id=str(user.tenant_id),
            user_id=str(user.id),
            query=intent_result.extracted_topic,
            mode=intent_result.action,
            notebook_id=None
        )
        res = await run_study_tool(req)
        return format_whatsapp_response(res, intent_result.action)

    return "I wasn't sure how to handle that request. Please try asking a question or requesting a quiz/flashcards!"
