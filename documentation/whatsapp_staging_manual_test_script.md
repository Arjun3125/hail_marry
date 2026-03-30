# WhatsApp Staging Manual Test Script

**Date:** 2026-03-29  
**Release gate:** [whatsapp_release_gate.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_release_gate.md)
**Evidence template:** [whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_staging_evidence_template.md)

## Goal

Run a real-device staging check against the WhatsApp channel before production rollout.

## Preconditions

- Meta webhook points at staging
- staging has valid WhatsApp credentials
- at least one test account exists for each role:
  - student
  - parent
  - teacher
  - admin
- a staging textbook or notes set is available for upload and grounded follow-up queries

## Pass Criteria

Every step below must either pass or be explicitly waived with a reason.

Before starting, create a fresh copy of the evidence template and record:

- environment URL / webhook target
- test device phone number
- tester names
- pre-run `GET /whatsapp/release-gate-snapshot?days=7` output

## Script

1. Verify webhook handshake still succeeds.
2. Send a plain text greeting from an unlinked number and confirm the phone-first linking flow starts.
3. Complete linking from a returning user and confirm a second message does not ask for login again.
4. Use `/logout`, then confirm the session ends but the phone can re-enter cleanly.
5. Use `/relink`, then confirm the verified phone binding is removed and the number must link again.
6. As a parent, switch children and confirm later questions are answered in the selected child scope only.
7. Send a mixed-language study request such as `quiz bana biology chapter 3` and confirm the routed tool matches the request.
8. Send a PDF with a caption-question and confirm the file is ingested and the answer is grounded in the uploaded material.
9. Send an image and a follow-up prompt in the same message flow and confirm OCR-backed ingestion works.
10. Send a plain link with `summarize this` and confirm the link is ingested and the follow-up answer uses the new notebook scope.
11. Ask for quiz, flashcards, mind map, flowchart, and concept map on the same uploaded topic.
12. Confirm diagram-style responses are summary-plus-link and do not expose raw Mermaid or raw JSON.
13. Trigger a known invalid request and confirm the user gets a readable remediation message instead of an internal error blob.
14. Replay the same inbound webhook payload and confirm no duplicate user-visible action occurs.
15. Induce or simulate a transient outbound failure and confirm retry classification is visible in logs or metrics.
16. Capture a post-run `GET /whatsapp/release-gate-snapshot?days=7` output and attach it to the evidence record.

## Evidence To Capture

- screenshots of key WhatsApp conversations
- webhook logs for duplicate-event replay
- outbound failure log with retry classification
- current Redis or operator snapshot of WhatsApp metrics
- pre-run and post-run `release-gate-snapshot` responses
- any defects with exact timestamp, phone, role, and reproduction steps

## Sign-Off

- QA owner:
- engineering owner:
- date:
- release decision:
