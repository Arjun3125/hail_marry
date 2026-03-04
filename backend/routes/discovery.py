"""Source Discovery — web search and URL ingestion for teachers."""
import httpx
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
import uuid

from auth.dependencies import get_current_user
from models.user import User
from database import get_db
from ai.ingestion import ingest_document, Chunk

router = APIRouter(prefix="/api/ai", tags=["AI Discovery"])


class DiscoverRequest(BaseModel):
    query: str
    max_results: int = 8


class IngestURLRequest(BaseModel):
    url: str
    title: str = ""
    subject_id: Optional[str] = None


def strip_html(html: str) -> str:
    """Remove HTML tags and decode entities, returning plain text."""
    text = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"&nbsp;", " ", text)
    text = re.sub(r"&amp;", "&", text)
    text = re.sub(r"&lt;", "<", text)
    text = re.sub(r"&gt;", ">", text)
    text = re.sub(r"&#\d+;", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


@router.post("/discover-sources")
async def discover_sources(
    request: DiscoverRequest,
    current_user: User = Depends(get_current_user),
):
    """Search the web for educational resources using DuckDuckGo HTML search."""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Only teachers and admins can discover sources")

    results = []
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Use DuckDuckGo HTML endpoint (no API key needed)
            response = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": f"{request.query} site:ncert.nic.in OR site:wikipedia.org OR filetype:pdf education"},
                headers={"User-Agent": "Mozilla/5.0 (educational research bot)"},
            )
            if response.status_code == 200:
                html = response.text
                # Parse results from DuckDuckGo HTML
                result_blocks = re.findall(
                    r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
                    r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                    html,
                    re.DOTALL,
                )
                for url, title, snippet in result_blocks[:request.max_results]:
                    clean_title = strip_html(title)
                    clean_snippet = strip_html(snippet)
                    # DuckDuckGo wraps URLs through redirect
                    actual_url = url
                    if "uddg=" in url:
                        import urllib.parse
                        parsed = urllib.parse.parse_qs(urllib.parse.urlparse(url).query)
                        actual_url = parsed.get("uddg", [url])[0]
                    results.append({
                        "title": clean_title,
                        "url": actual_url,
                        "snippet": clean_snippet,
                    })
    except Exception:
        # Fallback: return empty results gracefully
        pass

    return {"results": results, "query": request.query, "count": len(results)}


@router.post("/ingest-url")
async def ingest_url(
    request: IngestURLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Fetch a web URL, extract text, and ingest into the vector store."""
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Only teachers and admins can ingest sources")

    # Fetch the URL content
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(
                request.url,
                headers={"User-Agent": "Mozilla/5.0 (educational content ingestion)"},
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch URL (HTTP {response.status_code})")
            content = response.text
    except httpx.ConnectError:
        raise HTTPException(status_code=400, detail="Cannot connect to URL")
    except httpx.TimeoutException:
        raise HTTPException(status_code=400, detail="URL request timed out")

    # Extract text from HTML
    text = strip_html(content)
    if len(text) < 50:
        raise HTTPException(status_code=422, detail="Not enough text content found at this URL")

    # Truncate to reasonable size for ingestion
    text = text[:50000]

    title = request.title or request.url.split("/")[-1][:100] or "Web Source"
    doc_id = str(uuid.uuid4())

    # Create pages-like structure for the chunker
    pages = [{"page_number": 1, "text": text}]

    from ai.ingestion import hierarchical_chunk
    chunks = hierarchical_chunk(
        pages=pages,
        document_id=doc_id,
        tenant_id=str(current_user.tenant_id),
        source_file=title,
        subject_id=request.subject_id,
    )

    # Embed and store chunks
    if chunks:
        try:
            from ai.embeddings import embed_chunks
            from ai.vector_store import store_chunks
            embedded = await embed_chunks(chunks)
            store_chunks(embedded, tenant_id=str(current_user.tenant_id))
        except ImportError:
            pass  # Embedding modules may not be available in all environments

    return {
        "status": "ingested",
        "document_id": doc_id,
        "title": title,
        "url": request.url,
        "chunks_created": len(chunks),
        "text_length": len(text),
    }
