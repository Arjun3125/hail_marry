import asyncio
import os
import sys
from pathlib import Path
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from fastapi import HTTPException


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"


def test_shared_normalizer_keeps_structured_contract_for_all_supported_tools():
    from src.shared.ai_tools.study_tools import normalize_tool_output

    payloads = {
        "quiz": '[{"question":"Q1","options":["A. One","B. Two"],"correct":"A","citation":"[p1]"}]',
        "flashcards": '[{"front":"Term","back":"Definition","citation":"[p1]"}]',
        "mindmap": '{"label":"Root","children":[{"label":"Child A","citation":"[p1]"},{"label":"Child B","citation":"[p2]"}]}',
        "flowchart": '{"mermaid":"flowchart TD\\nA[Start] --> B[End]","steps":[{"id":"A","label":"Start","detail":"Begin.","citation":"[p1]"},{"id":"B","label":"End","detail":"Finish.","citation":"[p2]"}]}',
        "concept_map": '{"nodes":[{"id":"1","label":"Plant"},{"id":"2","label":"Leaf"}],"edges":[{"from":"1","to":"2","label":"has","citation":"[p1]"}]}',
    }

    normalized = {tool: normalize_tool_output(tool, raw) for tool, raw in payloads.items()}

    assert isinstance(normalized["quiz"], list)
    assert normalized["quiz"][0]["index"] == 1
    assert isinstance(normalized["flashcards"], list)
    assert normalized["flashcards"][0]["citation"] == "[p1]"
    assert normalized["mindmap"]["children"][0]["citation"] == "[p1]"
    assert normalized["flowchart"]["mermaid"].startswith("flowchart TD")
    assert normalized["concept_map"]["edges"][0]["citation"] == "[p1]"


def test_shared_normalizer_rejects_uncited_structured_outputs():
    from src.shared.ai_tools.study_tools import normalize_tool_output

    with pytest.raises(HTTPException, match="cited questions"):
        normalize_tool_output("quiz", '[{"question":"Q1","options":["A. One","B. Two"],"correct":"A"}]')

    with pytest.raises(HTTPException, match="cited cards"):
        normalize_tool_output("flashcards", '[{"front":"Term","back":"Definition"}]')

    with pytest.raises(HTTPException, match="valid cited edges"):
        normalize_tool_output("concept_map", '{"nodes":[{"id":"1","label":"Plant"}],"edges":[{"from":"1","to":"1","label":"self"}]}')


def test_execute_study_tool_retries_with_strict_json_prompt_and_preserves_metadata():
    from src.shared.ai_tools import study_tools

    ai_mock = AsyncMock(
        side_effect=[
            {
                "answer": "not valid json",
                "citations": [{"source": "biology.pdf", "page": "1"}],
                "token_usage": 13,
                "citation_valid": False,
            },
            {
                "answer": '[{"question":"Q1","options":["A. One","B. Two"],"correct":"A","citation":"[biology_p1]"}]',
                "citations": [{"source": "biology.pdf", "page": "1"}],
                "token_usage": 21,
                "citation_valid": True,
            },
        ]
    )

    with patch.object(study_tools, "execute_text_query", ai_mock):
        payload = asyncio.run(
            study_tools.execute_study_tool(
                study_tools.InternalStudyToolGenerateRequest(
                    tool="quiz",
                    topic="Create quiz on photosynthesis",
                    subject_id="biology",
                    notebook_id=uuid4(),
                    tenant_id=str(uuid4()),
                )
            )
        )

    assert ai_mock.await_count == 2
    retry_request = ai_mock.await_args_list[1].args[0]
    assert "STRICT valid JSON only" in retry_request.query
    assert "quiz" in retry_request.query
    assert payload["tool"] == "quiz"
    assert payload["citation_valid"] is True
    assert payload["token_usage"] == 21
    assert payload["data"][0]["citation"] == "[biology_p1]"
