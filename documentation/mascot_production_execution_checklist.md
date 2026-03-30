# Mascot Production Execution Checklist

**Date:** 2026-03-30  
**Source plan:** [mascot_production_upgrade_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_production_upgrade_plan.md)  
**Purpose:** break the mascot production upgrade into concrete implementation batches with verification gates.

## Current Status

- Shared mascot orchestration is implemented.
- Assistant pages and floating launcher are live for student, teacher, admin, and parent layouts.
- WhatsApp already delegates into the mascot layer.
- Phases 1 through 6 are now implemented and locally verified.
- Backend mascot routes, browser mascot flows, WhatsApp mascot adapter regressions, alerts, and release-gate operator surfaces are in place.
- The only remaining production blocker is the live WhatsApp mascot staging/device evidence run and sign-off.

### 2026-03-30 Phase 1 update

Implemented in this pass:

- added `POST /api/mascot/upload`
- added direct file/image attachment support in the mascot panel
- reused OCR conversion and document ingestion for mascot image/document uploads
- added notebook-scoped upload persistence through the shared `Document` model
- added upload plus same-turn follow-up chaining so users can attach a file and ask a question in one flow
- added backend regression coverage for mascot upload OCR metadata and upload-follow-up chaining
- added browser coverage for file attachment upload through the mascot assistant

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py backend/tests/test_mascot_whatsapp_adapter.py` -> `8 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/routes/mascot.py` -> passed
- `npm run build` in `frontend` -> passed
- `playwright test tests/e2e/mascot-assistant.spec.ts` -> `6 passed`

### 2026-03-30 Phase 2 slice update

Implemented in this pass:

- added teacher operator summaries for class insights and doubt heatmap
- added teacher assessment generation through the mascot
- added teacher subject-aware YouTube ingestion through the mascot
- added confirmation-gated teacher roster import through mascot uploads
- added confirmation-gated teacher attendance import through mascot uploads
- added confirmation-gated teacher marks import through mascot uploads
- threaded teacher page context from attendance, marks, and classes pages into mascot uploads
- added admin setup progress summary through the mascot
- added admin AI review summary through the mascot
- added confirmation-gated admin teacher onboarding import through mascot uploads
- added confirmation-gated admin student onboarding import through mascot uploads
- threaded admin setup-wizard step context into mascot uploads
- added parent operator summary for linked-child attendance and performance
- added admin operator summary for WhatsApp release-gate health
- expanded mascot capability metadata and role-aware suggestions for these new actions
- added backend regression coverage for teacher, parent, and admin role-summary flows plus teacher assessment, YouTube ingestion, and structured import confirmations

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py backend/tests/test_mascot_whatsapp_adapter.py` -> `20 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/services/mascot_registry.py` -> passed

### 2026-03-30 Phase 3 slice update

Implemented in this pass:

- added deterministic heuristic translation fallback when LLM interpretation is unavailable for mixed-language commands
- added multi-target navigation clarification instead of guessing between pages
- added notebook ambiguity clarification when multiple notebooks match the same name hint
- added session-level idempotency tracking for state-changing mascot actions
- preserved recent mutation history across mascot session updates so duplicate suppression survives follow-up turns
- added backend regression coverage for duplicate notebook creation, ambiguous navigation, and ambiguous notebook mutations

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py backend/tests/test_mascot_whatsapp_adapter.py` -> `23 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/routes/mascot.py backend/src/domains/platform/services/mascot_registry.py backend/src/domains/platform/services/mascot_schemas.py backend/src/domains/platform/services/mascot_session_store.py` -> passed

### 2026-03-30 Phase 3 safety follow-up

Implemented in this pass:

- blocked silent fallback to global scope when a user explicitly targets a notebook they do not own
- rejected mascot uploads that point at an inaccessible notebook instead of ingesting unscoped content
- revalidated teacher class and subject ownership at confirmation-time for attendance and marks imports
- added backend regression coverage for inaccessible notebook scope, admin-only confirmation denial, forbidden teacher marks confirmation, and upload-scope rejection

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py backend/tests/test_mascot_whatsapp_adapter.py` -> `27 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/routes/mascot.py backend/src/domains/platform/services/mascot_registry.py backend/src/domains/platform/services/mascot_schemas.py backend/src/domains/platform/services/mascot_session_store.py` -> passed

### 2026-03-30 Phase 4 formatting slice

Implemented in this pass:

- added compact WhatsApp-specific study-tool formatting driven by mascot artifacts
- added readable quiz previews with numbered questions and answer options
- added readable flashcard previews with term-definition pairs
- added readable mind map previews with expanded key branches
- added readable flowchart previews with ordered step summaries
- added readable concept map previews with relationship lines
- preserved existing navigation-link formatting while suppressing web navigation payloads on WhatsApp
- added regression coverage for mascot WhatsApp quiz, flashcard, mind map, flowchart, and concept map formatting

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py backend/tests/test_mascot_whatsapp_adapter.py` -> `32 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/interfaces/whatsapp_bot/agent.py` -> passed

### 2026-03-30 Phase 4 planning update

Planned in this pass:

- created a dedicated WhatsApp production plan for the mascot phase
- split Phase 4 into formatting, confirmation loops, notebook continuity, regression coverage, and staging certification
- locked the next implementation slice to compact map/flowchart/concept-map formatting

Planning artifact:

- [mascot_phase4_whatsapp_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_phase4_whatsapp_plan.md)

### 2026-03-30 Phase 4 confirmation loop slice

Implemented in this pass:

- added WhatsApp confirmation-loop support in the mascot adapter
- mapped `confirm` and `cancel` replies to the shared mascot pending-action executor
- persisted pending mascot confirmation IDs in the WhatsApp session
- cleared pending confirmation state after approval or cancellation
- passed WhatsApp session context through the mascot adapter and deferred media follow-up path
- added adapter and gateway regressions for approve/cancel behavior and session persistence

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_whatsapp_adapter.py backend/tests/test_whatsapp_gateway.py -k "mascot or whatsapp_agent or pending_mascot_confirmation or execute_whatsapp_media_ingestion_runs_deferred_follow_up or passes_active_notebook_id"` -> `7 passed`
- `python -m py_compile backend/src/interfaces/whatsapp_bot/agent.py backend/src/domains/platform/services/whatsapp_gateway.py backend/src/interfaces/rest_api/ai/ingestion_workflows.py` -> passed

### 2026-03-30 Phase 4 notebook continuity slice

Implemented in this pass:

- returned mascot `notebook_id` through the WhatsApp adapter result contract
- updated the WhatsApp gateway to persist mascot-selected notebook scope into `active_notebook_id`
- preserved continuity after notebook-creating mascot actions so the next WhatsApp turn stays scoped
- expanded adapter and gateway regressions for notebook carry-over and the updated WhatsApp result contract

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_whatsapp_adapter.py backend/tests/test_whatsapp_gateway.py -k "mascot or whatsapp_agent or pending_mascot_confirmation or notebook_id or passes_active_notebook_id or updates_active_notebook_from_mascot_result or execute_whatsapp_media_ingestion_runs_deferred_follow_up"` -> `9 passed`
- `python -m py_compile backend/src/interfaces/whatsapp_bot/agent.py backend/src/domains/platform/services/whatsapp_gateway.py` -> passed

### 2026-03-30 Phase 4 regression coverage slice

Implemented in this pass:

- added WhatsApp mascot regressions for confirmation cancel behavior
- added WhatsApp mascot regressions proving normal queries are not hijacked by pending confirmations
- added a two-turn WhatsApp gateway regression proving notebook scope created by one mascot turn is reused on the next turn
- strengthened the local WhatsApp mascot evidence set around session continuity and confirmation safety

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_whatsapp_adapter.py backend/tests/test_whatsapp_gateway.py -k "mascot or whatsapp_agent or pending_mascot_confirmation or notebook_id or confirm or cancel or reuses_mascot_created_notebook_on_next_turn or updates_active_notebook_from_mascot_result or execute_whatsapp_media_ingestion_runs_deferred_follow_up"` -> `12 passed`
- `python -m py_compile backend/src/interfaces/whatsapp_bot/agent.py backend/src/domains/platform/services/whatsapp_gateway.py` -> passed

### 2026-03-30 Phase 4 staging package update

Prepared in this pass:

- added a mascot-specific WhatsApp staging manual test script
- added a mascot-specific WhatsApp staging evidence template
- aligned the remaining Phase 4 exit with a real device/operator run instead of more local engineering work

Artifacts:

- [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md)
- [mascot_whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_evidence_template.md)

### 2026-03-30 Phase 5 context-aware shell slice

Implemented in this pass:

- surfaced active notebook context directly in the mascot panel
- surfaced route-aware page context badges derived from stored page metadata
- added page-aware guidance copy so the mascot explains what it can do from the current surface
- preserved notebook labels after mascot-created notebook flows
- expanded browser verification for assistant, teacher classes, and admin setup wizard context visibility

Verification completed:

- `npm run build` in `frontend` -> passed
- `playwright test tests/e2e/mascot-assistant.spec.ts` -> `6 passed`

### 2026-03-30 Phase 5 suggestion-quality slice

Implemented in this pass:

- extended mascot suggestion requests to include current page entity, not just route and notebook scope
- upgraded backend mascot suggestions to use role, route, notebook scope, and page entity together
- added stronger page-aware suggestions for teacher roster, attendance, marks, setup wizard, upload, and notebook-scoped assistant flows
- expanded backend regression coverage for notebook-scoped, teacher attendance, and admin setup suggestion routing
- expanded browser verification so mascot suggestion chips are visible on student, teacher, and admin surfaces

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py` -> `34 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/routes/mascot.py` -> passed
- `npm run build` in `frontend` -> passed
- `playwright test tests/e2e/mascot-assistant.spec.ts` -> `6 passed`

### 2026-03-30 Phase 5 landing and result-card slice

Implemented in this pass:

- added a shared full-page mascot assistant layout with role-specific landing copy for student, teacher, admin, and parent assistant pages
- upgraded mascot result cards to show workflow badges, action summaries, artifact summaries, navigation actions, and inline next-step chips
- threaded inline next-step chips back into the mascot send flow
- expanded browser verification for assistant-page landing content and richer result-card rendering

Verification completed:

- `npm run build` in `frontend` -> passed
- `python -m py_compile backend/src/domains/platform/routes/mascot.py` -> passed
- `playwright test tests/e2e/mascot-assistant.spec.ts` -> `6 passed`

### 2026-03-30 Phase 5 upload-affordance slice

Implemented in this pass:

- upgraded the mascot upload composer with clearer attach affordances and supported-format guidance
- surfaced selected-file metadata in the composer, including file kind, size, and ready-to-ingest state
- added clearer upload guidance for index-only vs upload-plus-follow-up flows
- expanded browser verification for the richer attachment UX

Verification completed:

- `npm run build` in `frontend` -> passed
- `playwright test tests/e2e/mascot-assistant.spec.ts` -> `6 passed`

### 2026-03-30 Phase 6 observability slice

Implemented in this pass:

- added mascot stage-latency metrics for interpretation, execution, confirmation, and upload flows
- added persistent mascot audit rows tied to existing `trace_id` values for message, confirmation, and upload actions
- reused the existing metrics registry and trace backend instead of creating a mascot-specific observability stack
- added focused backend regressions for mascot metrics emission and audit-log persistence

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py` -> `36 passed`
- `python -m py_compile backend/src/domains/platform/services/mascot_orchestrator.py backend/src/domains/platform/routes/mascot.py` -> passed

### 2026-03-30 Phase 6 mascot alerting slice

Implemented in this pass:

- added mascot-specific failure-rate alerts on top of shared stage metrics
- reused the existing alerting path so mascot failures appear alongside queue, OCR, and latency alerts
- added configuration thresholds for mascot failure-rate alerting
- added focused alerting regressions for high mascot failure rates and low-sample suppression

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_alerting.py backend/tests/test_mascot_routes.py` -> `48 passed`
- `python -m py_compile backend/src/domains/platform/services/alerting.py backend/src/domains/platform/services/mascot_orchestrator.py backend/config.py` -> passed

### 2026-03-30 Phase 6 release-gate slice

Implemented in this pass:

- added `GET /api/mascot/release-gate-snapshot?days=7` for operator-ready mascot certification data
- added `GET /api/mascot/release-gate-evidence?days=7` for prefilled mascot sign-off draft export
- added `GET /api/mascot/staging-packet?days=7` for a backend-generated combined mascot + WhatsApp certification packet
- surfaced mascot release-gate metrics in the admin dashboard
- added dashboard copy flow for mascot evidence drafting
- added dashboard copy flow for a combined mascot + WhatsApp staging packet
- added mascot release-gate documentation and an evidence template
- added backend and browser verification for the new release-gate operator path

Artifacts:

- [mascot_release_gate.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_release_gate.md)
- [mascot_release_gate_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_release_gate_evidence_template.md)

Verification completed:

- `python -m pytest -q -p no:cacheprovider backend/tests/test_mascot_routes.py` -> `37 passed`
- `npm run build` in `frontend` -> passed
- `playwright test tests/e2e/admin-dashboard.spec.ts` -> `1 passed`

## Priority Order

1. Phase 1: direct mascot upload/image ingestion
2. Phase 2: teacher/admin/parent workflow parity
3. Phase 3: command and confirmation hardening
4. Phase 4: WhatsApp production parity
5. Phase 5: UX productization
6. Phase 6: reliability and release gate

## Phase 1: Direct Ingestion and Core Workflow Parity

### A. Backend upload route

- [x] Add `POST /api/mascot/upload`
- [x] Accept file/image upload with notebook/session/message context
- [x] Validate file type and size
- [x] Reuse OCR conversion for image uploads
- [x] Reuse RAG ingestion and embedding path
- [x] Persist `Document` metadata with notebook scope
- [x] Return mascot-compatible response payload including OCR metadata

### B. Upload + follow-up behavior

- [x] Support upload-only flow
- [x] Support upload + same-turn follow-up prompt
- [x] Preserve active notebook in mascot session
- [x] Return follow-up suggestions after ingestion

### C. Web mascot UI attachments

- [x] Add attachment button/input to the mascot panel
- [x] Show selected file state in the shell
- [x] Send multipart request through `api.mascot`
- [x] Render upload result + OCR warning/confidence in assistant responses
- [x] Keep current text-only message flow intact

### D. Verification

- [x] Add backend tests for mascot upload success
- [x] Add backend tests for image OCR metadata path
- [x] Add backend tests for upload + follow-up behavior
- [x] Add Playwright coverage for assistant upload flow
- [x] Run focused backend tests
- [x] Run mascot browser tests

### Phase 1 exit criteria

- [x] Users can upload a PDF/image directly through the mascot
- [x] Image uploads surface OCR review signals
- [x] Uploaded content is notebook-scoped and queryable
- [x] Upload + follow-up is verified in tests

## Phase 2: Cross-Role Action Catalog Expansion

### A. Teacher parity

- [x] Attendance import actions
- [x] Marks import actions
- [x] Class roster / onboarding actions
- [x] Teacher upload and YouTube flows through mascot
- [x] Teacher insight and doubt-summary actions
- [x] Teacher assessment generation through mascot

### B. Admin parity

- [x] Setup wizard shortcuts and guided actions
- [x] WhatsApp release-gate review shortcuts
- [x] Safe onboarding and review actions

### C. Parent parity

- [x] Child report summary actions
- [x] Attendance/performance insight shortcuts
- [x] Safe navigation to parent surfaces

### Phase 2 exit criteria

- [x] Major teacher/admin/parent workflows are triggerable through mascot

## Phase 3: Command System Hardening

### A. Interpretation

- [x] Expand deterministic entity extraction
- [x] Improve ambiguity handling
- [x] Add deterministic fallback parser

### B. Safety

- [x] Expand confirmation coverage
- [x] Add idempotency for sensitive state changes
- [x] Harden permission enforcement and scope checks

### Phase 3 exit criteria

- [x] Mixed-language commands are stable
- [x] Risky operations are safe by default

## Phase 4: WhatsApp Production Parity

### A. Action parity

- [x] Extend mascot action support for WhatsApp command families
- [x] Improve notebook continuity after ingestion
- [x] Add confirmation loops through WhatsApp

### B. Formatting

- [x] Compact quiz formatting
- [x] Compact flashcard formatting
- [x] Compact map/flowchart summaries

### C. Validation

- [x] Expand WhatsApp regression coverage
- [ ] Run live staging/device script for mascot-driven flows

### Phase 4 exit criteria

- [x] Core mascot workflows are channel-consistent between web and WhatsApp

## Phase 5: Web UX Productization

### A. Context and guidance

- [x] Show active notebook context
- [x] Show page-aware guidance
- [x] Add richer suggestion sets

### B. UI polish

- [x] Improve assistant page layout
- [x] Improve upload affordances
- [x] Improve action/result cards

### Phase 5 exit criteria

- [x] Mascot feels like a first-class product surface, not a utility overlay

## Phase 6: Reliability, Audit, and Release Gate

### A. Observability

- [x] Add mascot stage metrics
- [x] Add failure counters and alerts
- [x] Add traceable action logging

### B. Certification

- [x] Backend mascot suite green
- [x] Browser mascot suite green
- [ ] WhatsApp mascot staging evidence complete
- [x] Release gate documented

### Phase 6 exit criteria

- [ ] Mascot rollout has objective production evidence

## Current Release Gate

- [x] Local mascot backend verification complete
- [x] Local mascot browser verification complete
- [x] Local mascot WhatsApp regression verification complete
- [x] Mascot release-gate snapshot and admin operator view implemented
- [ ] Live WhatsApp mascot staging/device evidence captured
- [ ] Final production sign-off recorded
