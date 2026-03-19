"""Tests for document ingestion watcher."""
import os
import tempfile
import pytest
from src.domains.platform.services.doc_watcher import (
    SUPPORTED_EXTENSIONS, compute_file_hash, get_watch_status,
    mark_processed, scan_directory, _processed_files,
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


def test_scan_empty_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        result = scan_directory(tmpdir)
        assert result == []


def test_scan_finds_txt():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "notes.txt")
        with open(path, "w") as f:
            f.write("test")
        result = scan_directory(tmpdir)
        assert len(result) == 1
        assert result[0]["name"] == "notes.txt"


def test_scan_skips_unsupported():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "image.jpg")
        with open(path, "w") as f:
            f.write("fake")
        result = scan_directory(tmpdir)
        assert len(result) == 0


def test_mark_processed_skips_rescan():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = os.path.join(tmpdir, "data.txt")
        with open(path, "w") as f:
            f.write("content")
        result1 = scan_directory(tmpdir)
        assert len(result1) == 1
        mark_processed(result1[0]["path"], result1[0]["hash"])
        result2 = scan_directory(tmpdir)
        assert len(result2) == 0


def test_watch_status():
    status = get_watch_status()
    assert "poll_interval_seconds" in status
    assert "supported_extensions" in status
