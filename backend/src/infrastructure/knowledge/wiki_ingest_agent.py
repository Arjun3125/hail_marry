"""Wiki Ingest Agent — reads source documents and updates wiki pages.

When a new document is ingested into VidyaOS, this agent:
  1. Reads the raw text (already extracted by the ingestion pipeline).
  2. Uses the configured LLM to extract key concepts, entities, and summaries.
  3. Creates/updates wiki pages for each concept.
  4. Updates ``index.md`` and appends to ``log.md``.

The agent is *incremental*: it merges new knowledge into existing pages
rather than overwriting them, so the wiki compounds over time.
"""

import json
import logging
from typing import Optional

from src.infrastructure.knowledge.wiki_manager import WikiManager

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# LLM extraction prompt
# ---------------------------------------------------------------------------

EXTRACT_PROMPT = """\
You are a knowledge curator. Given the following source document, extract the key
information and produce a structured JSON response.

SOURCE DOCUMENT:
---
{document_text}
---

Respond with valid JSON containing:
{{
  "title": "A concise title for this source",
  "summary": "A 2-3 sentence summary of the source",
  "concepts": [
    {{
      "name": "Concept or entity name",
      "description": "One-paragraph description",
      "related_concepts": ["list", "of", "related", "concept names"]
    }}
  ],
  "key_facts": [
    "Important facts extracted from the document"
  ]
}}

Rules:
- Extract 3-10 concepts depending on document richness.
- Use clear, canonical names for concepts (e.g. "Photosynthesis" not "the process").
- Include cross-references in related_concepts.
- Be factual; do not hallucinate information not in the source.
"""

UPDATE_PAGE_PROMPT = """\
You are maintaining a wiki page about "{concept_name}".

EXISTING PAGE CONTENT:
---
{existing_content}
---

NEW INFORMATION FROM A RECENTLY INGESTED SOURCE:
---
{new_info}
---

Write an updated version of the wiki page that:
1. Preserves all existing information that is still accurate.
2. Integrates the new information naturally.
3. Notes any contradictions between old and new information.
4. Maintains clear markdown formatting with headers and bullet points.
5. Keeps cross-references to related concepts in [[double brackets]].

Return ONLY the updated markdown page content, nothing else.
"""


# ---------------------------------------------------------------------------
# WikiIngestAgent
# ---------------------------------------------------------------------------

class WikiIngestAgent:
    """Agent that processes a raw document and updates the wiki."""

    def __init__(
        self,
        wiki: WikiManager,
        llm_provider=None,
    ):
        self.wiki = wiki
        self._llm = llm_provider

    async def _get_llm(self):
        """Lazy-load the LLM provider."""
        if self._llm is None:
            try:
                from src.infrastructure.llm.providers import get_llm_provider
                self._llm = get_llm_provider()
            except Exception:
                logger.warning("LLM provider unavailable — wiki ingest will use passthrough mode")
        return self._llm

    # -- public entry point --------------------------------------------------

    async def ingest_document(
        self,
        document_text: str,
        source_name: str,
        document_id: str | None = None,
    ) -> dict:
        """Process a document and update the wiki.

        Returns a summary dict with counts of pages created/updated.
        """
        llm = await self._get_llm()

        if llm is None:
            # Passthrough mode: store the raw text as a single page
            return self._passthrough_ingest(document_text, source_name, document_id)

        # Step 1: extract concepts via LLM
        extraction = await self._extract_concepts(document_text, llm)

        if not extraction:
            return self._passthrough_ingest(document_text, source_name, document_id)

        pages_created = 0
        pages_updated = 0

        # Step 2: upsert a source summary page
        title = extraction.get("title", source_name)
        summary = extraction.get("summary", "")
        key_facts = extraction.get("key_facts", [])

        source_page_content = f"# {title}\n\n{summary}\n\n"
        if key_facts:
            source_page_content += "## Key Facts\n\n"
            for fact in key_facts:
                source_page_content += f"- {fact}\n"

        source_slug = self.wiki.write_page(
            f"source_{source_name}",
            source_page_content,
            summary=summary[:120],
        )
        pages_created += 1

        # Step 3: upsert concept pages
        for concept in extraction.get("concepts", []):
            name = concept.get("name", "")
            if not name:
                continue

            existing = self.wiki.read_page(name)
            if existing:
                # Update existing page with new information
                updated = await self._update_concept_page(
                    name, existing, concept, llm
                )
                self.wiki.write_page(name, updated, summary=concept.get("description", "")[:120])
                pages_updated += 1
            else:
                # Create new concept page
                content = self._build_concept_page(concept, source_name)
                self.wiki.write_page(name, content, summary=concept.get("description", "")[:120])
                pages_created += 1

        # Step 4: log the ingest
        self.wiki.append_log(
            "ingest",
            f"{source_name} — {pages_created} pages created, {pages_updated} updated",
        )

        return {
            "source": source_name,
            "document_id": document_id,
            "pages_created": pages_created,
            "pages_updated": pages_updated,
            "concepts_extracted": len(extraction.get("concepts", [])),
        }

    # -- LLM interaction -----------------------------------------------------

    async def _extract_concepts(self, document_text: str, llm) -> dict | None:
        """Use the LLM to extract structured concepts from raw text."""
        # Truncate very long documents to avoid token limits
        truncated = document_text[:8000]
        prompt = EXTRACT_PROMPT.format(document_text=truncated)

        try:
            response = await llm.generate(prompt)
            text = response if isinstance(response, str) else str(response)
            # Try to parse JSON from the response
            # Strip markdown code fences if present
            text = text.strip()
            if text.startswith("```"):
                text = text.split("\n", 1)[1] if "\n" in text else text[3:]
            if text.endswith("```"):
                text = text[:-3]
            text = text.strip()
            if text.startswith("json"):
                text = text[4:].strip()
            return json.loads(text)
        except (json.JSONDecodeError, Exception) as exc:
            logger.warning("LLM concept extraction failed: %s", exc)
            return None

    async def _update_concept_page(
        self, concept_name: str, existing_content: str, new_concept: dict, llm
    ) -> str:
        """Use the LLM to merge new information into an existing concept page."""
        new_info = (
            f"Description: {new_concept.get('description', '')}\n"
            f"Related: {', '.join(new_concept.get('related_concepts', []))}"
        )
        prompt = UPDATE_PAGE_PROMPT.format(
            concept_name=concept_name,
            existing_content=existing_content[:4000],
            new_info=new_info,
        )
        try:
            response = await llm.generate(prompt)
            return response if isinstance(response, str) else str(response)
        except Exception as exc:
            logger.warning("LLM page update failed for %s: %s", concept_name, exc)
            # Fallback: just append
            return existing_content + f"\n\n## Update\n\n{new_info}"

    # -- helpers -------------------------------------------------------------

    @staticmethod
    def _build_concept_page(concept: dict, source_name: str) -> str:
        """Build a new concept page from structured extraction."""
        name = concept.get("name", "Untitled")
        desc = concept.get("description", "")
        related = concept.get("related_concepts", [])

        lines = [f"# {name}", "", desc, ""]
        if related:
            lines.append("## Related Concepts")
            lines.append("")
            for r in related:
                lines.append(f"- [[{r}]]")
            lines.append("")
        lines.append(f"---\n*First sourced from: {source_name}*")
        return "\n".join(lines)

    def _passthrough_ingest(self, text: str, source_name: str, document_id: str | None) -> dict:
        """Fallback: store raw text directly as a page (no LLM available)."""
        content = f"# {source_name}\n\n{text[:6000]}"
        self.wiki.write_page(f"source_{source_name}", content, summary=source_name)
        self.wiki.append_log("ingest_passthrough", source_name)
        return {
            "source": source_name,
            "document_id": document_id,
            "pages_created": 1,
            "pages_updated": 0,
            "concepts_extracted": 0,
            "mode": "passthrough",
        }
