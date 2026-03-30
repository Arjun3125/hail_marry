# Mascot WhatsApp Staging Manual Test Script

**Date:** 2026-03-30  
**Parent plan:** [mascot_phase4_whatsapp_plan.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_phase4_whatsapp_plan.md)  
**Base release gate:** [whatsapp_release_gate.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/whatsapp_release_gate.md)  
**Evidence template:** [mascot_whatsapp_staging_evidence_template.md](/c:/Users/naren/Work/Projects/proxy_notebooklm/documentation/mascot_whatsapp_staging_evidence_template.md)

## Goal

Validate that the mascot operates reliably through WhatsApp as a real conversational operator, not just as a transport wrapper.

## Preconditions

- staging WhatsApp webhook is live and healthy
- staging uses valid WhatsApp Cloud API credentials
- one real test device is available
- at least one test account exists for:
  - student
  - teacher
  - parent
  - admin
- at least one uploadable grounding source exists:
  - textbook PDF
  - image/screenshot with text
  - YouTube or article link

## Capture Before Starting

Record the following before the first message:

- staging build or commit
- test phone number
- webhook target URL
- pre-run `GET /whatsapp/release-gate-snapshot?days=7`
- current open mascot or WhatsApp staging waivers

## Test Flow

### 1. Basic entry and continuity

1. Send a plain greeting and confirm the linked account resumes without relogin.
2. Ask `Create notebook for Biology Chapter 10`.
3. Confirm the mascot replies with notebook creation text.
4. Immediately ask `Explain photosynthesis`.
5. Confirm the answer uses the notebook scope created in step 2 without restating notebook context.

### 2. Mixed-language command handling

1. Send `quiz bana biology chapter 10 ka`.
2. Send `mala flashcards pahije photosynthesis var`.
3. Send `mind map bana digestion process ka`.
4. Confirm the routed outputs match the requested tool in each case.

### 3. Structured output formatting

1. Ask for:
   - quiz
   - flashcards
   - mind map
   - flowchart
   - concept map
2. Confirm:
   - quiz is short and readable
   - flashcards are compact
   - mind map shows key branches
   - flowchart shows ordered steps
   - concept map shows relationship lines
3. Confirm no raw Mermaid or raw JSON is shown.

### 4. Ingestion and follow-up continuity

1. Send a PDF plus a follow-up question in the caption.
2. Send an image/screenshot plus a follow-up question.
3. Send a YouTube or article link with `summarize this`.
4. For each:
   - confirm ingestion succeeds
   - confirm a notebook is created or reused
   - ask one more follow-up question after ingestion
   - confirm the second turn stays grounded to the same notebook/source

### 5. Confirmation loop safety

1. Send a risky mascot command such as `Delete Biology notebook`.
2. Confirm WhatsApp returns a confirmation prompt with clear `CONFIRM` / `CANCEL` guidance.
3. Reply `CANCEL`.
4. Confirm no change is applied.
5. Trigger the same risky action again.
6. Reply `CONFIRM`.
7. Confirm the action executes and the pending confirmation is cleared.

### 6. Parent and role scoping

1. As a parent, switch child scope if needed.
2. Ask for attendance/performance summary.
3. Confirm the mascot stays within the selected child scope.
4. Confirm no teacher/admin-only behavior leaks into parent replies.

### 7. Error and retry behavior

1. Send an ambiguous request like `Open attendance and marks`.
2. Confirm the mascot asks for clarification rather than guessing.
3. Replay a duplicate inbound payload if available through staging tools/logs.
4. Confirm no duplicate user-visible mutation occurs.

### 8. Final evidence capture

1. Capture post-run `GET /whatsapp/release-gate-snapshot?days=7`.
2. Record latency notes for:
   - plain query
   - study-tool generation
   - upload/link ingestion + follow-up
3. Attach screenshots of each major flow.

## Pass Criteria

The mascot WhatsApp staging run passes only if:

- notebook continuity works across at least one two-turn flow
- mixed-language tool requests route correctly
- structured outputs are WhatsApp-safe
- risky actions require confirmation
- cancel/confirm both behave correctly
- ingestion + follow-up remains grounded
- no duplicate visible mutations occur

## Sign-Off

- QA owner:
- engineering owner:
- date:
- decision:
