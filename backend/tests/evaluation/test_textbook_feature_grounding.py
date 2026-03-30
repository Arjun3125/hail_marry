"""
Textbook-backed feature grounding acceptance suite.

This suite adds the missing deterministic evaluation gate from the RAG
execution checklist: a curated textbook fixture, expected concepts for a
single topic, forbidden hallucinations, and per-feature acceptance checks.
"""
from __future__ import annotations

import json
import os
import re
import sys
from typing import Any

import pytest

# Ensure backend imports resolve
backend_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

os.environ["TESTING"] = "true"
os.environ["DATABASE_URL"] = "sqlite:///:memory:"

from config import settings
from src.infrastructure.vector_store.retrieval import build_context_string, extract_citations
from src.shared.ai_tools.study_tools import normalize_tool_output


TEXTBOOK_TOPIC = "Class 10 Biology Chapter 10.1 Photosynthesis"
TEXTBOOK_QUERY = "Create flowchart for Chapter 10.1 photosynthesis"

TEXTBOOK_CHUNKS = [
    {
        "document_id": "class10-bio-ch10",
        "source": "class10_biology_ch10.pdf",
        "page": "120",
        "section": "10.1 Photosynthesis Overview",
        "citation": "[class10_biology_ch10.pdf_p120]",
        "text": (
            "Section 10.1 explains photosynthesis as the process by which green plants use "
            "sunlight, chlorophyll, carbon dioxide, and water to synthesize glucose and "
            "release oxygen."
        ),
        "vector_score": 0.95,
        "rerank_score": 0.97,
        "compressed": False,
    },
    {
        "document_id": "class10-bio-ch10",
        "source": "class10_biology_ch10.pdf",
        "page": "121",
        "section": "10.1 Site of Photosynthesis",
        "citation": "[class10_biology_ch10.pdf_p121]",
        "text": (
            "Photosynthesis takes place in chloroplasts in the mesophyll cells of leaves. "
            "Chlorophyll captures light energy needed to drive the process."
        ),
        "vector_score": 0.92,
        "rerank_score": 0.95,
        "compressed": False,
    },
    {
        "document_id": "class10-bio-ch10",
        "source": "class10_biology_ch10.pdf",
        "page": "122",
        "section": "10.1 Light Reaction",
        "citation": "[class10_biology_ch10.pdf_p122]",
        "text": (
            "In the light reaction, chlorophyll absorbs sunlight, water molecules split, "
            "oxygen is released, and ATP and NADPH are formed."
        ),
        "vector_score": 0.89,
        "rerank_score": 0.93,
        "compressed": False,
    },
    {
        "document_id": "class10-bio-ch10",
        "source": "class10_biology_ch10.pdf",
        "page": "123",
        "section": "10.1 Dark Reaction",
        "citation": "[class10_biology_ch10.pdf_p123]",
        "text": (
            "In the dark reaction, ATP and NADPH are used to fix carbon dioxide through the "
            "Calvin cycle and form glucose."
        ),
        "vector_score": 0.88,
        "rerank_score": 0.91,
        "compressed": False,
    },
    {
        "document_id": "class10-bio-ch10",
        "source": "class10_biology_ch10.pdf",
        "page": "130",
        "section": "10.2 Respiration",
        "citation": "[class10_biology_ch10.pdf_p130]",
        "text": (
            "Respiration breaks down glucose to release energy in living cells and is not the "
            "same process as photosynthesis."
        ),
        "vector_score": 0.21,
        "rerank_score": 0.18,
        "compressed": False,
    },
]

EXPECTED_CITATIONS = {
    "[class10_biology_ch10.pdf_p120]",
    "[class10_biology_ch10.pdf_p121]",
    "[class10_biology_ch10.pdf_p122]",
    "[class10_biology_ch10.pdf_p123]",
}

REQUIRED_CONCEPT_GROUPS = [
    {"photosynthesis"},
    {"sunlight", "light energy"},
    {"chlorophyll", "chloroplasts"},
    {"carbon dioxide", "co2"},
    {"water"},
    {"glucose"},
    {"oxygen"},
    {"light reaction"},
    {"dark reaction", "calvin cycle"},
]

FORBIDDEN_TERMS = {
    "mitosis",
    "earthquake",
    "tectonic",
    "volcano",
    "bacteria",
}

FEATURE_THRESHOLDS = {
    "qa": {"concept_coverage": 0.66, "grounding": 0.45, "citation_coverage": 1.0},
    "study_guide": {"concept_coverage": 0.66, "grounding": 0.35, "citation_coverage": 1.0},
    "quiz": {"concept_coverage": 0.55, "grounding": 0.15, "citation_coverage": 1.0},
    "flashcards": {"concept_coverage": 0.55, "grounding": 0.2, "citation_coverage": 1.0},
    "mindmap": {"concept_coverage": 0.55, "grounding": 0.15, "citation_coverage": 1.0},
    "flowchart": {"concept_coverage": 0.66, "grounding": 0.2, "citation_coverage": 1.0},
    "concept_map": {"concept_coverage": 0.55, "grounding": 0.15, "citation_coverage": 1.0},
    "socratic": {"concept_coverage": 0.44, "grounding": 0.35, "citation_coverage": 1.0},
    "debate": {"concept_coverage": 0.44, "grounding": 0.3, "citation_coverage": 1.0},
    "essay_review": {"concept_coverage": 0.44, "grounding": 0.3, "citation_coverage": 1.0},
}


FEATURE_OUTPUTS_RAW = {
    "qa": (
        "Photosynthesis is the process in which green plants use sunlight, chlorophyll, "
        "carbon dioxide, and water to make glucose and release oxygen. It occurs in "
        "chloroplasts of leaf mesophyll cells. The light reaction forms ATP and NADPH, and "
        "the dark reaction uses them to fix carbon dioxide into glucose [class10_biology_ch10.pdf_p120] "
        "[class10_biology_ch10.pdf_p121] [class10_biology_ch10.pdf_p122] [class10_biology_ch10.pdf_p123]."
    ),
    "study_guide": (
        "Study Guide: Photosynthesis\n"
        "- Definition: Green plants use sunlight, chlorophyll, carbon dioxide, and water to "
        "form glucose and oxygen [class10_biology_ch10.pdf_p120].\n"
        "- Site: The process occurs in chloroplasts in leaf mesophyll cells; chlorophyll "
        "captures light energy [class10_biology_ch10.pdf_p121].\n"
        "- Stages: The light reaction splits water and releases oxygen while making ATP and "
        "NADPH, then the dark reaction uses them in the Calvin cycle to produce glucose "
        "[class10_biology_ch10.pdf_p122] [class10_biology_ch10.pdf_p123]."
    ),
    "quiz": json.dumps(
        [
            {
                "question": "What do green plants use with carbon dioxide and water during photosynthesis?",
                "options": ["A. Sunlight", "B. Nitrogen", "C. Heat only", "D. Minerals"],
                "correct": "A",
                "citation": "[class10_biology_ch10.pdf_p120]",
            },
            {
                "question": "Where does photosynthesis take place in leaf cells?",
                "options": ["A. Nucleus", "B. Chloroplasts", "C. Vacuole", "D. Ribosomes"],
                "correct": "B",
                "citation": "[class10_biology_ch10.pdf_p121]",
            },
            {
                "question": "Which stage of photosynthesis releases oxygen?",
                "options": ["A. Dark reaction", "B. Calvin cycle", "C. Light reaction", "D. Respiration"],
                "correct": "C",
                "citation": "[class10_biology_ch10.pdf_p122]",
            },
            {
                "question": "What molecules are formed in the light reaction and used later?",
                "options": ["A. ATP and NADPH", "B. Starch and protein", "C. DNA and RNA", "D. Fats and oils"],
                "correct": "A",
                "citation": "[class10_biology_ch10.pdf_p122]",
            },
            {
                "question": "What does the dark reaction make by fixing carbon dioxide?",
                "options": ["A. Oxygen", "B. Glucose", "C. Water", "D. Chlorophyll"],
                "correct": "B",
                "citation": "[class10_biology_ch10.pdf_p123]",
            },
        ]
    ),
    "flashcards": json.dumps(
        [
            {"front": "Photosynthesis", "back": "Process by which plants make glucose using sunlight, carbon dioxide, and water.", "citation": "[class10_biology_ch10.pdf_p120]"},
            {"front": "Main pigment", "back": "Chlorophyll captures light energy for photosynthesis.", "citation": "[class10_biology_ch10.pdf_p121]"},
            {"front": "Site", "back": "Photosynthesis occurs in chloroplasts of mesophyll cells.", "citation": "[class10_biology_ch10.pdf_p121]"},
            {"front": "Light reaction", "back": "Splits water, releases oxygen, and forms ATP and NADPH.", "citation": "[class10_biology_ch10.pdf_p122]"},
            {"front": "Dark reaction", "back": "Uses ATP and NADPH to fix carbon dioxide in the Calvin cycle.", "citation": "[class10_biology_ch10.pdf_p123]"},
            {"front": "Input gas", "back": "Carbon dioxide is fixed during the dark reaction.", "citation": "[class10_biology_ch10.pdf_p123]"},
            {"front": "Output gas", "back": "Oxygen is released during the light reaction.", "citation": "[class10_biology_ch10.pdf_p122]"},
            {"front": "Food formed", "back": "Glucose is synthesized as the main food product.", "citation": "[class10_biology_ch10.pdf_p120]"},
        ]
    ),
    "mindmap": json.dumps(
        {
            "label": "Photosynthesis",
            "children": [
                {
                    "label": "Inputs",
                    "citation": "[class10_biology_ch10.pdf_p120]",
                    "children": [
                        {"label": "Sunlight", "citation": "[class10_biology_ch10.pdf_p120]"},
                        {"label": "Carbon dioxide", "citation": "[class10_biology_ch10.pdf_p120]"},
                        {"label": "Water", "citation": "[class10_biology_ch10.pdf_p120]"},
                    ],
                },
                {
                    "label": "Site",
                    "citation": "[class10_biology_ch10.pdf_p121]",
                    "children": [
                        {"label": "Chloroplasts", "citation": "[class10_biology_ch10.pdf_p121]"},
                        {"label": "Chlorophyll", "citation": "[class10_biology_ch10.pdf_p121]"},
                    ],
                },
                {
                    "label": "Stages",
                    "citation": "[class10_biology_ch10.pdf_p122]",
                    "children": [
                        {"label": "Light reaction", "citation": "[class10_biology_ch10.pdf_p122]"},
                        {"label": "Dark reaction", "citation": "[class10_biology_ch10.pdf_p123]"},
                    ],
                },
                {
                    "label": "Products",
                    "citation": "[class10_biology_ch10.pdf_p123]",
                    "children": [
                        {"label": "Glucose", "citation": "[class10_biology_ch10.pdf_p123]"},
                        {"label": "Oxygen", "citation": "[class10_biology_ch10.pdf_p122]"},
                    ],
                },
            ],
        }
    ),
    "flowchart": json.dumps(
        {
            "mermaid": (
                "flowchart TD\n"
                "A[Absorb light] --> B[Split water]\n"
                "B --> C[Release oxygen]\n"
                "C --> D[Make ATP and NADPH]\n"
                "D --> E[Fix carbon dioxide]\n"
                "E --> F[Form glucose]"
            ),
            "steps": [
                {
                    "id": "A",
                    "label": "Absorb light",
                    "detail": "Chlorophyll in chloroplasts absorbs sunlight to start photosynthesis.",
                    "citation": "[class10_biology_ch10.pdf_p121]",
                },
                {
                    "id": "B",
                    "label": "Light reaction",
                    "detail": "Water splits in the light reaction and oxygen is released.",
                    "citation": "[class10_biology_ch10.pdf_p122]",
                },
                {
                    "id": "D",
                    "label": "Store energy",
                    "detail": "ATP and NADPH are produced to power the next stage.",
                    "citation": "[class10_biology_ch10.pdf_p122]",
                },
                {
                    "id": "E",
                    "label": "Dark reaction",
                    "detail": "Carbon dioxide is fixed in the Calvin cycle using ATP and NADPH.",
                    "citation": "[class10_biology_ch10.pdf_p123]",
                },
                {
                    "id": "F",
                    "label": "Form glucose",
                    "detail": "The dark reaction produces glucose as food for the plant.",
                    "citation": "[class10_biology_ch10.pdf_p123]",
                },
            ],
        }
    ),
    "concept_map": json.dumps(
        {
            "nodes": [
                {"id": "1", "label": "Photosynthesis"},
                {"id": "2", "label": "Chloroplasts"},
                {"id": "3", "label": "Chlorophyll"},
                {"id": "4", "label": "Light reaction"},
                {"id": "5", "label": "Dark reaction"},
                {"id": "6", "label": "Glucose"},
                {"id": "7", "label": "Oxygen"},
            ],
            "edges": [
                {"from": "2", "to": "1", "label": "site of", "citation": "[class10_biology_ch10.pdf_p121]"},
                {"from": "3", "to": "4", "label": "absorbs light for", "citation": "[class10_biology_ch10.pdf_p121]"},
                {"from": "4", "to": "7", "label": "releases", "citation": "[class10_biology_ch10.pdf_p122]"},
                {"from": "4", "to": "5", "label": "supplies ATP and NADPH to", "citation": "[class10_biology_ch10.pdf_p122]"},
                {"from": "5", "to": "6", "label": "forms", "citation": "[class10_biology_ch10.pdf_p123]"},
            ],
        }
    ),
    "socratic": (
        "If photosynthesis happens in chloroplasts, what role might chlorophyll play there? "
        "Start by identifying what the plant takes in: sunlight, carbon dioxide, and water. "
        "Then ask yourself which stage releases oxygen and which stage fixes carbon dioxide into "
        "glucose through the Calvin cycle [class10_biology_ch10.pdf_p121] "
        "[class10_biology_ch10.pdf_p122] [class10_biology_ch10.pdf_p123]."
    ),
    "debate": (
        "Your thesis correctly connects photosynthesis to plant survival, but it is too narrow to say "
        "the process is only about making food. The textbook shows that chlorophyll in chloroplasts "
        "captures sunlight, the light reaction splits water and releases oxygen, and ATP plus NADPH "
        "power carbon dioxide fixation in the Calvin cycle [class10_biology_ch10.pdf_p121] "
        "[class10_biology_ch10.pdf_p122] [class10_biology_ch10.pdf_p123]. "
        "How will you defend your claim against the counter-argument that oxygen release and staged "
        "energy conversion are equally central to photosynthesis?"
    ),
    "essay_review": (
        "Strengths first: your response identifies sunlight, carbon dioxide, water, glucose, and oxygen, "
        "which aligns with the core definition of photosynthesis [class10_biology_ch10.pdf_p120]. "
        "Structural Integrity: Developing. Your explanation needs a clearer sequence from chlorophyll and "
        "chloroplasts to light reaction and dark reaction [class10_biology_ch10.pdf_p121] "
        "[class10_biology_ch10.pdf_p122] [class10_biology_ch10.pdf_p123]. "
        "Thematic Depth: Developing. Can you explain why ATP and NADPH matter before glucose forms? "
        "Evidence Quality: Strong. You reference the correct inputs and products, but add the Calvin cycle "
        "to support your claim [class10_biology_ch10.pdf_p123]. "
        "Argumentation: Developing. What is the difference between oxygen release in the light reaction and "
        "glucose formation in the dark reaction?"
    ),
}

BAD_FEATURE_OUTPUTS_RAW = {
    "study_guide": (
        "Study Guide: Plants are important for life. They are green and help the environment. "
        "Students should remember diagrams and definitions for the exam."
    ),
    "flowchart": json.dumps(
        {
            "mermaid": "flowchart TD\nA[Cell division] --> B[Chromosomes duplicate]\nB --> C[Two nuclei form]",
            "steps": [
                {
                    "id": "A",
                    "label": "Start mitosis",
                    "detail": "The cell begins mitosis and prepares chromosomes.",
                    "citation": "[class10_biology_ch10.pdf_p120]",
                },
                {
                    "id": "B",
                    "label": "Duplicate DNA",
                    "detail": "Chromosomes line up and separate during mitosis.",
                    "citation": "[class10_biology_ch10.pdf_p121]",
                },
            ],
        }
    ),
    "concept_map": json.dumps(
        {
            "nodes": [
                {"id": "1", "label": "Earthquake"},
                {"id": "2", "label": "Tectonic plates"},
                {"id": "3", "label": "Seismic waves"},
            ],
            "edges": [
                {"from": "2", "to": "1", "label": "cause", "citation": "[class10_biology_ch10.pdf_p122]"},
                {"from": "1", "to": "3", "label": "produce", "citation": "[class10_biology_ch10.pdf_p123]"},
            ],
        }
    ),
    "debate": (
        "I disagree because volcanoes and tectonic pressure are stronger forces than plants. "
        "Why should anyone care about your argument?"
    ),
    "essay_review": (
        "Good job. Strong / Strong / Strong / Strong. Your essay is perfect and needs no evidence."
    ),
}


def _evaluation_guard() -> None:
    if settings.app.demo_mode:
        raise AssertionError("Textbook grounding evaluation must run with demo mode disabled.")


def _tokenize(text: str) -> set[str]:
    return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))


def _normalize_text(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()


def _keyword_rank(query: str, chunks: list[dict[str, Any]]) -> list[dict[str, Any]]:
    query_tokens = _tokenize(query)
    ranked = []
    for chunk in chunks:
        text_tokens = _tokenize(f"{chunk['section']} {chunk['text']}")
        score = len(query_tokens.intersection(text_tokens))
        if "10.1" in chunk["section"]:
            score += 2
        ranked.append((score, chunk))
    ranked.sort(key=lambda item: item[0], reverse=True)
    return [chunk for _, chunk in ranked]


def _flatten_mindmap(node: dict[str, Any]) -> list[str]:
    labels = [str(node.get("label", "")).strip()]
    for child in node.get("children", []) or []:
        if isinstance(child, dict):
            labels.extend(_flatten_mindmap(child))
    return labels


def _artifact_text(mode: str, artifact: Any) -> str:
    if isinstance(artifact, str):
        return artifact
    if mode == "quiz":
        return " ".join(
            f"{item['question']} {' '.join(item['options'])} {item['citation']}" for item in artifact
        )
    if mode == "flashcards":
        return " ".join(f"{item['front']} {item['back']} {item['citation']}" for item in artifact)
    if mode == "mindmap":
        return " ".join(label for label in _flatten_mindmap(artifact) if label)
    if mode == "flowchart":
        step_text = " ".join(
            f"{step['label']} {step['detail']} {step['citation']}" for step in artifact["steps"]
        )
        return f"{artifact['mermaid']} {step_text}"
    if mode == "concept_map":
        node_text = " ".join(node["label"] for node in artifact["nodes"])
        edge_text = " ".join(
            f"{edge['label']} {edge['citation']}" for edge in artifact["edges"]
        )
        return f"{node_text} {edge_text}"
    raise AssertionError(f"Unsupported mode for artifact text: {mode}")


def _artifact_citations(mode: str, artifact: Any) -> set[str]:
    if isinstance(artifact, str):
        return set(re.findall(r"\[[^\]]+\]", artifact))
    if mode == "quiz":
        return {item["citation"] for item in artifact}
    if mode == "flashcards":
        return {item["citation"] for item in artifact}
    if mode == "flowchart":
        return {step["citation"] for step in artifact["steps"]}
    if mode == "concept_map":
        return {edge["citation"] for edge in artifact["edges"]}
    if mode == "mindmap":
        citations: set[str] = set()

        def walk(node: dict[str, Any]) -> None:
            citation = str(node.get("citation") or "").strip()
            if citation:
                citations.add(citation)
            for child in node.get("children", []) or []:
                if isinstance(child, dict):
                    walk(child)

        walk(artifact)
        return citations
    return set()


def _concept_coverage(text: str) -> float:
    normalized = _normalize_text(text)
    covered = 0
    for aliases in REQUIRED_CONCEPT_GROUPS:
        if any(alias in normalized for alias in aliases):
            covered += 1
    return covered / len(REQUIRED_CONCEPT_GROUPS)


def _grounding_score(text: str) -> float:
    artifact_tokens = _tokenize(text)
    if not artifact_tokens:
        return 0.0
    context_tokens = _tokenize(" ".join(chunk["text"] for chunk in TEXTBOOK_CHUNKS[:4]))
    return len(artifact_tokens.intersection(context_tokens)) / len(artifact_tokens)


def _forbidden_hits(text: str) -> set[str]:
    normalized = _normalize_text(text)
    return {term for term in FORBIDDEN_TERMS if term in normalized}


def _citation_coverage(citations: set[str]) -> float | None:
    if not citations:
        return None
    return len(citations.intersection(EXPECTED_CITATIONS)) / len(citations)


def _structurally_complete(mode: str, artifact: Any) -> bool:
    if mode in {"qa", "study_guide", "socratic", "debate"}:
        return len(_tokenize(str(artifact))) >= 18
    if mode == "essay_review":
        normalized = _normalize_text(str(artifact))
        required_sections = {
            "structural integrity",
            "thematic depth",
            "evidence quality",
            "argumentation",
        }
        return len(_tokenize(str(artifact))) >= 35 and required_sections.issubset(set(
            section for section in required_sections if section in normalized
        ))
    if mode == "quiz":
        return len(artifact) >= 5 and all(len(item["options"]) == 4 for item in artifact)
    if mode == "flashcards":
        return len(artifact) >= 8
    if mode == "mindmap":
        labels = [label for label in _flatten_mindmap(artifact) if label]
        return len(labels) >= 10 and len(artifact.get("children", []) or []) >= 3
    if mode == "flowchart":
        return len(artifact["steps"]) >= 4 and "-->" in artifact["mermaid"]
    if mode == "concept_map":
        return len(artifact["nodes"]) >= 5 and len(artifact["edges"]) >= 4
    raise AssertionError(f"Unsupported mode for completeness check: {mode}")


def _evaluate_feature_output(mode: str, artifact: Any) -> dict[str, Any]:
    text = _artifact_text(mode, artifact) if not isinstance(artifact, str) else artifact
    citations = _artifact_citations(mode, artifact)
    return {
        "concept_coverage": _concept_coverage(text),
        "grounding": _grounding_score(text),
        "citation_coverage": _citation_coverage(citations),
        "forbidden_hits": _forbidden_hits(text),
        "structurally_complete": _structurally_complete(mode, artifact),
    }


def _parse_feature_output(mode: str, raw_output: str) -> Any:
    if mode in {"quiz", "flashcards", "mindmap", "flowchart", "concept_map"}:
        return normalize_tool_output(mode, raw_output)
    return raw_output


@pytest.fixture(scope="module")
def normalized_feature_outputs() -> dict[str, Any]:
    _evaluation_guard()
    return {
        mode: _parse_feature_output(mode, raw_output)
        for mode, raw_output in FEATURE_OUTPUTS_RAW.items()
    }


def test_textbook_retrieval_probe_prefers_subtopic_chunks():
    _evaluation_guard()
    ranked = _keyword_rank(TEXTBOOK_QUERY, TEXTBOOK_CHUNKS)
    top_chunks = ranked[:4]

    assert all(chunk["section"].startswith("10.1") for chunk in top_chunks[:3])
    assert {chunk["citation"] for chunk in top_chunks} == EXPECTED_CITATIONS

    context = build_context_string(top_chunks)
    assert "[class10_biology_ch10.pdf_p120]" in context
    assert "[class10_biology_ch10.pdf_p123]" in context

    citations = extract_citations(top_chunks)
    assert {f"[{item['source']}_p{item['page']}]" for item in citations} == EXPECTED_CITATIONS


@pytest.mark.parametrize(
    "mode",
    ["qa", "study_guide", "quiz", "flashcards", "mindmap", "flowchart", "concept_map", "socratic", "debate", "essay_review"],
)
def test_textbook_feature_outputs_meet_grounding_gate(mode: str, normalized_feature_outputs: dict[str, Any]):
    artifact = normalized_feature_outputs[mode]
    evaluation = _evaluate_feature_output(mode, artifact)
    thresholds = FEATURE_THRESHOLDS[mode]

    assert evaluation["forbidden_hits"] == set(), f"{mode} included forbidden terms: {evaluation['forbidden_hits']}"
    assert evaluation["structurally_complete"] is True, f"{mode} output was structurally incomplete"
    assert evaluation["concept_coverage"] >= thresholds["concept_coverage"], (
        f"{mode} concept coverage too low: {evaluation['concept_coverage']:.2f}"
    )
    assert evaluation["grounding"] >= thresholds["grounding"], (
        f"{mode} grounding too low: {evaluation['grounding']:.2f}"
    )

    expected_citation_coverage = thresholds["citation_coverage"]
    if expected_citation_coverage is not None:
        assert evaluation["citation_coverage"] is not None
        assert evaluation["citation_coverage"] >= expected_citation_coverage, (
            f"{mode} citation coverage too low: {evaluation['citation_coverage']:.2f}"
        )


def test_flowchart_acceptance_requires_ordered_cited_steps(normalized_feature_outputs: dict[str, Any]):
    flowchart = normalized_feature_outputs["flowchart"]
    step_details = [f"{step['label']} {step['detail']}".lower() for step in flowchart["steps"]]

    light_idx = next(i for i, text in enumerate(step_details) if "light reaction" in text)
    dark_idx = next(i for i, text in enumerate(step_details) if "dark reaction" in text)

    assert light_idx < dark_idx
    assert {step["citation"] for step in flowchart["steps"]}.issubset(EXPECTED_CITATIONS)
    assert "glucose" in step_details[-1]


def test_concept_map_acceptance_requires_grounded_relationships(normalized_feature_outputs: dict[str, Any]):
    concept_map = normalized_feature_outputs["concept_map"]
    label_by_id = {node["id"]: node["label"] for node in concept_map["nodes"]}
    relationships = {
        (label_by_id[edge["from"]], label_by_id[edge["to"]], edge["label"].lower())
        for edge in concept_map["edges"]
    }

    assert ("Chloroplasts", "Photosynthesis", "site of") in relationships
    assert ("Light reaction", "Dark reaction", "supplies atp and nadph to") in relationships
    assert ("Dark reaction", "Glucose", "forms") in relationships
    assert {edge["citation"] for edge in concept_map["edges"]}.issubset(EXPECTED_CITATIONS)


def test_debate_acceptance_requires_grounded_counter_argument(normalized_feature_outputs: dict[str, Any]):
    debate = str(normalized_feature_outputs["debate"])
    lowered = debate.lower()

    assert "counter-argument" in lowered or "how will you defend" in lowered
    assert "oxygen" in lowered
    assert "calvin cycle" in lowered or "dark reaction" in lowered
    assert debate.strip().endswith("?")
    assert set(re.findall(r"\[[^\]]+\]", debate)).issubset(EXPECTED_CITATIONS)


def test_essay_review_acceptance_requires_dimension_ratings_and_guidance(normalized_feature_outputs: dict[str, Any]):
    review = str(normalized_feature_outputs["essay_review"])
    lowered = review.lower()

    assert "strengths first" in lowered
    assert "structural integrity" in lowered
    assert "thematic depth" in lowered
    assert "evidence quality" in lowered
    assert "argumentation" in lowered
    assert "strong" in lowered or "developing" in lowered or "needs work" in lowered
    assert review.count("?") >= 2
    assert set(re.findall(r"\[[^\]]+\]", review)).issubset(EXPECTED_CITATIONS)


@pytest.mark.parametrize("mode", ["study_guide", "flowchart", "concept_map", "debate", "essay_review"])
def test_grounding_gate_rejects_generic_or_hallucinated_outputs(mode: str):
    artifact = _parse_feature_output(mode, BAD_FEATURE_OUTPUTS_RAW[mode])
    evaluation = _evaluate_feature_output(mode, artifact)
    thresholds = FEATURE_THRESHOLDS[mode]

    passes = (
        not evaluation["forbidden_hits"]
        and evaluation["structurally_complete"]
        and evaluation["concept_coverage"] >= thresholds["concept_coverage"]
        and evaluation["grounding"] >= thresholds["grounding"]
        and (
            thresholds["citation_coverage"] is None
            or (
                evaluation["citation_coverage"] is not None
                and evaluation["citation_coverage"] >= thresholds["citation_coverage"]
            )
        )
    )

    assert passes is False, f"{mode} bad output unexpectedly passed the grounding gate"


def test_textbook_grounding_guard_raises_in_demo_mode(monkeypatch):
    original_value = settings.app.demo_mode
    monkeypatch.setattr(settings.app, "demo_mode", True)
    try:
        with pytest.raises(AssertionError, match="demo mode disabled"):
            _evaluation_guard()
    finally:
        monkeypatch.setattr(settings.app, "demo_mode", original_value)
