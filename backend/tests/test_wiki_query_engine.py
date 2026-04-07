"""Tests for WikiQueryEngine — wiki-first retrieval with RAG fallback.

Covers:
  · Wiki-only retrieval when coverage is sufficient
  · RAG-fallback when wiki is empty or thin
  · Hybrid mode (wiki + RAG merged)
  · Coverage assessment logic
  · Context chunk format matches the standard RAG shape
  · retrieve_with_wiki convenience function
"""

import os
import shutil
import tempfile
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest

_test_wiki_root = Path(tempfile.mkdtemp(prefix="vidyaos_wiki_query_test_"))
os.environ["WIKI_ROOT"] = str(_test_wiki_root)

from src.infrastructure.knowledge.wiki_manager import WikiManager
from src.infrastructure.knowledge.wiki_query_engine import (
    WikiQueryEngine,
    retrieve_with_wiki,
    WIKI_CONFIDENCE_THRESHOLD,
    WIKI_SCORE_THRESHOLD,
)


@pytest.fixture(autouse=True)
def clean_wiki():
    yield
    for child in _test_wiki_root.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)


def _seed_wiki(tenant: str, nb: str, pages: dict[str, str]):
    """Helper to seed wiki pages for testing."""
    wm = WikiManager(tenant, nb)
    for name, content in pages.items():
        wm.write_page(name, content, summary=name)
    return wm


class TestCoverageAssessment:
    """_assess_wiki_coverage returns 'sufficient' or 'insufficient'."""

    def test_empty_hits_is_insufficient(self):
        engine = WikiQueryEngine("t1", "nb")
        assert engine._assess_wiki_coverage([]) == "insufficient"

    def test_few_low_score_hits_is_insufficient(self):
        engine = WikiQueryEngine("t1", "nb")
        hits = [{"score": 0.1}]
        assert engine._assess_wiki_coverage(hits) == "insufficient"

    def test_enough_high_score_hits_is_sufficient(self):
        engine = WikiQueryEngine("t1", "nb")
        hits = [{"score": 0.8}, {"score": 0.7}, {"score": 0.6}]
        assert engine._assess_wiki_coverage(hits) == "sufficient"


class TestWikiOnlyRetrieval:
    """When wiki has sufficient coverage, RAG is not called."""

    @pytest.mark.asyncio
    async def test_wiki_only_when_coverage_sufficient(self):
        _seed_wiki("t2", "nb", {
            "photosynthesis": "# Photosynthesis\n\nPlants convert sunlight into glucose. Chlorophyll absorbs light.",
            "chloroplast": "# Chloroplast\n\nOrganelle where photosynthesis occurs. Contains chlorophyll.",
            "sunlight": "# Sunlight\n\nElectromagnetic radiation from the sun powers photosynthesis.",
        })

        engine = WikiQueryEngine("t2", "nb")

        with patch.object(engine, "_rag_fallback", new_callable=AsyncMock) as mock_rag:
            result = await engine.query("photosynthesis chlorophyll sunlight")

        # RAG should NOT have been called
        mock_rag.assert_not_called()
        assert result["source"] == "wiki"
        assert len(result["wiki_results"]) >= WIKI_CONFIDENCE_THRESHOLD
        assert len(result["context_chunks"]) > 0


class TestRAGFallback:
    """When wiki is empty, engine falls back to RAG."""

    @pytest.mark.asyncio
    async def test_rag_fallback_when_wiki_empty(self):
        engine = WikiQueryEngine("t3", "nb_empty")

        mock_rag_chunks = [
            {"text": "RAG chunk 1", "citation": "[doc1_p1]", "source": "doc1", "page": "1",
             "section": "", "score": 0.9, "vector_score": 0.9, "rerank_score": 0.9,
             "document_id": "d1", "compressed": False},
        ]

        with patch.object(engine, "_rag_fallback", new_callable=AsyncMock, return_value=mock_rag_chunks):
            result = await engine.query("quantum mechanics")

        assert result["source"] == "rag"
        assert len(result["rag_results"]) == 1
        assert result["context_chunks"][0]["text"] == "RAG chunk 1"


class TestHybridRetrieval:
    """When wiki has some coverage but not enough, both sources merge."""

    @pytest.mark.asyncio
    async def test_hybrid_when_wiki_partially_covers(self):
        # Seed with just ONE page — below the confidence threshold
        _seed_wiki("t4", "nb", {
            "gravity": "# Gravity\n\nNewton discovered gravity. Apples fall down.",
        })

        engine = WikiQueryEngine("t4", "nb")

        mock_rag_chunks = [
            {"text": "RAG: Einstein's general relativity", "citation": "[rel_p1]",
             "source": "relativity.pdf", "page": "1", "section": "", "score": 0.85,
             "vector_score": 0.85, "rerank_score": 0.85, "document_id": "d2", "compressed": False},
        ]

        with patch.object(engine, "_rag_fallback", new_callable=AsyncMock, return_value=mock_rag_chunks):
            result = await engine.query("gravity newton apples")

        assert result["source"] == "hybrid"
        assert len(result["wiki_results"]) >= 1
        assert len(result["rag_results"]) >= 1
        # Context should have chunks from both
        sources = {c.get("wiki_source", False) for c in result["context_chunks"]}
        assert True in sources or len(result["context_chunks"]) > 1


class TestContextChunkFormat:
    """Wiki chunks match the standard RAG context format."""

    @pytest.mark.asyncio
    async def test_wiki_chunks_have_standard_fields(self):
        _seed_wiki("t5", "nb", {
            "concept_a": "A is for apple. A is a vowel. Apples are fruit.",
            "concept_b": "B is for bee. Bees make honey. Bees are insects.",
            "concept_c": "C is for cat. Cats are pets. Cats purr when happy.",
        })

        engine = WikiQueryEngine("t5", "nb")
        with patch.object(engine, "_rag_fallback", new_callable=AsyncMock, return_value=[]):
            result = await engine.query("apple vowel fruit bees honey cats pets")

        for chunk in result["context_chunks"]:
            assert "text" in chunk
            assert "citation" in chunk
            assert "source" in chunk
            assert "score" in chunk
            assert "compressed" in chunk


class TestConvenienceFunction:
    """retrieve_with_wiki provides a drop-in API."""

    @pytest.mark.asyncio
    async def test_retrieve_with_wiki_returns_list(self):
        _seed_wiki("t6", "nb", {"topic": "Some topic content with keywords."})

        with patch(
            "src.infrastructure.knowledge.wiki_query_engine.WikiQueryEngine._rag_fallback",
            new_callable=AsyncMock,
            return_value=[],
        ):
            chunks = await retrieve_with_wiki("topic keywords", "t6", notebook_id="nb")
        assert isinstance(chunks, list)
