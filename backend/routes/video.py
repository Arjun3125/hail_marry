"""Video Overview — generates narrated slide deck from study materials."""
import httpx
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from auth.dependencies import get_current_user
from models.user import User
from database import get_db
from ai.retrieval import retrieve_context, build_context_string

router = APIRouter(prefix="/api/ai", tags=["AI Video"])

OLLAMA_URL = "http://localhost:11434"


class VideoOverviewRequest(BaseModel):
    topic: str
    num_slides: int = 6
    language: str = "english"


VIDEO_PROMPT = """You are creating a narrated slide presentation about the following topic using the provided study materials.
Generate exactly {num_slides} slides. Each slide should have:
- A short, clear title (5-8 words)
- 3-4 concise bullet points with key facts from the context
- A narration script (2-3 sentences) that explains the slide content naturally, as if presenting to a student

Topic: {topic}

Context from study materials:
{context}

Output ONLY valid JSON in this format:
{{"slides": [{{"title": "...", "bullets": ["...", "..."], "narration": "..."}}], "presentation_title": "...", "total_slides": {num_slides}}}"""


@router.post("/video-overview")
async def video_overview(
    request: VideoOverviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Generate a narrated slide deck from study materials."""
    context_chunks = await retrieve_context(
        query=request.topic,
        tenant_id=str(current_user.tenant_id),
        top_k=10,
    )
    if not context_chunks:
        raise HTTPException(status_code=422, detail="No study materials found. Upload content first.")

    context_string = build_context_string(context_chunks)
    num = max(3, min(request.num_slides, 12))

    prompt = VIDEO_PROMPT.format(
        topic=request.topic,
        context=context_string,
        num_slides=num,
    )

    if request.language.lower() != "english":
        prompt = f"Respond entirely in {request.language}.\n\n" + prompt

    try:
        async with httpx.AsyncClient(timeout=90.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.4, "num_predict": 2000},
                },
            )
            if response.status_code == 200:
                raw = response.json().get("response", "")
                import json
                try:
                    start = raw.find("{")
                    end = raw.rfind("}") + 1
                    if start >= 0 and end > start:
                        data = json.loads(raw[start:end])
                        return data
                except json.JSONDecodeError:
                    pass
                # Fallback: single slide from raw text
                return {
                    "slides": [{"title": request.topic, "bullets": [raw[:200]], "narration": raw[:300]}],
                    "presentation_title": request.topic,
                    "total_slides": 1,
                }
            else:
                raise HTTPException(status_code=502, detail="AI service error")
    except httpx.ConnectError:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama")
    except httpx.TimeoutException:
        raise HTTPException(status_code=504, detail="AI request timed out")
