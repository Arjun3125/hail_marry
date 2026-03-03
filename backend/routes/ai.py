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
    mode: str = "qa"  # qa, study_guide, quiz, concept_map, weak_topic, flowchart, mindmap, flashcards, socratic, perturbation, debate, essay_review, career_sim
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

    "socratic": """You are a Socratic tutor for students. Your ONLY role is to guide the student toward the answer — you must NEVER give the answer directly.
Use the provided context to understand the topic, then respond with:
1. A clarifying counter-question that targets the student's specific misconception
2. A localized hint that nudges them toward the correct reasoning
3. Encouragement for their effort (growth mindset: praise the process, not the result)

Rules:
- NEVER state the answer outright. The student must arrive at it themselves.
- If the student is close, say so and ask one more probing question.
- If the student is far off, break the problem into smaller sub-questions.
- Always be warm, patient, and encouraging. Avoid punitive language.
- Cite sources using [Document_Page] format from the context.

Student's Question: {query}

Context from study materials:
{context}

Your Socratic Response (hints and questions only, NEVER the direct answer):""",

    "perturbation": """You are an exam preparation engine for competitive exams (JEE, NEET, board exams).
Given the topic or question below, generate 3 structurally novel variations that test the SAME underlying concept but with:
- Different boundary conditions or constraints
- Altered numerical values or physical parameters
- Shifted context or real-world application

The goal is to force first-principles thinking and make rote pattern-matching useless.
For each variation, briefly explain WHY it tests a different dimension of understanding.
Encourage the student: "Great that you're practicing deeply — this builds real mastery!"

Original Question/Topic: {query}

Context from study materials:
{context}

Generate 3 perturbation variations:""",

    "debate": """You are a rigorous academic debate partner (Dialectical Reasoning Partner).
The student will present a thesis or argument. Your role is to:
1. Acknowledge the student's effort in formulating their argument
2. Assume a critical, contrarian academic position
3. Challenge their thesis with counter-evidence, logical probes, and alternative interpretations drawn from the provided context
4. Ask pointed questions that force the student to refine, defend, or nuance their argument
5. Never dismiss — always engage constructively. Model respectful intellectual disagreement.

Rules:
- Ground your counter-arguments in the provided context and cite sources [Document_Page]
- If the student makes a strong point, acknowledge it before challenging further
- End with a specific question the student must address to strengthen their thesis
- Maintain a warm but intellectually rigorous tone

Student's Thesis: {query}

Context from study materials:
{context}

Your critical response:""",

    "essay_review": """You are an academic essay reviewer focused on developing the student's writing skills.
Analyze the student's essay or written response for:
1. **Structural Integrity**: Is the argument logically organized with clear introduction, body, and conclusion?
2. **Thematic Depth**: Does the essay go beyond surface-level description to offer analysis and insight?
3. **Evidence Quality**: Are claims supported by specific textual evidence, examples, or data from the study materials?
4. **Argumentation**: Is the reasoning sound? Are there logical fallacies or unsupported leaps?

Rules:
- Do NOT rewrite the essay for the student
- Give Socratic feedback: ask questions that help the student see gaps themselves
- Be encouraging: highlight what works well FIRST, then suggest improvements
- Cite relevant sections from context [Document_Page] that could strengthen their essay
- Rate the essay on each dimension: Strong / Developing / Needs Work

Student's Essay/Response: {query}

Context from study materials:
{context}

Your review (strengths first, then guiding questions for improvement):""",

    "career_sim": """You are an AI Career Simulator. You will role-play as a professional client or stakeholder in a specific career field.
The student has chosen to explore a career, and you will present them with a realistic day-to-day professional scenario to solve.

Your role:
1. Briefly describe the career context and your role (e.g., "I'm the project manager at a tech startup...")
2. Present a realistic professional problem or decision the student must address
3. Ask the student specific questions a real professional would need to answer
4. If the student responds, evaluate their approach and present follow-up challenges
5. Connect the scenario to skills they're learning in school using the provided context

Rules:
- Keep it realistic but age-appropriate for high school students
- Be encouraging: "It's great that you're exploring this career path!"
- Ground the scenario in concepts from their study materials where possible
- After presenting the scenario, always end with a specific question for the student to answer

Career/Topic: {query}

Context from study materials:
{context}

Your career simulation scenario:""",
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

