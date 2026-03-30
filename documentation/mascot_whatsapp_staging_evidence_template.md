# Mascot WhatsApp Staging Evidence Template

**Date:** __________  
**Environment:** __________  
**Webhook target:** __________  
**Build / commit:** __________  
**QA owner:** __________  
**Engineering owner:** __________  
**Test device phone:** __________

## 1. Release-Gate Snapshot

### Pre-run

- endpoint: `GET /whatsapp/release-gate-snapshot?days=7`
- captured at: __________
- attachment / link: __________

### Post-run

- endpoint: `GET /whatsapp/release-gate-snapshot?days=7`
- captured at: __________
- attachment / link: __________

## 2. Mascot Staging Results

Use [mascot_whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_manual_test_script.md).

| Flow | Result | Evidence | Notes |
| --- | --- | --- | --- |
| 1. Basic entry and notebook continuity | __________ | __________ | __________ |
| 2. Mixed-language command handling | __________ | __________ | __________ |
| 3. Structured output formatting | __________ | __________ | __________ |
| 4. Ingestion and follow-up continuity | __________ | __________ | __________ |
| 5. Confirmation loop safety | __________ | __________ | __________ |
| 6. Parent and role scoping | __________ | __________ | __________ |
| 7. Error and retry behavior | __________ | __________ | __________ |
| 8. Final evidence capture complete | __________ | __________ | __________ |

## 3. Key Observations

### Notebook continuity

- created notebook reused on follow-up: __________
- post-ingestion notebook continuity verified: __________

### Confirmation safety

- cancel flow result: __________
- confirm flow result: __________

### WhatsApp formatting

- quiz readable: __________
- flashcards readable: __________
- mind map readable: __________
- flowchart readable: __________
- concept map readable: __________

## 4. Metrics Review

| Metric | Observed | Notes |
| --- | --- | --- |
| `routing_failure_total` | __________ | __________ |
| `duplicate_inbound_total` | __________ | __________ |
| `upload_ingest_failure_total` | __________ | __________ |
| `link_ingest_failure_total` | __________ | __________ |
| `visible_failure_total` | __________ | __________ |

## 5. Latency Notes

| Flow | Observed latency | Notes |
| --- | --- | --- |
| Plain mascot query | __________ | __________ |
| Study-tool generation | __________ | __________ |
| Upload/link + follow-up | __________ | __________ |

## 6. Defects

| Severity | Timestamp | Role | Reproduction | Status |
| --- | --- | --- | --- | --- |
| __________ | __________ | __________ | __________ | __________ |

## 7. Decision

- Recommendation: `Pass / Pass with waiver / Fail`
- Blocking issues: __________
- Waivers approved by: __________
- Follow-up actions: __________
