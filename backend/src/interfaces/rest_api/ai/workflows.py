"""Shared AI workflows used by the monolith and background worker."""
from __future__ import annotations

import json
import time
from pydantic import BaseModel, Field
from typing import List, Optional

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct: str
    citation: str

class QuizOutput(BaseModel):
    questions: List[QuizQuestion]

class ConceptMapNode(BaseModel):
    id: str
    label: str

class ConceptMapEdge(BaseModel):
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    label: str
    citation: str

class ConceptMapOutput(BaseModel):
    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]

class MindmapNode(BaseModel):
    label: str
    citation: Optional[str] = None
    children: Optional[List['MindmapNode']] = None

class Flashcard(BaseModel):
    front: str
    back: str
    citation: str

class FlashcardOutput(BaseModel):
    cards: List[Flashcard]

class FlowchartStep(BaseModel):
    id: str
    label: str
    detail: str
    citation: str

class FlowchartOutput(BaseModel):
    mermaid: str
    steps: List[FlowchartStep]

class AudioLine(BaseModel):
    speaker: str
    text: str

class AudioOutput(BaseModel):
    dialogue: List[AudioLine]
    title: str
    duration_estimate: str

class VideoSlide(BaseModel):
    title: str
    bullets: List[str]
    narration: str

class VideoOutput(BaseModel):
    slides: List[VideoSlide]
    presentation_title: str
    total_slides: int

# Mode to schema mapping
SCHEMA_MAP = {
    "quiz": QuizOutput,
    "concept_map": ConceptMapOutput,
    "mindmap": MindmapNode,
    "flashcards": FlashcardOutput,
    "flowchart": FlowchartOutput,
}


from fastapi import HTTPException
import httpx

from config import settings
from src.infrastructure.llm.providers import get_llm_provider
from src.infrastructure.vector_store.retrieval import (
    retrieve_context,
    build_context_string,
    build_retrieval_audit,
    extract_citations,
    sanitize_ai_output,
    enforce_citations,
)
from src.domains.platform.schemas.ai_runtime import (
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalVideoOverviewRequest,
)
from src.domains.platform.services.metrics_registry import observe_stage_latency
from src.domains.platform.services.traceability import TraceabilityError

LENGTH_TOKENS = {"brief": 250, "default": 800, "detailed": 1500}
LENGTH_INSTRUCTIONS = {
    "brief": "Keep your response concise and to the point, under 3 paragraphs.",
    "default": "",
    "detailed": "Provide a thorough, detailed explanation with examples and elaboration.",
}
EXPERTISE_INSTRUCTIONS = {
    "simple": "Explain as if talking to a young student (age 8-12). Use very simple language and everyday analogies.",
    "standard": "",
    "advanced": "Explain at an advanced academic level with precise terminology and technical depth.",
}

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
Each question must also include a "difficulty" field using only: "easy", "medium", or "hard".
Cite the source for each question using a required "citation" field.
Format as JSON array.

Topic: {query}

Context from study materials:
{context}

Generate quiz as JSON:
[{{"question": "...", "options": ["A. ...", "B. ...", "C. ...", "D. ..."], "correct": "B", "difficulty": "medium", "citation": "[source_page]"}}]""",
    "concept_map": """You are an academic concept mapper.
Create a concept map from the provided context about the given topic.
Output as JSON with nodes and edges.
Each node has an id and label. Each edge has from, to, label, and citation.
Every edge citation must use the exact [Document_Page] marker from context.

Topic: {query}

Context from study materials:
{context}

Output JSON:
{{"nodes": [{{"id": "1", "label": "..."}}, ...], "edges": [{{"from": "1", "to": "2", "label": "...", "citation": "[source_page]"}} , ...]}}""",
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
Create a grounded process flow from the provided context about the given topic.
Return JSON with:
- "mermaid": Mermaid.js syntax using flowchart TD format
- "steps": an ordered array of grounded steps
Every step must include:
- id
- label
- detail
- citation
Rules:
- Use ONLY the provided context
- Do not invent steps not present in the context
- Preserve source order when the context describes a process
- Keep node labels short (max 6 words)
- Use proper Mermaid syntax with --> for connections and [] for rectangles, {{}} for decisions
- Every step citation must use the exact [Document_Page] marker from context
- If the process is unclear, return a simple grounded linear summary with 3-5 cited steps rather than forcing a complex chart

Topic: {query}

Context from study materials:
{context}

Output JSON:
{{"mermaid": "flowchart TD\\nA[Step 1] --> B[Step 2]", "steps": [{{"id": "A", "label": "Step 1", "detail": "What happens in this step.", "citation": "[source_page]"}}]}}""",
    "mindmap": """You are an academic mind map generator.
Create a hierarchical mind map as JSON for the given topic using the provided context.
The root node is the main topic. Each node has a "label", optional "citation", and optional "children" array.
Rules:
- Use ONLY the provided context
- The root node may omit "citation"
- Every major non-root node should include a "citation" field using the exact [Document_Page] marker from context
- Keep labels concise (max 5 words). Aim for 3-4 levels of depth and 3-5 children per node.

Topic: {query}

Context from study materials:
{context}

Output JSON:
{{"label": "Topic", "children": [{{"label": "Subtopic 1", "citation": "[source_page]", "children": [{{"label": "Detail", "citation": "[source_page]"}}]}}, {{"label": "Subtopic 2", "citation": "[source_page]"}}]}}""",
    "flashcards": """You are an academic flashcard generator.
Create exactly 8 flashcards as a JSON array for the given topic using the provided context.
Each flashcard has a "front" (question or term) and "back" (answer or definition).
Each flashcard must also include a "citation" field using the exact [Document_Page] marker from context.
Keep fronts short and backs concise but informative.

Topic: {query}

Context from study materials:
{context}

Generate flashcards as JSON:
[{{"front": "What is...?", "back": "It is...", "citation": "[source_page]"}}]""",
    "socratic": """You are a Socratic tutor for students. Your ONLY role is to guide the student toward the answer - you must NEVER give the answer directly.
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
Encourage the student: "Great that you're practicing deeply - this builds real mastery!"

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
5. Never dismiss - always engage constructively. Model respectful intellectual disagreement.

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
1. Structural Integrity: Is the argument logically organized with clear introduction, body, and conclusion?
2. Thematic Depth: Does the essay go beyond surface-level description to offer analysis and insight?
3. Evidence Quality: Are claims supported by specific textual evidence, examples, or data from the study materials?
4. Argumentation: Is the reasoning sound? Are there logical fallacies or unsupported leaps?

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
}

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
Keep it concise but informative - cover 3-4 key points with examples.

Topic: {topic}

Context from study materials:
{context}

Output ONLY valid JSON in this format:
{{"dialogue": [{{"speaker": "Anika", "text": "..."}}], "title": "...", "duration_estimate": "X minutes"}}""",
    "debate": """You are a scriptwriter for an educational debate podcast. Two hosts - Anika (argues FOR) and Ravi (argues AGAINST) - debate the topic, backed by evidence from the context.
Generate at least 6 exchanges. Each host should use specific facts. End with both hosts finding common ground.

Topic: {topic}

Context from study materials:
{context}

Output ONLY valid JSON in this format:
{{"dialogue": [{{"speaker": "Anika", "text": "..."}}, {{"speaker": "Ravi", "text": "..."}}], "title": "...", "duration_estimate": "X minutes"}}""",
}

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


def _estimate_tokens(text: str) -> int:
    normalized = text.strip()
    if not normalized:
        return 0
    return max(1, len(normalized) // 4)


def _truncate_to_token_budget(text: str, max_tokens: int | None) -> str:
    if not max_tokens or max_tokens <= 0:
        return text
    if _estimate_tokens(text) <= max_tokens:
        return text
    max_chars = max_tokens * 4
    if max_chars <= 16:
        return text[: max_chars].strip()
    return text[: max_chars - 16].rstrip() + "\n...[truncated]"


def _apply_language_and_style(prompt: str, language: str, response_length: str, expertise_level: str) -> str:
    style_parts = []
    lang = language.strip().lower()
    if lang and lang != "english":
        style_parts.append(f"Respond entirely in {lang}.")
    length_instr = LENGTH_INSTRUCTIONS.get(response_length, "")
    if length_instr:
        style_parts.append(length_instr)
    expertise_instr = EXPERTISE_INSTRUCTIONS.get(expertise_level, "")
    if expertise_instr:
        style_parts.append(expertise_instr)
    if style_parts:
        prompt = "\n".join(style_parts) + "\n\n" + prompt
    return prompt


def _apply_personalization_context(
    prompt: str,
    learner_profile: dict | None,
    learner_topic_context: dict | None,
    *,
    mode: str = "qa",
) -> str:
    profile = learner_profile or {}
    topic_context = learner_topic_context or {}
    context_lines: list[str] = []

    expertise = str(profile.get("inferred_expertise_level") or "").strip()
    preferred_length = str(profile.get("preferred_response_length") or "").strip()
    preferred_language = str(profile.get("preferred_language") or "").strip()
    primary_subjects = list(profile.get("primary_subjects") or [])
    if expertise:
        context_lines.append(f"- learner expertise: {expertise}")
    if preferred_length:
        context_lines.append(f"- preferred response length: {preferred_length}")
    if preferred_language:
        context_lines.append(f"- preferred language: {preferred_language}")
    if primary_subjects:
        context_lines.append(f"- primary subjects: {', '.join(primary_subjects[:3])}")

    topic = str(topic_context.get("topic") or "").strip()
    mastery_score = topic_context.get("mastery_score")
    confidence_score = topic_context.get("confidence_score")
    focus_concepts = list(topic_context.get("focus_concepts") or [])
    repeated_confusion = topic_context.get("repeated_confusion_count")
    if topic:
        context_lines.append(f"- current topic: {topic}")
    if mastery_score is not None:
        context_lines.append(f"- current mastery score: {mastery_score}")
    if confidence_score is not None:
        context_lines.append(f"- current mastery confidence: {confidence_score}")
    if focus_concepts:
        context_lines.append(f"- focus concepts: {', '.join(focus_concepts[:4])}")
    if repeated_confusion:
        context_lines.append(f"- repeated confusion count on topic: {repeated_confusion}")

    adaptive_guidance_lines: list[str] = []
    simple_learner = expertise == "simple"
    advanced_learner = expertise == "advanced"
    lower_mastery = isinstance(mastery_score, (int, float)) and mastery_score < 60
    higher_mastery = isinstance(mastery_score, (int, float)) and mastery_score >= 80
    repeated_confusion_flag = bool(repeated_confusion and repeated_confusion >= 2)

    if mode == "study_guide":
        if simple_learner or lower_mastery or repeated_confusion_flag:
            adaptive_guidance_lines.extend(
                [
                    "- organize the study guide as basics first, then worked understanding, then quick review",
                    "- define key terms before deeper explanation",
                    "- keep bullet points short and scaffold the explanation step by step",
                ]
            )
        elif advanced_learner or higher_mastery:
            adaptive_guidance_lines.extend(
                [
                    "- start with a concise summary, then move into deeper reasoning and applications",
                    "- emphasize comparisons, implications, and higher-order connections when supported by context",
                ]
            )

    if not context_lines:
        return prompt

    personalization_block = (
        "Personalization context:\n"
        + "\n".join(context_lines)
        + (
            ("\nAdaptive guidance:\n" + "\n".join(adaptive_guidance_lines))
            if adaptive_guidance_lines
            else ""
        )
        + "\nUse this to adapt explanation depth, pacing, and scaffolding, but do not override explicit user instructions or invent facts outside the provided context."
    )
    return personalization_block + "\n\n" + prompt


async def execute_text_query(request: InternalAIQueryRequest) -> dict:
    retrieval_started = time.perf_counter()
    try:
        context_chunks = await retrieve_context(
            query=request.query,
            tenant_id=request.tenant_id,
            top_k=8,
            subject_id=request.subject_id,
            notebook_id=request.notebook_id,
        )
    except Exception as exc:
        observe_stage_latency("ai_query", "retrieval", (time.perf_counter() - retrieval_started) * 1000, "error")
        raise TraceabilityError("rag.retrieval", detail="RAG retrieval failed while loading grounded context.", cause=exc) from exc
    observe_stage_latency("ai_query", "retrieval", (time.perf_counter() - retrieval_started) * 1000, "success")
    if not context_chunks:
        raise TraceabilityError(
            "rag.retrieval",
            detail="No sufficiently relevant grounded context found. Upload matching study materials before querying AI.",
            status_code=422,
        )

    context_string = build_context_string(context_chunks)
    citations = extract_citations(context_chunks)
    retrieval_audit = build_retrieval_audit(context_chunks) if request.audit_retrieval else None
    mode = request.mode if request.mode in PROMPTS else "qa"
    prompt = PROMPTS[mode].format(query=request.query, context=context_string)
    prompt = _apply_personalization_context(
        prompt,
        request.learner_profile,
        request.learner_topic_context,
        mode=mode,
    )
    prompt = _apply_language_and_style(
        prompt,
        request.language,
        request.response_length,
        request.expertise_level,
    )
    prompt = _truncate_to_token_budget(prompt, request.max_prompt_tokens)

    llm = get_llm_provider()
    model_name = request.model_override or settings.llm.model
    max_completion_tokens = request.max_completion_tokens or LENGTH_TOKENS.get(
        request.response_length,
        settings.llm.max_new_tokens,
    )
    generation_started = time.perf_counter()
    try:
        if mode in SCHEMA_MAP:
            data = await llm.generate_structured(
                prompt,
                schema=SCHEMA_MAP[mode],
                model=model_name,
                temperature=settings.llm.temperature,
                max_tokens=max_completion_tokens,
            )
            data["response"] = json.dumps(data["response"]) # Keep downstream pipeline intact
        else:
            data = await llm.generate(
                prompt,
                model=model_name,
                temperature=settings.llm.temperature,
                num_predict=max_completion_tokens,
                max_tokens=max_completion_tokens,
            )
    except httpx.ConnectError as exc:
        observe_stage_latency("ai_query", "generation", (time.perf_counter() - generation_started) * 1000, "connect_error")
        raise TraceabilityError("llm.generation", detail="Cannot connect to AI runtime (Ollama).", status_code=503, cause=exc) from exc
    except httpx.TimeoutException as exc:
        observe_stage_latency("ai_query", "generation", (time.perf_counter() - generation_started) * 1000, "timeout")
        raise TraceabilityError("llm.generation", detail="AI request timed out. Try a simpler question.", status_code=504, cause=exc) from exc
    except httpx.HTTPStatusError as exc:
        observe_stage_latency("ai_query", "generation", (time.perf_counter() - generation_started) * 1000, "http_error")
        raise TraceabilityError("llm.generation", detail="AI runtime temporarily unavailable.", status_code=502, cause=exc) from exc
    observe_stage_latency("ai_query", "generation", (time.perf_counter() - generation_started) * 1000, "success")

    answer = sanitize_ai_output(data.get("response", "No response generated."))
    citation_result = enforce_citations(
        answer,
        mode,
        [chunk.get("citation", "") for chunk in context_chunks],
    )
    return {
        "answer": citation_result["response"],
        "citations": citations,
        "token_usage": data.get("token_usage", 0),
        "mode": mode,
        "has_context": True,
        "citation_valid": citation_result["citation_valid"],
        "citation_count": citation_result["citation_count"],
        "retrieval_audit": retrieval_audit,
        "model_used": model_name,
    }


async def execute_audio_overview(request: InternalAudioOverviewRequest) -> dict:
    context_chunks = await retrieve_context(
        query=request.topic,
        tenant_id=request.tenant_id,
        top_k=10,
        notebook_id=str(request.notebook_id) if request.notebook_id else None,
    )
    if not context_chunks:
        raise TraceabilityError("rag.retrieval", detail="No study materials found. Upload content first.", status_code=422)

    context_string = build_context_string(context_chunks)
    fmt = request.format if request.format in AUDIO_PROMPTS else "deep_dive"
    prompt = AUDIO_PROMPTS[fmt].format(topic=request.topic, context=context_string)
    if request.language.lower() != "english":
        prompt = f"Respond entirely in {request.language}.\n\n{prompt}"
    prompt = _truncate_to_token_budget(prompt, request.max_prompt_tokens)

    llm = get_llm_provider()
    model_name = request.model_override or settings.llm.model
    try:
        data = await llm.generate_structured(
            prompt,
            schema=AudioOutput,
            model=model_name,
            temperature=0.7,
            max_tokens=request.max_completion_tokens or settings.llm.max_new_tokens,
        )
    except httpx.ConnectError as exc:
        raise TraceabilityError("llm.generation", detail="Cannot connect to Ollama", status_code=503, cause=exc) from exc
    except httpx.TimeoutException as exc:
        raise TraceabilityError("llm.generation", detail="AI request timed out", status_code=504, cause=exc) from exc
    except httpx.HTTPStatusError as exc:
        raise TraceabilityError("llm.generation", detail="AI runtime error", status_code=502, cause=exc) from exc

    return data.get("response", {})


async def execute_video_overview(request: InternalVideoOverviewRequest) -> dict:
    context_chunks = await retrieve_context(
        query=request.topic,
        tenant_id=request.tenant_id,
        top_k=10,
    )
    if not context_chunks:
        raise TraceabilityError("rag.retrieval", detail="No study materials found. Upload content first.", status_code=422)

    context_string = build_context_string(context_chunks)
    num = max(3, min(request.num_slides, 12))
    prompt = VIDEO_PROMPT.format(topic=request.topic, context=context_string, num_slides=num)
    if request.language.lower() != "english":
        prompt = f"Respond entirely in {request.language}.\n\n{prompt}"
    prompt = _truncate_to_token_budget(prompt, request.max_prompt_tokens)

    llm = get_llm_provider()
    model_name = request.model_override or settings.llm.model
    try:
        data = await llm.generate_structured(
            prompt,
            schema=VideoOutput,
            model=model_name,
            temperature=0.4,
            max_tokens=request.max_completion_tokens or settings.llm.max_new_tokens,
        )
    except httpx.ConnectError as exc:
        raise TraceabilityError("llm.generation", detail="Cannot connect to Ollama", status_code=503, cause=exc) from exc
    except httpx.TimeoutException as exc:
        raise TraceabilityError("llm.generation", detail="AI request timed out", status_code=504, cause=exc) from exc
    except httpx.HTTPStatusError as exc:
        raise TraceabilityError("llm.generation", detail="AI runtime error", status_code=502, cause=exc) from exc

    return data.get("response", {})
