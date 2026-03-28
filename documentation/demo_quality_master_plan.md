# Demo Quality Master Plan

**Project:** VidyaOS / proxy_notebooklm  
**Date:** 2026-03-28  
**Status:** Ready for execution

## 1. Purpose

This plan converts the latest localhost deployment review into an implementation roadmap.

The main issue is not basic availability. The application runs locally, core navigation works, notebooks work, and AI Studio is usable. The problem is fidelity and trust:

- demo-mode AI behavior is misleading because several tools replay canned responses that do not match the active prompt
- API validation is too permissive for invalid or empty inputs
- some UI surfaces are visually weaker than the best part of the product
- the demo environment cannot honestly prove grounded RAG quality in its current form

This document defines the work needed to make the demo trustworthy, visually stronger, and easier to validate.

## 2. Objectives

The plan is designed to achieve five outcomes:

1. Demo AI behavior must be truthful and prompt-consistent.
2. Invalid user input must fail clearly and early.
3. AI Studio tool switching must be state-safe and predictable.
4. Student-facing UI should reach a more coherent, modern, and responsive quality bar.
5. The team must have a reliable QA path for both demo-mode checks and real RAG validation.

## 3. Current Problems

### 3.1 Demo AI fidelity

- `DEMO_MODE` currently bypasses the real RAG and generation flow in [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py).
- Several modes return stale mode-specific samples rather than outputs derived from the active prompt.
- This makes the app look functional while hiding whether the behavior is actually correct.

### 3.2 Input validation gaps

- empty queries are accepted
- invalid `mode` values are accepted
- the API returns `200` in cases that should be rejected with `400` or `422`

### 3.3 Tool-state leakage in AI Studio

- switching between tools like `Quiz` and `Flashcards` can leave stale content or stale expectations in the workspace
- the UI shell works, but the interaction model is not fully isolated per tool

### 3.4 UI hierarchy and responsiveness

- AI Studio is visually stronger than the student dashboard
- the dashboard is too dense and uses too many equal-weight cards
- mobile layouts work, but the dashboard becomes long and visually heavy
- chart containers emit Recharts size warnings

### 3.5 QA and RAG validation gap

- current demo mode is not suitable for honest RAG grounding evaluation
- there is no clearly defined localhost profile for non-demo RAG testing
- end-to-end coverage is incomplete for the highest-value student flows

## 4. Execution Strategy

Work should happen in four tracks:

1. Runtime truthfulness
2. Input and state safety
3. UX and layout refinement
4. QA and validation infrastructure

The recommended order is:

1. fix demo AI behavior
2. tighten API validation
3. fix AI Studio tool state
4. remove chart/layout issues
5. improve dashboard information hierarchy
6. add demo/live runtime labeling
7. add e2e coverage
8. add non-demo local RAG QA profile

## 5. Phase Plan

## Phase 1: Demo AI Truthfulness

**Priority:** Immediate  
**Goal:** Stop serving misleading study-tool output.

### Scope

Choose one of the following and implement it fully:

### Option A: Preferred

Run the real local Ollama-backed flow in demo mode whenever local model dependencies are available.

This means:

- do not short-circuit `/api/ai/query` to canned mode samples
- still allow demo login and seeded users
- keep lightweight demo data, but use the real query pipeline

### Option B: Acceptable fallback

If true generation must remain disabled in demo mode:

- generate canned responses dynamically from the active prompt
- label every AI response as demo content
- do not replay old unrelated outputs from stored logs

### Files to inspect

- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [ai_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_gateway.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/config.py)

### Acceptance criteria

- a `photosynthesis` query in `quiz`, `flashcards`, `mindmap`, `flowchart`, and `concept_map` produces prompt-relevant output
- responses no longer replay unrelated historical demo content
- demo runtime behavior is clearly documented

## Phase 2: API Validation Hardening

**Priority:** Immediate  
**Goal:** Reject malformed requests before execution.

### Scope

- reject empty or whitespace-only queries
- restrict `mode` to supported values
- validate `response_length` and `expertise_level` consistently
- return structured validation errors with `400` or `422`

### Files to inspect

- [ai_runtime.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/schemas/ai_runtime.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)

### Acceptance criteria

- empty query returns validation failure
- invalid mode returns validation failure
- UI surfaces display a useful error state instead of silently accepting bad input

## Phase 3: AI Studio Tool-State Isolation

**Priority:** Immediate  
**Goal:** Prevent stale content or stale prompts when switching tools.

### Scope

- reset tool-specific input state when the active tool changes
- clear or compartmentalize previous generation results where appropriate
- ensure placeholder text, examples, and output renderer match the selected tool
- ensure `Quiz` cannot leak into `Flashcards`, `Mind Map`, or other tools

### Files to inspect

- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/ai-studio/page.tsx)
- [LearningWorkspace.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/ai-studio/components/LearningWorkspace.tsx)
- [ToolRail.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/ai-studio/components/ToolRail.tsx)

### Acceptance criteria

- switching tools updates placeholder, examples, renderer, and result state correctly
- old quiz JSON does not appear in flashcards or other tool views
- browser interaction tests confirm clean switching across at least five tools

## Phase 4: Chart Sizing And Console Warning Cleanup

**Priority:** Immediate  
**Goal:** Remove layout instability and noisy warnings.

### Scope

- identify chart components rendering with width or height `-1`
- add explicit container sizing or `minHeight`
- ensure responsive chart wrappers do not mount into zero-sized containers

### Files to inspect

- student dashboard components using Recharts
- chart wrappers under [frontend/src/components](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/components)
- student overview surface under [student/overview](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/overview)

### Acceptance criteria

- no repeated Recharts width/height warnings in browser console on overview pages
- charts render correctly on desktop and mobile

## Phase 5: Demo Citation Transparency

**Priority:** Short-term  
**Goal:** Make citation trust explicit.

### Scope

Choose one:

1. enable real citations in local demo mode through live retrieval
2. label demo responses clearly as non-grounded sample output

If option 2 is used, the UI must not imply true document-grounded citations.

### Files to inspect

- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [api.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/lib/api.ts)
- AI response rendering components in student AI pages

### Acceptance criteria

- citation area either shows real grounded sources or an explicit demo disclaimer
- no empty citation shell that implies grounding when none occurred

## Phase 6: Student Dashboard UX Rework

**Priority:** Short-term  
**Goal:** Reduce density and improve task prioritization.

### Scope

Rework the dashboard around three layers:

1. Today
2. Urgent / due soon
3. Study / progress

Reduce the number of same-weight cards on first load.

Design direction:

- stronger section hierarchy
- fewer parallel panels
- more whitespace between major groups
- clearer primary actions
- secondary data behind accordions or tabs where useful

### Files to inspect

- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/overview/page.tsx)
- related dashboard widgets and cards
- shared student layout components

### Acceptance criteria

- first screen communicates the most important student tasks in under 5 seconds
- reduced visual clutter on desktop
- mobile version avoids excessively long unprioritized card stacks

## Phase 7: Mobile Layout Refinement

**Priority:** Short-term  
**Goal:** Make student pages feel intentionally mobile, not just stacked.

### Scope

- collapse secondary sections more aggressively
- reduce card padding where dense
- trim repeated headers and decorative blocks
- verify bottom navigation does not compete with workspace CTAs

### Files to inspect

- student overview page and widgets
- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/ai-studio/page.tsx)
- bottom navigation and shared shell components

### Acceptance criteria

- mobile screenshots show clear vertical rhythm
- no critical content is hidden behind bottom-nav overlap
- AI Studio mobile remains usable without crowding the input area

## Phase 8: Demo-vs-Live Runtime Labeling

**Priority:** Medium-term  
**Goal:** Make the runtime mode obvious to users and testers.

### Scope

- add a runtime badge in AI surfaces
- values should include at least `Demo` and `Live`
- badge should explain whether responses are:
  - canned
  - live generated
  - citation-grounded

### Files to inspect

- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/ai/page.tsx)
- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/student/ai-studio/page.tsx)
- runtime config or environment helpers in frontend

### Acceptance criteria

- testers can tell within one glance whether the environment is demo or live
- no ambiguity remains about whether a response is grounded

## Phase 9: End-to-End QA Coverage

**Priority:** Medium-term  
**Goal:** Ensure the highest-risk flows are executable and regression-tested.

### Mandatory coverage

- notebook creation
- notebook selection
- Q&A flow
- each study tool mode
- upload flow
- history detail view
- mobile layout smoke tests

### Files to inspect

- Playwright config and e2e test folders under [frontend](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend)

### Acceptance criteria

- CI can run at least a demo-mode smoke suite
- failures clearly identify whether the issue is route, data, rendering, or interaction

## Phase 10: Non-Demo Local RAG QA Profile

**Priority:** Medium-term  
**Goal:** Make grounded retrieval testable on localhost without manual reconfiguration each time.

### Scope

Create a dedicated local profile for honest RAG testing:

- real query path enabled
- local embedding provider available
- local vector store enabled
- seeded or uploadable materials
- no demo short-circuit for AI responses

### Files to inspect

- [config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/config.py)
- local startup scripts
- [quickstart.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/quickstart.md)

### Acceptance criteria

- one documented command path starts a real localhost RAG environment
- QA can upload a document, query it, and verify grounded citations

## 6. Work Breakdown By Layer

### Backend

- make demo response strategy truthful
- add request validation for `query`, `mode`, and other enum-like fields
- optionally expose runtime metadata in API responses
- ensure structured modes save prompt-consistent outputs only

### Frontend

- isolate tool state by mode
- surface validation errors clearly
- add runtime badge and citation disclaimers
- improve dashboard information hierarchy
- fix responsive chart sizing and mobile spacing

### QA

- add repeatable smoke tests for demo mode
- add repeatable RAG tests for non-demo local profile
- capture screenshot baselines for desktop and mobile

### Documentation

- document demo behavior honestly
- document live local RAG QA profile separately from demo mode
- document supported AI modes and validation rules

## 7. Recommended Implementation Order

### Sprint 1

- Phase 1: Demo AI Truthfulness
- Phase 2: API Validation Hardening
- Phase 3: AI Studio Tool-State Isolation
- Phase 4: Chart Sizing And Console Warning Cleanup

### Sprint 2

- Phase 5: Demo Citation Transparency
- Phase 6: Student Dashboard UX Rework
- Phase 7: Mobile Layout Refinement

### Sprint 3

- Phase 8: Demo-vs-Live Runtime Labeling
- Phase 9: End-to-End QA Coverage
- Phase 10: Non-Demo Local RAG QA Profile

## 8. Success Metrics

This plan should be considered successful when the following are true:

- demo AI outputs match the current prompt
- invalid mode and empty query are rejected
- switching AI Studio tools cannot leak stale output
- browser console is clean on key student pages
- dashboard readability improves on desktop and mobile
- testers can distinguish demo behavior from live behavior instantly
- at least one localhost profile can validate true grounded RAG behavior

## 9. Definition Of Done

The work is done when:

1. localhost demo is visually credible
2. localhost demo is behaviorally truthful
3. localhost live-RAG profile exists for real QA
4. the highest-value student flows are covered by automated e2e tests
5. the documentation no longer overstates what demo mode proves

