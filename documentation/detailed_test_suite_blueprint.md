# Detailed Test Suite Blueprint

Date: 2026-03-30

## Purpose

Define the complete testing structure needed to keep the AI learning system production-ready across:

- ingestion
- OCR
- RAG retrieval and grounding
- LLM orchestration
- study-tool generation
- WhatsApp workflows
- UI-to-backend integration
- release-gate and observability behavior

This document is not just a list of tests that already exist. It separates:

- `already covered`
- `should remain mandatory`
- `still missing or should be expanded`

## 1. Test Strategy

The system needs five test layers:

1. unit and service tests for deterministic business logic
2. route and integration tests for API behavior
3. evaluation tests for retrieval, OCR, intent, and grounding quality
4. browser E2E tests for real user flows
5. staging and release-gate tests for live external systems

Rule of thumb:

- if the logic is pure or mockable, test it in `backend/tests/`
- if the behavior depends on grounded output quality, test it in `backend/tests/evaluation/`
- if the risk is UI state, rendering, or browser wiring, test it in `frontend/tests/e2e/`
- if the dependency is real WhatsApp or real provider behavior, capture it in staging scripts and evidence docs

## 2. Current Test Locations

### Backend

- Core backend tests: `backend/tests/`
- Evaluation and quality gates: `backend/tests/evaluation/`
- Integration-only webhook coverage: `backend/tests/integration/`
- OCR fixtures: `backend/tests/fixtures/ocr/`

### Frontend

- Browser E2E tests: `frontend/tests/e2e/`

### Documentation-driven release checks

- [full_system_audit_report.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/full_system_audit_report.md)
- [production_certification_execution_checklist.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/production_certification_execution_checklist.md)
- [whatsapp_release_gate.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_release_gate.md)
- [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md)
- [ocr_manual_qa_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/ocr_manual_qa_script.md)

## 3. Mandatory Suite Map

### A. Backend route and service regression suite

Purpose:
Protect core backend behavior from silent regressions.

Keep in:
- `backend/tests/`

Already covered:
- AI query routing
- notebook retrieval
- WhatsApp gateway and integration
- OCR integration and audit
- queue and alerting behavior
- auth, security, rate limiting, upload security

Must remain mandatory:
- `backend/tests/test_ai_query_routes.py`
- `backend/tests/test_notebook_retrieval.py`
- `backend/tests/test_whatsapp_gateway.py`
- `backend/tests/test_whatsapp_integration.py`
- `backend/tests/test_ocr_integration.py`
- `backend/tests/test_ocr_audit.py`
- `backend/tests/test_ai_queue.py`
- `backend/tests/test_metrics_registry.py`
- `backend/tests/test_alerting.py`
- `backend/tests/test_security_regressions.py`

Still needed or should be expanded:
- add direct route coverage for WhatsApp release-gate snapshot edge cases:
  - missing metrics
  - partial analytics
  - stale snapshot timestamps
- add stronger tests around OCR confidence propagation on every OCR-enabled route:
  - student uploads
  - teacher uploads
  - teacher attendance import
  - teacher marks import
  - admin onboarding
- add explicit async failure/retry tests for queued WhatsApp audio/video jobs

Recommended new files:
- `backend/tests/test_whatsapp_release_gate.py`
- `backend/tests/test_ocr_route_metadata.py`
- `backend/tests/test_whatsapp_media_queue_failures.py`

### B. Evaluation and quality gate suite

Purpose:
Verify that the system is not merely functional, but grounded and useful.

Keep in:
- `backend/tests/evaluation/`

Already covered:
- OCR benchmark
- retrieval benchmark
- RAGAS-lite evaluation
- textbook feature grounding
- intent classifier benchmark

Must remain mandatory:
- `backend/tests/evaluation/test_ocr_benchmark.py`
- `backend/tests/evaluation/test_retrieval_benchmark.py`
- `backend/tests/evaluation/test_textbook_feature_grounding.py`
- `backend/tests/evaluation/test_intent_classifier_benchmark.py`

Optional-but-useful when dependency exists:
- `backend/tests/evaluation/test_ragas_evaluation.py`

Still needed or should be expanded:
- add evaluation rows for weak-topic remediation
- add evaluation rows for perturbation mode
- add evaluation rows for audio overview and video overview
- add multilingual WhatsApp intent classification cases that mix English, Hindi, and Marathi in one utterance
- add grounding evaluation for same-message WhatsApp link or media plus follow-up question

Recommended new files:
- `backend/tests/evaluation/test_whatsapp_grounded_followups.py`
- `backend/tests/evaluation/test_multilingual_intent_routing.py`
- `backend/tests/evaluation/test_extended_study_tool_grounding.py`

### C. OCR-specific system suite

Purpose:
Ensure OCR works as a universal input method, not just as a backend helper.

Keep in:
- `backend/tests/`
- `backend/tests/evaluation/`
- `frontend/tests/e2e/`

Already covered:
- benchmarked OCR corpus
- OCR route integration
- admin/student/teacher browser review slices

Must remain mandatory:
- OCR benchmark fixture gate
- OCR integration tests
- OCR review browser tests

Still needed or should be expanded:
- add route tests for unsupported image types and oversized images
- add OCR failure messaging tests for blur/low confidence on every structured import flow
- add browser coverage for teacher attendance OCR and teacher marks OCR
- add browser coverage for student upload retry or edit-after-preview cases

Recommended new files:
- `backend/tests/test_ocr_failure_modes.py`
- `frontend/tests/e2e/teacher-ocr-imports.spec.ts`
- `frontend/tests/e2e/student-upload-review-retry.spec.ts`

### D. RAG and notebook-scoped behavior suite

Purpose:
Guarantee that all major AI features use the same knowledge base and fail closed when context is missing.

Keep in:
- `backend/tests/`
- `backend/tests/evaluation/`

Already covered:
- notebook retrieval
- textbook feature grounding
- citation behavior
- fail-closed empty-context behavior

Must remain mandatory:
- retrieval benchmark
- notebook retrieval tests
- citation tests
- textbook feature grounding tests

Still needed or should be expanded:
- add explicit tests that every supported tool mode uses notebook-scoped retrieval, not ad hoc prompting
- add tests that cross-tenant notebook leakage cannot occur through follow-up jobs or WhatsApp flows
- add tests for stale or deleted notebook references in queued workflows

Recommended new files:
- `backend/tests/test_rag_tool_mode_scoping.py`
- `backend/tests/test_notebook_job_scope_regressions.py`

### E. LLM orchestration suite

Purpose:
Verify that the orchestrator chooses the correct path, injects context, and degrades safely.

Keep in:
- `backend/tests/`
- `backend/tests/evaluation/`

Already covered:
- orchestrator routing
- admin assistant fallback
- mode-specific study tool grounding

Must remain mandatory:
- `backend/tests/test_agent_orchestrator.py`
- `backend/tests/test_ai_gateway_errors.py`
- `backend/tests/evaluation/test_textbook_feature_grounding.py`

Still needed or should be expanded:
- add explicit tests for no-context rejection across every grounded feature mode
- add tests for fallback behavior when LLM provider is slow or unavailable during queued completion
- add tests that structured outputs remain schema-valid for quiz, flashcards, mind map, flowchart, and concept map

Recommended new files:
- `backend/tests/test_llm_fail_closed_modes.py`
- `backend/tests/test_structured_tool_output_contracts.py`

### F. WhatsApp workflow suite

Purpose:
Protect the messaging channel as a first-class product surface.

Keep in:
- `backend/tests/`
- `backend/tests/evaluation/`
- staging docs

Already covered:
- webhook verification
- OTP linking
- deduplication
- rate limiting
- text, media, link, and same-message follow-up flows
- queued media ingestion behavior
- release-gate snapshot route

Must remain mandatory:
- `backend/tests/test_whatsapp_gateway.py`
- `backend/tests/test_whatsapp_integration.py`
- `backend/tests/test_whatsapp.py`

Still needed or should be expanded:
- add deterministic tests for mixed-language intent-to-tool routing over WhatsApp
- add tests for long-running queued media jobs that complete after session context changes
- add tests for notification failure or outbound send retry behavior
- add live staging evidence after each release candidate, using:
  - [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md)
  - [whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_evidence_template.md)

Recommended new files:
- `backend/tests/test_whatsapp_multilingual_routing.py`
- `backend/tests/test_whatsapp_async_completion_state.py`
- `backend/tests/test_whatsapp_outbound_retries.py`

### G. Frontend browser E2E suite

Purpose:
Verify real user journeys through the browser against the built app.

Keep in:
- `frontend/tests/e2e/`

Already covered:
- smoke entry
- student upload OCR-aware flow
- student study-tool generation
- admin dashboard metrics visibility
- admin queue
- OCR review flows for admin, student, teacher

Must remain mandatory:
- `frontend/tests/e2e/smoke.spec.ts`
- `frontend/tests/e2e/student-learning-flows.spec.ts`
- `frontend/tests/e2e/ocr-review-flows.spec.ts`
- `frontend/tests/e2e/admin-dashboard.spec.ts`
- `frontend/tests/e2e/admin-queue.spec.ts`

Still needed or should be expanded:
- add student tools failure-path coverage for queued jobs timing out
- add browser coverage for teacher attendance OCR import
- add browser coverage for teacher marks OCR import
- add browser coverage for WhatsApp operator dashboard actions if a UI exists
- add browser coverage for upload progress, retry, and cancellation behaviors
- split the suite into:
  - smoke
  - critical-path regression
  - slower operator/admin regression

Recommended new files:
- `frontend/tests/e2e/teacher-academic-imports.spec.ts`
- `frontend/tests/e2e/upload-resilience.spec.ts`
- `frontend/tests/e2e/student-tool-failure-paths.spec.ts`

### H. Performance and observability suite

Purpose:
Prevent production regressions that only show up as slowness, queue backup, or metric blind spots.

Keep in:
- `backend/tests/`
- `documentation/`

Already covered:
- metrics registry
- alerting
- queue instrumentation

Must remain mandatory:
- `backend/tests/test_metrics_registry.py`
- `backend/tests/test_alerting.py`
- `backend/tests/test_ai_queue.py`

Still needed or should be expanded:
- add tests that every critical stage emits timing metrics:
  - transcription
  - embedding
  - retrieval
  - generation
  - queued completion
- add tests for alert thresholds crossing after minimum sample volume
- add benchmark or soak script for queue backlog and long media jobs

Recommended new files:
- `backend/tests/test_pipeline_stage_metrics.py`
- `backend/tests/test_latency_budget_alert_thresholds.py`
- `documentation/performance_soak_test_script.md`

## 4. Release-Gate Test Groups

These are the minimum release gates that should be enforced before production deployment.

### Gate 1: backend regression

Run:

```powershell
python -m pytest -q backend/tests
```

Expected:

- all backend route, service, and integration tests pass

### Gate 2: evaluation and grounding

Run:

```powershell
python -m pytest -q backend/tests/evaluation
```

Expected:

- OCR benchmark passes
- retrieval benchmark passes
- grounding suite passes
- intent benchmark passes

### Gate 3: browser smoke

Run:

```powershell
npm run test:e2e:smoke
```

Expected:

- core UI flows pass in CI on every normal change

### Gate 4: browser full regression

Run:

```powershell
npm run test:e2e:full
```

Expected:

- all maintained browser journeys pass before release candidates

### Gate 5: live WhatsApp staging

Run:

- execute [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md)
- capture evidence with [whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_evidence_template.md)

Expected:

- real device
- real webhook
- real outbound replies
- release-gate snapshot exported before and after the run

## 5. Priority Test Additions

These are the highest-value suites still worth adding next.

### Priority 1

- `backend/tests/test_ocr_route_metadata.py`
- `backend/tests/test_whatsapp_media_queue_failures.py`
- `backend/tests/test_structured_tool_output_contracts.py`
- `frontend/tests/e2e/teacher-academic-imports.spec.ts`

Why:

- they close practical production risks that are not fully covered yet

### Priority 2

- `backend/tests/evaluation/test_whatsapp_grounded_followups.py`
- `backend/tests/test_notebook_job_scope_regressions.py`
- `frontend/tests/e2e/upload-resilience.spec.ts`
- `backend/tests/test_pipeline_stage_metrics.py`

Why:

- they improve release confidence under async, queued, and failure-prone conditions

### Priority 3

- `backend/tests/evaluation/test_extended_study_tool_grounding.py`
- `backend/tests/test_whatsapp_outbound_retries.py`
- `frontend/tests/e2e/student-tool-failure-paths.spec.ts`

Why:

- they harden lower-frequency but still production-relevant cases

## 6. Ownership Guidance

### Backend engineer

Own:

- route regressions
- queue behavior
- WhatsApp workflow tests
- metrics and alerting tests
- retrieval and scope regressions

### AI/RAG engineer

Own:

- grounding suites
- retrieval benchmark
- OCR benchmark
- multilingual intent and routed grounding evaluation

### Frontend engineer

Own:

- browser smoke and regression suites
- OCR review/edit flows
- upload failure and retry flows
- dashboard/operator visibility flows

### QA / release owner

Own:

- live staging script execution
- evidence capture
- release-gate pass/fail sign-off

## 7. Definition of “Tested Enough”

The system should only be called production-ready when all of the following are true:

- backend regression suite passes
- evaluation suite passes
- browser smoke suite passes in CI
- browser full suite passes for release candidates
- OCR benchmark remains green
- WhatsApp staging script is executed on a real device with documented evidence
- known low-confidence OCR paths still show review-first UX instead of silent auto-commit
- grounded features fail closed when context is missing

## 8. Immediate Recommendation

If only one new test bundle is added next, add this:

1. `backend/tests/test_ocr_route_metadata.py`
2. `backend/tests/test_whatsapp_media_queue_failures.py`
3. `frontend/tests/e2e/teacher-academic-imports.spec.ts`
4. `backend/tests/test_structured_tool_output_contracts.py`

That set gives the best near-term gain because it protects:

- OCR metadata consistency
- async WhatsApp recovery behavior
- structured-import browser UX
- schema integrity of the most visible AI outputs
