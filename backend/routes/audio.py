"""Audio Overview — generates podcast-style dialogue between 2 AI hosts."""
import uuid
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from models.user import User
from database import get_db
from ai.retrieval import retrieve_context, build_context_string

router = APIRouter(prefix="/api/ai", tags=["AI Audio"])

OLLAMA_URL = "http://localhost:11434"


class AudioOverviewRequest(BaseModel):
    topic: str
    format: str = "deep_dive"  # deep_dive, brief, debate
    language: str = "english"


AUDIO_PROMPTS = {
    "deep_dive": """You are a scriptwriter for an educational podcast with two hosts: Anika and Ravi.
Generate a lively, engaging conversation between them about the following topic, using the provided context.
The conversation should:
- Start with a brief intro by Anika welcoming listeners
- Have natural back-and-forth dialogue (at least 8 exchanges)
- Anika explains concepts clearly, Ravi asks smart follow-up questions and adds analogies
- Include specific facts and examples from the context
- End with a summary and key takeaway

Topic: {topic}

Context from study materials:
{context}

Output ONLY valid JSON in this format:
{{"dialogue": [{{"speaker": "Anika", "text": "..."}}, {{"speaker": "Ravi", "text": "..."}}], "title": "...", "duration_estimate": "X minutes"}}""",

    "brief": """You are a scriptwriter. Create a brief 3-minute educational audio summary by a single presenter named Anika about the following topic using the context.
Keep it concise but informative — cover 3-4 key points with examples.

Topic: {topic}

Context from study materials:
{context}

Output ONLY valid JSON in this format:
{{"dialogue": [{{"speaker": "Anika", "text": "..."}}], "title": "...", "duration_estimate": "X minutes"}}""",

    "debate": """You are a scriptwriter for an educational debate podcast. Two hosts — Anika (argues FOR) and Ravi (argues AGAINST) — debate the topic, backed by evidence from the context.
Generate at least 6 exchanges. Each host should use specific facts. End with both hosts finding common ground.

Topic: {topic}

Context from study materials:
{context}

Output ONLY valid JSON in this format:
{{"dialogue": [{{"speaker": "Anika", "text": "..."}}, {{"speaker": "Ravi", "text": "..."}}], "title": "...", "duration_estimate": "X minutes"}}""",
}


@router.post("/audio-overview")
async def audio_overview(
    request: AudioOverviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a podcast-style dialogue about a topic from study materials."""
    # Retrieve relevant context
    context_chunks = await retrieve_context(
        query=request.topic,
        tenant_id=str(current_user.tenant_id),
        top_k=10,
    )
    if not context_chunks:
        raise HTTPException(status_code=422, detail="No study materials found. Upload content first.")

    context_string = build_context_string(context_chunks)

    fmt = request.format if request.format in AUDIO_PROMPTS else "deep_dive"
    prompt = AUDIO_PROMPTS[fmt].format(topic=request.topic, context=context_string)

    if request.language.lower() != "english":
        prompt = f"Respond entirely in {request.language}.\n\n" + prompt

    # LLM call
    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.7, "num_predict": 2000},
                },
            )
            if response.status_code == 200:
                raw = response.json().get("response", "")
                # Try to parse JSON from response
                import json
                try:
                    # Find JSON in response
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(raw[start:end])
                        return data
                except json.JSONDecodeError:
                    pass
                # Fallback: create dialogue from raw text
                return {
                    "dialogue": [{"speaker": "Anika", "text": raw}],
                    "title": f"Overview: {request.topic}",
                    "duration_estimate": "3 minutes",
                }
            else:
                raise HTTPException(status_code=502, detail="AI service error")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI request timed out")
