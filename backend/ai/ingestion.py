"""
Document Ingestion Service
Handles PDF, DOCX, and YouTube transcript parsing with hierarchical chunking.
"""
import re
from pathlib import Path
from typing import List, Dict, Optional
from dataclasses import dataclass, field


@dataclass
class Chunk:
    """A single document chunk with metadata."""
    text: str
    chunk_id: int
    document_id: str
    tenant_id: str
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    subject_id: Optional[str] = None
    class_id: Optional[str] = None
    source_file: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


def extract_text_from_pdf(file_path: str) -> List[Dict]:
    """Extract text from PDF with page tracking."""
    try:
        import fitz  # PyMuPDF
    except ImportError:
        raise ImportError("PyMuPDF not installed. Run: pip install PyMuPDF")

    doc = fitz.open(file_path)
    pages = []
    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text")
        if text.strip():
            pages.append({
                "text": text.strip(),
                "page_number": page_num + 1,
            })
    doc.close()
    return pages


def extract_text_from_docx(file_path: str) -> List[Dict]:
    """Extract text from DOCX with paragraph tracking."""
    try:
        from docx import Document
    except ImportError:
        raise ImportError("python-docx not installed. Run: pip install python-docx")

    doc = Document(file_path)
    pages = []
    current_text = []
    current_section = ""

    for para in doc.paragraphs:
        text = para.text.strip()
        if not text:
            continue

        # Detect section headings
        if para.style.name.startswith("Heading"):
            if current_text:
                pages.append({
                    "text": "\n".join(current_text),
                    "page_number": len(pages) + 1,
                    "section_title": current_section,
                })
                current_text = []
            current_section = text
        current_text.append(text)

    if current_text:
        pages.append({
            "text": "\n".join(current_text),
            "page_number": len(pages) + 1,
            "section_title": current_section,
        })

    return pages


def extract_youtube_transcript(url: str) -> List[Dict]:
    """Extract transcript from YouTube video."""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except ImportError:
        raise ImportError("youtube-transcript-api not installed. Run: pip install youtube-transcript-api")

    # Extract video ID from URL
    video_id = None
    patterns = [
        r'(?:v=|/v/|youtu\.be/)([a-zA-Z0-9_-]{11})',
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            video_id = match.group(1)
            break

    if not video_id:
        raise ValueError(f"Could not extract video ID from URL: {url}")

    transcript = YouTubeTranscriptApi.get_transcript(video_id)

    # Group transcript into ~300 word segments
    segments = []
    current_text = []
    current_start = 0
    word_count = 0

    for entry in transcript:
        words = entry["text"].split()
        word_count += len(words)
        current_text.append(entry["text"])

        if word_count >= 250:
            segments.append({
                "text": " ".join(current_text),
                "page_number": len(segments) + 1,
                "section_title": f"Segment {len(segments) + 1} ({int(current_start)}s)",
            })
            current_text = []
            word_count = 0
            current_start = entry["start"]

    if current_text:
        segments.append({
            "text": " ".join(current_text),
            "page_number": len(segments) + 1,
            "section_title": f"Segment {len(segments) + 1}",
        })

    return segments


def hierarchical_chunk(
    pages: List[Dict],
    document_id: str,
    tenant_id: str,
    source_file: str = "",
    subject_id: str = None,
    class_id: str = None,
    chunk_size: int = 400,
    chunk_overlap: int = 80,
) -> List[Chunk]:
    """
    Split pages into overlapping chunks of ~chunk_size tokens.
    Preserves page numbers and section titles.
    """
    chunks = []
    chunk_id = 0

    for page_data in pages:
        text = page_data["text"]
        page_num = page_data.get("page_number")
        section = page_data.get("section_title", "")

        # Split by sentences first
        sentences = re.split(r'(?<=[.!?])\s+', text)
        current_chunk = []
        current_len = 0

        for sentence in sentences:
            word_count = len(sentence.split())

            if current_len + word_count > chunk_size and current_chunk:
                # Emit chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    document_id=document_id,
                    tenant_id=tenant_id,
                    page_number=page_num,
                    section_title=section,
                    subject_id=subject_id,
                    class_id=class_id,
                    source_file=source_file,
                    metadata={
                        "word_count": len(chunk_text.split()),
                        "page": page_num,
                        "section": section,
                    },
                ))
                chunk_id += 1

                # Overlap: keep last N words
                overlap_words = " ".join(current_chunk).split()[-chunk_overlap:]
                current_chunk = [" ".join(overlap_words)]
                current_len = len(overlap_words)

            current_chunk.append(sentence)
            current_len += word_count

        # Emit final chunk for this page
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            if len(chunk_text.split()) > 20:  # Skip tiny fragments
                chunks.append(Chunk(
                    text=chunk_text,
                    chunk_id=chunk_id,
                    document_id=document_id,
                    tenant_id=tenant_id,
                    page_number=page_num,
                    section_title=section,
                    subject_id=subject_id,
                    class_id=class_id,
                    source_file=source_file,
                    metadata={
                        "word_count": len(chunk_text.split()),
                        "page": page_num,
                        "section": section,
                    },
                ))
                chunk_id += 1

    return chunks


def ingest_document(
    file_path: str,
    document_id: str,
    tenant_id: str,
    subject_id: str = None,
    class_id: str = None,
) -> List[Chunk]:
    """
    Full ingestion pipeline: parse → chunk → return chunks for embedding.
    """
    path = Path(file_path)
    ext = path.suffix.lower()

    if ext == ".pdf":
        pages = extract_text_from_pdf(file_path)
    elif ext in (".docx", ".doc"):
        pages = extract_text_from_docx(file_path)
    elif ext == ".txt":
        text = path.read_text(encoding="utf-8")
        pages = [{"text": text, "page_number": 1}]
    else:
        raise ValueError(f"Unsupported file type: {ext}")

    return hierarchical_chunk(
        pages=pages,
        document_id=document_id,
        tenant_id=tenant_id,
        source_file=path.name,
        subject_id=subject_id,
        class_id=class_id,
    )


def ingest_youtube(
    url: str,
    document_id: str,
    tenant_id: str,
    subject_id: str = None,
) -> List[Chunk]:
    """Ingest a YouTube transcript."""
    pages = extract_youtube_transcript(url)
    return hierarchical_chunk(
        pages=pages,
        document_id=document_id,
        tenant_id=tenant_id,
        source_file=url,
        subject_id=subject_id,
    )
