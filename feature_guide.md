# VidyaOS — Complete Feature Guide

A plain-language guide to every feature, who it helps, and whether it needs AI.

**Last reviewed:** 2026-03-19 · **Backend tests:** 438 across 52 files · **All thresholds centralized in `constants.py`**

---

## Quick Reference: AI vs Non-AI

| # | Feature | Needs AI? | Users |
|---|---------|-----------|-------|
| 1 | Bulk Attendance & Marks (CSV) | ❌ No | Teachers |
| 2 | Real-Time Notifications | ❌ No | Everyone |
| 3 | Offline Mode (PWA) | ❌ No | Everyone |
| 4 | Dark Mode Persistence | ❌ No | Everyone |
| 5 | Study Streaks & Badges | ❌ No | Students |
| 6 | Smart Weakness Alerts | ❌ No | Students |
| 7 | Parent Weekly Email Digest | ❌ No | Parents |
| 8 | AI Grading Co-Pilot | ✅ Yes | Teachers |
| 9 | Accessibility Improvements | ❌ No | Everyone |
| 10 | AI Study Tools (Quiz, Flashcards, Mind Maps) | ✅ Yes | Students |
| 11 | Document Intelligence (Upload & Ask) | ✅ Yes | Students, Teachers |
| 12 | AI Chat (Grounded Q&A) | ✅ Yes | Students |
| 13 | YouTube Lecture Ingestion | ✅ Yes | Teachers |
| 14 | Student Onboarding via Photo (OCR) | ✅ Yes | Teachers |
| 15 | Spaced Repetition (SM-2 Algorithm) | ❌ No | Students |
| 16 | Attendance Tracking | ❌ No | Teachers, Parents |
| 17 | Exam & Marks Management | ❌ No | Teachers, Admin |
| 18 | Assignment Management | ❌ No | Teachers, Students |
| 19 | Complaint System | ❌ No | Students, Admin |
| 20 | Parent Dashboard | ❌ No | Parents |
| 21 | Admin Dashboard & User Management | ❌ No | Admin |
| 22 | Multi-Tenant Architecture | ❌ No | All Schools |
| 23 | Compliance & Data Export | ❌ No | Admin |
| 24 | Incident Management | ❌ No | Admin |
| 25 | Leaderboard & Rankings | ❌ No | Students, Teachers |
| 26 | Report Card PDF Generation | ❌ No | Teachers, Parents |
| 27 | WhatsApp Notifications | ❌ No | Parents |
| 28 | Webhook Subscriptions | ❌ No | Admin |
| 29 | Queue Operations & Monitoring | ❌ No | Admin |
| 30 | Trace Viewer | ❌ No | Admin |
| 31 | Observability Alerts | ❌ No | Admin |
| 32 | Enterprise SSO (SAML) | ❌ No | Admin |
| 33 | Audio & Video Overviews | ✅ Yes | Students |
| 34 | Performance Heatmap | ❌ No | Admin, Teachers |
| 35 | Upload Security (DOCX Sanitization) | ❌ No | System-wide |
| 36 | Razorpay Billing Integration | ❌ No | Admin |
| 37 | Hindi + Regional Language Support (i18n) | ❌ No | Everyone |
| 38 | Self-Service Tenant Onboarding | ❌ No | Admin |
| 39 | Admission Workflow | ❌ No | Admin, Parents |
| 40 | Fee Management Module | ❌ No | Admin |
| 41 | OpenAI-Compatible API (Ollama + 3rd Party) | ✅ Yes | Developers |
| 42 | Knowledge Graph Index | ✅ Yes | System (AI) |
| 43 | HyDE Query Transform | ✅ Yes | System (AI) |
| 44 | Extended Data Connectors (PPTX/Excel/Notion) | ✅ Wired (uploads + URL ingestion) | Teachers |
| 45 | Refresh Token Blacklisting | ❌ No | System (Security) |
| 46 | Clickable Citations | ✅ Yes | Students |
| 47 | Document Ingestion Watch | ❌ No | System |
| 48 | Agent Orchestration (Multi-Step Workflows) | ✅ Yes | Students, Teachers |
| 49 | reCAPTCHA / Bot Protection | ✅ Yes (requires secret) | System (Security) |
| 50 | Module Plugin Architecture | ❌ No | Developers |
| 51 | Library Management | ❌ No | Admin, Students |
| 52 | Self-Service Team Invitation | ❌ No | Admin |
| 53 | Docker Multi-Stage Build | ❌ No | DevOps |
| 54 | Docs-as-AI Chatbot | ✅ Yes | Everyone |
| 55 | DPDP Act 2023 Compliance | ❌ No | Legal, Admin |

---

Use this section as the source of truth for current operational status.

---

## Features That Work WITHOUT AI

These features run purely on standard logic — databases, calculations, and templates. No language model or machine learning is needed.

---

### 1. 📋 Bulk Attendance & Marks via CSV
**What it does:** Teachers can upload a simple spreadsheet (CSV file) to mark attendance or enter exam marks for an entire class at once — instead of entering each student one by one.

**Who benefits:** Teachers who manage multiple classes daily.

**How it helps:**
- A teacher with 5 classes of 40 students each currently needs ~200 individual clicks to mark attendance. With CSV upload, it takes one file upload.
- Schools can also download attendance/marks as spreadsheets for record-keeping or sending to parents.
- Saves 30-60 minutes per day for busy teachers.

---

### 2. 🔔 Real-Time Notifications
**What it does:** Instead of students having to refresh the page to check if their AI-generated quiz is ready, the system automatically pushes a notification the moment it's done. Same for assignment deadlines, complaint updates, and marks publication.

**Who benefits:** All users — students, teachers, parents.

**How it helps:**
- Students get instant "Your quiz is ready!" alerts without repeatedly checking.
- Teachers get notified when a student submits an assignment.
- Parents get updates when exam results are published.
- Works like WhatsApp or Instagram notifications — the update comes to you.
- Notifications are persisted in the database for durability across restarts, with WebSocket push for real-time delivery.

---

### 3. 📱 Offline Mode (Works Without Internet)
**What it does:** The app saves important pages (dashboard, timetable, past results) on the device so they can be viewed even without internet. When connectivity returns, any queued actions are automatically sent.

**Who benefits:** Students and teachers in areas with unreliable internet.

**How it helps:**
- In rural Indian schools where internet drops frequently, students can still check their timetable, review past results, and read study materials.
- Teachers can prepare attendance entries offline and they sync when connection resumes.
- The app installs like a phone app — add to home screen, full-screen experience.

---

### 4. 🌙 Dark Mode That Remembers Your Choice
**What it does:** When you switch to dark mode (easier on the eyes, especially at night), the app remembers your choice. Next time you open it, it stays in dark mode.

**Who benefits:** Everyone, especially students studying late at night.

**How it helps:**
- Currently, every time you reopen the app, it resets to the default theme. This fix remembers your preference forever.
- Reduces eye strain during late-night study sessions.
- Automatically matches your phone/computer's system theme if you haven't set a preference.

---

### 5. 🔥 Study Streaks & Achievement Badges
**What it does:** The app tracks consecutive days of study. Every day you log in and study, your "streak" grows. Hit milestones (7 days, 30 days, 100 days) and earn badges that appear on your dashboard.

**Who benefits:** Students who need motivation to study consistently.

**How it helps:**
- Works like Duolingo streaks — "Don't break the chain!" psychology.
- Badges include: 🏅 "First Login", 🔥 "7-Day Streak", ⭐ "30-Day Scholar", 🏆 "100-Day Champion"
- The student dashboard shows your current streak counter prominently.
- Creates a fun, game-like feel that encourages daily engagement.

---

### 6. ⚠️ Smart Weakness Alerts
**What it does:** Instead of students manually digging through their marks to find weak areas, the system automatically detects when a subject average drops below 60% and sends a friendly alert: *"Your Physics average is at 45% — here are review flashcards to help."*

**Who benefits:** Students who struggle with specific subjects.

**How it helps:**
- Proactive help — the system identifies problems before the student may even realize.
- One-click access to spaced repetition review cards specifically for the weak topic.
- Works purely on marks data — no AI needed, just math.
- Alerts appear directly on the student's dashboard.

---

### 7. 📧 Parent Weekly Email Digest
**What it does:** Every week, parents receive an email summarizing their child's school activity: attendance percentage, latest exam scores, and how much they used the study tools. No login required.

**Who benefits:** Parents who don't regularly log into the app.

**How it helps:**
- Many parents in the target market prefer email/WhatsApp over web apps.
- No need to remember passwords or navigate a website — the summary comes to their inbox.
- Includes: attendance rate, marks from recent exams, number of AI study sessions.
- Admins can trigger digests manually or set them on a weekly schedule.

---

### 15. 🧠 Spaced Repetition (SM-2 Algorithm)
**What it does:** Uses a proven memory algorithm to schedule review sessions at optimal intervals. If you get a concept right, it waits longer before asking again. If you struggle, it asks again soon.

**Who benefits:** Students preparing for exams.

**How it helps:**
- Based on the same algorithm used by Anki and other top study apps.
- No AI needed — it's pure math based on your response ratings (Again, Hard, Good, Easy, Perfect).
- Maximizes retention with minimum study time by focusing on what you're about to forget.

---

### 16-21. 📊 Core School Management
**Attendance, Marks, Assignments, Complaints, Dashboards, User Management** — these are the backbone of VidyaOS. All work without AI:
- **Teachers** mark attendance, enter marks, create assignments
- **Students** view their records, submit assignments, file complaints
- **Parents** see their child's attendance and results
- **Admins** manage users, classes, subjects, and school settings

---

### 22. 🏫 Multi-Tenant Architecture
**What it does:** Each school is completely isolated — their data, users, and settings are separate. One VidyaOS installation can serve hundreds of schools without any data mixing.

**Who benefits:** Schools, education boards, and SaaS operators.

---

### 23-24. 🔒 Compliance & Incident Management
**What it does:** Admins can export all school data as a ZIP file (for audits or data requests), manage data deletion requests, and track security incidents.

**Who benefits:** School administrators, IT teams, and legal/compliance teams.

---

## Features That REQUIRE AI

These features use a language model (LLM like Ollama/GPT) to understand text, generate content, or analyze images.

---

### 8. 🤖 AI Grading Co-Pilot
**What it does:** Teachers upload a photo of a student's handwritten answer sheet. The AI reads the handwriting, evaluates the answers, and suggests grades with explanations. The teacher then reviews and approves.

**Who benefits:** Teachers spending hours grading stacks of papers.

**How it helps:**
- Turns hours of grading into minutes — AI does the heavy analysis, teacher just reviews.
- The AI explains *why* it suggests each grade, so teachers can easily agree or adjust.
- Especially useful for descriptive/essay answers where manual grading is most time-consuming.
- Teacher always has final say — AI suggests, human decides.

**Why it needs AI:** Reading handwriting, understanding answer quality, and generating grade explanations all require a language model.

---

### 10. 📝 AI Study Tools
**What it does:** Students upload their study materials (PDFs, notes) and then ask the AI to generate:
- **Quizzes** — Multiple-choice questions with correct answers
- **Flashcards** — Front/back review cards
- **Mind Maps** — Visual topic hierarchies
- **Concept Maps** — Nodes and connections between ideas
- **Flowcharts** — Process diagrams

**Who benefits:** Students who need active recall practice materials.

**How it helps:**
- Instead of manually creating quiz questions, the AI reads your notes and generates them instantly.
- Every question comes with a citation — you can trace back to exactly which document/page the answer came from.
- Multiple formats suit different learning styles.

**Why it needs AI:** Understanding document content and generating structured educational materials requires language comprehension.

---

### 11. 📄 Document Intelligence (Upload & Ask)
**What it does:** Upload PDFs or Word documents, and the system:
1. Breaks them into searchable chunks
2. Creates embeddings (mathematical representations)
3. Stores them in a vector database
4. Lets you ask questions and get answers grounded in your actual documents

**Who benefits:** Students and teachers.

**How it helps:**
- "What does Chapter 7 say about photosynthesis?" → Gets an answer with exact page citations.
- No hallucination — answers are strictly grounded in uploaded materials.

**Why it needs AI:** Document chunking, embedding generation, and grounded question answering all require AI models.

---

### 12. 💬 AI Chat (Grounded Q&A)
**What it does:** A chat interface where students ask questions about their study materials and get accurate, citation-backed answers.

**Who benefits:** Students who want instant tutoring.

**How it helps:**
- Like having a tutor available 24/7 who has read all your textbooks.
- Every answer includes source citations so students can verify.
- Privacy-first — each school's data is isolated.

**Why it needs AI:** Natural language understanding and generation require an LLM.

---

### 13. 🎥 YouTube Lecture Ingestion
**What it does:** Teachers paste a YouTube URL, and the system extracts the transcript, chunks it, and makes it searchable via the AI tools.

**Who benefits:** Teachers who use video lectures.

**How it helps:**
- Class recordings and educational videos become part of the AI knowledge base.
- Students can ask questions about video content just like they can about PDFs.

**Why it needs AI:** Transcript processing and embedding generation require AI.

---

### 14. 📸 Student Onboarding via Photo
**What it does:** Teachers take a photo of a handwritten class list, and the system uses OCR (Optical Character Recognition) to extract student names and auto-create their accounts.

**Who benefits:** Teachers in schools where class lists are handwritten.

**How it helps:**
- No need to manually type 40+ student names — snap a photo and accounts are created.
- Works with JPG/PNG images of handwritten or printed lists.

**Why it needs AI:** Reading text from images (OCR) is an AI capability.

---

## Summary

> **Key takeaway:** 77% of VidyaOS features work without any AI infrastructure. Schools can start using the core management, gamification, and communication features immediately. AI features add the "wow factor" — intelligent tutoring, auto-grading, and study material generation.
>
> **Code quality:** All grading thresholds, attendance limits, file size constraints, and PDF colors are centralized in `backend/constants.py`. Frontend uses 50+ dark-mode-safe semantic CSS utilities — no hardcoded colors in components.

---

## New Features (25–35)

These features were added during the platform buildout and are fully implemented in the codebase.

---

### 25. 🏆 Leaderboard & Rankings
**What it does:** After exams, the system automatically ranks students by score percentage. Ties are broken by time taken. Each student can see their rank, percentile, and position relative to peers.

**Who benefits:** Students who thrive on healthy competition; teachers who want to identify top performers.

**How it helps:**
- Rankings are calculated per exam series, not globally — so every test is a fresh competition.
- Default leaderboard shows top 50 students.
- Students can look up their individual rank for any specific test.
- No AI needed — pure math on marks data.

**Backend:** `services/leaderboard.py` · **Tests:** `test_leaderboard.py` (7 tests)

---

### 26. 📄 Report Card PDF Generation
**What it does:** One-click PDF report cards for any student, including attendance summary, subject-wise marks, computed grades (A+ through F), and school branding. Uses the centralized grading scale from `constants.py`.

**Who benefits:** Teachers preparing for parent-teacher meetings; parents wanting printed progress records.

**How it helps:**
- Automatic grade computation: 90+ = A+, 80+ = A, 70+ = B+, etc.
- PDF uses consistent school colors (configurable via `PDF_PRIMARY_COLOR` and `PDF_MUTED_COLOR`).
- No manual formatting — fill in marks, click generate.

**Backend:** `services/report_card.py` · **Tests:** `test_report_card.py` (3 tests)

---

### 27. 📱 WhatsApp Notifications
**What it does:** Sends automated WhatsApp messages to parents for key events: attendance alerts ("Your child was absent today"), weekly performance digests, and exam result notifications with score emoji (🟢 ≥80%, 🟡 ≥50%, 🔴 <50%).

**Who benefits:** Parents who don't use web apps but always check WhatsApp.

**How it helps:**
- 80%+ of Indian parents prefer WhatsApp over email or web portals.
- Attendance alerts sent same day — parents know immediately if their child skipped class.
- Weekly digests include attendance %, marks summary, and AI usage count.
- No parent login required — updates come directly to their phone.

**Backend:** `services/whatsapp.py` · **Tests:** `test_whatsapp.py` (12 tests)

---

### 28. 🔗 Webhook Subscriptions
**What it does:** Schools can subscribe to system events (student enrolled, document ingested, AI query completed, exam results published, attendance marked, complaint status changed, alert raised) and receive real-time HTTP callbacks at their configured URL.

**Who benefits:** School IT teams integrating VidyaOS with other systems (SMS gateways, parent apps, analytics).

**How it helps:**
- Each subscription has a unique secret for payload signature verification.
- Delivery logs track every webhook attempt with status codes and response bodies.
- Retry logic for failed deliveries.
- Enables event-driven architecture for external integrations.

**Backend:** `services/webhooks.py` · **Tests:** `test_webhooks.py` (2 tests)

---

### 29. ⚙️ Queue Operations & Monitoring
**What it does:** Admins can view, pause, resume, drain, cancel, and retry AI jobs in the Redis-backed queue. Dead-letter handling catches permanently failed jobs. Full audit trail for every queue action.

**Who benefits:** School IT admins and platform operators.

**How it helps:**
- Real-time queue metrics: pending, processing, completed, failed, dead-letter counts.
- Cancel stuck jobs without restarting the system.
- Retry failed jobs with one click.
- Audit history shows who did what and when.

**Backend:** `services/ai_queue.py`, `routes/ai_jobs.py` · **Tests:** `test_ai_queue.py`, `test_queue_resiliency.py`

---

### 30. 🔎 Trace Viewer
**What it does:** Every AI query and queued job generates a `trace_id`. Admins can look up any trace to see the full execution timeline: retrieval, embedding, generation, sanitization, and citation validation — all with timestamps.

**Who benefits:** Admins debugging AI quality issues; platform operators diagnosing latency.

**How it helps:**
- Pinpoint exactly where in the pipeline a response went wrong.
- See which documents were retrieved, what context was built, and how citations were validated.
- Trace events are persisted in PostgreSQL for long-term analysis.

**Backend:** `services/trace_backend.py` · Persistent storage in `trace_event_records` table.

---

### 31. 🚨 Observability Alerts
**What it does:** The system evaluates configurable alert conditions (queue backlog, error rate spikes, latency thresholds) and dispatches notifications through webhook subscriptions plus email/SMS alert transports. Active alerts appear in the admin dashboard.

**Who benefits:** Platform operators who need proactive incident detection.

**How it helps:**
- No more "discovering the system was down after 3 hours."
- Alerts fire automatically when conditions are met.
- Dispatch through webhooks to Slack, PagerDuty, custom endpoints, email, or SMS.
- Alert lifecycle tracked: raised → acknowledged → resolved.

**Backend:** `services/alerting.py`, `services/observability_notifier.py` · Prometheus alert rules in `ops/observability/`.

---

### 32. 🔐 Enterprise SSO (SAML)
**What it does:** Schools using Microsoft Active Directory, Google Workspace, or other SAML identity providers can configure single sign-on. Backend stores SAML metadata, entity IDs, certificates, and attribute mappings per tenant.

**Who benefits:** Large schools and education boards with existing IT infrastructure.

**How it helps:**
- Teachers and students sign in with their school credentials — no separate VidyaOS password.
- Admin configures SSO per-tenant via API.
- Supports metadata import from IdP.
- ACS (Assertion Consumer Service) endpoint handles SAML responses.

**Backend:** `services/saml_sso.py`, `routes/enterprise.py` · Requires `python3-saml` package.

---

### 33. 🎧 Audio & Video Overviews
**What it does:** AI generates podcast-style audio discussions and narrated video slide presentations from uploaded study materials. Students can listen to or watch summaries instead of reading.

**Who benefits:** Students who learn better through audio/visual content; students with reading difficulties.

**How it helps:**
- Audio overviews sound like two people discussing the topic — engaging and natural.
- Video overviews create slide-by-slide narrated presentations.
- Both are generated from the same RAG-grounded context as text responses.
- Queued as heavy jobs — students get notified when ready.

**Why it needs AI:** Audio/video script generation requires LLM comprehension of source materials.

**Backend:** `routes/audio.py`, `routes/video.py`

---

### 34. 📊 Performance Heatmap
**What it does:** A visual matrix showing performance across subjects × classes. Color-coded cells immediately reveal which subject-class combinations are struggling (red) vs excelling (green).

**Who benefits:** Admins and teachers who need a bird's-eye view of school performance.

**How it helps:**
- Instantly spot: "Class 8B is struggling in Physics" without digging through individual marks.
- Data-driven resource allocation — assign additional support where the heatmap shows red.
- Exportable as CSV for board meetings and parent-teacher conferences.

**Backend:** Admin dashboard API · No AI needed — pure aggregation of marks data.

---

### 35. 🛡️ Upload Security (DOCX Sanitization)
**What it does:** Every DOCX file uploaded by teachers or students is automatically scanned for embedded macros (VBA projects). Malicious macros are stripped before the file is stored. Content types are rewritten from macro-enabled to standard format.

**Who benefits:** Everyone — this is a system-wide security layer.

**How it helps:**
- Prevents malicious macro execution on other users' devices.
- Transparent to uploaders — clean files pass through unchanged.
- Macro-infected files are sanitized, not rejected — the actual document content is preserved.
- Non-DOCX files (PDFs, images) are validated for type correctness.

**Backend:** `utils/upload_security.py` · **Tests:** `test_upload_security.py` (5 tests)

---

## New Features (36–55): Gap Implementations

These features were added to close all identified gaps from the STAR Features Analysis.

---

### 36. 💳 Razorpay Billing Integration
**What it does:** Automated payment collection with billing plans (basic/standard/premium), tenant subscriptions, and payment recording via Razorpay gateway.

**Who benefits:** School administrators who need automated revenue collection.

**Backend:** `models/billing.py`, `services/billing.py`, `routes/billing.py` · **Tests:** `test_billing.py` (10 tests)

---

### 37. 🌐 Hindi + Regional Language Support (i18n)
**What it does:** Full internationalization with English (en), Hindi (hi), and Marathi (mr) locale files. API endpoints for fetching translations and listing available locales.

**Who benefits:** Parents and teachers in non-English speaking regions — critical for rural Indian school adoption.

**Backend:** `locales/{en,hi,mr}.json`, `services/i18n.py`, `routes/i18n.py` · **Tests:** `test_i18n.py` (14 tests)

---

### 38. 🏢 Self-Service Tenant Onboarding
**What it does:** Schools can register themselves via API: creates tenant, admin user, default classes/subjects, and returns login credentials. Includes CSV student import.

**Who benefits:** Sales velocity — no manual DB setup per school.

**Backend:** `services/onboarding.py`, `routes/onboarding.py` · **Tests:** `test_onboarding.py` (12 tests)

---

### 39. 🎓 Admission Workflow
**What it does:** Full enrollment pipeline: application submission → document verification → review → admission/rejection. Status tracking for each applicant.

**Who benefits:** Schools that need a formal admission process instead of manual student addition.

**Backend:** `models/admission.py`, `services/admission.py`, `routes/admission.py` · **Tests:** `test_admission.py` (11 tests)

---

### 40. 💰 Fee Management Module
**What it does:** Create fee structures (tuition/lab/transport), generate invoices (bulk per class), record payments, track partial payments, generate financial reports, and view student ledgers.

**Who benefits:** School finance departments — replaces spreadsheet-based fee tracking.

**Backend:** `models/fee.py`, `services/fee_management.py`, `routes/fees.py` (7 endpoints) · **Tests:** `test_fee_management.py` (9 tests)

---

### 41. 🤖 OpenAI-Compatible API
**What it does:** Exposes `/v1/chat/completions`, `/v1/models`, `/v1/providers` endpoints in OpenAI format. Default backend is self-hosted Ollama; supports OpenAI and Anthropic as alternatives. Custom providers can be registered via `ProviderRegistry.register()`.

**Who benefits:** Developers integrating VidyaOS with external tools (LangChain, AutoGen, etc.).

**Why it needs AI:** Routes to LLM providers for chat completions.

**Backend:** `services/llm_providers.py`, `routes/openai_compat.py` · **Tests:** `test_openai_compat.py` (11 tests)

---

### 42. 🕸️ Knowledge Graph Index
**What it does:** Adds concept-relationship indexing alongside FAISS vector search. Concepts are linked via typed relationships (prerequisite, related, part_of, leads_to, example_of). BFS graph traversal retrieves related concepts.

**Who benefits:** Improved answer quality for "how does X relate to Y" queries.

**Why it needs AI:** Concept extraction and relationship inference.

**Backend:** `models/knowledge_graph.py`, `services/knowledge_graph.py` · **Tests:** `test_knowledge_graph.py` (6 tests)

---

### 43. 💭 HyDE Query Transform
**What it does:** For complex queries, generates a hypothetical answer first, then embeds that answer for retrieval instead of the raw question. Improves retrieval for multi-clause and comparison queries.

**Who benefits:** Students asking complex questions — better retrieval = better answers.

**Why it needs AI:** Hypothetical answer generation requires LLM.

**Backend:** `ai/hyde.py` · **Tests:** `test_hyde.py` (12 tests)

---

### 44. 📂 Extended Data Connectors
**What it does:** Adds PPTX (python-pptx), Excel (openpyxl), Google Docs (export URL), and Notion (API) connectors. Each returns standardized `{text, metadata, chunks}` for ingestion.

**Who benefits:** Teachers who use PowerPoint, spreadsheets, or Notion for materials.

**Why it needs AI:** Document parsing feeds into the RAG pipeline.

**Backend:** `ai/connectors.py` · **Tests:** `test_connectors.py` (8 tests)

**Integration:** PPTX/XLSX are supported in teacher/student upload flows; Google Docs and Notion are supported in `/api/ai/ingest-url` when API tokens are configured.

---

### 45. 🔒 Refresh Token Blacklisting
**What it does:** Each refresh token now carries a unique JTI (JWT ID). On rotation, old tokens are blacklisted. In-memory LRU cache (5000 entries) + PostgreSQL for persistent storage.

**Who benefits:** Security — prevents reuse of old tokens after rotation.

**Backend:** `auth/token_blacklist.py`, `auth/jwt.py` · **Tests:** `test_token_blacklist.py` (6 tests)

---

### 46. 🔗 Clickable Citations
**What it does:** AI responses enriched with clickable citations that link to source documents. Parses citation strings, resolves document IDs, generates URLs for document viewing.

**Who benefits:** Students verifying AI answers against source material.

**Why it needs AI:** Citation parsing and document-response linking.

**Backend:** `ai/citation_linker.py` · **Tests:** `test_citations.py` (10 tests)

---

### 47. 📥 Document Ingestion Watch
**What it does:** Monitors configured directories for new/modified files and auto-flags them for ingestion. Hash-based change detection prevents re-processing.

**Who benefits:** Schools that want automatic document ingestion from shared folders.

**Backend:** `services/doc_watcher.py` · **Tests:** `test_doc_watcher.py` (7 tests)

---

### 48. 🧠 Agent Orchestration (Multi-Step Workflows)
**What it does:** Chains AI modes into stateful multi-step workflows with context accumulation. 3 templates: **Deep Study** (research→quiz→study guide), **Exam Prep** (summary→practice→analysis), **Lesson Plan** (research→assessment→handout).

**Who benefits:** Students and teachers who need comprehensive outputs.

**Why it needs AI:** Orchestrates multiple LLM calls with shared state.

**Backend:** `ai/agent_orchestrator.py` · **Tests:** `test_agent_orchestrator.py` (10 tests)

---

### 49. 🫣 reCAPTCHA / Bot Protection
**What it does:** Google reCAPTCHA v3 validation on public endpoints (registration, admission, login). Score-based human detection with configurable threshold.

**Who benefits:** System security — prevents automated abuse.

**Backend:** `middleware/captcha.py` · **Tests:** `test_captcha.py` (6 tests)

---

### 50. 🧩 Module Plugin Architecture
**What it does:** Extensible plugin system with 6 hooks (on_student_enrolled, on_fee_paid, on_document_ingested, on_ai_query, on_attendance_marked, on_exam_graded). Plugins register handlers; hooks execute all handlers on events.

**Who benefits:** Developers building extensions — no core code modification needed.

**Backend:** `services/plugin_registry.py` · **Tests:** `test_plugin_registry.py` (9 tests)

---

### 51. 📚 Library Management
**What it does:** Book cataloging (ISBN, copies, shelf location), lending with due dates, return processing with overdue fine calculation (₹2/day), overdue tracking, and library stats dashboard.

**Who benefits:** Schools with libraries — replaces manual lending registers.

**Backend:** `models/library.py`, `services/library.py`, `routes/library.py` (6 endpoints) · **Tests:** `test_library.py` (7 tests)

---

### 52. ✉️ Self-Service Team Invitation
**What it does:** Admins invite teachers/staff via email with tokenized signup links. Invitees get pre-assigned role and tenant. Tokens expire after 72h and can be revoked.

**Who benefits:** Admins who need to onboard staff without manual user creation.

**Backend:** `services/team_invite.py`, `routes/invitations.py` (5 endpoints) · **Tests:** `test_team_invite.py` (9 tests)

---

### 53. 🐳 Docker Multi-Stage Build
**What it does:** Production-optimized Dockerfile: Stage 1 compiles dependencies with gcc, Stage 2 copies only runtime packages. Non-root user, health checks, gunicorn with uvicorn workers. ~120MB vs ~800MB image.

**Who benefits:** DevOps — faster deploys, smaller images, better security.

**Backend:** `Dockerfile.production`

---

**Why it needs AI:** FAQ matching uses keyword overlap scoring and supports grounded responses from VidyaOS documentation.

**Backend:** `services/docs_chatbot.py` · **Tests:** `test_docs_chatbot.py` (8 tests)

---

### 55. 📜 DPDP Act 2023 Compliance Review
**What it does:** Comprehensive compliance document covering consent, children's data, data principal rights, fiduciary obligations, cross-border transfers, and security measures. Includes prioritized action items for legal sign-off.

**Who benefits:** Legal, compliance — required before any production pilot with student data.

**Documentation:** `documentation/DPDP_COMPLIANCE.md`

---

## Summary

| Category | Count | Examples |
|----------|-------|---------|
| **Works without AI** | 41 features | Attendance, marks, fees, library, admission, onboarding, invitations, streaks, alerts, CSV bulk ops, PWA, dark mode, notifications, leaderboard, report cards, WhatsApp, webhooks, queue ops, trace viewer, alerts, SSO, heatmap, upload security, billing, i18n, plugins, token blacklisting, reCAPTCHA, doc watcher, Docker, DPDP |
| **Requires AI** | 14 features | AI chat, study tools, document intelligence, grading co-pilot, YouTube ingestion, photo onboarding, audio/video overviews, OpenAI API, knowledge graph, HyDE, connectors, citations, agent orchestration, docs chatbot |
| **Total** | **55 features** | |

> **Key takeaway:** 75% of VidyaOS features work without any AI infrastructure. Schools can start using the core management, billing, library, gamification, and communication features immediately. AI features add intelligent tutoring, auto-grading, study material generation, and ecosystem compatibility.
>
> **Code quality:** All grading thresholds, attendance limits, file size constraints, fee types, and LLM provider configs are centralized in `backend/constants.py`. Frontend uses 50+ dark-mode-safe semantic CSS utilities — no hardcoded colors in components. **438+ tests across 52 files.**
