"""Study tool generation helpers shared by routes and queued workers."""
from __future__ import annotations

import json
import re
from typing import Any

from fastapi import HTTPException

from src.domains.ai_engine.ai.workflows import execute_text_query
from src.domains.ai_engine.schemas.ai_runtime import InternalAIQueryRequest, InternalStudyToolGenerateRequest


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
        cleaned = answer.split("\n\nSources:")[0].strip()
        if not cleaned:
            raise HTTPException(status_code=422, detail="Tool output is empty")
        return cleaned

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
            match = re.search(r"[A-D]", correct_raw)
            correct = match.group(0) if match else "A"
            if not question or len(options) < 2:
                continue
            normalized.append(
                {
                    "question": question,
                    "options": options,
                    "correct": correct,
                    "citation": str(item.get("citation", "")).strip() or None,
                    "index": idx + 1,
                }
            )
        if not normalized:
            raise HTTPException(status_code=422, detail="Quiz output did not contain valid questions")
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
            if front and back:
                cards.append({"front": front, "back": back})
        if not cards:
            raise HTTPException(status_code=422, detail="Flashcards output was empty")
        return cards

    if tool == "mindmap":
        if not isinstance(parsed, dict) or not str(parsed.get("label", "")).strip():
            raise HTTPException(status_code=422, detail="Mind map output must include a root label")
        return parsed

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
            if edge_from and edge_to:
                normalized_edges.append({"from": edge_from, "to": edge_to, "label": edge_label})
        if not normalized_nodes:
            raise HTTPException(status_code=422, detail="Concept map output had no valid nodes")
        return {"nodes": normalized_nodes, "edges": normalized_edges}

    raise HTTPException(status_code=400, detail="Unsupported tool")


async def execute_study_tool(request: InternalStudyToolGenerateRequest) -> dict[str, Any]:
    ai_result = await execute_text_query(
        InternalAIQueryRequest(
            query=request.topic,
            mode=request.tool,
            subject_id=request.subject_id,
            language="english",
            response_length="default",
            expertise_level="standard",
            tenant_id=request.tenant_id,
        )
    )

    answer = str(ai_result.get("answer", ""))
    try:
        structured_data = normalize_tool_output(request.tool, answer)
    except HTTPException as exc:
        if exc.status_code != 422 or request.tool == "flowchart":
            raise

        strict_query = (
            f"{request.topic}\n\nReturn STRICT valid JSON only for tool mode '{request.tool}'. "
            "Do not include markdown fences or extra prose."
        )
        ai_result = await execute_text_query(
            InternalAIQueryRequest(
                query=strict_query,
                mode=request.tool,
                subject_id=request.subject_id,
                language="english",
                response_length="default",
                expertise_level="standard",
                tenant_id=request.tenant_id,
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
    }
