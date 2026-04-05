"""Tests for document ingestion watcher."""
import os
import tempfile
from src.domains.platform.services.doc_watcher import (
    SUPPORTED_EXTENSIONS, compute_file_hash, get_watch_status,
    mark_processed, scan_directory,
)


def test_supported_extensions():
    assert ".pdf" in SUPPORTED_EXTENSIONS
    assert ".docx" in SUPPORTED_EXTENSIONS
    assert ".pptx" in SUPPORTED_EXTENSIONS
    assert ".xlsx" in SUPPORTED_EXTENSIONS
    assert ".txt" in SUPPORTED_EXTENSIONS


def test_compute_file_hash():
    with tempfile.NamedTemporaryFile(delete=False, suffix=".txt") as f:
        f.write(b"test content")
        f.flush()
        h = compute_file_hash(f.name)
    os.unlink(f.name)
    assert len(h) == 32  # MD5 hex digest


def test_scan_empty_dir(tmp_path):
    result = scan_directory(str(tmp_path))
    assert result == []


def test_scan_finds_txt(tmp_path):
    path = tmp_path / "notes.txt"
    path.write_text("test", encoding="utf-8")
    result = scan_directory(str(tmp_path))
    assert len(result) == 1
    assert result[0]["name"] == "notes.txt"


def test_scan_skips_unsupported(tmp_path):
    path = tmp_path / "image.jpg"
    path.write_text("fake", encoding="utf-8")
    result = scan_directory(str(tmp_path))
    assert len(result) == 0


def test_mark_processed_skips_rescan(tmp_path):
    path = tmp_path / "data.txt"
    path.write_text("content", encoding="utf-8")
    result1 = scan_directory(str(tmp_path))
    assert len(result1) == 1
    mark_processed(result1[0]["path"], result1[0]["hash"])
    result2 = scan_directory(str(tmp_path))
    assert len(result2) == 0


def test_watch_status():
    status = get_watch_status()
    assert "poll_interval_seconds" in status
    assert "supported_extensions" in status
