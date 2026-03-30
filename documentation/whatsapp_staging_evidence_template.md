# WhatsApp Staging Evidence Template

**Date:** __________  
**Environment:** __________  
**Webhook target:** __________  
**QA owner:** __________  
**Engineering owner:** __________  
**Test device phone:** __________  
**Build / commit:** __________

## 1. Release-Gate Snapshot

### Pre-run snapshot

- endpoint: `GET /whatsapp/release-gate-snapshot?days=7`
- captured at: __________
- attachment / paste location: __________

### Post-run snapshot

- endpoint: `GET /whatsapp/release-gate-snapshot?days=7`
- captured at: __________
- attachment / paste location: __________

## 2. Manual Staging Results

Record pass/fail/waiver for each step in [whatsapp_staging_manual_test_script.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_manual_test_script.md).

| Step | Result | Evidence | Notes |
| --- | --- | --- | --- |
| 1. Webhook handshake | __________ | __________ | __________ |
| 2. Unlinked greeting starts linking flow | __________ | __________ | __________ |
| 3. Returning user re-entry works | __________ | __________ | __________ |
| 4. Logout works cleanly | __________ | __________ | __________ |
| 5. Relink removes binding | __________ | __________ | __________ |
| 6. Parent child switching stays scoped | __________ | __________ | __________ |
| 7. Mixed-language tool routing works | __________ | __________ | __________ |
| 8. PDF + caption question ingestion works | __________ | __________ | __________ |
| 9. Image + follow-up OCR ingestion works | __________ | __________ | __________ |
| 10. Plain link + summarize flow works | __________ | __________ | __________ |
| 11. Quiz/flashcards/mind map/flowchart/concept map all work | __________ | __________ | __________ |
| 12. Diagram outputs stay WhatsApp-safe | __________ | __________ | __________ |
| 13. Invalid request returns remediation text | __________ | __________ | __________ |
| 14. Duplicate webhook replay is suppressed | __________ | __________ | __________ |
| 15. Outbound retry classification is visible | __________ | __________ | __________ |
| 16. Post-run snapshot captured | __________ | __________ | __________ |

## 3. Release-Gate Metrics Review

| Metric | Expected interpretation | Observed | Notes |
| --- | --- | --- | --- |
| `duplicate_inbound_total` | No duplicate visible responses | __________ | __________ |
| `routing_failure_total` | Should stay near baseline | __________ | __________ |
| `upload_ingest_failure_total` | Should be zero for tested supported types | __________ | __________ |
| `link_ingest_failure_total` | Should be zero for tested supported links | __________ | __________ |
| `outbound_retryable_failure_total` | Must be visible if induced | __________ | __________ |
| `visible_failure_total` | No unexpected spikes during run | __________ | __________ |

## 4. Defects

| Severity | Timestamp | Phone / Role | Reproduction | Status |
| --- | --- | --- | --- | --- |
| __________ | __________ | __________ | __________ | __________ |

## 5. Decision

- Release recommendation: `Pass / Pass with waiver / Fail`
- Blocking issues: __________
- Waivers approved by: __________
- Follow-up actions: __________
