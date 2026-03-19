# WhatsApp Access Implementation Plan

This rollout plan is the working implementation companion for VidyaOS WhatsApp access. It translates the higher-level gateway design into a staged delivery plan focused on maximizing practical feature coverage through WhatsApp while preserving the web app for workflows that are inherently visual, dense, or operationally complex.

## 1. Goal and Scope

### Primary goal

Create a bidirectional WhatsApp interface that lets students, teachers, parents, and admins:

- ask questions in natural language,
- retrieve ERP data,
- trigger AI functions,
- receive asynchronous results,
- stay within role-based access limits.

### Practical scope

Target the following through WhatsApp:

- all read/query functions,
- all safe trigger functions,
- AI generation jobs with queued execution,
- complex visual/admin workflows via summary + deep link fallback.

### Non-goals

Do **not** try to fully recreate these as chat-native first:

- large dashboards,
- rich visual editing,
- multi-column admin review tools,
- bulk uploads/management,
- advanced analytics exploration.

Those are better served by the existing frontend.

## 2. Product Strategy

### Recommended access model

Each function should fall into one of these delivery patterns:

#### A. Direct WhatsApp response

For simple, lightweight actions:

- timetable,
- attendance,
- marks,
- assignments,
- fee summary,
- admin usage stats.

#### B. Async WhatsApp job

For heavy AI functions:

- quiz generation,
- study guide generation,
- audio overviews,
- large grounded Q&A jobs.

#### C. WhatsApp summary + web deep link

For complex actions:

- governance review,
- trace browsing,
- detailed admin dashboards,
- large report interaction,
- rich visual study outputs.

## 3. Architecture Plan

### 3.1 Core architecture

Use the WhatsApp gateway already described in the design spec:

- Meta WhatsApp Cloud API webhook,
- WhatsApp gateway service,
- phone-to-user mapping,
- Redis session state,
- LangGraph orchestrator,
- ERP tool routing,
- response formatter for text/list/media.

### 3.2 Reuse existing backend instead of duplicating logic

Do **not** implement business logic inside the WhatsApp handler.

Instead:

- keep existing service/domain logic in API/backend,
- expose each capability as a reusable service/tool,
- let WhatsApp be a new channel that invokes those same capabilities.

This keeps the web app, API clients, and WhatsApp consistent.

### 3.3 Interaction model

Natural-language flow:

1. user sends message,
2. gateway authenticates phone,
3. gateway loads role + tenant + session,
4. intent classifier identifies target function,
5. tool router executes service or enqueues AI job,
6. formatter returns chat-friendly output,
7. outbound WhatsApp sends response.

## 4. Feature Classification Matrix

To implement efficiently, classify functions into four groups.

### Group 1 — Simple ERP reads

Implement first. High value, low risk.

Examples:

- student timetable,
- student tests,
- pending assignments,
- attendance summary,
- latest results,
- weak topics,
- teacher schedule,
- absent students,
- child performance,
- child attendance,
- child homework,
- school attendance summary,
- fee pending report,
- AI usage stats.

**Implementation method:** direct tool invocation + formatted text/list reply.

### Group 2 — Safe trigger functions

Examples:

- generate quiz,
- request report card PDF,
- request summary audio,
- trigger notification/report workflows.

**Implementation method:** confirmation prompt + enqueue or trigger service.

### Group 3 — Conversational AI/RAG

Examples from the main product:

- Q&A,
- study guide,
- quiz,
- flashcards,
- weak topic help,
- Socratic tutoring,
- citations-backed answers,
- docs chatbot.

**Implementation method:** LangGraph-backed conversational mode with role-scoped retrieval.

### Group 4 — Complex web-only or hybrid

Examples:

- admin operations consoles,
- trace viewer,
- AI review dashboard,
- queue operations with detailed filters,
- complex visual study outputs.

**Implementation method:** WhatsApp summary + deep link back to web app.

## 5. Rollout Phases

### Phase 0 — Foundations

**Objective:** prepare the backend so WhatsApp is just another interface layer.

#### Deliverables

- inventory all callable functions by domain,
- define a canonical tool registry,
- normalize input/output contracts,
- identify which functions are sync vs async,
- define response formatting rules.

#### Tasks

- map every major feature to a backend service/tool,
- tag each as `read`, `write`, `ai_sync`, `ai_async`, `web_only`,
- standardize tool metadata:
  - tool name,
  - description,
  - role access,
  - required params,
  - output type,
  - channel suitability.

#### Exit criteria

- complete function inventory,
- agreed taxonomy,
- no feature handled only in frontend code without service backing.

### Phase 1 — WhatsApp Gateway MVP

**Objective:** enable inbound WhatsApp messages and authenticated sessions.

#### Deliverables

- `POST /api/v1/whatsapp/webhook`,
- `GET /api/v1/whatsapp/webhook`,
- phone-to-account linking,
- Redis-backed WhatsApp session state,
- signature verification,
- rate limiting,
- deduplication.

#### Tasks

- implement webhook verification endpoint,
- implement inbound webhook receiver,
- verify Meta signatures,
- add message dedupe using message ID,
- persist WhatsApp sessions in Redis,
- build OTP/account-linking flow,
- map phone number to tenant + user + role.

#### Exit criteria

- authenticated user can send a message and receive a validated response,
- duplicate webhook delivery does not duplicate actions.

### Phase 2 — ERP Read Access for All Roles

**Objective:** deliver broad utility quickly.

#### Deliverables

Implement the WhatsApp ERP tool set already listed in the design doc.

#### Tasks

##### Student

- timetable,
- upcoming tests,
- assignments,
- attendance,
- results,
- weak topics.

##### Teacher

- schedule,
- absent students.

##### Parent

- child performance,
- child attendance,
- child homework.

##### Admin

- school attendance summary,
- fee pending report,
- AI usage stats.

##### UX tasks

- plain text output for short responses,
- list messages for disambiguation,
- buttons for “more”, “download”, “next action”.

#### Exit criteria

- all listed read tools work end-to-end,
- role restrictions enforced,
- users can complete common informational tasks without logging into the web app.

### Phase 3 — Async Action Triggers

**Objective:** add productive actions without blocking the webhook.

#### Deliverables

- queued job trigger path for heavy requests,
- status acknowledgment pattern,
- outbound result delivery.

#### Tasks

- connect WhatsApp commands to existing queue worker,
- implement job ID tracking,
- build “queued / processing / completed / failed” response templates,
- send final result back to the same conversation,
- support retries and failure explanations.

#### Best first actions

- generate quiz,
- generate study guide,
- request audio overview,
- report card delivery as PDF/media.

#### Exit criteria

- heavy jobs never block the webhook,
- users get immediate acknowledgment and later completion message.

### Phase 4 — Conversational AI Access

**Objective:** expose the main AI layer through WhatsApp.

#### Deliverables

- natural-language Q&A,
- citation-grounded answers,
- selected study tools,
- support chatbot access,
- optional multilingual support.

#### Tasks

- connect WhatsApp agent to `/api/ai` capability equivalents,
- support RAG retrieval on user documents/materials,
- add citation rendering for WhatsApp-friendly output,
- expose docs chatbot through `/api/support`,
- support Hindi/Marathi response preferences.

#### Constraints

WhatsApp text UX is limited, so:

- concise answers first,
- “reply with MORE” for extended detail,
- attach files/media when better than long text,
- offer web deep link when citations/results are too dense.

#### Exit criteria

- user can ask educational/support questions in WhatsApp and get grounded answers,
- large AI responses degrade gracefully.

### Phase 5 — Hybrid Access for Complex Functions

**Objective:** cover “all practical functions” without forcing everything into chat.

#### Deliverables

For web-heavy functions:

- WhatsApp summary,
- secure deep links,
- downloadable artifacts where possible.

#### Candidate hybrid functions

- governance dashboards,
- queue management,
- trace investigation,
- complex analytics,
- rich diagram editing,
- admin review workflows.

#### Exit criteria

Every important function is either:

- directly available in WhatsApp,
- triggerable from WhatsApp,
- or accessible through a secure WhatsApp-to-web handoff.

## 6. Backend Workstreams

### 6.1 Tool registry

Create a unified registry for channel-safe tools:

- tool name,
- handler,
- roles,
- tenant rules,
- sync/async flag,
- output formatter,
- feature category.

This should become the compatibility layer between web/API/WhatsApp.

### 6.2 Intent router

Implement intent classification for:

- informational query,
- ERP query,
- AI query,
- admin query,
- action trigger,
- unsupported request.

Fallback:

- ask a clarifying question,
- or send deep link to web.

### 6.3 Formatter layer

Need response renderers for:

- plain text,
- quick replies,
- list messages,
- media/file attachments.

### 6.4 Session memory

Multi-turn context is explicitly on the roadmap. Build:

- current active child/class/student context,
- recent tool outputs,
- pending confirmation actions,
- last AI mode used.

## 7. Security and Governance Plan

### 7.1 Identity and account linking

Every user must link their WhatsApp number to their ERP account before access.

#### Tasks

- OTP verification,
- secure phone binding,
- account relink/unlink flow,
- multi-user-per-device guardrails if needed.

### 7.2 RBAC

The design already defines role-based tool access. This must be enforced centrally, not in the prompt only.

#### Tasks

- verify every tool request against role,
- ensure tenant isolation,
- redact restricted fields in outputs.

### 7.3 Auditability

For sensitive actions, log:

- requester,
- tool used,
- tenant,
- parameters,
- outcome,
- timestamp,
- trace/job ID.

### 7.4 Rate limiting

Use the rate-limiting and dedupe model from the spec.

## 8. UX Design Rules for WhatsApp

### Rule 1 — Keep messages short

Send short answers first. Allow drill-down:

- “Reply 1 for details”
- “Reply PDF for full report”

### Rule 2 — Use structured menus

For repeatable actions, provide:

- buttons,
- list messages,
- child/class selector.

### Rule 3 — Confirm risky actions

Before triggering anything impactful:

- “Do you want me to generate the quiz now?”
- “Reply YES to continue”

### Rule 4 — Use async for heavy work

Never block on large AI jobs. Always acknowledge first.

### Rule 5 — Fall back to web where needed

If output is too complex:

- send a summary in chat,
- attach file/media,
- link to the exact page in the web app.

## 9. Testing Plan

### Functional tests

- webhook verification,
- inbound parsing,
- message dedupe,
- OTP/account linking,
- role access,
- tenant isolation,
- tool routing,
- error handling,
- async result delivery.

### AI tests

- Q&A routing,
- citation formatting,
- long answer truncation,
- queue handoff,
- recovery on worker failure.

### Security tests

- unauthorized phone number,
- role escalation attempts,
- cross-tenant access attempts,
- webhook signature spoofing,
- repeated replayed messages.

### UX tests

- message length quality,
- menu usability,
- ambiguous query handling,
- multilingual behavior.

## 10. Suggested Milestones

### Milestone 1 — Channel foundation

**Time:** 1–2 weeks

Includes:

- webhook endpoints,
- auth/linking,
- session storage,
- logging/rate limiting.

### Milestone 2 — ERP utility access

**Time:** 1–2 weeks

Includes:

- all read-only WhatsApp ERP tools,
- role-safe access,
- formatter layer.

### Milestone 3 — Async productivity

**Time:** 1 week

Includes:

- queue-backed AI triggers,
- result callbacks,
- PDFs/media responses.

### Milestone 4 — Conversational AI

**Time:** 1–2 weeks

Includes:

- grounded Q&A,
- docs chatbot,
- study tool access,
- memory and multilingual support.

### Milestone 5 — Hybrid completion

**Time:** 1 week

Includes:

- deep links,
- unsupported-flow handling,
- admin/web-only summaries.

This aligns well with the staged roadmap in the WhatsApp design document.

## 11. Recommended Priority Order

For fastest ROI, implement in this order:

1. webhook + auth/linking,
2. student/parent read-only tools,
3. teacher/admin read-only tools,
4. queued quiz generation,
5. grounded Q&A,
6. study guides / audio summaries,
7. hybrid web handoff for complex functions,
8. multilingual + multi-turn memory.

This delivers user value before the full AI layer is complete.

## 12. Decision Summary

### Should we do this?

Yes. The architecture already supports it conceptually.

### Should we make literally every function native in chat?

No. We should make every important function reachable from WhatsApp, but not force every complex UI flow into chat.

### Best implementation principle

**“WhatsApp-accessible” is the goal, not “WhatsApp-only.”**
