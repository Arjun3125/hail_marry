"""AI query route — full RAG pipeline with Ollama + citation enforcement."""
import uuid
import time
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from pydantic import BaseModel
from datetime import date
import httpx

from database import get_db
from auth.dependencies import get_current_user
from models.user import User
from models.ai_query import AIQuery
from models.tenant import Tenant
from ai.retrieval import retrieve_context, build_context_string, extract_citations, sanitize_ai_output, enforce_citations
from ai.cache import get_cached_response, cache_response
from services.webhooks import emit_webhook_event

router = APIRouter(prefix="/api/ai", tags=["AI"])

OLLAMA_URL = "http://localhost:11434"


class AIQueryRequest(BaseModel):
    query: str
    mode: str = "qa"  # qa, study_guide, quiz, concept_map, weak_topic, flowchart, mindmap, flashcards
    subject_id: str | None = None


# ─── Prompt Templates ─────────────────────────────────────────
PROMPTS = {
    "qa": """You are an academic assistant for students.
Answer the following question using ONLY the provided context.
Cite sources using [Document_Page] format exactly as shown in the context.
If the answer is not in the context, say: "Not found in provided materials."
Do NOT speculate or make up information.

Question: {query}

Context from study materials:
{context}

Answer with citations:""",

    "study_guide": """You are an academic study guide generator.
Create a structured study guide using ONLY the provided context.
Use clear headings, bullet points, and key takeaways.
Cite sources using the [Document_Page] markers from the context.

Topic: {query}

Context from study materials:
{context}

Study Guide:""",

    "quiz": """You are an academic quiz generator.
Generate exactly 5 multiple-choice questions using ONLY the provided context.
Each question must have 4 options (A, B, C, D) with one correct answer.
Cite the source for each question.
Format as JSON array.

Topic: {query}

Context from study materials:
{context}

Generate quiz as JSON:
[{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "correct": "B", "citation": "[source_page]"}}]""",

    "concept_map": """You are an academic concept mapper.
Create a concept map from the provided context about the given topic.
Output as JSON with nodes and edges.
Each node has an id and label. Each edge has from, to, and label.

Topic: {query}

Context from study materials:
{context}

Output JSON:
{{"nodes": [{{"id": "1", "label": "..."}}, ...], "edges": [{{"from": "1", "to": "2", "label": "..."}}, ...]}}""",

    "weak_topic": """You are an academic performance analyst.
The student is weak in the following area based on their exam performance.
Using the provided study materials, create a TARGETED remediation plan:
1. Key concepts they likely missed
2. A brief explanation of each
3. Practice exercises

Weak Area: {query}

Context from study materials:
{context}

Remediation Plan:""",

    "flowchart": """You are an academic flowchart generator.
Create a flowchart in Mermaid.js syntax for the given topic using the provided context.
Use the flowchart TD (top-down) format. Keep node labels short (max 6 words).
Use proper Mermaid syntax with --> for connections and [] for rectangles, {{}} for decisions.
Do NOT wrap in ```mermaid code fences. Output ONLY the raw Mermaid code.

Topic: {query}

Context from study materials:
{context}

Mermaid flowchart:""",

    "mindmap": """You are an academic mind map generator.
Create a hierarchical mind map as JSON for the given topic using the provided context.
The root node is the main topic. Each node has a "label" and optional "children" array.
Keep labels concise (max 5 words). Aim for 3-4 levels of depth and 3-5 children per node.

Topic: {query}

Context from study materials:
{context}

Output JSON:
{{"label": "Topic", "children": [{{"label": "Subtopic 1", "children": [{{"label": "Detail"}}]}}, {{"label": "Subtopic 2"}}]}}""",

    "flashcards": """You are an academic flashcard generator.
Create exactly 8 flashcards as a JSON array for the given topic using the provided context.
Each flashcard has a "front" (question or term) and "back" (answer or definition).
Keep fronts short and backs concise but informative.

Topic: {query}

Context from study materials:
{context}

Generate flashcards as JSON:
[{{"front": "What is...?", "back": "It is..."}}]""",
}

@router.post("/query")
async def ai_query(
    request: AIQueryRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Process an AI query through the full RAG pipeline."""
    trace_id = str(uuid.uuid4())[:8]
    start_time = time.time()

    # ── Rate limiting ──────────────────────────────────
    tenant = db.query(Tenant).filter(Tenant.id == current_user.tenant_id).first()
    daily_limit = tenant.ai_daily_limit if tenant else 50

    today_count = db.query(AIQuery).filter(
        AIQuery.tenant_id == current_user.tenant_id,
        AIQuery.user_id == current_user.id,
        func.date(AIQuery.created_at) == date.today(),
    ).count()

    if today_count >= daily_limit:
        raise HTTPException(
            status_code=429,
            detail=f"Daily AI query limit reached ({daily_limit}). Try again tomorrow.",
        )

    # ── Cache Check ────────────────────────────────────
    cached = get_cached_response(
        tenant_id=str(current_user.tenant_id),
        query=request.query,
        mode=request.mode,
        subject_id=request.subject_id or "",
    )
    if cached:
        cached["cached"] = True
        return cached

    # ── RAG Retrieval ──────────────────────────────────
    context_chunks = await retrieve_context(
        query=request.query,
        tenant_id=str(current_user.tenant_id),
        top_k=8,
        subject_id=request.subject_id,
    )

    has_context = len(context_chunks) > 0
    if not has_context:
        raise HTTPException(
            status_code=422,
            detail="No grounded context found. Upload study materials before querying AI.",
        )

    context_string = build_context_string(context_chunks) if has_context else ""
    citations = extract_citations(context_chunks) if has_context else []

    # ── Build Prompt ───────────────────────────────────
    mode = request.mode if request.mode in PROMPTS else "qa"
    prompt = PROMPTS[mode].format(query=request.query, context=context_string)

    # ── LLM Inference ──────────────────────────────────
    answer = ""
    token_usage = 0
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{OLLAMA_URL}/api/generate",
                json={
                    "model": "llama3.2",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,
                        "num_predict": 800,
                    },
                },
            )
            if response.status_code == 200:
                data = response.json()
                answer = data.get("response", "No response generated.")
                token_usage = data.get("eval_count", 0)
            else:
                answer = "AI service temporarily unavailable."
    except httpx.ConnectError:
        answer = "Cannot connect to AI service (Ollama). Make sure Ollama is running on port 11434."
    except httpx.TimeoutException:
        answer = "AI request timed out. Try a simpler question."
    except Exception as e:
        answer = f"AI error: {str(e)}"

    # ── Output Sanitization ────────────────────────────
    answer = sanitize_ai_output(answer)

    # ── Citation Enforcement ───────────────────────────
    available_citation_strs = [c.get("citation", "") for c in context_chunks] if has_context else []
    citation_result = enforce_citations(answer, mode, available_citation_strs)
    answer = citation_result["response"]

    elapsed_ms = int((time.time() - start_time) * 1000)

    # ── Log Query ──────────────────────────────────────
    ai_log = AIQuery(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        query_text=request.query,
        mode=mode,
        response_text=answer,
        token_usage=token_usage,
        response_time_ms=elapsed_ms,
        trace_id=trace_id,
        citation_count=citation_result["citation_count"],
    )
    db.add(ai_log)
    db.commit()

    result = {
        "answer": answer,
        "citations": citations,
        "trace_id": trace_id,
        "token_usage": token_usage,
        "response_time_ms": elapsed_ms,
        "mode": mode,
        "has_context": has_context,
        "citation_valid": citation_result["citation_valid"],
    }

    try:
        await emit_webhook_event(
            db=db,
            tenant_id=current_user.tenant_id,
            event_type="ai.query.completed",
            data={
                "query_id": str(ai_log.id),
                "user_id": str(current_user.id),
                "mode": mode,
                "trace_id": trace_id,
                "token_usage": token_usage,
                "response_time_ms": elapsed_ms,
            },
        )
    except Exception:
        # AI response should not fail due to webhook delivery issues.
        pass

    # ── Cache Store ───────────────────────────────────
    cache_response(
        tenant_id=str(current_user.tenant_id),
        query=request.query,
        mode=mode,
        response=result,
        subject_id=request.subject_id or "",
    )

    return result

