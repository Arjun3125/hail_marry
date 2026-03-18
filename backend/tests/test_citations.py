"""Tests for clickable citation linker."""
import pytest
from src.domains.ai_engine.ai.citation_linker import _parse_citation_string, _format_citation_text


# ── Citation parsing ──

def test_parse_simple_citation():
    result = _parse_citation_string("notes.pdf, p.3")
    assert result["source"] == "notes.pdf"
    assert result["page"] == "3"


def test_parse_citation_with_brackets():
    result = _parse_citation_string("[biology.pdf, p.12]")
    assert result["source"] == "biology.pdf"
    assert result["page"] == "12"


def test_parse_citation_no_page():
    result = _parse_citation_string("textbook.pdf")
    assert result["source"] == "textbook.pdf"
    assert result["page"] == ""


def test_parse_citation_page_word():
    result = _parse_citation_string("notes.pdf page 5")
    assert result["page"] == "5"


def test_parse_citation_colon_page():
    result = _parse_citation_string("document.pdf:7")
    assert result["page"] == "7"


# ── Citation formatting ──

def test_format_with_page():
    text = _format_citation_text("notes.pdf", "3")
    assert text == "[notes.pdf, p.3]"


def test_format_without_page():
    text = _format_citation_text("textbook.pdf", "")
    assert text == "[textbook.pdf]"


# ── Enrichment structure ──

def test_enriched_citation_structure():
    """Enriched citations should have correct keys."""
    citation = {
        "text": "[notes.pdf, p.3]",
        "source": "notes.pdf",
        "document_id": "abc-123",
        "page": "3",
        "url": "/api/documents/abc-123/view#page=3",
        "clickable": True,
    }
    assert citation["clickable"] is True
    assert "#page=3" in citation["url"]


def test_non_clickable_citation():
    """Citations without matching documents should not be clickable."""
    citation = {
        "text": "[unknown.pdf]",
        "source": "unknown.pdf",
        "document_id": None,
        "page": None,
        "url": None,
        "clickable": False,
    }
    assert citation["clickable"] is False
    assert citation["url"] is None
