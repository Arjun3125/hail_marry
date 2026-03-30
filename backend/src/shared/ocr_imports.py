"""Helpers for turning OCR/image uploads into structured import rows."""
from __future__ import annotations

import csv
import io
import re
from dataclasses import dataclass, field
from pathlib import Path

from src.infrastructure.vector_store.ocr_service import (
    OCRExtractionResult,
    extract_ocr_result_from_image_bytes,
)

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
ATTENDANCE_STATUS_ALIASES = {
    "p": "present",
    "present": "present",
    "a": "absent",
    "absent": "absent",
    "l": "late",
    "late": "late",
}


@dataclass(slots=True)
class StructuredImportParseResult:
    rows: list[tuple[str, object]]
    unmatched_lines: list[str] = field(default_factory=list)
    total_nonempty_lines: int = 0
    review_required: bool = False
    warning: str | None = None


def _is_plausible_name(value: str) -> bool:
    text = value.strip()
    if len(text) < 3:
        return False
    alpha_chars = sum(1 for char in text if char.isalpha())
    if alpha_chars < 2:
        return False
    return alpha_chars >= max(2, len(text) // 3)


def get_extension(filename: str) -> str:
    return Path(filename or "").suffix.lower().lstrip(".")


def decode_utf8_upload(content: bytes) -> str:
    try:
        return content.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ValueError("Invalid encoding. Use UTF-8.") from exc


def build_plaintext_upload_result(content: bytes) -> OCRExtractionResult:
    text = decode_utf8_upload(content)
    return OCRExtractionResult(
        text=text,
        used_ocr=False,
        languages=[],
        preprocessing_applied=[],
        engine="plaintext",
        extracted_characters=len(text.strip()),
        review_required=False,
        warning=None,
    )


def extract_upload_content_result(filename: str, content: bytes) -> OCRExtractionResult:
    """Return text plus OCR metadata for text or image uploads."""
    ext = get_extension(filename)
    if ext in {"csv", "txt"}:
        return build_plaintext_upload_result(content)
    if ext in IMAGE_EXTENSIONS:
        return extract_ocr_result_from_image_bytes(content, suffix=f".{ext}")
    raise ValueError("Unsupported file type")


def extract_text_from_upload_content(filename: str, content: bytes) -> tuple[str, bool]:
    """Backward-compatible helper returning text plus OCR usage."""
    result = extract_upload_content_result(filename, content)
    return result.text, result.used_ocr


def normalize_name_lines(text: str) -> list[str]:
    lines: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        line = re.sub(r"^[\d\W_]+", "", line).strip()
        if not line:
            continue
        lines.append(re.sub(r"\s+", " ", line))
    return lines


def make_generated_email(name: str, *, default_domain: str = "example.com") -> str:
    local = re.sub(r"[^a-zA-Z0-9]+", ".", name.lower()).strip(".")
    return f"{local or 'student'}@{default_domain}"


def build_student_import_csv_from_text(text: str) -> str:
    """Convert OCR/name text into the same CSV shape the onboarding service expects."""
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["full_name", "email", "class_name"])
    for name in normalize_name_lines(text):
        writer.writerow([name, make_generated_email(name), ""])
    return output.getvalue()


def parse_account_rows_with_diagnostics(
    text: str,
    *,
    default_password: str,
    generated_domain: str = "example.com",
) -> StructuredImportParseResult:
    rows: list[dict[str, str]] = []
    unmatched_lines: list[str] = []
    nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = _split_candidate_fields(line)
        if not parts:
            unmatched_lines.append(line)
            continue
        name = parts[0].strip()
        if not _is_plausible_name(name):
            unmatched_lines.append(line)
            continue
        email = parts[1].strip().lower() if len(parts) > 1 and "@" in parts[1] else make_generated_email(name, default_domain=generated_domain)
        password = parts[2].strip() if len(parts) > 2 and parts[2].strip() else default_password
        rows.append({"name": name, "email": email, "password": password})

    review_required = bool(unmatched_lines and rows)
    warning = None
    if review_required:
        warning = f"OCR parsed {len(rows)} account rows but {len(unmatched_lines)} lines need review."
    return StructuredImportParseResult(
        rows=[("row", row) for row in rows],
        unmatched_lines=unmatched_lines,
        total_nonempty_lines=len(nonempty_lines),
        review_required=review_required,
        warning=warning,
    )


def parse_student_import_rows_with_diagnostics(
    text: str,
    *,
    generated_domain: str = "example.com",
) -> StructuredImportParseResult:
    rows: list[dict[str, str]] = []
    unmatched_lines: list[str] = []
    nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = _split_candidate_fields(line)
        if not parts:
            unmatched_lines.append(line)
            continue
        name = parts[0].strip()
        if not _is_plausible_name(name):
            unmatched_lines.append(line)
            continue
        email = parts[1].strip().lower() if len(parts) > 1 and "@" in parts[1] else make_generated_email(name, default_domain=generated_domain)
        class_name = parts[2].strip() if len(parts) > 2 else ""
        rows.append({"full_name": name, "email": email, "class_name": class_name})

    review_required = bool(unmatched_lines and rows)
    warning = None
    if review_required:
        warning = f"OCR parsed {len(rows)} student rows but {len(unmatched_lines)} lines need review."
    return StructuredImportParseResult(
        rows=[("row", row) for row in rows],
        unmatched_lines=unmatched_lines,
        total_nonempty_lines=len(nonempty_lines),
        review_required=review_required,
        warning=warning,
    )


def _split_candidate_fields(line: str) -> list[str]:
    if any(delimiter in line for delimiter in ("|", ",", ";", "\t")):
        parts = re.split(r"[|,;\t]+", line)
        return [part.strip() for part in parts if part.strip()]
    return [part.strip() for part in re.split(r"\s{2,}", line) if part.strip()]


def parse_attendance_rows_with_diagnostics(text: str) -> StructuredImportParseResult:
    rows: list[tuple[str, str]] = []
    unmatched_lines: list[str] = []
    nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames:
        lowered = {field.strip().lower() for field in reader.fieldnames if field}
        if {"student_id", "status"} <= lowered or {"student_name", "status"} <= lowered or {"name", "status"} <= lowered:
            for row in reader:
                identifier = (row.get("student_id") or row.get("student_name") or row.get("name") or "").strip()
                status = ATTENDANCE_STATUS_ALIASES.get((row.get("status") or "").strip().lower())
                if identifier and status:
                    rows.append((identifier, status))
            if rows:
                return StructuredImportParseResult(rows=rows, total_nonempty_lines=len(nonempty_lines))

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = _split_candidate_fields(line)
        if len(parts) >= 2:
            status = ATTENDANCE_STATUS_ALIASES.get(parts[-1].strip().lower())
            if status:
                identifier = " ".join(parts[:-1]).strip()
                if identifier:
                    rows.append((identifier, status))
                    continue
        tokens = line.split()
        if len(tokens) >= 2:
            status = ATTENDANCE_STATUS_ALIASES.get(tokens[-1].strip().lower())
            if status:
                identifier = " ".join(tokens[:-1]).strip()
                if identifier:
                    rows.append((identifier, status))
                    continue
        unmatched_lines.append(line)

    review_required = bool(unmatched_lines and rows)
    warning = None
    if review_required:
        warning = f"OCR parsed {len(rows)} attendance rows but {len(unmatched_lines)} lines need review."
    return StructuredImportParseResult(
        rows=rows,
        unmatched_lines=unmatched_lines,
        total_nonempty_lines=len(nonempty_lines),
        review_required=review_required,
        warning=warning,
    )


def parse_attendance_rows(text: str) -> list[tuple[str, str]]:
    return [(identifier, str(status)) for identifier, status in parse_attendance_rows_with_diagnostics(text).rows]


def parse_marks_rows_with_diagnostics(text: str) -> StructuredImportParseResult:
    rows: list[tuple[str, int]] = []
    unmatched_lines: list[str] = []
    nonempty_lines = [line.strip() for line in text.splitlines() if line.strip()]
    reader = csv.DictReader(io.StringIO(text))
    if reader.fieldnames:
        lowered = {field.strip().lower() for field in reader.fieldnames if field}
        if {"student_id", "marks_obtained"} <= lowered or {"student_name", "marks_obtained"} <= lowered or {"name", "marks_obtained"} <= lowered:
            for row in reader:
                identifier = (row.get("student_id") or row.get("student_name") or row.get("name") or "").strip()
                marks_str = (row.get("marks_obtained") or "").strip()
                if identifier and re.fullmatch(r"\d+(?:\.\d+)?", marks_str):
                    rows.append((identifier, int(float(marks_str))))
            if rows:
                return StructuredImportParseResult(rows=rows, total_nonempty_lines=len(nonempty_lines))

    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        parts = _split_candidate_fields(line)
        if len(parts) >= 2 and re.fullmatch(r"\d+(?:\.\d+)?", parts[-1]):
            rows.append((" ".join(parts[:-1]).strip(), int(float(parts[-1]))))
            continue
        tokens = line.split()
        if len(tokens) >= 2 and re.fullmatch(r"\d+(?:\.\d+)?", tokens[-1]):
            rows.append((" ".join(tokens[:-1]).strip(), int(float(tokens[-1]))))
            continue
        unmatched_lines.append(line)

    rows = [(identifier, marks) for identifier, marks in rows if identifier]
    review_required = bool(unmatched_lines and rows)
    warning = None
    if review_required:
        warning = f"OCR parsed {len(rows)} marks rows but {len(unmatched_lines)} lines need review."
    return StructuredImportParseResult(
        rows=rows,
        unmatched_lines=unmatched_lines,
        total_nonempty_lines=len(nonempty_lines),
        review_required=review_required,
        warning=warning,
    )


def parse_marks_rows(text: str) -> list[tuple[str, int]]:
    return [(identifier, int(marks)) for identifier, marks in parse_marks_rows_with_diagnostics(text).rows]
