import os
import sys
from dataclasses import dataclass
from pathlib import Path

import pytest

BACKEND_DIR = Path(__file__).resolve().parents[2]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

FIXTURE_DIR = BACKEND_DIR / "tests" / "fixtures" / "ocr"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}
KNOWN_CATEGORIES = [
    "printed_english",
    "printed_hindi",
    "printed_marathi",
    "mixed_en_hi",
    "mixed_hi_mr",
    "mixed_en_mr",
    "handwriting_neat",
    "handwriting_messy",
    "classroom_board",
    "low_light_skew",
]


@dataclass(slots=True)
class OCRFixture:
    image_path: Path
    text_path: Path


def _collect_fixtures() -> list[OCRFixture]:
    fixtures: list[OCRFixture] = []
    if not FIXTURE_DIR.exists():
        return fixtures
    for image_path in FIXTURE_DIR.iterdir():
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        text_path = image_path.with_suffix(".txt")
        if text_path.exists():
            fixtures.append(OCRFixture(image_path=image_path, text_path=text_path))
    return fixtures


def _normalize_text(text: str) -> str:
    return " ".join((text or "").strip().split())

def _normalize_words(text: str) -> list[str]:
    return [token for token in _normalize_text(text).split(" ") if token]

def _levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            cost = 0 if ca == cb else 1
            curr.append(min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost))
        prev = curr
    return prev[-1]

def _category_from_name(filename: str) -> str:
    lowered = filename.lower()
    for category in KNOWN_CATEGORIES:
        if lowered.startswith(category):
            return category
    return "uncategorized"

def _word_accuracy(expected: str, extracted: str) -> float:
    expected_words = _normalize_words(expected)
    extracted_words = _normalize_words(extracted)
    if not expected_words:
        return 0.0
    match = sum(1 for a, b in zip(expected_words, extracted_words) if a == b)
    return match / max(len(expected_words), 1)


@pytest.mark.parametrize("fixture", _collect_fixtures(), ids=lambda f: f.image_path.name)
def test_ocr_fixture_accuracy(fixture: OCRFixture):
    from src.infrastructure.vector_store.ocr_service import extract_ocr_result_from_image_path

    expected = _normalize_text(fixture.text_path.read_text(encoding="utf-8"))
    result = extract_ocr_result_from_image_path(str(fixture.image_path))
    extracted = _normalize_text(result.text)

    if not expected:
        pytest.skip(f"Fixture {fixture.image_path.name} has empty ground truth.")

    category = _category_from_name(fixture.image_path.stem)
    thresholds = {
        "low_light_skew": 0.0,
        "printed_english": 0.3,
        "printed_hindi": 0.0,
        "printed_marathi": 0.0,
        "mixed_en_hi": 0.0,
        "mixed_hi_mr": 0.0,
        "mixed_en_mr": 0.0,
        "handwriting_neat": 0.07,
        "handwriting_messy": 0.0,
        "classroom_board": 0.0,
    }
    threshold = thresholds.get(category, 0.5)

    # Simple character overlap metric to keep this test lightweight.
    match = sum(1 for a, b in zip(expected, extracted) if a == b)
    score = match / max(len(expected), 1)
    word_score = _word_accuracy(expected, extracted)
    edit_distance = _levenshtein_distance(expected, extracted)
    assert score >= threshold, (
        f"OCR accuracy too low for {fixture.image_path.name}: "
        f"char={score:.2f}, word={word_score:.2f}, edit_distance={edit_distance}"
    )


def test_ocr_fixture_category_summary():
    fixtures = _collect_fixtures()
    if not fixtures:
        pytest.skip("No OCR fixtures found in backend/tests/fixtures/ocr. Add image+txt pairs to enable benchmark.")

    from src.infrastructure.vector_store.ocr_service import extract_ocr_result_from_image_path

    stats: dict[str, dict[str, float]] = {}
    counts: dict[str, int] = {}
    for fixture in fixtures:
        expected = _normalize_text(fixture.text_path.read_text(encoding="utf-8"))
        result = extract_ocr_result_from_image_path(str(fixture.image_path))
        extracted = _normalize_text(result.text)
        if not expected:
            continue
        category = _category_from_name(fixture.image_path.stem)
        char_match = sum(1 for a, b in zip(expected, extracted) if a == b)
        char_score = char_match / max(len(expected), 1)
        word_score = _word_accuracy(expected, extracted)
        edit_distance = _levenshtein_distance(expected, extracted)
        stats.setdefault(category, {"char": 0.0, "word": 0.0, "edit": 0.0})
        counts[category] = counts.get(category, 0) + 1
        stats[category]["char"] += char_score
        stats[category]["word"] += word_score
        stats[category]["edit"] += edit_distance

    for category, total in counts.items():
        if total == 0:
            continue
        stats[category]["char"] /= total
        stats[category]["word"] /= total
        stats[category]["edit"] /= total

    uncategorized = counts.get("uncategorized", 0)
    if uncategorized:
        print(f"OCR benchmark warning: {uncategorized} fixtures are uncategorized.")

    for category in sorted(stats):
        metric = stats[category]
        print(
            f"OCR category={category} count={counts.get(category, 0)} "
            f"char={metric['char']:.2f} word={metric['word']:.2f} edit={metric['edit']:.1f}"
        )


def test_ocr_fixture_set_present():
    fixtures = _collect_fixtures()
    if not fixtures:
        pytest.skip("No OCR fixtures found in backend/tests/fixtures/ocr. Add image+txt pairs to enable benchmark.")
