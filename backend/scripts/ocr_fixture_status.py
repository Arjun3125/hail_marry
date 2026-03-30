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
        fieldnames = reader.fieldnames or []
        for row in reader:
            rows.append(row)

    if not fieldnames:
        print("manifest.csv has no headers.")
        return 1

    for row in rows:
        filename = (row.get("filename") or "").strip()
        if not filename:
            continue
        image_path = FIXTURE_DIR / filename
        text_path = image_path.with_suffix(".txt")
        row["image_status"] = "present" if image_path.exists() else "missing"
        row["text_status"] = "present" if text_path.exists() else "missing"

    with MANIFEST.open("w", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print("Updated fixture statuses in manifest.csv.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
