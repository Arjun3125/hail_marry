# OCR Benchmark Report

**Date:** 2026-03-30  
**Purpose:** Track OCR accuracy across multilingual, mixed-language, and handwriting fixtures.

## 1. Fixture Coverage

Record how many fixture pairs are present per category.

| Category | Fixture Count | Notes |
| --- | --- | --- |
| printed_english | 1 | IIIT5K sample |
| printed_hindi | 1 | apjanco/hindi-ocr sample |
| printed_marathi | 1 | Marathi signboard (Wikimedia Commons) |
| mixed_en_hi | 1 | Spitting sign (Wikimedia Commons) |
| mixed_hi_mr | 1 | Phursungi station sign (Wikimedia Commons) |
| mixed_en_mr | 1 | Beware sign (Wikimedia Commons) |
| handwriting_neat | 1 | IAM Sentences sample |
| handwriting_messy | 1 | Marathi handwritten sample |
| classroom_board | 1 | Einstein formula blackboard (Wikimedia Commons) |
| low_light_skew | 1 | ICDAR2015 sample |

## 2. Accuracy Metrics

Report aggregate metrics for each category.

| Category | Character Accuracy | Word Accuracy | Edit Distance (avg) | Notes |
| --- | --- | --- | --- | --- |
| printed_english | 0.33 | 0.00 | 2.0 | 1 sample; CPU easyocr |
| printed_hindi | 0.00 | 0.00 | 61.0 | 1 sample; CPU easyocr |
| printed_marathi | 0.00 | 0.33 | 2.0 | 1 sample; CPU easyocr |
| mixed_en_hi | 0.41 | 0.33 | 7.0 | 1 sample; CPU easyocr |
| mixed_hi_mr | 0.36 | 0.33 | 15.0 | 1 sample; CPU easyocr |
| mixed_en_mr | 0.00 | 0.80 | 3.0 | 1 sample; CPU easyocr |
| handwriting_neat | 0.13 | 0.04 | 70.0 | 1 sample; CPU easyocr |
| handwriting_messy | 0.00 | 0.00 | 2.0 | 1 sample; CPU easyocr |
| classroom_board | 0.00 | 0.00 | 6.0 | 1 sample; CPU easyocr |
| low_light_skew | 0.00 | 0.00 | 15.0 | 1 sample; CPU easyocr |

## 3. Structured Import Accuracy

Use OCR-derived structured import tests to verify row extraction quality.

| Import Type | Fixture Set | Row Extraction Success | Notes |
| --- | --- | --- | --- |
| teacher_onboarding | TBD | TBD | |
| student_onboarding | TBD | TBD | |
| attendance | TBD | TBD | |
| marks | TBD | TBD | |

## 4. Benchmark Commands

```bash
pytest -q backend/tests/evaluation/test_ocr_benchmark.py
```

## 5. Fixture Log

Use this section to record when each category was populated and by whom.

| Date | Category | Count Added | Notes |
| --- | --- | --- | --- |
| 2026-03-29 | baseline | 2 | Added 1 printed_english and 1 low_light_skew fixture from HF OCR datasets. |
| 2026-03-29 | expansion | 3 | Added 1 printed_hindi fixture from apjanco/hindi-ocr, 1 handwriting_neat fixture from IAM Sentences, and 1 handwriting_messy fixture from Marathi_Handwritten. |
| 2026-03-29 | expansion | 5 | Added 1 printed_marathi, 3 mixed-language, and 1 classroom_board fixture from Wikimedia Commons. |
| 2026-03-29 | tuning | 1 | Added multi-pass OCR preprocessing (raw + standard + aggressive) with best-result selection. |
| 2026-03-30 | tuning | 1 | Added stronger candidate scoring penalties for tiny false positives, mixed-script cleanup, upscale/invert fallback passes, and revalidated the full OCR regression gate (`12 passed`). |

## 6. Observations

Summarize qualitative OCR behavior here after each run.

- EasyOCR baseline on CPU shows low accuracy for the low-light sample; needs more fixtures before conclusions.
- Mixed-language and classroom-board fixtures are now present; accuracy remains low and needs preprocessing/model tuning before go-live claims.
- The latest full regression gate now passes after tightening candidate selection for printed-English false positives and cleaning mixed-script handwriting output.
- Hard categories still remain review-heavy in practice, so the benchmark should be treated as a release guardrail, not as evidence that OCR no longer needs preview/edit UX.
