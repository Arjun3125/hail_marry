"""Study tool generation helpers shared by routes and queued workers."""
from __future__ import annotations

import json
import re
from typing import Any

from fastapi import HTTPException

from src.interfaces.rest_api.ai.workflows import execute_text_query
from src.domains.platform.schemas.ai_runtime import InternalAIQueryRequest, InternalStudyToolGenerateRequest


def extract_json_payload(text: str) -> Any:
    raw = (text or "").strip()
    if not raw:
        return None

    try:
        return json.loads(raw)
    except Exception:
        pass

    fenced = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw)
    if fenced:
        candidate = fenced.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    for start_char, end_char in (("[", "]"), ("{", "}")):
        start_idx = raw.find(start_char)
        end_idx = raw.rfind(end_char)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            candidate = raw[start_idx : end_idx + 1]
            try:
                return json.loads(candidate)
            except Exception:
                continue

    return None


def normalize_tool_output(tool: str, answer: str) -> Any:
    if tool == "flowchart":
        parsed = extract_json_payload(answer)
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=422, detail="Flowchart output must be a JSON object")
        mermaid = str(parsed.get("mermaid", "")).strip()
        steps = parsed.get("steps", [])
        if not mermaid.startswith("flowchart TD") or "-->" not in mermaid:
            raise HTTPException(status_code=422, detail="Flowchart Mermaid syntax is invalid")
        if re.search(r"\[\s*\]|\{\{\s*\}\}", mermaid):
            raise HTTPException(status_code=422, detail="Flowchart contains empty nodes")
        if not isinstance(steps, list):
            raise HTTPException(status_code=422, detail="Flowchart steps are invalid")
        normalized_steps = []
        for step in steps:
            if not isinstance(step, dict):
                continue
            step_id = str(step.get("id", "")).strip()
            label = str(step.get("label", "")).strip()
            detail = str(step.get("detail", "")).strip()
            citation = str(step.get("citation", "")).strip()
            if step_id and label and detail and citation:
                normalized_steps.append(
                    {"id": step_id, "label": label, "detail": detail, "citation": citation}
                )
        if len(normalized_steps) < 2:
            raise HTTPException(status_code=422, detail="Flowchart output did not contain enough cited steps")
        return {"mermaid": mermaid, "steps": normalized_steps}

    parsed = extract_json_payload(answer)
    if parsed is None:
        raise HTTPException(status_code=422, detail="Failed to parse tool output as JSON")

    if tool == "quiz":
        if not isinstance(parsed, list):
            raise HTTPException(status_code=422, detail="Quiz output must be a JSON array")
        normalized: list[dict[str, Any]] = []
        for idx, item in enumerate(parsed):
            if not isinstance(item, dict):
                continue
            question = str(item.get("question", "")).strip()
            options_raw = item.get("options", [])
            if isinstance(options_raw, list):
                options = [str(option).strip() for option in options_raw if str(option).strip()]
            else:
                options = []
            correct_raw = str(item.get("correct", "")).strip().upper()
            citation = str(item.get("citation", "")).strip()
            difficulty = str(item.get("difficulty", "medium")).strip().lower()
            match = re.search(r"[A-D]", correct_raw)
            correct = match.group(0) if match else "A"
            if difficulty not in {"easy", "medium", "hard"}:
                difficulty = "medium"
            if not question or len(options) < 2 or not citation:
                continue
            normalized.append(
                {
                    "question": question,
                    "options": options,
                    "correct": correct,
                    "citation": citation,
                    "difficulty": difficulty,
                    "index": idx + 1,
                }
            )
        if not normalized:
            raise HTTPException(status_code=422, detail="Quiz output did not contain valid cited questions")
        return normalized

    if tool == "flashcards":
        if not isinstance(parsed, list):
            raise HTTPException(status_code=422, detail="Flashcards output must be a JSON array")
        cards = []
        for item in parsed:
            if not isinstance(item, dict):
                continue
            front = str(item.get("front", "")).strip()
            back = str(item.get("back", "")).strip()
            citation = str(item.get("citation", "")).strip()
            if front and back and citation:
                cards.append({"front": front, "back": back, "citation": citation})
        if not cards:
            raise HTTPException(status_code=422, detail="Flashcards output did not contain valid cited cards")
        return cards

    if tool == "mindmap":
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=422, detail="Mind map output must be a JSON object")

        cited_nodes = 0

        def normalize_node(node: Any, *, is_root: bool = False) -> dict[str, Any] | None:
            nonlocal cited_nodes
            if not isinstance(node, dict):
                return None

            label = str(node.get("label", "")).strip()
            if not label:
                return None

            normalized_node: dict[str, Any] = {"label": label}
            citation = str(node.get("citation", "")).strip()
            if citation:
                normalized_node["citation"] = citation
                if not is_root:
                    cited_nodes += 1

            children = []
            for child in node.get("children", []) or []:
                normalized_child = normalize_node(child)
                if normalized_child:
                    children.append(normalized_child)
            if children:
                normalized_node["children"] = children

            return normalized_node

        normalized_root = normalize_node(parsed, is_root=True)
        if not normalized_root:
            raise HTTPException(status_code=422, detail="Mind map output must include a root label")
        if cited_nodes < 2:
            raise HTTPException(status_code=422, detail="Mind map output did not contain enough cited nodes")
        return normalized_root

    if tool == "concept_map":
        if not isinstance(parsed, dict):
            raise HTTPException(status_code=422, detail="Concept map output must be a JSON object")
        nodes = parsed.get("nodes", [])
        edges = parsed.get("edges", [])
        if not isinstance(nodes, list) or not isinstance(edges, list):
            raise HTTPException(status_code=422, detail="Concept map nodes/edges are invalid")
        normalized_nodes = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            node_id = str(node.get("id", "")).strip()
            label = str(node.get("label", "")).strip()
            if node_id and label:
                normalized_nodes.append({"id": node_id, "label": label})
        normalized_edges = []
        for edge in edges:
            if not isinstance(edge, dict):
                continue
            edge_from = str(edge.get("from", "")).strip()
            edge_to = str(edge.get("to", "")).strip()
            edge_label = str(edge.get("label", "")).strip()
            edge_citation = str(edge.get("citation", "")).strip()
            if edge_from and edge_to and edge_citation:
                normalized_edges.append(
                    {"from": edge_from, "to": edge_to, "label": edge_label, "citation": edge_citation}
                )
        if not normalized_nodes:
            raise HTTPException(status_code=422, detail="Concept map output had no valid nodes")
        if not normalized_edges:
            raise HTTPException(status_code=422, detail="Concept map output had no valid cited edges")
        return {"nodes": normalized_nodes, "edges": normalized_edges}

    raise HTTPException(status_code=400, detail="Unsupported tool")


def _build_adaptive_tool_topic(request: InternalStudyToolGenerateRequest) -> str:
    topic = request.topic.strip()
    instruction_lines: list[str] = []

    learner_profile = request.learner_profile or {}
    learner_topic_context = request.learner_topic_context or {}

    if request.tool == "quiz" and request.adaptive_quiz_profile:
        quiz_suffix = str(request.adaptive_quiz_profile.get("prompt_suffix", "")).strip()
        if quiz_suffix:
            instruction_lines.append(quiz_suffix)

    expertise = str(learner_profile.get("inferred_expertise_level") or "").strip().lower()
    preferred_length = str(learner_profile.get("preferred_response_length") or "").strip().lower()
    mastery_score = learner_topic_context.get("mastery_score")
    focus_concepts = [
        str(item).strip()
        for item in learner_topic_context.get("focus_concepts", []) or []
        if str(item).strip()
    ]
    repeated_confusion = int(learner_topic_context.get("repeated_confusion_count") or 0)
    struggling = (isinstance(mastery_score, (int, float)) and mastery_score < 60) or repeated_confusion >= 2
    advanced = isinstance(mastery_score, (int, float)) and mastery_score >= 80 and expertise == "advanced"

    if request.tool == "flashcards":
        instruction_lines.append(
            "Prioritize the weakest or most confusing concepts first in the flashcard order."
        )
        if focus_concepts:
            instruction_lines.append(
                f"Make sure these concepts appear early if grounded in context: {', '.join(focus_concepts[:4])}."
            )
        if struggling:
            instruction_lines.append(
                "Include at least one misconception-correction or step-by-step recall card for the hardest concept."
            )
        if expertise == "simple" or preferred_length == "brief":
            instruction_lines.append("Keep each flashcard back especially concise and easy to recall.")

    if request.tool in {"mindmap", "flowchart", "concept_map"}:
        if struggling or expertise == "simple":
            instruction_lines.append(
                "Prefer a simpler structure with foundational ideas first, clear labels, and no unnecessary branching."
            )
        elif advanced:
            instruction_lines.append(
                "Include deeper relationships, applications, or causal links where clearly supported by context."
            )

    if not instruction_lines:
        return topic

    return topic + "\n\nAdaptive generation guidance:\n- " + "\n- ".join(instruction_lines)


async def execute_study_tool(request: InternalStudyToolGenerateRequest) -> dict[str, Any]:
    effective_topic = _build_adaptive_tool_topic(request)

    ai_result = await execute_text_query(
        InternalAIQueryRequest(
            query=effective_topic,
            mode=request.tool,
            subject_id=request.subject_id,
            notebook_id=request.notebook_id,
            language="english",
            response_length="default",
            expertise_level="standard",
            tenant_id=request.tenant_id,
            user_id=request.user_id,
            learner_profile=request.learner_profile,
            learner_topic_context=request.learner_topic_context,
            model_override=request.model_override,
            max_prompt_tokens=request.max_prompt_tokens,
            max_completion_tokens=request.max_completion_tokens,
        )
    )

    answer = str(ai_result.get("answer", ""))
    try:
        structured_data = normalize_tool_output(request.tool, answer)
    except HTTPException as exc:
        if exc.status_code != 422:
            raise

        strict_query = (
            f"{effective_topic}\n\nReturn STRICT valid JSON only for tool mode '{request.tool}'. "
            "Do not include markdown fences or extra prose."
        )
        ai_result = await execute_text_query(
            InternalAIQueryRequest(
                query=strict_query,
                mode=request.tool,
                subject_id=request.subject_id,
                notebook_id=request.notebook_id,
                language="english",
                response_length="default",
                expertise_level="standard",
                tenant_id=request.tenant_id,
                user_id=request.user_id,
                learner_profile=request.learner_profile,
                learner_topic_context=request.learner_topic_context,
                model_override=request.model_override,
                max_prompt_tokens=request.max_prompt_tokens,
                max_completion_tokens=request.max_completion_tokens,
            )
        )
        structured_data = normalize_tool_output(request.tool, str(ai_result.get("answer", "")))

    return {
        "tool": request.tool,
        "topic": request.topic,
        "data": structured_data,
        "citations": ai_result.get("citations", []),
        "token_usage": ai_result.get("token_usage", 0),
        "citation_valid": ai_result.get("citation_valid", False),
        "adaptive_quiz_profile": request.adaptive_quiz_profile,
        "model_used": ai_result.get("model_used"),
    }
