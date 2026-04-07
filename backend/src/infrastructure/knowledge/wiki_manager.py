"""WikiManager — CRUD layer for the LLM-Wiki persistent knowledge base.

Implements the Karpathy LLM-Wiki pattern:
  · Each tenant+notebook pair owns a wiki directory of Markdown pages.
  · Two special files are always present:
      - index.md  — a catalog of all pages with one-line summaries
      - log.md    — chronological, append-only ingest/query log
  · All other pages are entity/concept/topic pages created by the LLM.

Storage: local filesystem under ``WIKI_ROOT/<tenant_id>/<notebook_id>/``.
Each page is a plain ``.md`` file.  The wiki is just a directory of text —
no database, no vector store, no embedding.  The index is enough for the LLM
to navigate at moderate scale (~hundreds of pages).
"""

import logging
import os
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

WIKI_ROOT = Path(os.getenv("WIKI_ROOT", "wiki_store"))

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _wiki_dir(tenant_id: str, notebook_id: str | None = None) -> Path:
    """Return the wiki directory for a tenant (optionally scoped to a notebook)."""
    base = WIKI_ROOT / tenant_id
    if notebook_id:
        base = base / notebook_id
    else:
        base = base / "_global"
    return base


def _sanitize_page_name(name: str) -> str:
    """Convert an arbitrary string into a safe filename slug."""
    slug = re.sub(r"[^\w\s-]", "", name.lower())
    slug = re.sub(r"[\s_]+", "_", slug).strip("_")
    return slug[:120] or "untitled"


# ---------------------------------------------------------------------------
# WikiManager
# ---------------------------------------------------------------------------

class WikiManager:
    """CRUD manager for a single wiki instance (tenant + optional notebook)."""

    def __init__(self, tenant_id: str, notebook_id: str | None = None):
        self.tenant_id = tenant_id
        self.notebook_id = notebook_id
        self.root = _wiki_dir(tenant_id, notebook_id)
        self._ensure_scaffold()

    # -- bootstrap ----------------------------------------------------------

    def _ensure_scaffold(self) -> None:
        """Create the wiki directory and seed index/log if missing."""
        self.root.mkdir(parents=True, exist_ok=True)
        index_path = self.root / "index.md"
        log_path = self.root / "log.md"
        if not index_path.exists():
            index_path.write_text(
                "# Wiki Index\n\n"
                "This file catalogs every page in the wiki.\n\n"
                "| Page | Summary |\n"
                "|------|------|\n",
                encoding="utf-8",
            )
        if not log_path.exists():
            log_path.write_text(
                "# Wiki Log\n\n"
                "Chronological record of ingest and query events.\n\n",
                encoding="utf-8",
            )

    # -- page CRUD ----------------------------------------------------------

    def list_pages(self) -> list[dict]:
        """Return metadata for every ``.md`` page (excluding index/log)."""
        pages = []
        for f in sorted(self.root.glob("*.md")):
            if f.name in ("index.md", "log.md"):
                continue
            stat = f.stat()
            pages.append({
                "name": f.stem,
                "filename": f.name,
                "size_bytes": stat.st_size,
                "modified": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            })
        return pages

    def read_page(self, page_name: str) -> Optional[str]:
        """Read a wiki page by slug name.  Returns ``None`` if not found."""
        slug = _sanitize_page_name(page_name)
        path = self.root / f"{slug}.md"
        if not path.exists():
            return None
        return path.read_text(encoding="utf-8")

    def write_page(self, page_name: str, content: str, *, summary: str = "") -> str:
        """Create or overwrite a wiki page. Updates the index automatically."""
        slug = _sanitize_page_name(page_name)
        path = self.root / f"{slug}.md"
        path.write_text(content, encoding="utf-8")
        self._update_index_entry(slug, summary or page_name)
        return slug

    def append_page(self, page_name: str, content: str) -> str:
        """Append content to an existing page (or create it)."""
        slug = _sanitize_page_name(page_name)
        path = self.root / f"{slug}.md"
        existing = path.read_text(encoding="utf-8") if path.exists() else ""
        path.write_text(existing + "\n\n" + content, encoding="utf-8")
        return slug

    def delete_page(self, page_name: str) -> bool:
        """Delete a wiki page. Returns True if found and deleted."""
        slug = _sanitize_page_name(page_name)
        path = self.root / f"{slug}.md"
        if path.exists():
            path.unlink()
            self._remove_index_entry(slug)
            return True
        return False

    # -- index management ---------------------------------------------------

    def read_index(self) -> str:
        """Return the full contents of ``index.md``."""
        return (self.root / "index.md").read_text(encoding="utf-8")

    def _update_index_entry(self, slug: str, summary: str) -> None:
        """Add or update a row in the index table."""
        index_path = self.root / "index.md"
        text = index_path.read_text(encoding="utf-8")
        # Remove existing entry for this slug
        lines = text.splitlines()
        filtered = [ln for ln in lines if f"| [{slug}]" not in ln]
        entry = f"| [{slug}]({slug}.md) | {summary.replace('|', '-')} |"
        filtered.append(entry)
        index_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")

    def _remove_index_entry(self, slug: str) -> None:
        index_path = self.root / "index.md"
        text = index_path.read_text(encoding="utf-8")
        lines = text.splitlines()
        filtered = [ln for ln in lines if f"| [{slug}]" not in ln]
        index_path.write_text("\n".join(filtered) + "\n", encoding="utf-8")

    # -- log management -----------------------------------------------------

    def read_log(self) -> str:
        """Return the full contents of ``log.md``."""
        return (self.root / "log.md").read_text(encoding="utf-8")

    def append_log(self, event_type: str, detail: str) -> None:
        """Append a timestamped entry to the log."""
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        entry = f"## [{ts}] {event_type} | {detail}\n"
        log_path = self.root / "log.md"
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n" + entry)

    # -- search (index-based, no embeddings) --------------------------------

    def search_pages(self, query: str, *, max_results: int = 10) -> list[dict]:
        """Keyword search across all wiki pages. Returns matched snippets.

        This is intentionally simple (BM25-like word overlap) and avoids
        embedding infrastructure.  For wikis under ~500 pages the index
        file + keyword search is more than sufficient per Karpathy.
        """
        query_terms = set(query.lower().split())
        if not query_terms:
            return []

        results: list[tuple[float, dict]] = []
        for f in self.root.glob("*.md"):
            if f.name in ("index.md", "log.md"):
                continue
            text = f.read_text(encoding="utf-8").lower()
            words = set(text.split())
            if not words:
                continue
            overlap = len(query_terms & words)
            if overlap == 0:
                continue
            score = overlap / len(query_terms)
            # Extract a snippet around the first matching term
            snippet = self._extract_snippet(text, query_terms)
            results.append((score, {
                "page": f.stem,
                "filename": f.name,
                "score": round(score, 3),
                "snippet": snippet,
            }))

        results.sort(key=lambda x: x[0], reverse=True)
        return [r[1] for r in results[:max_results]]

    @staticmethod
    def _extract_snippet(text: str, terms: set[str], window: int = 200) -> str:
        """Find the first occurrence of any query term and return surrounding text."""
        for term in terms:
            idx = text.find(term)
            if idx >= 0:
                start = max(0, idx - window // 2)
                end = min(len(text), idx + window // 2)
                return text[start:end].replace("\n", " ").strip()
        return text[:window].replace("\n", " ").strip()

    # -- bulk read for LLM context ------------------------------------------

    def read_pages_for_context(self, page_names: list[str], *, max_chars: int = 12000) -> str:
        """Read multiple pages and concatenate into a single context string."""
        parts: list[str] = []
        total = 0
        for name in page_names:
            content = self.read_page(name)
            if content is None:
                continue
            if total + len(content) > max_chars:
                remaining = max_chars - total
                if remaining > 200:
                    parts.append(f"--- {name} (truncated) ---\n{content[:remaining]}")
                break
            parts.append(f"--- {name} ---\n{content}")
            total += len(content)
        return "\n\n".join(parts)
