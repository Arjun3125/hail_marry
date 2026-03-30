# WhatsApp Tier 4.5 Release Gate

**Date:** 2026-03-29  
**Execution checklist:** [whatsapp_tier_4_5_execution_checklist.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_tier_4_5_execution_checklist.md)  
**Staging script:** [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md)
**Evidence template:** [whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_evidence_template.md)

## Purpose

Define the minimum engineering gate required before claiming the WhatsApp channel is at Tier 4.5 readiness.

## Automated Gate

The release is blocked unless all of the following pass:

1. `python -m pytest -q -p no:cacheprovider backend/tests/test_whatsapp_gateway.py`
2. `python -m pytest -q -p no:cacheprovider backend/tests/test_whatsapp_integration.py`
3. `python -m pytest -q -p no:cacheprovider backend/tests/evaluation/test_intent_classifier_benchmark.py`
4. `python -m py_compile backend/src/domains/platform/services/whatsapp_gateway.py backend/src/domains/platform/routes/whatsapp.py backend/src/interfaces/whatsapp_bot/agent.py backend/src/shared/ai_tools/whatsapp_tools.py`

## Mandatory Functional Coverage

The automated suite must continue to cover:

- auth and relink flows
- parent child switching
- mixed-language intent routing
- study-tool parity and role access
- upload to ingest to grounded follow-up flows
- notebook scope continuity
- duplicate inbound suppression
- outbound retry classification
- WhatsApp-safe response formatting and chunking

## Required Telemetry Fields

Operators must be able to retrieve or derive at least these signals:

- `inbound_total`
- `duplicate_inbound_total`
- `rate_limited_total`
- `unlinked_inbound_total`
- `routing_success_total`
- `routing_failure_total`
- `upload_ingest_success_total`
- `upload_ingest_failure_total`
- `link_ingest_success_total`
- `link_ingest_failure_total`
- `outbound_success_total`
- `outbound_failure_total`
- `outbound_retryable_failure_total`
- `outbound_non_retryable_failure_total`
- `visible_failure_total`

These are emitted through structured gateway logging plus Redis-backed WhatsApp metrics in [whatsapp_gateway.py](/c:/Users/naren/Work/Projects/proxy_notebooklm/backend/src/domains/platform/services/whatsapp_gateway.py).

For staging evidence capture, operators can fetch a single structured snapshot from:

- `GET /whatsapp/release-gate-snapshot?days=7`

This endpoint combines route analytics with the Redis-backed release-gate metrics and derived failure percentages.

## Failure Thresholds

Do not ship if any of the following are true in staging validation:

- duplicate inbound events cause duplicate visible responses
- upload plus follow-up fails for any supported source type in the staging script
- parent child-switch leaks notebook or child context
- diagram tools expose raw Mermaid or raw JSON to the WhatsApp user
- outbound retryable failures are not visible in telemetry
- routing failure rate is materially above baseline during the staging run

## Human Gate

A release is still blocked until the real-device checks in [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md) are executed and signed off.

The signed run should attach a completed copy of [whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_evidence_template.md), including the release-gate snapshot output and links to supporting screenshots/logs.

## Exit Condition

The WhatsApp channel may be called Tier 4.5-ready only when:

- the automated gate passes
- the telemetry fields are available
- the manual staging script passes without critical defects
- no open P0 or P1 WhatsApp regressions remain
