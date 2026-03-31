# Traceability And Diagnostics Framework

Date: 2026-03-31

## Goal

Provide one system-wide failure path that:

- detects failures
- assigns a structured error code
- records the failure in logs and audit trails
- returns the code to the API client
- shows the code in the UI
- groups repeated failures for admin diagnostics and alerting

## Error Code Taxonomy

Format:

- `MODULE-CATEGORY-CODE`

Examples now implemented:

- `WA-CONN-001` — WhatsApp connection failure
- `WA-WEB-002` — WhatsApp webhook failure
- `OCR-READ-002` — OCR extraction failure
- `FILE-UPL-003` — file upload failure
- `RAG-RET-003` — RAG retrieval failure
- `LLM-GEN-004` — LLM generation failure
- `FLOW-GEN-005` — flowchart generation failure
- `API-CALL-006` — external API failure
- `DB-VEC-007` — vector database failure
- `UI-ACT-008` — UI action failure
- `QUIZ-GEN-009` — quiz generation failure
- `CARD-GEN-010` — flashcard generation failure
- `MIND-GEN-011` — mind map generation failure
- `CMAP-GEN-012` — concept map generation failure
- `CACHE-OPS-013` — cache failure
- `JOB-EXEC-014` — background job failure
- `EMB-GEN-015` — embedding generation failure
- `ING-CHNK-016` — document chunking failure
- `API-VAL-017` — validation failure
- `API-AUTH-018` — authentication / authorization failure
- `API-SRV-019` — unhandled server failure

Source of truth:

- [traceability.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/traceability.py)

## Implementation Architecture

### Backend

Shared traceability service:

- [traceability.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/traceability.py)

Responsibilities:

- taxonomy and code resolution
- route/message-based fallback classification
- structured failure payload generation
- audit persistence for trace errors
- trace event recording
- error metrics emission
- admin diagnostics summary generation

Global exception handling:

- [main.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/main.py)

Handlers now convert:

- `TraceabilityError`
- `HTTPException`
- uncaught exceptions

into a consistent JSON response:

```json
{
  "detail": "OCR processing failed.",
  "error_code": "OCR-READ-002",
  "subsystem": "ocr",
  "error_title": "OCR extraction failure",
  "severity": "warning",
  "trace_id": "abc123...",
  "status_code": 500,
  "support_message": "Please contact support with error code OCR-READ-002."
}
```

### Workflow integration

Shared AI workflow integration:

- [workflows.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/interfaces/rest_api/ai/workflows.py)

Central retrieval/generation failures now emit explicit traceable errors for:

- RAG retrieval
- AI runtime connectivity
- generation timeout
- upstream AI runtime failure

### Logging

Structured logging now includes:

- `error_code`
- `subsystem`
- `error_category`

in:

- [structured_logging.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/structured_logging.py)

### Metrics and alerting

Traceability counters are now emitted by:

- [metrics_registry.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/metrics_registry.py)

Repeated critical codes now raise observability alerts via:

- [alerting.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/alerting.py)

Config thresholds:

- [config.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/config.py)

## UI Error Display

Frontend API client parsing:

- [api.ts](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/lib/api.ts)

The client now preserves backend error codes and appends them to displayed API messages.

Error remediation UI:

- [ErrorRemediation.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/components/ui/ErrorRemediation.tsx)

It now surfaces:

- error code
- support copy text
- trace/reference identifiers

## Admin Diagnostic Dashboard

Traceability summary API:

- `GET /api/admin/observability/traceability?days=7`

Route:

- [admin.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/administrative/routes/admin.py)

Developer/admin viewer:

- [page.tsx](/c:/Users/naren/Work/Projects/proxy_notebooklm/frontend/src/app/admin/traces/page.tsx)

It now shows:

- grouped errors by code
- subsystem totals
- recent traceability failures
- trace lookup timeline

## Testing

Focused backend regressions:

- [test_traceability.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_traceability.py)
- [test_alerting.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/tests/test_alerting.py)

Covered:

- subsystem classification
- API error-code response formatting
- uncaught exception handling
- diagnostics summary aggregation
- repeated-error alerting

## Current Coverage

The framework now reliably covers:

- API-level failures
- OCR failures surfaced through API responses
- shared RAG / LLM workflow failures
- repeated subsystem failures via alerting
- UI-visible error code display
- admin diagnostics grouping

## Recommended Next Extensions

To deepen coverage further:

1. Raise `TraceabilityError` directly inside more subsystem-specific hotspots:
   - WhatsApp send/download helpers
   - OCR import parsers
   - vector/embedding infrastructure adapters
2. Add frontend telemetry for client-only UI failures and map them to `UI-ACT-*` codes.
3. Add traceability cards to the admin dashboard homepage, not just the traces page.
4. Add live incident creation rules from repeated critical traceability codes.
