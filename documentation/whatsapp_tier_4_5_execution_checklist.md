# WhatsApp Tier 4.5 Execution Checklist

**Date:** 2026-03-29  
**Source plan:** [whatsapp_tier_4_5_upgrade_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_tier_4_5_upgrade_plan.md)  
**Purpose:** Convert the WhatsApp Tier 4.5 upgrade plan into concrete implementation work mapped to code files.

## 1. Priority Order

Execute in this order:

1. complete remaining AI and ERP feature parity through WhatsApp
2. finish upload and RAG parity for all inbound media and links
3. harden WhatsApp-first authentication and session behavior
4. standardize WhatsApp response design and output shaping
5. improve mixed-language interpretation and clarification behavior
6. close transport reliability and idempotency gaps
7. add production observability, acceptance tests, and release gate checks

## 2. Workstream A: Tool Parity and Orchestration

### Problem

The WhatsApp layer already supports core study tools and some ERP actions, but Tier 4.5 requires near-full parity for the priority feature surface. The remaining risk is channel drift, where WhatsApp wrappers lag behind the main application capabilities or format them inconsistently.

### Files

- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)
- [agent.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/whatsapp_bot/agent.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)

### Tasks

- Audit the WhatsApp registry against the target Tier 4.5 feature surface.
- Ensure each supported AI feature maps to one canonical backend service path.
- Remove feature-specific logic duplication between WhatsApp wrappers and web routes where possible.
- Add or complete wrappers for any missing priority features:
  - Q&A
  - study guide
  - quiz
  - flashcards
  - mind map
  - flowchart
  - concept map
  - Socratic tutor
  - debate assistant
  - essay review
- Verify role-based ERP access for student, teacher, parent, and admin intents.
- Add summary-plus-link behavior for outputs that are too visual or too long for WhatsApp alone.

### Acceptance criteria

- Every Tier 4.5 priority feature is callable from WhatsApp.
- No major study feature depends on frontend-only logic.
- ERP actions obey role restrictions consistently.
- WhatsApp tool names, prompts, and output contracts are stable and test-covered.

## 3. Workstream B: Media Ingestion and RAG Parity

### Problem

Tier 4.5 requires that files, links, and media sent over WhatsApp flow into the same ingestion and retrieval path as the main app. Core media ingestion has been improved, but parity is not complete until all supported source types and post-upload query behavior are proven end to end.

### Files

- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)
- [whatsapp.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/routes/whatsapp.py)
- [router.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/whatsapp/router.py)
- [agent.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/whatsapp/agent.py)
- [ingestion_workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/ingestion_workflows.py)
- [discovery_workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/discovery_workflows.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)

### Tasks

- Verify support for inbound:
  - PDF
  - image
  - text note
  - video reference
  - YouTube link
- Normalize all WhatsApp uploads into the same document or discovery ingestion pipeline used by the web app.
- Support caption-aware follow-up so users can send a file plus a question in one conversational flow.
- Preserve notebook scope after upload and apply it to the next retrieval-backed request.
- Ensure ingestion failure responses are actionable and user-readable.
- Add explicit tests for “upload over WhatsApp -> ingest -> query grounded content over WhatsApp”.

### Acceptance criteria

- A document or link sent through WhatsApp is queryable through WhatsApp after ingestion.
- Post-upload grounded answers use the same tenant and notebook scope as the web path.
- Failed uploads return clear remediation messages instead of generic errors.

## 4. Workstream C: Authentication and Session UX

### Problem

WhatsApp can only be a serious primary interface if phone-based identity, re-entry, active-child memory, and session continuity feel natural. The current system has role-aware session behavior, but the phone-first product flow is not fully hardened.

### Files

- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)
- [whatsapp_models.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/models/whatsapp_models.py)
- [agent.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/whatsapp_bot/agent.py)
- [whatsapp.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/services/whatsapp.py)
- [config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/config.py)

### Tasks

- Complete the WhatsApp-number-first link or signup flow.
- Ensure returning users can resume without repeated login prompts.
- Harden logout, relink, and session-expiry handling.
- Preserve active child selection for parent users across normal conversations.
- Ensure notebook scope and child scope reset safely on user switching and relink events.
- Add tests for first-time linking, returning-user re-entry, expired session, and parent child-switch behavior.

### Acceptance criteria

- A new user can link or sign in through the WhatsApp flow without admin assistance.
- Returning users keep working without repetitive authentication prompts.
- Parent child switching is explicit, stable, and does not leak context across children.

## 5. Workstream D: Response Design and WhatsApp UX

### Problem

Backend feature correctness is not enough. Outputs need to be readable and useful inside WhatsApp’s text-first constraints. The current formatting is better than before, but still uneven across feature types and long responses.

### Files

- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)
- [agent.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/whatsapp_bot/agent.py)
- [ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_queue.py)
- [ai_jobs.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai_jobs.py)

### Tasks

- Define one formatting standard for:
  - short Q&A
  - quiz
  - flashcards
  - mind map
  - flowchart summary
  - concept map summary
  - study guide
  - errors
  - progress or async job notifications
- Add chunking or continuation rules for long outputs.
- Standardize summary-plus-link fallback for diagram-like or visually dense artifacts.
- Ensure no raw JSON, raw Mermaid, or web-shaped payloads are exposed directly to users.
- Add disambiguation prompts that are short and mobile-readable.

### Acceptance criteria

- Major outputs are readable inside mobile WhatsApp.
- Long outputs are summarized or chunked predictably.
- There is one consistent user-facing style for success, failure, and async job updates.

## 6. Workstream E: LLM Interpretation and Language Normalization

### Problem

Mixed-language understanding exists, but Tier 4.5 requires benchmarked and replayable accuracy across English, Hindi, Marathi, and code-mixed educational prompts. Clarification behavior also needs to be deterministic when confidence is low.

### Files

- [agent.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/whatsapp_bot/agent.py)
- [whatsapp_tools.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/shared/ai_tools/whatsapp_tools.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [test_whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_whatsapp_gateway.py)
- [test_intent_classifier_benchmark.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/evaluation/test_intent_classifier_benchmark.py)

### Tasks

- Expand the mixed-language benchmark corpus with real educational prompts.
- Separate deterministic command aliases from LLM-based interpretation more clearly.
- Add confidence-aware clarification prompts when the request is ambiguous.
- Log normalization output, chosen route, and fallback path for replayable debugging.
- Measure intent accuracy and false-positive rate for priority WhatsApp actions.

### Acceptance criteria

- Priority mixed-language intent accuracy reaches the target benchmark threshold.
- Ambiguous requests are clarified instead of routed silently to the wrong tool.
- Tool-routing failures are diagnosable from logs and tests.

## 7. Workstream F: Channel Reliability and Transport Hardening

### Problem

Tier 4.5 requires production-stable webhook handling, duplicate suppression, outbound retry logic, and safe idempotency. The integration exists, but transport reliability has to be treated as a release-blocking engineering surface rather than an integration detail.

### Files

- [router.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/whatsapp/router.py)
- [whatsapp.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/routes/whatsapp.py)
- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)
- [whatsapp.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/services/whatsapp.py)
- [whatsapp_models.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/models/whatsapp_models.py)
- [config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/config.py)

### Tasks

- Verify webhook verification and signature enforcement paths.
- Add inbound duplicate-event suppression using Meta message identifiers.
- Make repeated webhook deliveries idempotent for tool execution and media ingestion.
- Classify outbound failures into retryable vs non-retryable.
- Add bounded retry or queue handoff for transient outbound failures.
- Add tests for webhook replay, duplicate inbound events, and outbound send failures.

### Acceptance criteria

- Duplicate webhook deliveries do not trigger duplicate user-visible actions.
- Outbound failures are logged with retry classification.
- Monitored test runs show no silent inbound or outbound message loss.

## 8. Workstream G: Production Hardening, QA, and Release Gate

### Problem

Passing unit tests is not enough to claim Tier 4.5. The channel needs operational metrics, replayable acceptance tests, and a clear release gate that blocks rollout when critical WhatsApp behaviors regress.

### Files

- [test_whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_whatsapp_gateway.py)
- [test_whatsapp_integration.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_whatsapp_integration.py)
- [test_ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_ai_queue.py)
- [sentry_config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/sentry_config.py)
- [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py)
- [ai_queue.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/ai_queue.py)

### Tasks

- Define a release gate for the WhatsApp channel with mandatory automated checks.
- Add channel-level regression coverage for:
  - auth and session
  - mixed-language routing
  - uploads and RAG retrieval
  - async jobs
  - ERP role actions
  - failure handling
- Add measurable metrics:
  - webhook success rate
  - duplicate suppression rate
  - outbound failure rate
  - routing success rate
  - upload-to-query success rate
  - visible failure rate
- Add dashboards or at minimum structured logging fields needed to build them.
- Create a staging manual test script for real-device WhatsApp validation.

### Acceptance criteria

- There is a documented release gate for the WhatsApp channel.
- Critical WhatsApp regressions are covered by automated tests.
- Operators can detect webhook, routing, and ingestion failures from telemetry.

## 9. Recommended First Implementation Slice

Start here:

1. audit the current WhatsApp registry against the target Tier 4.5 feature surface
2. list any missing or partial wrappers by role and feature
3. add one regression matrix proving each Tier 4.5 feature is callable from WhatsApp
4. then close the remaining upload-plus-follow-up parity gaps

This is the highest-leverage start because it exposes the real distance between current functionality and Tier 4.5 instead of assuming parity from individual fixes.

## 10. Suggested Status Marking

Track each workstream with one of:

- `not started`
- `in progress`
- `partially complete`
- `complete`
- `blocked`

Current status snapshot:

- `A` Tool Parity and Orchestration: complete
- `B` Media Ingestion and RAG Parity: complete
- `C` Authentication and Session UX: complete
- `D` Response Design and WhatsApp UX: complete
- `E` LLM Interpretation and Language Normalization: complete
- `F` Channel Reliability and Transport Hardening: complete
- `G` Production Hardening, QA, and Release Gate: complete

## 11. Release Gate for WhatsApp Tier 4.5

Do not claim Tier 4.5 until all of the following are true:

- all priority AI features are callable through WhatsApp
- major role-based ERP actions are accessible through WhatsApp
- WhatsApp uploads reach the same ingestion and retrieval path as the web app
- mixed-language benchmark performance meets the target threshold
- auth and session flows are stable for new and returning users
- duplicate inbound events are idempotent
- outbound failures are visible and recoverable
- outputs are WhatsApp-safe and do not expose raw internal payloads
- the channel has a repeatable automated regression suite
- staging manual validation with real devices is defined
