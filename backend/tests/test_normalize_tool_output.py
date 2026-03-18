"""Tests for _extract_json_payload and _normalize_tool_output in routes/students.py."""
import os
import sys
import unittest
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from fastapi import HTTPException
from src.domains.academic.routes.students import _extract_json_payload, _normalize_tool_output


class ExtractJsonPayloadTests(unittest.TestCase):
    """Verify JSON extraction from various LLM output formats."""

    def test_plain_json_array(self):
        result = _extract_json_payload('[{"a": 1}]')
        self.assertEqual(result, [{"a": 1}])

    def test_plain_json_object(self):
        result = _extract_json_payload('{"key": "value"}')
        self.assertEqual(result, {"key": "value"})

    def test_fenced_code_block(self):
        text = 'Here is the output:\n```json\n[{"q": "Q1"}]\n```\nDone.'
        result = _extract_json_payload(text)
        self.assertEqual(result, [{"q": "Q1"}])

    def test_fenced_without_language(self):
        text = '```\n{"label": "Root"}\n```'
        result = _extract_json_payload(text)
        self.assertEqual(result, {"label": "Root"})

    def test_embedded_in_text(self):
        text = 'The answer is: [{"item": 1}] and that is all.'
        result = _extract_json_payload(text)
        self.assertEqual(result, [{"item": 1}])

    def test_embedded_object_in_text(self):
        text = 'Result: {"nodes": [], "edges": []} end'
        result = _extract_json_payload(text)
        self.assertEqual(result, {"nodes": [], "edges": []})

    def test_empty_string_returns_none(self):
        self.assertIsNone(_extract_json_payload(""))

    def test_none_returns_none(self):
        self.assertIsNone(_extract_json_payload(None))

    def test_invalid_json_returns_none(self):
        self.assertIsNone(_extract_json_payload("this is not json at all"))

    def test_malformed_json_returns_none(self):
        self.assertIsNone(_extract_json_payload("[{broken json}"))


class NormalizeToolOutputTests(unittest.TestCase):
    """Verify _normalize_tool_output for all supported tools."""

    # ─── Flowchart ───────────────────────────────────────────

    def test_flowchart_returns_cleaned_text(self):
        answer = "flowchart TD\nA[Start] --> B[End]\n\nSources: notes.pdf"
        result = _normalize_tool_output("flowchart", answer)
        self.assertEqual(result, "flowchart TD\nA[Start] --> B[End]")

    def test_flowchart_without_sources_unchanged(self):
        answer = "flowchart TD\nA --> B"
        result = _normalize_tool_output("flowchart", answer)
        self.assertEqual(result, "flowchart TD\nA --> B")

    def test_flowchart_empty_raises_422(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("flowchart", "")
        self.assertEqual(ctx.exception.status_code, 422)

    # ─── Quiz ────────────────────────────────────────────────

    def test_quiz_valid_array(self):
        answer = '[{"question":"Q1","options":["A. One","B. Two"],"correct":"B"}]'
        result = _normalize_tool_output("quiz", answer)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["question"], "Q1")
        self.assertEqual(result[0]["correct"], "B")
        self.assertEqual(result[0]["index"], 1)

    def test_quiz_rejects_non_array(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("quiz", '{"question":"Q1"}')
        self.assertEqual(ctx.exception.status_code, 422)

    def test_quiz_filters_items_with_fewer_than_2_options(self):
        answer = '[{"question":"Q1","options":["A. One"],"correct":"A"},{"question":"Q2","options":["A. X","B. Y"],"correct":"A"}]'
        result = _normalize_tool_output("quiz", answer)
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["question"], "Q2")

    def test_quiz_normalizes_correct_letter(self):
        answer = '[{"question":"Q1","options":["A. X","B. Y","C. Z"],"correct":"the correct one is C"}]'
        result = _normalize_tool_output("quiz", answer)
        self.assertEqual(result[0]["correct"], "C")

    def test_quiz_all_bad_items_raises_422(self):
        answer = '[{"question":"","options":[],"correct":""}]'
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("quiz", answer)
        self.assertEqual(ctx.exception.status_code, 422)

    # ─── Flashcards ──────────────────────────────────────────

    def test_flashcards_valid(self):
        answer = '[{"front":"F1","back":"B1"},{"front":"F2","back":"B2"}]'
        result = _normalize_tool_output("flashcards", answer)
        self.assertEqual(len(result), 2)

    def test_flashcards_filters_empty_front_back(self):
        answer = '[{"front":"","back":"B1"},{"front":"F2","back":"B2"}]'
        result = _normalize_tool_output("flashcards", answer)
        self.assertEqual(len(result), 1)

    def test_flashcards_rejects_non_array(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("flashcards", '{"front":"F"}')
        self.assertEqual(ctx.exception.status_code, 422)

    def test_flashcards_all_empty_raises_422(self):
        answer = '[{"front":"","back":""}]'
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("flashcards", answer)
        self.assertEqual(ctx.exception.status_code, 422)

    # ─── Mind Map ────────────────────────────────────────────

    def test_mindmap_valid(self):
        answer = '{"label":"Root","children":[{"label":"Child"}]}'
        result = _normalize_tool_output("mindmap", answer)
        self.assertEqual(result["label"], "Root")

    def test_mindmap_missing_label_raises_422(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("mindmap", '{"children":[]}')
        self.assertEqual(ctx.exception.status_code, 422)

    def test_mindmap_rejects_non_object(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("mindmap", '[]')
        self.assertEqual(ctx.exception.status_code, 422)

    # ─── Concept Map ─────────────────────────────────────────

    def test_concept_map_valid(self):
        answer = '{"nodes":[{"id":"1","label":"Cell"}],"edges":[{"from":"1","to":"1","label":"self"}]}'
        result = _normalize_tool_output("concept_map", answer)
        self.assertEqual(len(result["nodes"]), 1)
        self.assertEqual(len(result["edges"]), 1)

    def test_concept_map_filters_bad_nodes(self):
        answer = '{"nodes":[{"id":"","label":""},{"id":"2","label":"Valid"}],"edges":[]}'
        result = _normalize_tool_output("concept_map", answer)
        self.assertEqual(len(result["nodes"]), 1)
        self.assertEqual(result["nodes"][0]["label"], "Valid")

    def test_concept_map_no_valid_nodes_raises_422(self):
        answer = '{"nodes":[{"id":"","label":""}],"edges":[]}'
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("concept_map", answer)
        self.assertEqual(ctx.exception.status_code, 422)

    def test_concept_map_rejects_non_object(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("concept_map", '[]')
        self.assertEqual(ctx.exception.status_code, 422)

    # ─── Unsupported Tool ────────────────────────────────────

    def test_unsupported_tool_raises_400(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("unknown_tool", '{}')
        self.assertEqual(ctx.exception.status_code, 400)

    # ─── Invalid JSON passed to structured tool ──────────────

    def test_structured_tool_invalid_json_raises_422(self):
        with self.assertRaises(HTTPException) as ctx:
            _normalize_tool_output("quiz", "totally not json")
        self.assertEqual(ctx.exception.status_code, 422)


if __name__ == "__main__":
    unittest.main()
