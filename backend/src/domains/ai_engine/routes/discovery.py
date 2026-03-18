"""Source discovery and queued URL ingestion for teachers."""
import httpx
import re
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from src.domains.ai_engine.ai.discovery_workflows import strip_html
from auth.dependencies import get_current_user
from database import get_db
from src.domains.identity.models.user import User
from src.domains.ai_engine.schemas.ai_runtime import IngestURLRequest, InternalIngestURLRequest
from src.domains.ai_engine.services.ai_queue import JOB_TYPE_URL_INGEST, enqueue_job

router = APIRouter(prefix="/api/ai", tags=["AI Discovery"])


class DiscoverRequest(BaseModel):
    query: str
    max_results: int = 8


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
            response = await client.get(
                "https://html.duckduckgo.com/html/",
                params={"q": f"{request.query} site:ncert.nic.in OR site:wikipedia.org OR filetype:pdf education"},
                headers={"User-Agent": "Mozilla/5.0 (educational research bot)"},
            )
            if response.status_code == 200:
                html = response.text
                result_blocks = re.findall(
                    r'<a[^>]*class="result__a"[^>]*href="([^"]*)"[^>]*>(.*?)</a>.*?'
                    r'<a[^>]*class="result__snippet"[^>]*>(.*?)</a>',
                    html,
                    re.DOTALL,
                )
                for url, title, snippet in result_blocks[:request.max_results]:
                    clean_title = strip_html(title)
                    clean_snippet = strip_html(snippet)
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
        pass

    return {"results": results, "query": request.query, "count": len(results)}


@router.post("/ingest-url")
async def ingest_url(
    request: IngestURLRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Queue a URL ingestion job for background embedding and storage."""
    _ = db
    if current_user.role not in ("teacher", "admin"):
        raise HTTPException(status_code=403, detail="Only teachers and admins can ingest sources")

    payload = InternalIngestURLRequest(
        **request.model_dump(),
        tenant_id=str(current_user.tenant_id),
    )
    return enqueue_job(
        JOB_TYPE_URL_INGEST,
        payload.model_dump(),
        tenant_id=str(current_user.tenant_id),
        user_id=str(current_user.id),
    )
