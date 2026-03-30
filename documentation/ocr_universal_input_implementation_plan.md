# OCR Universal Input Implementation Plan

## Goal

Make OCR a reliable, product-grade universal input method across the application so users can submit images, screenshots, scans, and photos anywhere the system currently accepts text-bearing input.

## Target Outcome

After this plan is completed, the system should support:

- typed text
- CSV/TXT imports
- uploaded documents
- screenshots
- phone-camera captures
- scanned notes
- classroom-board photos
- printed sheets
- handwriting where quality is sufficient

with this standard pipeline:

`image input -> image validation -> preprocessing -> OCR -> extracted text review/edit -> normal feature workflow`

## Current State Summary

Based on [ocr_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_system_audit_report.md):

- backend OCR exists and is now enabled across the major text-bearing upload/import routes
- student uploads, assignment submission, WhatsApp uploads, and AI grading already used OCR
- teacher KB upload, attendance import, marks import, admin student onboarding, and self-serve onboarding import were upgraded
- multilingual configuration now includes `en`, `hi`, `mr`
- major gaps are now product quality and UX, not basic backend enablement

## Definition of Done

OCR implementation is considered complete only when all of the following are true:

1. Every text-bearing input surface either:
   - accepts OCR image input directly, or
   - is explicitly documented as non-text / OCR-not-applicable.
2. The frontend exposes image/camera-based OCR input clearly.
3. Users can review and edit extracted text before final submission where structure matters.
4. OCR behavior is benchmarked on:
   - English
   - Hindi
   - Marathi
   - mixed-language content
   - printed text
   - handwriting
5. Failure handling is user-friendly and actionable.
6. Automated tests cover the critical OCR routes and structured-import paths.

## Execution Strategy

Implement in six workstreams. Execute in order.

---

## Workstream A: Input Surface Inventory and Ownership Lock

### Objective

Freeze the exact list of supported input points and prevent new upload surfaces from bypassing OCR standards.

### Tasks

1. Convert the audit table into a maintained source-of-truth document.
2. Add a lightweight architecture note that classifies each `UploadFile` route as:
   - `ocr_required`
   - `ocr_optional`
   - `ocr_not_applicable`
3. Add a regression test or lint-style guard for new `UploadFile` routes so future additions are reviewed for OCR support.

### Primary files

- [ocr_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_system_audit_report.md)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
- [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)

### Acceptance criteria

- all existing upload routes are classified
- any newly added upload route must declare OCR applicability in code review or tests

---

## Workstream B: OCR Core Quality Hardening

### Objective

Improve OCR extraction quality and make multilingual extraction more stable.

### Tasks

1. Add preprocessing helpers before OCR:
   - grayscale normalization
   - contrast enhancement
   - denoising
   - optional thresholding
   - optional deskew
2. Add a “preprocess then OCR” wrapper in the shared OCR service.
3. Add host-safe Unicode font configuration for OCR-generated PDFs.
4. Add optional OCR metadata output:
   - engine used
   - languages used
   - preprocessing applied
   - extraction length
5. Evaluate whether EasyOCR remains sufficient or whether a second OCR engine fallback is needed.

### Primary files

- [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
- [ocr_imports.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ocr_imports.py)

### Acceptance criteria

- OCR service supports preprocessing flags
- generated OCR PDFs preserve Devanagari reliably on supported hosts
- OCR diagnostics are available for debugging and QA

---

## Workstream C: Structured Import Robustness

### Objective

Make OCR-based structured imports resilient when users upload real-world attendance sheets, marks sheets, or lists.

### Tasks

1. Strengthen row parsers for:
   - student lists
   - teacher lists
   - attendance sheets
   - marks sheets
2. Add header-aware parsing and heuristic parsing for freeform OCR text.
3. Add fuzzy matching and normalization for:
   - attendance statuses
   - name spacing
   - punctuation noise
   - OCR digit confusion
4. Add review-required responses when row confidence is weak.
5. Add line-level error reporting for structured OCR imports.

### Primary files

- [ocr_imports.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ocr_imports.py)
- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)
- [onboarding.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/identity/routes/onboarding.py)

### Acceptance criteria

- OCR imports can parse both template-like and rough real-world sheets
- errors point to specific rows or lines
- ambiguous rows are not silently imported

---

## Workstream D: Frontend OCR UX

### Objective

Expose OCR clearly in the product so users understand that image input is supported and can correct extraction errors before submission.

### Tasks

1. Add OCR-oriented UI affordances where relevant:
   - `Upload Image`
   - `Scan with Camera`
   - `Import from Photo`
2. For structured inputs, show extracted text or parsed rows before final submit.
3. Allow inline correction of OCR text/rows before committing.
4. Show user-facing messages for:
   - image accepted
   - OCR in progress
   - OCR succeeded
   - OCR failed
   - OCR needs review
5. Add mobile-friendly camera capture UX where the frontend supports it.

### Likely frontend areas

- student upload / tools pages
- teacher import/upload pages
- admin onboarding/import pages
- any mobile-oriented or WhatsApp-linked upload entry points

### Acceptance criteria

- OCR is discoverable in the UI
- structured OCR imports support correction before final save
- failure states are readable and actionable

---

## Workstream E: Benchmarking and QA Certification

### Objective

Measure OCR quality instead of assuming it.

### Tasks

1. Build a benchmark corpus with labeled fixtures:
   - printed English notes
   - Hindi document
   - Marathi document
   - English/Hindi mixed screenshot
   - Hindi/Marathi mixed note
   - neat handwriting
   - messy handwriting
   - classroom-board photo
   - low-light phone image
   - skewed scan
2. Define metrics:
   - character accuracy
   - word accuracy
   - row extraction success for structured imports
   - language coverage
   - edit distance
3. Add automated OCR evaluation tests or scripts.
4. Add a manual QA checklist for phone-camera and screenshot workflows.

### Primary files

- new evaluation tests under `backend/tests/evaluation/`
- new fixture assets under a dedicated test-fixture directory
- docs under `documentation/`

### Acceptance criteria

- baseline OCR accuracy numbers are available
- mixed-language and handwriting performance is measured, not guessed
- regressions are detectable in CI or local QA runs

---

## Workstream F: Failure Handling, Review, and Observability

### Objective

Prevent silent bad OCR from causing bad system behavior.

### Tasks

1. Add explicit OCR failure categories:
   - blurry image
   - unreadable text
   - unsupported structure
   - unsupported language
   - low confidence
2. Add response metadata such as:
   - `ocr_processed`
   - `ocr_review_required`
   - `ocr_warning`
   - `ocr_languages`
3. Add structured logging for OCR outcomes.
4. Add metrics for:
   - OCR success rate
   - OCR failure rate
   - review-required rate
   - structured-import correction rate
5. Add optional trace events around OCR execution in critical workflows.

### Primary files

- [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
- OCR-consuming routes and services
- observability/logging services already present in the platform layer

### Acceptance criteria

- OCR failures are diagnosable
- review-required outputs are explicit
- production behavior can be monitored over time

---

## Recommended Implementation Order

### Phase 1: Backend hardening

1. Workstream B
2. Workstream C
3. Workstream F

Reason:
The backend should stop producing fragile OCR results before frontend UX is built around them.

### Phase 2: Product UX

1. Workstream D

Reason:
Once the backend can return structured OCR outcomes and review-required flags, the frontend can expose correction workflows cleanly.

### Phase 3: Certification

1. Workstream E
2. Workstream A final lock

Reason:
Benchmarking should validate the final implemented behavior, not an intermediate state.

---

## Immediate Next Slice

The best next implementation slice is:

### Slice 1: OCR preprocessing + structured-review metadata

Implement:

1. preprocessing hooks in [ocr_service.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/vector_store/ocr_service.py)
2. OCR result metadata object in the shared OCR layer
3. route responses that surface:
   - `ocr_processed`
   - `ocr_review_required`
   - `ocr_warning`
4. stronger parsing diagnostics in [ocr_imports.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ocr_imports.py)

Why this slice first:

- it improves actual OCR quality
- it unlocks UI review flows
- it provides the observability needed for the benchmark phase

---

## Risks

1. OCR quality may vary heavily by deployment host if fonts and OCR dependencies differ.
2. Handwriting support may remain inconsistent without a stronger model or preprocessing.
3. Aggressive heuristics for attendance/marks parsing can create false positives if not gated with review-required states.
4. Frontend review UX can become cumbersome if extraction output is noisy.

## Non-Goals

This plan does not assume:

- OCR for purely visual/logo extraction paths
- perfect handwriting recognition
- replacing all CSV workflows; OCR should complement them
- automatic acceptance of low-confidence structured imports without review

## Release Gate

Do not call OCR universal-input work complete until:

- all text-bearing upload/import routes are covered
- UI review/edit exists for high-risk structured imports
- multilingual and handwriting benchmarks are available
- OCR failure handling is explicit and measurable
- a final audit report is updated with post-implementation status

## Deliverables

When this plan is fully executed, the documentation set should include:

1. updated [ocr_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_system_audit_report.md)
2. this implementation plan
3. an execution checklist
4. a benchmark report
5. a manual QA script
6. a completion summary
