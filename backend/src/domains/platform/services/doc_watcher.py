"""Document ingestion watch — auto-ingest from watched folders.

Monitors configured directories for new files and automatically
ingests them into the AI knowledge base.
"""
import os
import hashlib
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from config import settings

WATCH_POLL_INTERVAL = settings.doc_watch.poll_interval_seconds
WATCH_DIRS = settings.doc_watch.dirs
SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md"}

# In-memory registry of already-processed files
_processed_files: dict[str, str] = {}  # path → content hash


def compute_file_hash(file_path: str) -> str:
    """Compute MD5 hash of file contents for change detection."""
    hasher = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def scan_directory(directory: str) -> list[dict]:
    """Scan a directory for new or modified files suitable for ingestion."""
    new_files = []
    if not os.path.isdir(directory):
        return new_files

    for root, _dirs, files in os.walk(directory):
        for fname in files:
            ext = os.path.splitext(fname)[1].lower()
            if ext not in SUPPORTED_EXTENSIONS:
                continue

            full_path = os.path.join(root, fname)
            try:
                file_hash = compute_file_hash(full_path)
            except (OSError, PermissionError):
                continue

            # Skip if already processed with same hash
            if _processed_files.get(full_path) == file_hash:
                continue

            stat = os.stat(full_path)
            new_files.append({
                "path": full_path,
                "name": fname,
                "extension": ext.lstrip("."),
                "size_bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
                "hash": file_hash,
            })

    return new_files


def mark_processed(file_path: str, file_hash: str):
    """Mark a file as processed (after successful ingestion)."""
    _processed_files[file_path] = file_hash


def get_watch_status() -> dict:
    """Get current watcher status and stats."""
    return {
        "enabled": bool(WATCH_DIRS and WATCH_DIRS[0]),
        "poll_interval_seconds": WATCH_POLL_INTERVAL,
        "watched_directories": [d for d in WATCH_DIRS if d],
        "processed_file_count": len(_processed_files),
        "supported_extensions": sorted(SUPPORTED_EXTENSIONS),
    }


def run_watch_cycle(tenant_id: Optional[UUID] = None) -> dict:
    """Run one watch cycle: scan all directories and return new files.

    In production, this would be called by a background worker
    (Celery task or asyncio loop) that also triggers ingestion.
    """
    all_new = []
    for directory in WATCH_DIRS:
        directory = directory.strip()
        if not directory:
            continue
        new_files = scan_directory(directory)
        all_new.extend(new_files)

    return {
        "cycle_at": datetime.now(timezone.utc).isoformat(),
        "new_files_found": len(all_new),
        "files": all_new,
    }
