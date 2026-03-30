from __future__ import annotations

from collections import defaultdict
from pathlib import Path

import sys

BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

from src.infrastructure.vector_store.ocr_service import extract_ocr_result_from_image_path


FIXTURE_DIR = BACKEND_DIR / "tests" / "fixtures" / "ocr"
IMAGE_SUFFIXES = {".png", ".jpg", ".jpeg"}


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
    for category in (
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
    ):
        if lowered.startswith(category):
            return category
    return "uncategorized"


def main() -> int:
    fixtures = []
    for image_path in FIXTURE_DIR.iterdir():
        if image_path.suffix.lower() not in IMAGE_SUFFIXES:
            continue
        text_path = image_path.with_suffix(".txt")
        if text_path.exists():
            fixtures.append((image_path, text_path))

    if not fixtures:
        print("No fixtures found.")
        return 1

    stats = defaultdict(lambda: {"char": 0.0, "word": 0.0, "edit": 0.0, "count": 0})

    for image_path, text_path in fixtures:
        expected = _normalize_text(text_path.read_text(encoding="utf-8"))
        result = extract_ocr_result_from_image_path(str(image_path))
        extracted = _normalize_text(result.text)
        if not expected:
            continue
        category = _category_from_name(image_path.stem)
        char_match = sum(1 for a, b in zip(expected, extracted) if a == b)
        char_score = char_match / max(len(expected), 1)
        expected_words = _normalize_words(expected)
        extracted_words = _normalize_words(extracted)
        word_match = sum(1 for a, b in zip(expected_words, extracted_words) if a == b)
        word_score = word_match / max(len(expected_words), 1)
        edit_distance = _levenshtein_distance(expected, extracted)
        stats[category]["char"] += char_score
        stats[category]["word"] += word_score
        stats[category]["edit"] += edit_distance
        stats[category]["count"] += 1

    for category, row in stats.items():
        count = row["count"]
        if count == 0:
            continue
        print(
            f"{category}\tcount={count}\t"
            f"char={row['char']/count:.2f}\t"
            f"word={row['word']/count:.2f}\t"
            f"edit={row['edit']/count:.1f}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
