# VidyaOS Mitigation Execution Plan

**Date:** 2026-03-28  
**Basis:** Structural audit of codebase, configuration, routing, and documentation

---

## 1. Goal

This plan turns the audit findings into an implementation sequence that reduces risk in the right order:

1. close security and integrity holes
2. restore broken user-facing flows
3. fix data-model drift
4. converge architecture decisions
5. add verification to stop the same drift from returning

---

## 2. Guiding Decision

For the next release cycle, VidyaOS is treated as:

- a FastAPI modular monolith
- a Redis-backed worker
- an external Ollama dependency

The repository does **not** currently implement a standalone AI service. Any future extraction is deferred until the monolith is stabilized.

---

## 3. Priority Matrix

### P0 - Immediate

- Secure feature-flag administration
- Harden OpenAI-compatible auth
- Remove duplicate auth route definitions
- Normalize broken route prefixes for feature flags and branding
- Fix swapped enterprise pages and payload drift

### P1 - Short Term

- Repair notebook-scoped retrieval
- Align notebook and generated-content models with tenant rules
- Add focused regression tests for the broken flows

### P2 - Medium Term

- Consolidate provider abstractions
- Decide whether to fully keep monolith runtime or extract AI service later
- Add stronger API contract testing

---

## 4. Execution Phases

## Phase 0 - Lock Target State

**Objective:** Stop building against two contradictory architectures.

Tasks:
- Keep `README.md` and `documentation/system_docs/*` as the current source of truth
- Treat dedicated AI service references as future-state only
- Avoid new implementation work against `backend/src/domains/ai_engine/router.py`

Exit criteria:
- team aligns on `API + worker` as current runtime

## Phase 1 - Security and Integrity

**Objective:** Remove the highest-risk issues first.

Tasks:
- Require admin auth for feature-flag routes
- Add audit logs for feature-flag mutations
- Replace permissive bearer handling in `/v1/*`
- Remove duplicate auth router and QR-login declarations

Exit criteria:
- unauthenticated or non-admin access to feature-flag endpoints fails
- mutation actions are auditable

## Phase 2 - User-Facing Contract Repair

**Objective:** Make existing features usable.

Tasks:
- Normalize `/api/features` and `/api/branding` behavior
- Fix enterprise compliance/incidents page swaps
- Align frontend types with backend serializers

Exit criteria:
- admin feature-flags page works
- admin branding page works
- enterprise pages render correct payloads

## Phase 3 - Notebook RAG Repair

**Objective:** Make notebook scoping real instead of metadata-only.

Tasks:
- Add `notebook_id` support to retrieval boundary
- ensure notebook metadata participates in retrieval filtering
- verify notebook isolation in query results

Exit criteria:
- notebook A queries cannot retrieve notebook B material

## Phase 4 - Tenant Model Convergence

**Objective:** Resolve schema drift.

Tasks:
- add `tenant_id` to notebooks and generated content, or formally document a different ownership model
- backfill and index correctly
- update queries to enforce tenant and ownership checks together

Exit criteria:
- tenant policy is consistent across ERP and AI-support tables

## Phase 5 - Regression Protection

**Objective:** Prevent repeat drift.

Tasks:
- backend integration tests for feature flags, branding, notebooks, enterprise contracts, `/v1/*` auth
- Playwright tests for feature flags, branding, enterprise pages, notebook flow
- route-contract checks in CI

Exit criteria:
- the previously broken flows are covered automatically

## Phase 6 - Architecture Convergence

**Objective:** Reduce long-term confusion.

Preferred path:
- keep monolith + worker
- remove misleading “dedicated AI service” assumptions from runtime/config comments over time

Deferred path:
- extract a true AI service only after Phases 1-5 are complete

---

## 5. Initial Implementation Batch

This is the recommended first code batch:

1. secure feature-flag routes
2. align feature-flag route prefix with the frontend client
3. harden feature-flag mutation auditing
4. remove duplicate auth route declarations
5. repair notebook retrieval boundary

---

## 6. Current Execution Status

### Batch 1

- [x] Create mitigation plan document
- [ ] Secure feature-flag admin endpoints
- [ ] Add audit logging for feature-flag mutations
- [ ] Verify feature-flag route behavior
- [ ] Continue into auth deduplication and notebook retrieval fixes

---

## 7. Definition of Done for “Stabilized MVP”

VidyaOS can be considered a stabilized MVP when:

- security-sensitive admin routes enforce auth and RBAC
- documented UI routes actually work end-to-end
- notebook scoping affects retrieval, not just persistence
- tenant rules are consistent across notebook-related models
- docs match runtime topology
- the repaired flows are covered by automated tests
