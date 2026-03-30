from __future__ import annotations

from io import BytesIO
from pathlib import Path
from time import sleep
from urllib.request import urlopen

from datasets import load_dataset
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "ocr"

DATASET_TARGETS = [
    {
        "dataset": "MiXaiLL76/IIIT5K_OCR",
        "split": "train",
        "category": "printed_english",
        "index": 0,
    },
    {
        "dataset": "apjanco/hindi-ocr",
        "split": "train",
        "category": "printed_hindi",
        "index": 0,
    },
    {
        "dataset": "MiXaiLL76/ICDAR2015_OCR",
        "split": "train",
        "category": "low_light_skew",
        "index": 0,
    },
    {
        "dataset": "alpayariyak/IAM_Sentences",
        "split": "train",
        "category": "handwriting_neat",
        "index": 0,
        "streaming": True,
    },
    {
        "dataset": "Process-Venue/Marathi_Handwritten",
        "split": "train",
        "category": "handwriting_messy",
        "index": 0,
        "streaming": True,
    },
]

TEXT_FIELDS = ("text", "label", "gt", "transcription", "ground_truth")
IMAGE_FIELDS = ("image", "img", "image_path")
URL_TARGETS = [
    {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Marathi_sign_board.JPG",
        "category": "printed_marathi",
        "filename": "printed_marathi_001.jpg",
        "text": "महाराष्ट्र पोलिस मुख्यालय",
    },
    {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Sign_board.jpg",
        "category": "mixed_en_mr",
        "filename": "mixed_en_mr_001.jpg",
        "text": "BEWARE\nFEROCIOUS DOGS & GHOSTS\nकुत्र्या व भूतांपासून सावध रहा",
    },
    {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Spitting_is_Prohibited_(5847076727).jpg",
        "category": "mixed_en_hi",
        "filename": "mixed_en_hi_001.jpg",
        "text": "थूकना मना है\n(थूकने पर २०० रु का जुर्माना)\nSpitting is Prohibited\n(Fine of Rs. 200/- for spitting)",
    },
    {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Trilingual_signboard_of_Phursungi_Railway_Station.jpg",
        "category": "mixed_hi_mr",
        "filename": "mixed_hi_mr_001.jpg",
        "text": "फुरसुंगी\nफुरसुंगी\nPHURSUNGI",
    },
    {
        "url": "https://commons.wikimedia.org/wiki/Special:FilePath/Einstein_formula_on_blackboard_20190401.jpg",
        "category": "classroom_board",
        "filename": "classroom_board_001.jpg",
        "text": "E=mc2",
    },
]


def _extract_text(row: dict) -> str:
    for field in TEXT_FIELDS:
        if field in row and row[field]:
            return str(row[field]).strip()
    raise ValueError("No text field found in dataset row.")


def _extract_image(row: dict):
    for field in IMAGE_FIELDS:
        if field in row and row[field] is not None:
            return row[field]
    raise ValueError("No image field found in dataset row.")


def main() -> int:
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)

    for target in DATASET_TARGETS:
        dataset = load_dataset(
            target["dataset"],
            split=target["split"],
            streaming=bool(target.get("streaming")),
        )
        if target.get("streaming"):
            row = next(iter(dataset))
        else:
            row = dataset[int(target["index"])]
        text = _extract_text(row)
        image = _extract_image(row)
        filename = f"{target['category']}_001.jpg"
        image_path = FIXTURE_DIR / filename
        text_path = image_path.with_suffix(".txt")

        try:
            if hasattr(image, "mode") and image.mode not in ("RGB", "L"):
                image = image.convert("RGB")
            image.save(image_path, format="JPEG")
        except Exception as exc:
            raise RuntimeError(f"Failed to save image for {target['dataset']}: {exc}") from exc

        text_path.write_text(text, encoding="utf-8")
        print(f"Saved {image_path.name} and {text_path.name}")

    for target in URL_TARGETS:
        image_path = FIXTURE_DIR / target["filename"]
        text_path = image_path.with_suffix(".txt")
        if image_path.exists() and text_path.exists():
            continue
        with urlopen(target["url"]) as response:
            payload = response.read()
        image = Image.open(BytesIO(payload))
        if image.mode not in ("RGB", "L"):
            image = image.convert("RGB")
        image.save(image_path, format="JPEG")
        text_path.write_text(target["text"], encoding="utf-8")
        print(f"Saved {image_path.name} and {text_path.name}")
        sleep(1)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
