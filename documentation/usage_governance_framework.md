# Usage Governance Framework

## Overview

The platform now enforces a shared usage-governance layer across AI generation, study tools, ingestion, OCR, queued jobs, and tenant burst traffic.

Core implementation files:

- [usage_governance.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/usage_governance.py)
- [usage_counter.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/models/usage_counter.py)
- [20260331_0014_create_usage_counters_table.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/alembic/versions/20260331_0014_create_usage_counters_table.py)
- [rate_limit.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/middleware/rate_limit.py)
- [ai.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai.py)
- [ai_jobs.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/ai_jobs.py)
- [students.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/students.py)
- [teacher.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/academic/routes/teacher.py)
- [audio.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/audio.py)
- [video.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/video.py)
- [discovery.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/routes/discovery.py)
- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)
- [providers.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/infrastructure/llm/providers.py)
- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/admin/ai-usage/page.tsx)

## Architecture

The governance flow is:

1. Request enters a governed route.
2. Route resolves the usage metric for the feature.
3. Governance service checks:
   - per-user daily quota
   - per-user monthly quota
   - per-user token budget
   - tenant token pressure
4. Governance returns:
   - allow or reject
   - token ceilings
   - model fallback decision
   - queue recommendation for heavy batchable tools
5. Route executes with the resolved model and token caps.
6. Usage is recorded into `usage_counters`.
7. Admin analytics read the same counters and show cost/pressure trends.

## Quota Enforcement

Per-user quotas are persisted in `usage_counters` with `day` and `month` buckets.

Tracked metrics include:

- `qa_requests`
- `study_guide_generations`
- `quiz_generations`
- `flashcard_generations`
- `mindmap_generations`
- `flowchart_generations`
- `concept_map_generations`
- `socratic_sessions`
- `debate_sessions`
- `essay_reviews`
- `audio_overviews`
- `video_overviews`
- `documents_uploaded`
- `youtube_ingestions`
- `ocr_operations`
- `batch_jobs_queued`
- `llm_tokens`

Rejected requests return `429` with a readable quota message such as:

- `You have reached today's quiz generations limit. Try again tomorrow.`
- `You have reached today's AI token budget. Try again tomorrow.`

## Token Limit Enforcement

Token ceilings are enforced per tool before generation reaches the provider layer.

Current prompt/completion ceilings:

- `qa`: `2000 / 800`
- `study_guide`: `2200 / 1000`
- `quiz`: `1500 / 700`
- `flashcards`: `1000 / 500`
- `mindmap`: `1200 / 600`
- `flowchart`: `1200 / 600`
- `concept_map`: `1200 / 600`
- `socratic`: `1800 / 700`
- `debate`: `2000 / 900`
- `essay_review`: `2200 / 900`
- `audio_overview`: `2200 / 900`
- `video_overview`: `2200 / 900`

Prompt text is trimmed in the shared workflow layer, and provider calls use the governed completion cap.

## Upload and Ingestion Budgets

Upload governance is enforced in student, teacher, and discovery routes.

Current usage buckets:

- document uploads -> `documents_uploaded`
- YouTube ingestion -> `youtube_ingestions`
- image OCR -> `ocr_operations`

This protects the heaviest cost paths without blocking normal learning workflows.

## Tenant Rate Limiting

Burst rate limiting is enforced in middleware with Redis first and in-memory fallback.

Governed paths:

- `/api/ai/`
- `/api/student/tools/`
- `/api/student/upload`
- `/api/teacher/upload`
- `/api/teacher/youtube`
- `/api/mascot/upload`

Current defaults:

- per-user burst: `5 requests/minute`
- per-tenant burst: `100 requests/minute`

## Model Routing and Cost Fallback

The governance layer can force a cheaper fallback model when:

- a user is near their daily token ceiling
- a user is near a per-feature daily quota
- tenant token pressure is elevated

The route layer resolves the effective model through:

- primary model from `settings.llm.model`
- fallback model from `settings.llm.fallback_model`

The chosen model is recorded in usage analytics.

## Caching and Efficiency

Governed usage recording distinguishes cache hits from live generation.

Current behavior:

- cached AI answers do not consume new generation tokens
- cache hits are counted in governance analytics
- usage snapshot includes cache-hit totals and model mix

## Batch Generation

Non-urgent tools are queue-friendly and tracked separately through `batch_jobs_queued`.

Batchable metrics:

- `quiz_generations`
- `flashcard_generations`
- `mindmap_generations`
- `flowchart_generations`
- `concept_map_generations`
- `study_guide_generations`

The existing AI job queue remains the execution path for deferred heavy work. Governance marks when queueing is recommended during guardrail pressure.

## Cost Guardrails

Guardrails activate when token pressure rises.

Current responses:

- cheaper fallback model selection
- queue recommendation for batchable tools
- quota-based rejection once hard limits are exceeded

Estimated cost units are also recorded in `usage_counters` to support tenant monitoring.

## Monitoring Dashboard

Admin usage analytics now expose governance data through the existing AI usage surface.

Dashboard fields include:

- requests today
- tokens used today
- cache hits today
- top tool usage
- model mix
- heavy users
- quota pressure
- guardrail status

Primary UI:

- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/admin/ai-usage/page.tsx)

Primary backend source:

- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)

## Logging and Traceability

Usage events are recorded into `usage_counters` and, when available, into audit logs.

Stored governance context includes:

- tenant
- user
- metric
- bucket window
- token usage
- cache hit count
- estimated cost units
- last model used
- route metadata

## Verified Coverage

Targeted verification completed for:

- quota enforcement
- token-budget rejection
- fallback model routing
- queued AI job compatibility
- middleware rate limiting
- personalization and mascot compatibility
- admin analytics rendering

Most recent verification bundle:

- backend: `82 passed`
- frontend build: passed

## Operational Notes

This framework is designed to be strict enough for predictable cost and fair-use protection, while still allowing normal student usage to continue without abrupt silent failures.

The remaining tuning work is policy tuning, not missing architecture:

- plan-specific quotas
- stricter file-size limits if needed
- stronger queue auto-routing based on `queue_recommended`
- richer admin export/reporting on usage pressure
