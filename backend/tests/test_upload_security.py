"""Tests for upload security utilities."""
import io
import zipfile
import pytest

from utils.upload_security import (
    UploadValidationError,
    sanitize_docx_bytes,
)


class TestSanitizeDocxBytes:
    """Test DOCX macro stripping."""

    def _make_docx(self, entries: dict[str, bytes]) -> bytes:
        """Create a minimal DOCX-like zip in memory."""
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w") as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
        return buf.getvalue()

    def test_non_zip_raises(self):
        with pytest.raises(UploadValidationError):
            sanitize_docx_bytes(b"this is not a zip file")

    def test_clean_docx_returns_unchanged(self):
        content = self._make_docx({
            "[Content_Types].xml": b"<Types></Types>",
            "word/document.xml": b"<document>Hello</document>",
        })
        result, removed = sanitize_docx_bytes(content)
        assert removed is False
        assert result == content

    def test_macros_stripped(self):
        content = self._make_docx({
            "[Content_Types].xml": b"<Types></Types>",
            "word/document.xml": b"<document>Hello</document>",
            "word/vbaProject.bin": b"malicious-macro-code",
        })
        result, removed = sanitize_docx_bytes(content)
        assert removed is True
        result_zip = zipfile.ZipFile(io.BytesIO(result))
        assert "word/vbaProject.bin" not in result_zip.namelist()
        assert "word/document.xml" in result_zip.namelist()

    def test_content_types_rewritten(self):
        macro_ct = "application/vnd.ms-word.document.macroEnabled.main+xml"
        standard_ct = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"
        content = self._make_docx({
            "[Content_Types].xml": f'<Types><Default ContentType="{macro_ct}"/></Types>'.encode(),
            "word/document.xml": b"<doc/>",
            "word/vbaProject.bin": b"macro-data",
        })
        result, removed = sanitize_docx_bytes(content)
        assert removed is True
        ct_xml = zipfile.ZipFile(io.BytesIO(result)).read("[Content_Types].xml").decode()
        assert macro_ct not in ct_xml
        assert standard_ct in ct_xml

    def test_empty_zip(self):
        content = self._make_docx({})
        result, removed = sanitize_docx_bytes(content)
        assert removed is False
