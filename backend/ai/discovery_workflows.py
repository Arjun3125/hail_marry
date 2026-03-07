"""Discovery and URL-ingestion workflows for queued execution."""
from __future__ import annotations

import re
import socket
import ipaddress
import uuid
from urllib.parse import urlparse

import httpx
from fastapi import HTTPException

from ai.ingestion import hierarchical_chunk
from ai.providers import get_embedding_provider, get_vector_store_provider
from schemas.ai_runtime import InternalIngestURLRequest


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


def is_safe_url(url: str) -> bool:
    """Validate that the URL resolves to a public, globally-routable IP to prevent SSRF."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
            
        ip_str = socket.gethostbyname(hostname)
        ip = ipaddress.ip_address(ip_str)
        
        if ip.is_private or ip.is_loopback or ip.is_link_local or ip.is_reserved or not ip.is_global:
            return False
        return True
    except Exception:
        return False


async def execute_url_ingestion(request: InternalIngestURLRequest) -> dict:
    if not is_safe_url(request.url):
        raise HTTPException(status_code=403, detail="URL ingestion rejected. Destination must be a public IP.")
        
    try:
        async with httpx.AsyncClient(timeout=20.0, follow_redirects=True) as client:
            response = await client.get(
                request.url,
                headers={"User-Agent": "Mozilla/5.0 (educational content ingestion)"},
            )
            if response.status_code != 200:
                raise HTTPException(status_code=400, detail=f"Failed to fetch URL (HTTP {response.status_code})")
            content = response.text
    except httpx.ConnectError as exc:
        raise HTTPException(status_code=400, detail="Cannot connect to URL") from exc
    except httpx.TimeoutException as exc:
        raise HTTPException(status_code=400, detail="URL request timed out") from exc

    text = strip_html(content)
    if len(text) < 50:
        raise HTTPException(status_code=422, detail="Not enough text content found at this URL")

    text = text[:50000]
    title = request.title or request.url.split("/")[-1][:100] or "Web Source"
    doc_id = str(uuid.uuid4())
    pages = [{"page_number": 1, "text": text}]

    chunks = hierarchical_chunk(
        pages=pages,
        document_id=doc_id,
        tenant_id=request.tenant_id,
        source_file=title,
        subject_id=request.subject_id,
    )
    if not chunks:
        raise HTTPException(status_code=422, detail="No chunks could be created from the URL content")

    try:
        texts = [chunk.text for chunk in chunks]
        embeddings = await get_embedding_provider().embed_batch(texts)
        store = get_vector_store_provider(request.tenant_id)
        chunk_dicts = [{
            "text": chunk.text,
            "document_id": chunk.document_id,
            "page_number": chunk.page_number,
            "section_title": chunk.section_title or "",
            "subject_id": chunk.subject_id or "",
            "source_file": chunk.source_file or "",
        } for chunk in chunks]
        store.add_chunks(chunk_dicts, embeddings)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Failed to embed and store discovered content: {exc}") from exc

    return {
        "status": "ingested",
        "document_id": doc_id,
        "title": title,
        "url": request.url,
        "chunks_created": len(chunks),
        "text_length": len(text),
    }
