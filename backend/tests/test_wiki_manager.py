"""Tests for WikiManager — the Karpathy LLM-Wiki CRUD layer.

Covers:
  · Scaffold creation (index.md, log.md)
  · Page CRUD (create, read, update, append, delete)
  · Index auto-update on write/delete
  · Log append
  · Keyword search with snippets
  · Bulk page reads for LLM context
  · Slug sanitization edge cases
"""

import os
import shutil
import tempfile
from pathlib import Path

import pytest

# Patch WIKI_ROOT before importing so tests use a temp directory
_test_wiki_root = Path(tempfile.mkdtemp(prefix="vidyaos_wiki_test_"))
os.environ["WIKI_ROOT"] = str(_test_wiki_root)

from src.infrastructure.knowledge.wiki_manager import WikiManager, _sanitize_page_name


@pytest.fixture(autouse=True)
def clean_wiki_root():
    """Ensure a clean wiki root for each test."""
    yield
    # Clean up after each test
    for child in _test_wiki_root.iterdir():
        if child.is_dir():
            shutil.rmtree(child, ignore_errors=True)


class TestScaffold:
    """WikiManager bootstraps index.md and log.md on first init."""

    def test_scaffold_creates_index_and_log(self):
        wm = WikiManager("tenant_a", "nb_1")
        assert (wm.root / "index.md").exists()
        assert (wm.root / "log.md").exists()

    def test_scaffold_is_idempotent(self):
        wm1 = WikiManager("tenant_a", "nb_2")
        (wm1.root / "index.md").write_text("custom", encoding="utf-8")
        wm2 = WikiManager("tenant_a", "nb_2")
        # Should NOT overwrite the custom content
        assert wm2.read_index() == "custom"

    def test_global_wiki_uses_global_dir(self):
        wm = WikiManager("tenant_b")
        assert "_global" in str(wm.root)


class TestPageCRUD:
    """Page create, read, append, delete."""

    def test_write_and_read_page(self):
        wm = WikiManager("t1", "nb")
        slug = wm.write_page("Photosynthesis", "# Photosynthesis\n\nPlants make food.", summary="Biology concept")
        assert slug == "photosynthesis"
        content = wm.read_page("Photosynthesis")
        assert "Plants make food" in content

    def test_read_missing_page_returns_none(self):
        wm = WikiManager("t1", "nb2")
        assert wm.read_page("does_not_exist") is None

    def test_append_page(self):
        wm = WikiManager("t1", "nb3")
        wm.write_page("topic", "First version.")
        wm.append_page("topic", "Second paragraph.")
        content = wm.read_page("topic")
        assert "First version." in content
        assert "Second paragraph." in content

    def test_delete_page(self):
        wm = WikiManager("t1", "nb4")
        wm.write_page("obsolete", "Old stuff.")
        assert wm.delete_page("obsolete") is True
        assert wm.read_page("obsolete") is None

    def test_delete_nonexistent_returns_false(self):
        wm = WikiManager("t1", "nb5")
        assert wm.delete_page("ghost") is False

    def test_list_pages_excludes_index_and_log(self):
        wm = WikiManager("t1", "nb6")
        wm.write_page("alpha", "A.")
        wm.write_page("beta", "B.")
        pages = wm.list_pages()
        names = [p["name"] for p in pages]
        assert "alpha" in names
        assert "beta" in names
        assert "index" not in names
        assert "log" not in names


class TestIndexManagement:
    """Index is auto-updated on write and delete."""

    def test_write_adds_index_entry(self):
        wm = WikiManager("t2", "nb")
        wm.write_page("Gravity", "Force of attraction.", summary="Physics concept")
        index = wm.read_index()
        assert "[gravity]" in index
        assert "Physics concept" in index

    def test_delete_removes_index_entry(self):
        wm = WikiManager("t2", "nb2")
        wm.write_page("temp", "Temporary.", summary="Temp")
        wm.delete_page("temp")
        index = wm.read_index()
        assert "[temp]" not in index


class TestLog:
    """Log append creates timestamped entries."""

    def test_append_log(self):
        wm = WikiManager("t3", "nb")
        wm.append_log("ingest", "chapter_1.pdf — 5 pages created")
        log = wm.read_log()
        assert "ingest" in log
        assert "chapter_1.pdf" in log


class TestSearch:
    """Keyword search across wiki pages."""

    def test_search_finds_matching_pages(self):
        wm = WikiManager("t4", "nb")
        wm.write_page("cell_biology", "Cells are the basic unit of life. Mitochondria is the powerhouse.")
        wm.write_page("chemistry", "Atoms and molecules form chemical bonds.")
        results = wm.search_pages("mitochondria powerhouse")
        assert len(results) >= 1
        assert results[0]["page"] == "cell_biology"

    def test_search_returns_empty_for_no_match(self):
        wm = WikiManager("t4", "nb2")
        wm.write_page("math", "Algebra and calculus.")
        results = wm.search_pages("quantum entanglement")
        assert results == []

    def test_search_respects_max_results(self):
        wm = WikiManager("t4", "nb3")
        for i in range(20):
            wm.write_page(f"page_{i}", f"Common keyword repeated page {i}.")
        results = wm.search_pages("common keyword", max_results=5)
        assert len(results) <= 5


class TestBulkRead:
    """read_pages_for_context returns concatenated content."""

    def test_bulk_read(self):
        wm = WikiManager("t5", "nb")
        wm.write_page("a", "Content A.")
        wm.write_page("b", "Content B.")
        context = wm.read_pages_for_context(["a", "b"])
        assert "Content A" in context
        assert "Content B" in context

    def test_bulk_read_respects_max_chars(self):
        wm = WikiManager("t5", "nb2")
        wm.write_page("big", "x" * 20000)
        context = wm.read_pages_for_context(["big"], max_chars=500)
        assert len(context) <= 600  # allow small overhead


class TestSlugSanitization:
    """Edge cases in page name → slug conversion."""

    def test_special_characters_stripped(self):
        assert _sanitize_page_name("Hello World!@#") == "hello_world"

    def test_empty_string_returns_untitled(self):
        assert _sanitize_page_name("") == "untitled"

    def test_long_names_truncated(self):
        long_name = "a" * 200
        assert len(_sanitize_page_name(long_name)) <= 120
