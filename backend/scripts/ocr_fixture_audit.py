from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "ocr"
MANIFEST = FIXTURE_DIR / "manifest.csv"


def main() -> int:
    if not MANIFEST.exists():
        print("manifest.csv not found.")
        return 1

    rows = []
    with MANIFEST.open("r", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows.append(row)

    missing_images = []
    missing_text = []
    for row in rows:
        filename = row.get("filename", "").strip()
        if not filename:
            continue
        image_path = FIXTURE_DIR / filename
        text_path = image_path.with_suffix(".txt")
        if not image_path.exists():
            missing_images.append(filename)
        if not text_path.exists():
            missing_text.append(text_path.name)

    if missing_images or missing_text:
        print("OCR fixture audit:")
        if missing_images:
            print(f"- Missing images: {', '.join(missing_images)}")
        if missing_text:
            print(f"- Missing text: {', '.join(missing_text)}")
        return 2

    print("OCR fixture audit: all manifest entries present.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
