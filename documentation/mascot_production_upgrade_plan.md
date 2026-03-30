# Mascot Production Upgrade Plan

**Date:** 2026-03-30  
**Current baseline:** shared mascot orchestration, web shell, assistant pages, and WhatsApp delegation are implemented  
**Goal:** move the mascot from a strong MVP into a production-level central operator with broad feature parity, safe execution, and release-grade validation.

## 1. Objective

Make the mascot the default conversational control layer for the platform across:

- website interface
- WhatsApp
- role-scoped assistant pages
- notebook-aware study workflows
- OCR and document ingestion

The mascot is considered production-level only when users can complete the major learning workflows through it without falling back to separate pages for core operations.

## 2. Current State

Already implemented:

- shared orchestration and intent handling
- notebook create / rename / archive flows
- study tool generation
- grounded query modes
- URL and YouTube ingestion
- direct web mascot file/image upload with OCR and RAG ingestion
- role-aware navigation
- web launcher + assistant pages
- WhatsApp adapter into mascot orchestration
- confirmation support for high-risk actions
- teacher roster, attendance, and marks imports through mascot upload + confirmation
- teacher insights, doubt heatmap, and assessment generation through mascot
- parent child progress summary and admin release-gate summary through mascot
- admin onboarding/setup progress summary and AI review summary through mascot
- admin teacher/student onboarding imports through mascot upload + confirmation

Main gaps:

1. the live WhatsApp mascot staging/device certification run still needs to be executed
2. production sign-off still depends on captured operator evidence from that run

## 3. Production-Level Definition

The mascot is production-level only when all of the following are true:

1. Users can upload documents and images directly through the mascot in the web UI.
2. The mascot can trigger the major notebook, ingestion, study-tool, OCR, and navigation workflows for all supported roles.
3. Sensitive or destructive actions are confirmation-gated and auditable.
4. Web and WhatsApp use the same action contract and notebook/session continuity rules.
5. Mascot behavior is covered by backend, browser, and WhatsApp regression suites.
6. Mascot action latency, failure rate, and fallback behavior are observable.

## 4. Phase Plan

### Phase 1: Direct Ingestion and Core Workflow Parity

**Objective**

Remove the biggest MVP limitation by allowing direct file/image upload into the mascot and tightening the core web workflow around notebook-scoped ingestion.

**Scope**

- add multipart mascot upload endpoint
- support file and image attachments in the mascot panel
- run OCR automatically for image uploads
- ingest uploaded content into notebook-scoped RAG
- allow optional same-turn prompt after upload
- return upload metadata, OCR confidence, and next-step suggestions

**Primary files**

- [backend/src/domains/platform/routes/mascot.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/routes/mascot.py)
- [backend/src/domains/platform/services/mascot_orchestrator.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/mascot_orchestrator.py)
- [backend/src/domains/platform/services/mascot_schemas.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/mascot_schemas.py)
- [frontend/src/lib/api.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/lib/api.ts)
- [frontend/src/components/mascot/MascotShell.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/components/mascot/MascotShell.tsx)
- [frontend/src/components/mascot/MascotPanel.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/components/mascot/MascotPanel.tsx)

**Acceptance criteria**

1. The mascot panel accepts document/image attachments directly.
2. Uploaded files are indexed into the same RAG system as the standard upload routes.
3. Image uploads return OCR metadata and warnings in the mascot response.
4. Users can upload plus ask a follow-up in one flow.
5. Browser and backend tests cover the new path.

### Phase 2: Cross-Role Action Catalog Expansion

**Objective**

Expand mascot control from learning actions into the major teacher, admin, and parent workflows that still require direct page interaction.

**Scope**

- teacher attendance and marks operations
- teacher roster/import flows
- admin onboarding and review surfaces
- parent reporting shortcuts and safe child-insight actions
- saved artifact actions and notebook organization flows

**Acceptance criteria**

1. The mascot can trigger the main teacher/admin role actions that are already implemented elsewhere.
2. Permissions are enforced through the existing role boundaries.
3. Risky mutations are gated behind confirmation.

### Phase 3: Command System Hardening

**Objective**

Make mascot interpretation more deterministic, safer, and more consistent across channels.

**Scope**

- richer entity extraction
- deterministic fallback parsing
- confirmation expansion
- idempotency for state-changing actions
- better ambiguity handling

**Acceptance criteria**

1. Mixed-language commands resolve consistently across web and WhatsApp.
2. Ambiguous requests ask for clarification instead of guessing.
3. Repeat or retried requests do not accidentally duplicate stateful changes.

**Current status**

- deterministic fallback parsing is implemented
- ambiguity handling is implemented for conflicting page navigation and notebook-name resolution
- session-level idempotency is implemented for state-changing mascot mutations
- notebook-targeted actions now fail closed when the requested notebook is inaccessible
- teacher attendance and marks confirmations now recheck class and subject ownership at execution time
- remaining work is broader confirmation expansion

### Phase 4: WhatsApp Production Parity

**Objective**

Push the mascot from “WhatsApp-capable” to “WhatsApp-first usable” for the same core platform actions.

**Scope**

- same shared action contract as web
- better compact formatting for structured outputs
- confirmation loops over WhatsApp
- notebook-aware follow-up after upload/link ingestion
- broader mixed-language regression coverage

**Acceptance criteria**

1. Core study and ingestion flows work equally through WhatsApp.
2. Confirmation messages are understandable and safe.
3. Live staging evidence can be collected for mascot-driven WhatsApp flows.

**Current status**

- WhatsApp already delegates through the shared mascot orchestration path
- compact quiz, flashcard, mind map, flowchart, and concept map formatting is implemented for mascot study-tool responses
- confirmation loops are implemented for risky mascot actions on WhatsApp
- notebook continuity is implemented for mascot-selected WhatsApp scope carry-over
- focused local WhatsApp regression coverage is implemented for formatting, confirmations, and notebook continuity
- the remaining work is now the real staging/device certification run and any gaps discovered there

**Detailed execution plan**

- [mascot_phase4_whatsapp_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_phase4_whatsapp_plan.md)

### Phase 5: Web UX Productization

**Objective**

Turn the mascot from a functional shell into a polished operator experience.

**Scope**

- page-aware suggestions
- better attachment affordances
- action/result cards
- richer assistant landing pages
- context badges for active notebook and route

**Acceptance criteria**

1. The mascot feels native to each role surface.
2. The user can tell what notebook/page context the mascot is acting on.
3. Follow-up actions are obvious without extra prompting.

**Current status**

- active notebook context is now surfaced directly in the mascot panel
- route-aware page context badges are now surfaced from stored page metadata
- page-aware guidance copy is now shown in the shell for assistant, teacher, and admin surfaces
- mascot suggestions now use role, route, notebook scope, and page entity together for stronger operator prompts
- assistant pages now have role-specific landing layouts
- mascot result cards now surface workflow badges, artifact summaries, navigation actions, and inline next-step chips
- mascot upload affordances now show supported formats, selected-file metadata, and clearer ingest-vs-follow-up guidance
- mascot stage metrics now cover interpretation, execution, confirmation, and upload
- mascot actions now persist audit rows tied to the shared `trace_id`
- mascot-specific failure-rate alerts now run through the shared alerting system
- mascot now exposes a release-gate snapshot endpoint and admin dashboard operator view
- mascot now exposes a prefilled release-gate evidence export for operator copy/sign-off
- mascot admin tooling now exposes a combined mascot + WhatsApp staging packet copy flow for live-device certification
- mascot now exposes a backend `staging-packet` export so the combined certification packet is available through API and dashboard alike
- mascot release-gate documentation and evidence template are now in place
- Phase 5 is complete; the only remaining production gate is live WhatsApp mascot staging evidence

### Phase 6: Reliability, Audit, and Release Gate

**Objective**

Add the operational layer needed for production ownership.

**Scope**

- audit logs for mascot actions
- stage metrics and failure counters
- fallback/error taxonomy
- browser/WhatsApp/backend release gates
- operator dashboards and traceability

**Acceptance criteria**

1. Mascot actions are measurable and debuggable.
2. Failure handling is consistent and actionable.
3. Production rollout can be gated on objective evidence.

## 5. Execution Order

Implement in this order:

1. Phase 1: direct ingestion and core workflow parity
2. Phase 2: cross-role action catalog expansion
3. Phase 3: command system hardening
4. Phase 4: WhatsApp production parity
5. Phase 5: web UX productization
6. Phase 6: reliability, audit, and release gate

## 6. Immediate Next Step

Continue with Phase 6 by adding:

- live WhatsApp mascot staging evidence and final sign-off

## 7. Status Summary

- Local mascot production implementation is complete across backend, browser, and WhatsApp regression layers.
- Mascot-specific observability, alerting, audit logging, release-gate metrics, and admin operator visibility are implemented.
- The remaining open work is external certification, not core engineering:
  - run [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md)
  - capture evidence in [mascot_release_gate_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_release_gate_evidence_template.md)
  - record final mascot production sign-off
