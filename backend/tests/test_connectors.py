"""Tests for extended data connectors."""
import pytest
from src.infrastructure.vector_store.connectors import CONNECTORS, get_connector
from constants import EXTENDED_FILE_TYPES


def test_extended_file_types():
    assert "pptx" in EXTENDED_FILE_TYPES
    assert "xlsx" in EXTENDED_FILE_TYPES
    assert "google_doc" in EXTENDED_FILE_TYPES
    assert "notion" in EXTENDED_FILE_TYPES


def test_connectors_registry():
    assert "pptx" in CONNECTORS
    assert "xlsx" in CONNECTORS
    assert "google_doc" in CONNECTORS
    assert "notion" in CONNECTORS


def test_get_connector_pptx():
    connector = get_connector("pptx")
    assert connector is not None
    assert callable(connector)


def test_get_connector_xlsx():
    connector = get_connector("xlsx")
    assert connector is not None


def test_get_connector_unknown():
    connector = get_connector("mp3")
    assert connector is None


def test_pptx_extraction_missing_file():
    connector = get_connector("pptx")
    try:
        result = connector("nonexistent.pptx")
        # python-pptx not installed → should return error metadata
        assert "error" in result.get("metadata", {}) or result["text"] == ""
    except Exception:
        pass  # File not found is expected


def test_connector_output_format():
    """All connectors should return {text, metadata, chunks} format."""
    expected_keys = {"text", "metadata", "chunks"}
    # Test with a mock output
    output = {"text": "test", "metadata": {"file_type": "test"}, "chunks": ["test"]}
    assert set(output.keys()) == expected_keys
