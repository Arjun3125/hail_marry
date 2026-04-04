"""
Document Ingestion Service
Handles PDF, DOCX, PPTX, XLSX, TXT, CSV, HTML, and YouTube transcript parsing with hierarchical chunking.
"""
import re
import subprocess
import tempfile
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
    notebook_id: Optional[str] = None
    class_id: Optional[str] = None
    source_file: Optional[str] = None
    metadata: Dict = field(default_factory=dict)


def _pages_from_connector(result: Dict, *, label: str) -> List[Dict]:
    metadata = result.get("metadata") or {}
    error = metadata.get("error")
    if error:
        raise ValueError(f"{label} ingestion failed: {error}")

    chunks = result.get("chunks") or []
    if chunks:
        return [
            {"text": chunk, "page_number": idx + 1}
            for idx, chunk in enumerate(chunks)
            if str(chunk).strip()
        ]

    text = (result.get("text") or "").strip()
    if not text:
        raise ValueError(f"{label} ingestion failed: no text extracted")
    return [{"text": text, "page_number": 1}]


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

    preferred_languages = ["en", "hi", "mr"]
    transcript = None
    language_code = None
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id, languages=preferred_languages)
        language_code = preferred_languages[0]
    except Exception:
        try:
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        except Exception as exc:
            raise ValueError("Could not fetch YouTube captions for that video.") from exc

        for lang in preferred_languages:
            try:
                found = transcript_list.find_transcript([lang])
                transcript = found.fetch()
                language_code = found.language_code
                break
            except Exception:
                continue

        if transcript is None:
            fallback = None
            try:
                fallback = next(iter(transcript_list._manually_created_transcripts.values()))  # type: ignore[attr-defined]
            except Exception:
                fallback = None
            if fallback is None:
                try:
                    fallback = next(iter(transcript_list._generated_transcripts.values()))  # type: ignore[attr-defined]
                except Exception:
                    fallback = None
            if fallback is None:
                raise ValueError("No captions were available for that YouTube video.")
            try:
                transcript = fallback.fetch()
                language_code = getattr(fallback, "language_code", None)
            except Exception as exc:
                raise ValueError("Failed to download captions for that YouTube video.") from exc

    # Group transcript into ~300 word segments
    segments = []
    current_text = []
    current_start = 0
    current_end = 0
    word_count = 0

    for entry in transcript:
        words = entry["text"].split()
        word_count += len(words)
        current_text.append(entry["text"])

        current_end = entry.get("start", 0) + entry.get("duration", 0)

        if word_count >= 250:
            segments.append({
                "text": " ".join(current_text),
                "page_number": len(segments) + 1,
                "section_title": f"Segment {len(segments) + 1} ({int(current_start)}s-{int(current_end)}s)",
                "metadata": {
                    "timestamp_start": current_start,
                    "timestamp_end": current_end,
                    "language": language_code,
                },
            })
            current_text = []
            word_count = 0
            current_start = entry.get("start", 0)

    if current_text:
        segments.append({
            "text": " ".join(current_text),
            "page_number": len(segments) + 1,
            "section_title": f"Segment {len(segments) + 1}",
            "metadata": {
                "timestamp_start": current_start,
                "timestamp_end": current_end,
                "language": language_code,
            },
        })

    return segments


def hierarchical_chunk(
    pages: List[Dict],
    document_id: str,
    tenant_id: str,
    source_file: str = "",
    subject_id: str = None,
    notebook_id: str = None,
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
        page_metadata = page_data.get("metadata", {}) or {}

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
                    notebook_id=notebook_id,
                    class_id=class_id,
                    source_file=source_file,
                    metadata={
                        "word_count": len(chunk_text.split()),
                        "page": page_num,
                        "section": section,
                        **page_metadata,
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
                    notebook_id=notebook_id,
                    class_id=class_id,
                    source_file=source_file,
                    metadata={
                        "word_count": len(chunk_text.split()),
                        "page": page_num,
                        "section": section,
                        **page_metadata,
                    },
                ))
                chunk_id += 1

    return chunks


def ingest_document(
    file_path: str,
    document_id: str,
    tenant_id: str,
    subject_id: str = None,
    notebook_id: str = None,
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
    elif ext == ".pptx":
        from src.infrastructure.vector_store.connectors import extract_pptx
        connector_result = extract_pptx(file_path)
        pages = _pages_from_connector(connector_result, label="PPTX")
    elif ext in (".xlsx", ".xls"):
        from src.infrastructure.vector_store.connectors import extract_excel
        connector_result = extract_excel(file_path)
        pages = _pages_from_connector(connector_result, label="Excel")
    elif ext in (".txt", ".md"):
        text = path.read_text(encoding="utf-8")
        pages = [{"text": text, "page_number": 1}]
    elif ext in (".csv",):
        import csv
        text_rows = []
        with open(file_path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                line = " | ".join(f"{k}: {v}" for k, v in row.items() if v)
                text_rows.append(line)
        pages = [{"text": "\n".join(text_rows), "page_number": 1}]
    elif ext in (".html", ".htm"):
        raw_html = path.read_text(encoding="utf-8")
        text = re.sub(r"<script[^>]*>.*?</script>", "", raw_html, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<style[^>]*>.*?</style>", "", text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r"<[^>]+>", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        pages = [{"text": text, "page_number": 1}]
    else:
        raise ValueError(
            "Unsupported file type: "
            f"{ext}. Supported: .pdf, .docx, .pptx, .xlsx, .txt, .md, .csv, .html"
        )

    return hierarchical_chunk(
        pages=pages,
        document_id=document_id,
        tenant_id=tenant_id,
        source_file=path.name,
        subject_id=subject_id,
        notebook_id=notebook_id,
        class_id=class_id,
    )


def ingest_youtube(
    url: str,
    document_id: str,
    tenant_id: str,
    subject_id: str = None,
    notebook_id: str = None,
) -> List[Chunk]:
    """Ingest a YouTube transcript."""
    pages = extract_youtube_transcript(url)
    return hierarchical_chunk(
        pages=pages,
        document_id=document_id,
        tenant_id=tenant_id,
        source_file=url,
        subject_id=subject_id,
        notebook_id=notebook_id,
    )


_whisper_pipeline = None


def _get_whisper_pipeline():
    global _whisper_pipeline
    if _whisper_pipeline is None:
        try:
            from transformers import pipeline
        except ImportError as exc:
            raise ImportError("transformers is required for media transcription.") from exc
        _whisper_pipeline = pipeline(
            "automatic-speech-recognition",
            model="openai/whisper-tiny",
            device=-1,
        )
    return _whisper_pipeline


def extract_media_transcript(file_path: str) -> str:
    """Extract transcript from an audio or video file using Whisper."""
    pipeline = _get_whisper_pipeline()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        wav_path = tmp.name

    try:
        subprocess.run(
            [
                "ffmpeg",
                "-y",
                "-i",
                file_path,
                "-ac",
                "1",
                "-ar",
                "16000",
                wav_path,
            ],
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError as exc:
        raise ValueError("ffmpeg is required to decode audio/video uploads for transcription.") from exc
    except subprocess.CalledProcessError as exc:
        raise ValueError("Unable to decode the audio/video file for transcription.") from exc

    try:
        result = pipeline(wav_path)
    finally:
        Path(wav_path).unlink(missing_ok=True)

    text = (result or {}).get("text", "")
    if not text or not text.strip():
        raise ValueError("No transcript text could be extracted from that media file.")
    return str(text).strip()


def ingest_media_transcript(
    file_path: str,
    document_id: str,
    tenant_id: str,
    subject_id: str = None,
    notebook_id: str = None,
    class_id: str = None,
) -> List[Chunk]:
    transcript = extract_media_transcript(file_path)
    pages = [{
        "text": transcript,
        "page_number": 1,
        "section_title": "Transcript",
    }]
    return hierarchical_chunk(
        pages=pages,
        document_id=document_id,
        tenant_id=tenant_id,
        source_file=Path(file_path).name,
        subject_id=subject_id,
        notebook_id=notebook_id,
        class_id=class_id,
    )
