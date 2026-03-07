"""Upload hardening helpers for server-side file handling."""
from __future__ import annotations

import io
import os
import re
import zipfile
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[2]
STORAGE_ROOT = Path(
    os.getenv("VidyaOS_STORAGE_ROOT", str(PROJECT_ROOT / "private_storage"))
).resolve()

_REL_VBA_PATTERN = re.compile(r"<Relationship[^>]*vbaProject[^>]*/>", flags=re.IGNORECASE)
_MACRO_DOC_MAIN = "application/vnd.ms-word.document.macroEnabled.main+xml"
_STANDARD_DOC_MAIN = "application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"


class UploadValidationError(ValueError):
    """Raised when uploaded content fails security validation."""


def ensure_storage_dir(*parts: str) -> Path:
    """Create and return a storage path rooted in private storage."""
    path = STORAGE_ROOT.joinpath(*parts)
    path.mkdir(parents=True, exist_ok=True)
    return path


def sanitize_docx_bytes(content: bytes) -> tuple[bytes, bool]:
    """
    Strip macro artifacts from DOCX content.
    Returns (sanitized_bytes, macros_removed).
    """
    in_buffer = io.BytesIO(content)
    if not zipfile.is_zipfile(in_buffer):
        raise UploadValidationError("Invalid DOCX file.")

    with zipfile.ZipFile(in_buffer, "r") as src_zip:
        names = src_zip.namelist()
        macro_entries = [
            name
            for name in names
            if "vbaproject" in name.lower() or "/vba" in name.lower()
        ]
        if not macro_entries:
            return content, False

        out_buffer = io.BytesIO()
        with zipfile.ZipFile(out_buffer, "w", compression=zipfile.ZIP_DEFLATED) as dst_zip:
            for info in src_zip.infolist():
                name = info.filename
                lowered = name.lower()
                if "vbaproject" in lowered or "/vba" in lowered:
                    continue

                data = src_zip.read(name)
                if name == "[Content_Types].xml":
                    text = data.decode("utf-8", errors="ignore")
                    text = text.replace(_MACRO_DOC_MAIN, _STANDARD_DOC_MAIN)
                    data = text.encode("utf-8")
                elif name.endswith(".rels"):
                    text = data.decode("utf-8", errors="ignore")
                    text = _REL_VBA_PATTERN.sub("", text)
                    data = text.encode("utf-8")

                dst_zip.writestr(name, data)

        return out_buffer.getvalue(), True
