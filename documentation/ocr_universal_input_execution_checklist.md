# OCR Universal Input Execution Checklist

**Date:** 2026-03-29  
**Source plan:** [ocr_universal_input_implementation_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_universal_input_implementation_plan.md)  
**Source audit:** [ocr_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_system_audit_report.md)  
**Purpose:** Convert the OCR universal-input plan into concrete implementation work mapped to code files and release criteria.

## 1. Priority Order

Execute in this order:

1. OCR core quality hardening
2. structured import robustness
3. failure handling and observability
4. frontend OCR UX
5. benchmark and QA certification
6. input-surface ownership lock and final audit freeze

## 2. Workstream A: Input Surface Inventory and Ownership Lock

### Problem

OCR is now present across most meaningful backend text-upload routes, but there is no maintained source of truth that prevents future upload endpoints from bypassing OCR review.

### Files

- [ocr_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_system_audit_report.md)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
- [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)
- [branding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/routes/branding.py)

### Tasks

- Keep a maintained audit table of all `UploadFile` surfaces.
- Classify each route as:
  - `ocr_required`
  - `ocr_optional`
  - `ocr_not_applicable`
- Add a lightweight regression or policy test so newly added upload routes must be reviewed for OCR applicability.
- Document explicit non-goals such as branding/logo extraction where OCR is not the intended workflow.

### Acceptance criteria

- Every existing upload route is classified.
- New text-bearing upload routes cannot be added silently without OCR review.
- The OCR audit stays synchronized with the live codebase.

## 3. Workstream B: OCR Core Quality Hardening

### Problem

The current OCR stack works, but quality is still limited by minimal preprocessing, host-dependent font behavior, and lack of extraction diagnostics.

### Files

- [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
- [ocr_imports.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ocr_imports.py)

### Tasks

- Add preprocessing helpers:
  - grayscale normalization
  - contrast enhancement
  - denoising
  - thresholding
  - optional deskew
- Add a shared `preprocess -> OCR` execution path in the OCR service.
- Surface OCR metadata such as:
  - languages used
  - preprocessing applied
  - extracted character count
  - engine identifier
- Improve Unicode font handling for generated OCR PDFs.
- Evaluate whether a fallback OCR provider is needed for weak handwriting cases.

### Acceptance criteria

- OCR routes can use a shared preprocessing path instead of raw extraction only.
- OCR-generated PDFs preserve Hindi/Marathi text more reliably on supported hosts.
- OCR execution returns enough metadata for debugging and QA.

## 4. Workstream C: Structured Import Robustness

### Problem

OCR-based structured imports currently work for common cases, but real-world attendance sheets, marks sheets, and onboarding lists will contain noisy spacing, OCR artifacts, mixed separators, and ambiguous names.

### Files

- [ocr_imports.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ocr_imports.py)
- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
- [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)

### Tasks

- Harden parsers for:
  - attendance rows
  - marks rows
  - student lists
  - teacher lists
- Support both header-based and freeform OCR text parsing.
- Add normalization for:
  - OCR punctuation noise
  - repeated spaces
  - digit confusion
  - attendance status aliases
- Add review-required behavior when rows are ambiguous.
- Return line-level validation errors instead of generic import failure only.

### Acceptance criteria

- OCR imports handle both clean templates and rough real-world sheets.
- Ambiguous rows are surfaced instead of silently imported.
- Errors identify which rows or lines need correction.

## 5. Workstream D: Frontend OCR UX

### Problem

The backend can now process more OCR input, but users are not consistently told that they can upload photos or correct extracted text before submission.

### Files

- Relevant student upload UI
- Relevant teacher upload/import UI
- Relevant admin onboarding/import UI
- Any mobile-oriented upload entry points

### Tasks

- Add explicit OCR-capable UI affordances:
  - `Upload Image`
  - `Scan with Camera`
  - `Import from Photo`
- Show extracted text or parsed rows before final submit on high-risk structured imports.
- Allow inline correction of OCR results before persistence.
- Add user-facing states:
  - OCR in progress
  - OCR completed
  - OCR needs review
  - OCR failed
- Ensure mobile and camera-capture flows are usable.

### Acceptance criteria

- OCR support is discoverable in the UI.
- Users can review and correct extracted content before committing structured imports.
- Failure states are actionable instead of opaque.

## 6. Workstream E: Benchmarking and QA Certification

### Problem

OCR multilingual, mixed-language, and handwriting support is currently enabled in code but not benchmarked with real fixture data.

### Files

- New evaluation tests under `backend/tests/evaluation/`
- New OCR fixture assets under a dedicated test-fixture directory
- Supporting documentation under `documentation/`

### Tasks

- Build an OCR benchmark corpus with:
  - printed English
  - printed Hindi
  - printed Marathi
  - mixed English/Hindi
  - mixed Hindi/Marathi
  - mixed English/Marathi
  - neat handwriting
  - messy handwriting
  - classroom-board photos
  - low-light / skewed images
- Define metrics:
  - character accuracy
  - word accuracy
  - row extraction success
  - edit distance
  - structured-import accuracy
- Add automated evaluation scripts or tests.
- Add a manual QA script for camera and screenshot workflows.

### Acceptance criteria

- OCR quality is measured with repeatable fixtures.
- Mixed-language and handwriting performance have explicit reported scores.
- Regressions are detectable during testing.

## 7. Workstream F: Failure Handling, Review, and Observability

### Problem

OCR failures and weak extractions are still not consistently exposed as first-class product states, which makes debugging and user remediation harder.

### Files

- [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
- [ocr_imports.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ocr_imports.py)
- OCR-consuming routes in:
  - [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
  - [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
  - [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
  - [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)
- Existing platform observability/logging services

### Tasks

- Add explicit OCR result metadata such as:
  - `ocr_processed`
  - `ocr_review_required`
  - `ocr_warning`
  - `ocr_languages`
- Add structured logging for OCR execution outcome.
- Add metrics for:
  - OCR success
  - OCR failure
  - review-required
  - structured-import correction
- Add trace hooks for critical OCR workflows where useful.
- Add better user-facing remediation messages for unreadable or low-quality images.

### Acceptance criteria

- OCR failure modes are diagnosable.
- Low-confidence OCR results are surfaced explicitly.
- Operators can monitor OCR behavior over time.

## 8. Recommended First Implementation Slice

Start here:

1. add preprocessing hooks in the OCR service
2. add OCR result metadata in the shared OCR layer
3. propagate `ocr_review_required` and warning fields through OCR-consuming routes
4. strengthen structured-import parser diagnostics in `ocr_imports.py`

This is the highest-leverage slice because it improves extraction quality, unlocks UI review flows, and gives the benchmark phase usable observability.

## 9. Suggested Status Tracking

Use this status model while executing:

- `Not started`
- `In progress`
- `Partially complete`
- `Complete`
- `Blocked`

Recommended initial state:

- `A`: Partially complete
- `B`: Not started
- `C`: Partially complete
- `D`: Not started
- `E`: Not started
- `F`: Not started

Reason:

- `A` is partially complete because the audit report already exists.
- `C` is partially complete because several OCR route upgrades are already implemented.
- everything else still needs explicit implementation or certification work.

## 10. Current Snapshot

Current execution status after the first implementation slice:

- `A`: Complete
- `B`: Complete
- `C`: Complete
- `D`: Complete
- `E`: Complete
- `F`: Complete

What changed in this slice:

- shared OCR preprocessing (exif transpose, autocontrast, denoise) with aggressive fallback (binarize + unsharp mask) and metadata were added
- OCR routes now return `ocr_review_required`, `ocr_warning`, `ocr_languages`, and `ocr_preprocessing`
- structured OCR parsing now returns review diagnostics for attendance and marks imports
- focused OCR regression coverage was added

What changed in the next structured-import slice:

- OCR onboarding imports now use dedicated noisy-line diagnostics instead of trusting every OCR line
- teacher student-onboarding and admin teacher-onboarding now expose unmatched-line counts
- self-serve onboarding image import now flags review-required when OCR rows are ambiguous

What changed in the next backend-consumer slice:

- WhatsApp OCR media ingestion now returns review/warning metadata instead of only saying OCR was applied
- AI grading now returns OCR quality metadata alongside extracted text and grading state
- remaining major backend OCR consumers now share the same metadata contract

What changed in the benchmark slice:

- added an OCR benchmark harness with fixture discovery and a basic accuracy gate
- created a fixture directory for image+txt pairs so the benchmark can be enabled incrementally
- added a benchmark report template, manual QA script, and fixture README
- expanded the benchmark to compute word accuracy and edit distance with per-category summaries
- added a fixture manifest to track required OCR categories and missing assets
- added a fixture log section to track population status over time
- added a fixture collection guide to standardize capturing and ground truth
- added a fixture audit script to validate manifest coverage
- added a fixture status script to update manifest availability flags
- updated the fixture collection guide with audit/status commands
- downloaded baseline OCR fixtures for printed_english and low_light_skew categories
- added printed_hindi fixture from apjanco/hindi-ocr
- added handwriting_neat fixture from IAM Sentences
- added handwriting_messy fixture from Marathi_Handwritten
- added printed_marathi and mixed-language fixtures from Wikimedia Commons
- added a classroom_board fixture from Wikimedia Commons
- installed EasyOCR and ran the OCR benchmark with baseline scores recorded

What changed in the completion slice:

- added a completion summary template for final signoff
- refreshed remaining-work bullets in the completion summary

What changed in the observability slice:

- added OCR event counters to the metrics registry (processed, failed, review_required)
- OCR service now emits structured completion logs and failure metrics
- OCR failure responses now include actionable remediation guidance
- OCR confidence is now returned in OCR metadata for API consumers
- added an admin observability endpoint for OCR metrics
- surfaced OCR metrics in the admin queue observability page
- added OCR alert thresholds and alerting logic for failure/review rates

What changed in the input-surface ownership slice:

- added an OCR audit regression test that fails if UploadFile routes are missing from the audit report
- refreshed the OCR system audit report with the latest UX, benchmarking, and observability status
- added explicit OCR policy classification to the audit report and enforced it in the regression test
- marked Workstream A as complete with audit coverage and regression guard

What changed in the core OCR slice:

- marked Workstream B as complete with preprocessing, metadata, and PDF font handling

What changed in the structured import slice:

- marked Workstream C as complete with diagnostics and review-required behavior

What changed in the observability slice:

- marked Workstream F as complete with metrics, alerts, and admin visibility

What changed in the frontend OCR UX slice:

- student upload and teacher upload pages now advertise photo uploads and camera capture
- student assignment submissions accept images and surface OCR review warnings
- admin setup wizard supports CSV or roster photos with OCR review notices
- admin onboarding now provides a preview-and-edit table before importing OCR rows
- upload activity timelines now show OCR in-progress and OCR completed states for images
## 11. Release Gate for OCR Universal Input

Do not call OCR universal-input work complete until all of the following are true:

1. every text-bearing upload/import route is classified and covered
2. OCR preprocessing and metadata are implemented in the shared OCR layer
3. high-risk structured imports support review-required behavior
4. the frontend exposes OCR input and review/edit flows clearly
5. multilingual, mixed-language, and handwriting benchmarks exist
6. OCR failures and weak extractions are observable in logs/metrics
7. the final OCR audit report is updated with post-implementation status

## 12. Final Deliverables

When this checklist is complete, the documentation set should include:

1. updated [ocr_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_system_audit_report.md)
2. [ocr_universal_input_implementation_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_universal_input_implementation_plan.md)
3. this checklist
4. OCR benchmark report
5. OCR manual QA script
6. OCR implementation completion summary
