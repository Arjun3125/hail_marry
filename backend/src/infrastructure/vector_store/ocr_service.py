"""
OCR Service — EasyOCR-based handwriting/text recognition with PDF generation.

Accepts image files (JPG, JPEG, PNG), extracts text using EasyOCR,
and generates a clean PDF containing the extracted text.
"""
from __future__ import annotations

import io
import logging
import os
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# Lazy-loaded EasyOCR reader (heavy model, ~200MB on first download)
_reader = None

IMAGE_EXTENSIONS = {"jpg", "jpeg", "png"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB per image
OCR_LANGUAGES = ["en", "hi", "mr"]  # English + Hindi + Marathi
MIN_OCR_CONFIDENCE_REVIEW = 0.4
UNICODE_FONT_CANDIDATES = [
    Path("C:/Windows/Fonts/Nirmala.ttc"),
    Path("C:/Windows/Fonts/Mangal.ttf"),
]


def _testing_mode_enabled() -> bool:
    return os.getenv("TESTING", "").strip().lower() in {"1", "true", "yes", "on"}


class _TestingEasyOCRReader:
    """Deterministic OCR reader used only in tests when EasyOCR is unavailable."""

    def readtext(self, image_input, detail=1, paragraph=True, rotation_info=None):
        _ = (paragraph, rotation_info)
        text = ""
        if isinstance(image_input, (str, Path)):
            image_path = Path(image_input)
            sidecar = image_path.with_suffix(".txt")
            if sidecar.exists():
                text = sidecar.read_text(encoding="utf-8").strip()
        elif isinstance(image_input, bytes):
            try:
                text = image_input.decode("utf-8").strip()
            except UnicodeDecodeError:
                text = ""

        if not text:
            return []
        if detail:
            return [([0, 0, 1, 1], text, 0.99)]
        return [text]


@dataclass(slots=True)
class OCRExtractionResult:
    text: str
    used_ocr: bool
    languages: list[str] = field(default_factory=list)
    preprocessing_applied: list[str] = field(default_factory=list)
    engine: str = "easyocr"
    extracted_characters: int = 0
    confidence: float | None = None
    review_required: bool = False
    warning: str | None = None


def _get_reader():
    """
    Lazy-initialise the EasyOCR reader so the heavy model is only loaded
    once per process and only when actually needed.
    """
    global _reader
    if _reader is None:
        try:
            import easyocr
        except ImportError:
            if not _testing_mode_enabled():
                raise ImportError(
                    "easyocr is not installed. Run: pip install easyocr"
                )
            logger.info("EasyOCR unavailable; using deterministic testing OCR reader")
            _reader = _TestingEasyOCRReader()
        else:
            logger.info("Loading EasyOCR reader for languages: %s", OCR_LANGUAGES)
            _reader = easyocr.Reader(OCR_LANGUAGES, gpu=False)
            logger.info("EasyOCR reader loaded successfully")
    return _reader


def _serialize_image(image, *, suffix: str) -> bytes:
    output = io.BytesIO()
    target_format = "JPEG" if suffix.lower() in {".jpg", ".jpeg"} else "PNG"
    save_image = image
    if target_format == "JPEG" and image.mode not in {"RGB", "L"}:
        save_image = image.convert("RGB")
    save_image.save(output, format=target_format)
    return output.getvalue()


def _preprocess_image_variant(
    image,
    *,
    aggressive: bool,
    upscale: bool = False,
    invert: bool = False,
) -> tuple[object, list[str]]:
    from PIL import ImageFilter, ImageOps, ImageStat

    applied: list[str] = []
    image = ImageOps.exif_transpose(image)
    applied.append("exif_transpose")
    if upscale:
        width, height = image.size
        if width < 1800 and height < 1800:
            image = image.resize((max(width * 2, 1), max(height * 2, 1)))
            applied.append("upscale_2x")
    image = image.convert("L")
    applied.append("grayscale")
    image = ImageOps.autocontrast(image)
    applied.append("autocontrast")
    image = image.filter(ImageFilter.MedianFilter(size=3))
    applied.append("median_denoise")

    if aggressive:
        image = ImageOps.equalize(image)
        applied.append("equalize")
        image = image.filter(ImageFilter.SHARPEN)
        applied.append("sharpen")
        image = image.filter(ImageFilter.UnsharpMask(radius=1, percent=150, threshold=3))
        applied.append("unsharp_mask")
        try:
            mean_luma = ImageStat.Stat(image).mean[0]
            threshold = max(100, min(180, int(mean_luma)))
            image = image.point(lambda p: 255 if p > threshold else 0)
            applied.append("binarize")
        except Exception:
            logger.debug("Skipping OCR binarization step", exc_info=True)

    if invert:
        image = ImageOps.invert(image)
        applied.append("invert")

    return image, applied


def preprocess_image_bytes(content: bytes, *, suffix: str = ".png") -> tuple[bytes, list[str]]:
    """Best-effort preprocessing to stabilize OCR on noisy phone captures."""
    applied: list[str] = []
    try:
        from PIL import Image
    except ImportError:
        logger.info("Pillow not installed; OCR preprocessing disabled")
        return content, applied

    with Image.open(io.BytesIO(content)) as image:
        image.load()
        image, applied = _preprocess_image_variant(image, aggressive=False)
        return _serialize_image(image, suffix=suffix), applied


def _build_result(
    text: str,
    *,
    used_ocr: bool,
    preprocessing_applied: list[str] | None = None,
    confidence: float | None = None,
    warning: str | None = None,
    review_required: bool = False,
    emit_metrics: bool = True,
    log_result: bool = True,
) -> OCRExtractionResult:
    try:
        from src.domains.platform.services.metrics_registry import increment_ocr_metric
    except Exception:
        increment_ocr_metric = None

    clean_text = text.strip()
    ascii_letters = sum(1 for char in clean_text if char.isascii() and char.isalpha())
    non_ascii = sum(1 for char in clean_text if ord(char) > 127)
    if ascii_letters >= 10 and non_ascii >= 3:
        ascii_only = "".join(
            char for char in clean_text
            if char.isascii() and (char.isalnum() or char.isspace() or char in ".,:;!?+-'\"()[]")
        )
        ascii_only = " ".join(ascii_only.split())
        if len(ascii_only) >= max(10, int(len(clean_text) * 0.5)):
            clean_text = ascii_only

    extracted_characters = len(clean_text)
    effective_warning = warning
    effective_review = review_required

    if used_ocr and confidence is not None and confidence < MIN_OCR_CONFIDENCE_REVIEW:
        effective_review = True
        effective_warning = effective_warning or "OCR confidence is low. Review the extracted text before continuing."
    if used_ocr and not clean_text:
        effective_review = True
        effective_warning = effective_warning or "OCR could not extract readable text from the image."
    elif used_ocr and extracted_characters < 20:
        effective_review = True
        effective_warning = effective_warning or "OCR extracted very little text. Review the image quality before proceeding."

    if used_ocr and emit_metrics and increment_ocr_metric:
        increment_ocr_metric("processed", "easyocr")
        if effective_review:
            increment_ocr_metric("review_required", "easyocr")

    if log_result:
        logger.info(
            "OCR completed chars=%s confidence=%s review_required=%s warning=%s",
            extracted_characters,
            confidence,
            effective_review,
            bool(effective_warning),
        )

    return OCRExtractionResult(
        text=clean_text,
        used_ocr=used_ocr,
        languages=list(OCR_LANGUAGES) if used_ocr else [],
        preprocessing_applied=preprocessing_applied or [],
        engine="easyocr",
        extracted_characters=extracted_characters,
        confidence=confidence,
        review_required=effective_review,
        warning=effective_warning,
    )


def extract_text_from_image(image_path: str) -> str:
    """
    Run OCR on a single image and return the extracted text.

    Args:
        image_path: Absolute path to the image file.

    Returns:
        Extracted text as a single string with line breaks preserved.
    """
    text, _ = _extract_text_with_confidence(image_path)
    logger.info(
        "OCR extracted %d characters from %s",
        len(text),
        Path(image_path).name,
    )
    return text


def _extract_text_with_confidence(
    image_source: str | bytes,
    *,
    apply_aggressive_preprocessing: bool = False,
    upscale: bool = False,
    invert: bool = False,
    paragraph: bool = True,
) -> tuple[str, float | None]:
    from PIL import Image

    reader = _get_reader()
    image_input: str | bytes = image_source
    if apply_aggressive_preprocessing or upscale or invert:
        with Image.open(io.BytesIO(image_source) if isinstance(image_source, bytes) else image_source) as image:
            image.load()
            processed, _ = _preprocess_image_variant(
                image,
                aggressive=apply_aggressive_preprocessing,
                upscale=upscale,
                invert=invert,
            )
            image_input = _serialize_image(processed, suffix=".png")
    results = reader.readtext(
        image_input,
        detail=1,
        paragraph=paragraph,
        rotation_info=[90, 180, 270],
    )
    texts: list[str] = []
    confidences: list[float] = []
    for item in results:
        if not isinstance(item, (list, tuple)):
            continue
        if len(item) >= 3:
            _, text, conf = item[0], item[1], item[2]
        elif len(item) == 2:
            if isinstance(item[1], (int, float)):
                text, conf = item[0], item[1]
            else:
                text, conf = item[1], None
        else:
            continue
        if text:
            texts.append(str(text))
        if isinstance(conf, (int, float)):
            confidences.append(float(conf))
    joined = "\n".join(texts)
    avg_conf = sum(confidences) / len(confidences) if confidences else None
    return joined, avg_conf


def _is_better_result(candidate: OCRExtractionResult, baseline: OCRExtractionResult) -> bool:
    def score(result: OCRExtractionResult) -> float:
        text = result.text.strip()
        words = [token for token in text.replace("\n", " ").split(" ") if token]
        confidence = result.confidence or 0.0
        non_ascii = sum(1 for char in text if ord(char) > 127)
        short_penalty = 0.0
        if result.extracted_characters <= 2:
            short_penalty += 140.0
        elif result.extracted_characters < 5:
            short_penalty += 80.0
        elif result.extracted_characters < 12:
            short_penalty += 25.0
        return (
            (result.extracted_characters * 1.0)
            + (len(words) * 10.0)
            + (confidence * 35.0)
            + min(non_ascii, 60) * 0.4
            - (20.0 if result.review_required else 0.0)
            - short_penalty
        )

    candidate_score = score(candidate)
    baseline_score = score(baseline)
    if abs(candidate_score - baseline_score) > 1.0:
        return candidate_score > baseline_score
    if candidate.extracted_characters != baseline.extracted_characters:
        return candidate.extracted_characters > baseline.extracted_characters
    candidate_conf = candidate.confidence or 0.0
    baseline_conf = baseline.confidence or 0.0
    return candidate_conf > baseline_conf


def extract_ocr_result_from_image_bytes(
    content: bytes,
    *,
    suffix: str = ".png",
    apply_preprocessing: bool = True,
) -> OCRExtractionResult:
    """Run OCR on image bytes and return text plus quality metadata."""
    validate_image_size(content)
    processed_bytes = content
    preprocessing_applied: list[str] = []
    if apply_preprocessing:
        processed_bytes, preprocessing_applied = preprocess_image_bytes(content, suffix=suffix)

    try:
        text, confidence = _extract_text_with_confidence(processed_bytes)
        processed_result = _build_result(
            text,
            used_ocr=True,
            preprocessing_applied=preprocessing_applied,
            confidence=confidence,
            emit_metrics=False,
            log_result=False,
        )
        best_result = processed_result

        raw_result: OCRExtractionResult | None = None
        if apply_preprocessing and processed_bytes != content:
            raw_text, raw_confidence = _extract_text_with_confidence(content)
            raw_result = _build_result(
                raw_text,
                used_ocr=True,
                preprocessing_applied=[],
                confidence=raw_confidence,
                emit_metrics=False,
                log_result=False,
            )

        if raw_result is not None and _is_better_result(raw_result, best_result):
            best_result = raw_result

        if best_result.review_required:
            candidate_variants = [
                (
                    {"image_source": content, "apply_aggressive_preprocessing": True, "paragraph": True},
                    preprocessing_applied + ["aggressive_variant"],
                ),
                (
                    {"image_source": content, "upscale": True, "paragraph": True},
                    preprocessing_applied + ["upscaled_variant"],
                ),
                (
                    {"image_source": content, "apply_aggressive_preprocessing": True, "upscale": True, "paragraph": True},
                    preprocessing_applied + ["upscaled_variant", "aggressive_variant"],
                ),
                (
                    {"image_source": content, "apply_aggressive_preprocessing": True, "invert": True, "paragraph": True},
                    preprocessing_applied + ["aggressive_variant", "invert_variant"],
                ),
                (
                    {"image_source": content, "upscale": True, "paragraph": False},
                    preprocessing_applied + ["upscaled_variant", "line_mode"],
                ),
            ]
            for kwargs, applied in candidate_variants:
                text, confidence = _extract_text_with_confidence(**kwargs)
                candidate_result = _build_result(
                    text,
                    used_ocr=True,
                    preprocessing_applied=applied,
                    confidence=confidence,
                    emit_metrics=False,
                    log_result=False,
                )
                if _is_better_result(candidate_result, best_result):
                    best_result = candidate_result

        return _build_result(
            best_result.text,
            used_ocr=True,
            preprocessing_applied=best_result.preprocessing_applied,
            confidence=best_result.confidence,
            warning=best_result.warning,
            review_required=best_result.review_required,
        )
    except Exception:
        try:
            from src.domains.platform.services.metrics_registry import increment_ocr_metric
            increment_ocr_metric("failed", "easyocr")
        except Exception:
            pass
        logger.exception("OCR extraction failed")
        raise


def extract_ocr_result_from_image_path(
    image_path: str,
    *,
    apply_preprocessing: bool = True,
) -> OCRExtractionResult:
    """Run OCR with metadata starting from a file path."""
    path = Path(image_path)
    if _testing_mode_enabled():
        sidecar = path.with_suffix(".txt")
        if sidecar.exists():
            return _build_result(
                sidecar.read_text(encoding="utf-8"),
                used_ocr=True,
                preprocessing_applied=["test_fixture_sidecar"],
                confidence=0.99,
                review_required=False,
            )
    content = path.read_bytes()
    return extract_ocr_result_from_image_bytes(
        content,
        suffix=path.suffix or ".png",
        apply_preprocessing=apply_preprocessing,
    )


def extract_text_from_image_bytes(content: bytes, *, suffix: str = ".png") -> str:
    """Persist image bytes to a temp file, run OCR, and clean up."""
    return extract_ocr_result_from_image_bytes(content, suffix=suffix).text


def _apply_pdf_font(pdf) -> bool:
    """Prefer a Unicode-capable font when present so Devanagari text survives."""
    for font_path in UNICODE_FONT_CANDIDATES:
        if not font_path.exists():
            continue
        try:
            pdf.add_font("VidyaOCRUnicode", "", str(font_path))
            pdf.set_font("VidyaOCRUnicode", "", 14)
            return True
        except Exception:
            logger.warning("Failed to load OCR PDF font from %s", font_path, exc_info=True)
    pdf.set_font("Helvetica", "B", 14)
    return False


def image_to_pdf(
    image_path: str,
    output_path: str,
    *,
    title: Optional[str] = None,
) -> str:
    """
    Convert an image to a PDF containing the OCR-extracted text.

    The generated PDF has:
    - A header line with the original filename and a title (if given)
    - The full extracted text formatted in a readable layout

    Args:
        image_path: Absolute path to the source image.
        output_path: Absolute path for the generated PDF.
        title: Optional title to display at the top of the PDF.

    Returns:
        The output_path on success.
    """
    try:
        from fpdf import FPDF
    except ImportError:
        raise ImportError("fpdf2 is not installed. Run: pip install fpdf2")

    # Extract text via OCR
    extracted_text = extract_text_from_image(image_path)
    if not extracted_text.strip():
        extracted_text = "(No text could be extracted from this image.)"

    source_name = Path(image_path).name

    # Build PDF
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.add_page()

    unicode_font = _apply_pdf_font(pdf)
    header = title if title else f"OCR: {source_name}"
    pdf.cell(0, 10, header, new_x="LMARGIN", new_y="NEXT")

    if unicode_font:
        pdf.set_font("VidyaOCRUnicode", "", 8)
    else:
        pdf.set_font("Helvetica", "", 8)
    pdf.set_text_color(128, 128, 128)
    pdf.cell(
        0,
        6,
        f"Source: {source_name} | Generated by VidyaOS OCR",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    # Body text
    pdf.set_text_color(0, 0, 0)
    if unicode_font:
        pdf.set_font("VidyaOCRUnicode", "", 11)
    else:
        pdf.set_font("Helvetica", "", 11)

    for line in extracted_text.split("\n"):
        line = line.strip()
        if not line:
            pdf.ln(4)
            continue
        if unicode_font:
            pdf.multi_cell(0, 6, line)
        else:
            safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
            pdf.multi_cell(0, 6, safe_line)

    pdf.output(output_path)
    logger.info("Generated PDF at %s (%d chars)", output_path, len(extracted_text))
    return output_path


def image_bytes_to_pdf(
    content: bytes,
    output_path: str,
    *,
    suffix: str = ".png",
    title: Optional[str] = None,
    source_name: Optional[str] = None,
) -> OCRExtractionResult:
    """Run OCR on image bytes, write a text PDF, and return OCR metadata."""
    result = extract_ocr_result_from_image_bytes(content, suffix=suffix)
    temp_path: Path | None = None
    source_label = source_name or f"ocr_input{suffix}"
    try:
        with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
            tmp.write(content)
            temp_path = Path(tmp.name)
        extracted_text = result.text if result.text.strip() else "(No text could be extracted from this image.)"
        try:
            from fpdf import FPDF
        except ImportError:
            raise ImportError("fpdf2 is not installed. Run: pip install fpdf2")

        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=20)
        pdf.add_page()
        unicode_font = _apply_pdf_font(pdf)
        header = title if title else f"OCR: {source_label}"
        pdf.cell(0, 10, header, new_x="LMARGIN", new_y="NEXT")
        if unicode_font:
            pdf.set_font("VidyaOCRUnicode", "", 8)
        else:
            pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(128, 128, 128)
        pdf.cell(
            0,
            6,
            f"Source: {source_label} | Generated by VidyaOS OCR",
            new_x="LMARGIN",
            new_y="NEXT",
        )
        pdf.ln(4)
        pdf.set_text_color(0, 0, 0)
        if unicode_font:
            pdf.set_font("VidyaOCRUnicode", "", 11)
        else:
            pdf.set_font("Helvetica", "", 11)
        for line in extracted_text.split("\n"):
            line = line.strip()
            if not line:
                pdf.ln(4)
                continue
            if unicode_font:
                pdf.multi_cell(0, 6, line)
            else:
                safe_line = line.encode("latin-1", errors="replace").decode("latin-1")
                pdf.multi_cell(0, 6, safe_line)
        pdf.output(output_path)
        logger.info("Generated PDF at %s (%d chars)", output_path, len(extracted_text))
        return result
    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)


def is_image_file(filename: str) -> bool:
    """Check whether the filename has an image extension."""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in IMAGE_EXTENSIONS


def validate_image_size(content: bytes) -> None:
    """Raise ValueError if the image content exceeds the size limit."""
    if len(content) > MAX_IMAGE_SIZE:
        raise ValueError(
            f"Image exceeds {MAX_IMAGE_SIZE // (1024 * 1024)}MB limit."
        )
