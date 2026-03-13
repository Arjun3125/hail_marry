"""Citation linker — enriches raw citations with document URLs and page numbers.

Transforms plain-text citations like "[notes.pdf, p.3]" into clickable
structured objects with document IDs and viewer URLs.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.orm import Session

from models.document import Document


def enrich_citations(
    citations: list[dict | str],
    tenant_id: UUID,
    db: Session,
) -> list[dict]:
    """Enrich raw citations with document metadata and clickable URLs.

    Input formats supported:
    - String: "notes.pdf, p.3"
    - Dict: {"source": "notes.pdf", "page": "3"}

    Returns structured citation objects with:
    - text: display text
    - document_id: UUID of the source document
    - page: page number (if available)
    - url: clickable URL to view the document at that page
    """
    enriched = []

    for citation in citations:
        # Normalize to dict
        if isinstance(citation, str):
            parsed = _parse_citation_string(citation)
        elif isinstance(citation, dict):
            parsed = citation
        else:
            continue

        source_name = parsed.get("source", "")
        page = parsed.get("page", "")

        # Look up document by filename
        doc = None
        if source_name:
            doc = db.query(Document).filter(
                Document.tenant_id == tenant_id,
                Document.file_name.ilike(f"%{source_name}%"),
            ).first()

        doc_id = str(doc.id) if doc else None
        url = None
        if doc_id:
            url = f"/api/documents/{doc_id}/view"
            if page:
                url += f"#page={page}"

        enriched.append({
            "text": _format_citation_text(source_name, page),
            "source": source_name,
            "document_id": doc_id,
            "page": str(page) if page else None,
            "url": url,
            "clickable": url is not None,
        })

    return enriched


def _parse_citation_string(citation: str) -> dict:
    """Parse a citation string like 'notes.pdf, p.3' into components."""
    import re

    # Try to extract filename and page
    # Patterns: "[source, p.N]", "source (page N)", "source:N"
    page = ""
    source = citation.strip().strip("[]")

    # Extract page number
    page_match = re.search(r'(?:p\.?\s*|page\s*|:\s*)(\d+)', source, re.IGNORECASE)
    if page_match:
        page = page_match.group(1)
        source = source[:page_match.start()].strip().rstrip(",").strip()

    return {"source": source, "page": page}


def _format_citation_text(source: str, page: str) -> str:
    """Format a citation for display."""
    if page:
        return f"[{source}, p.{page}]"
    return f"[{source}]"


def make_citations_clickable(ai_response: dict, tenant_id: UUID, db: Session) -> dict:
    """Post-process an AI response to make all citations clickable.

    Modifies the 'citations' field in-place and returns the updated response.
    """
    raw_citations = ai_response.get("citations", [])
    if raw_citations:
        ai_response["citations"] = enrich_citations(raw_citations, tenant_id, db)
    return ai_response
