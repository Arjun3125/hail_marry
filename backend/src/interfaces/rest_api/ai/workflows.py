"""Shared AI workflows used by the monolith and background worker."""
from __future__ import annotations

import json
from pydantic import BaseModel, Field
from typing import List, Optional

class QuizQuestion(BaseModel):
    question: str
    options: List[str]
    correct: str
    citation: Optional[str] = None

class QuizOutput(BaseModel):
    questions: List[QuizQuestion]

class ConceptMapNode(BaseModel):
    id: str
    label: str

class ConceptMapEdge(BaseModel):
    from_node: str = Field(alias="from")
    to_node: str = Field(alias="to")
    label: str

class ConceptMapOutput(BaseModel):
    nodes: List[ConceptMapNode]
    edges: List[ConceptMapEdge]

class MindmapNode(BaseModel):
    label: str
    children: Optional[List['MindmapNode']] = None

class Flashcard(BaseModel):
    front: str
    back: str

class FlashcardOutput(BaseModel):
    cards: List[Flashcard]

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
}


from fastapi import HTTPException
import httpx

from config import settings
from src.infrastructure.llm.providers import get_llm_provider
from src.infrastructure.vector_store.retrieval import (
    retrieve_context,
    build_context_string,
    extract_citations,
    sanitize_ai_output,
    enforce_citations,
)
from src.domains.platform.schemas.ai_runtime import (
    InternalAIQueryRequest,
    InternalAudioOverviewRequest,
    InternalVideoOverviewRequest,
)

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


async def execute_text_query(request: InternalAIQueryRequest) -> dict:
    context_chunks = await retrieve_context(
        query=request.query,
        tenant_id=request.tenant_id,
        top_k=8,
        subject_id=request.subject_id,
        notebook_id=request.notebook_id,
    )
    if not context_chunks:
        raise HTTPException(
            status_code=422,
            detail="No grounded context found. Upload study materials before querying AI.",
        )

    context_string = build_context_string(context_chunks)
    citations = extract_citations(context_chunks)
    mode = request.mode if request.mode in PROMPTS else "qa"
    prompt = PROMPTS[mode].format(query=request.query, context=context_string)
    prompt = _apply_language_and_style(
        prompt,
        request.language,
        request.response_length,
        request.expertise_level,
    )

    llm = get_llm_provider()
    try:
        if mode in SCHEMA_MAP:
            data = await llm.generate_structured(
                prompt,
                schema=SCHEMA_MAP[mode],
                model=settings.llm.model,
                temperature=settings.llm.temperature,
            )
            data["response"] = json.dumps(data["response"]) # Keep downstream pipeline intact
        else:
            data = await llm.generate(
                prompt,
                model=settings.llm.model,
                temperature=settings.llm.temperature,
                num_predict=LENGTH_TOKENS.get(request.response_length, settings.llm.max_new_tokens),
            )
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to AI runtime (Ollama).") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out. Try a simpler question.") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI runtime temporarily unavailable.") from exc

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
    }


async def execute_audio_overview(request: InternalAudioOverviewRequest) -> dict:
    context_chunks = await retrieve_context(
        query=request.topic,
        tenant_id=request.tenant_id,
        top_k=10,
    )
    if not context_chunks:
        raise HTTPException(status_code=422, detail="No study materials found. Upload content first.")

    context_string = build_context_string(context_chunks)
    fmt = request.format if request.format in AUDIO_PROMPTS else "deep_dive"
    prompt = AUDIO_PROMPTS[fmt].format(topic=request.topic, context=context_string)
    if request.language.lower() != "english":
        prompt = f"Respond entirely in {request.language}.\n\n{prompt}"

    llm = get_llm_provider()
    try:
        data = await llm.generate_structured(prompt, schema=AudioOutput, model=settings.llm.model, temperature=0.7)
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI runtime error") from exc

    return data.get("response", {})


async def execute_video_overview(request: InternalVideoOverviewRequest) -> dict:
    context_chunks = await retrieve_context(
        query=request.topic,
        tenant_id=request.tenant_id,
        top_k=10,
    )
    if not context_chunks:
        raise HTTPException(status_code=422, detail="No study materials found. Upload content first.")

    context_string = build_context_string(context_chunks)
    num = max(3, min(request.num_slides, 12))
    prompt = VIDEO_PROMPT.format(topic=request.topic, context=context_string, num_slides=num)
    if request.language.lower() != "english":
        prompt = f"Respond entirely in {request.language}.\n\n{prompt}"

    llm = get_llm_provider()
    try:
        data = await llm.generate_structured(prompt, schema=VideoOutput, model=settings.llm.model, temperature=0.4)
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=503, detail="Cannot connect to Ollama") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=504, detail="AI request timed out") from exc
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=502, detail="AI runtime error") from exc

    return data.get("response", {})
