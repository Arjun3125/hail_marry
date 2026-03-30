# OCR Fixture Collection Guide

**Date:** 2026-03-29  
**Goal:** Standardize how OCR benchmark fixtures are captured and labeled.

## 1. Capture Rules

1. Use original camera photos whenever possible. Avoid screenshots of text unless that is the target category.
2. Keep each image focused on a single paragraph or list (5–15 lines).
3. Store the exact ground-truth text in a `.txt` file with the same base name.
4. Preserve punctuation and line breaks in ground truth. Do not “clean up” OCR errors.

## 2. Naming Convention

`{category}_{index}.jpg` + `{category}_{index}.txt`

Example:
`printed_english_001.jpg`
`printed_english_001.txt`

## 3. Categories to Cover

- printed_english
- printed_hindi
- printed_marathi
- mixed_en_hi
- mixed_hi_mr
- mixed_en_mr
- handwriting_neat
- handwriting_messy
- classroom_board
- low_light_skew

## 4. Ground-Truth Template

Use the text as seen in the image. If the image contains:

- headings: include them
- bullet points: include bullets or dashes
- mixed languages: keep the original language order

## 5. Quality Notes

Add short notes in `backend/tests/fixtures/ocr/manifest.csv` once fixtures are added:

- lighting conditions
- handwriting style
- mixed-language structure

## 6. After Adding Fixtures

1. Run the OCR benchmark:

```bash
pytest -q backend/tests/evaluation/test_ocr_benchmark.py
```

2. Update manifest flags:

```bash
python backend/scripts/ocr_fixture_status.py
python backend/scripts/ocr_fixture_audit.py
```

3. Update `documentation/ocr_benchmark_report.md` with category scores.
