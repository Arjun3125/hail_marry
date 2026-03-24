# VidyaOS Deep Feature Guide — Under The Hood

**What actually runs when you click a button or send a WhatsApp message.**
Written for school decision-makers who want to know exactly what they're buying.

---

## 📱 THE WHATSAPP ENGINE — The Heart of VidyaOS

This is what sets VidyaOS apart from every competitor in India.

### How It Actually Works (Technical Truth)

**Step 1: Parent sends "Mera bachcha aaj school gaya tha kya?" on WhatsApp**

**Step 2: Three-Stage AI Classification** (takes less than 1 second)
1. **Heuristic Match:** The system checks for Hindi/English keywords like "attendance," "absent," "homework" — instant match, zero AI cost
2. **Similarity Score:** If keywords don't match, it uses Jaccard similarity scoring against 14 tool descriptions — still no AI needed
3. **LLM Fallback:** Only for truly complex questions does the system call the AI model

**Step 3: Role-Based Access Control (RBAC)**
- If you're a **parent** and type "attendance" → You see *your child's* attendance
- If you're a **teacher** and type "attendance" → You see *which students are absent*
- If you're an **admin** and type "attendance" → You see *whole school summary*
- Same word, different data. Nobody sees what they shouldn't.

**Step 4: Security Stack**
- **HMAC-SHA256 Signature Verification:** Every incoming WhatsApp message is cryptographically verified
- **OTP Authentication:** 6-digit code, 5-minute expiry, max 3 attempts, then auto-locks
- **Rate Limiting:** 10 messages per minute per phone — prevents spam abuse
- **Message Deduplication:** If WhatsApp sends the same message twice (network glitch), system processes it only once
- **Session Durability:** Your conversation state is stored in both Redis (speed) and PostgreSQL (permanence). If Redis crashes, PostgreSQL takes over within milliseconds

### 14 WhatsApp Tools — What Each Does

| Tool | Who Can Use | What It Returns |
|---|---|---|
| `get_student_timetable` | Student | Today's class schedule with times and subjects |
| `get_student_tests` | Student | Upcoming exams and quiz schedule |
| `get_student_assignments` | Student | Pending homework with due dates |
| `get_student_attendance` | Student | Attendance record (present/absent/leave) |
| `get_student_results` | Student | Subject-wise marks and averages |
| `get_student_weak_topics` | Student | Subjects scoring below 60% with study suggestions |
| `get_teacher_absent_students` | Teacher | Today's absent students list |
| `get_teacher_schedule` | Teacher | Teacher's own class schedule |
| `get_child_performance` | Parent | Child's marks, grades, and weak subjects |
| `get_child_attendance` | Parent | Child's attendance record |
| `get_child_homework` | Parent | Child's pending assignments |
| `get_school_attendance_summary` | Admin | School-wide present/absent counts |
| `get_fee_pending_report` | Admin | Outstanding fee amounts with breakdowns |
| `check_library_catalog` | Admin | Book availability and catalog search |

**Plus:** Unlimited natural-language AI chat for anything else — "Explain photosynthesis," "What's the capital of France," etc.

---

## 🏫 ENTERPRISE ONBOARDING ENGINE

### What Happens When You Upload a 500-Student CSV

**The "5-Way Relational Link" — under 2 seconds:**

```
CSV Row: "Rahul Sharma, Class 8B, parent: rahul.parent@gmail.com, +919876543210"
```

1. ✅ **Creates Student Account** → `User(role="student", name="Rahul Sharma")`
2. ✅ **Creates Parent Account** → `User(role="parent", email="rahul.parent@gmail.com")`
3. ✅ **Links Parent ↔ Child** → `ParentLink(parent_id, child_id)`
4. ✅ **Enrolls in Class** → `Enrollment(student_id, class_id="8B")`
5. ✅ **Triggers WhatsApp Welcome** → Webhook fires → Parent gets a magic login link on WhatsApp

**Error Handling:** If a parent email already exists, the system links to the existing account instead of failing. If a class doesn't exist, it creates it. No manual cleanup needed.

---

## 📅 TIMETABLE GENERATOR — The Constraint Solver

### What Actually Happens When You Click "Generate"

This isn't a random assignment. It's a **heuristic backtracking algorithm** that:

1. **Builds a Time Grid:** Configurable days per week (5 or 6), periods per day (7-8), period length (40-45 min), and break slots
2. **Maps Teacher Availability:** Available days, blocked periods, max hours per day, max hours per week
3. **Places Fixed Lessons First:** If Physics must be Period 1 on Monday, it locks that in first
4. **Runs Smart Backtracking:**
   - Tries most constrained requirements first (fewer options = solve first)
   - Balances subjects across the week (no 3 Math on Monday)
   - Prevents same-subject back-to-back for classes
   - Prevents same-teacher back-to-back (teacher needs a break)
   - Explores up to 200,000 candidate placements before declaring infeasible
5. **Returns:** Complete schedule with times, teacher loads (daily + weekly), and a balance score

**If it fails:** Returns a detailed conflict report saying exactly which constraint couldn't be satisfied — "Teacher X needs 6 periods but only has 4 available slots."

---

## 💰 FEE MANAGEMENT — Every Rupee Tracked

### The Financial Sub-Ledger

- **Fee Structures:** Tuition ₹5,000/month, Lab Fee ₹2,000/term, Transport ₹1,500/month — per class or school-wide
- **Bulk Invoice Generation:** Select Class 8B → System finds 40 enrolled students → Creates 40 individual invoices → Skips duplicates automatically
- **Partial Payment Tracking:**
  - Invoice: ₹12,000 due
  - Payment 1: ₹5,000 on Jan 15 via Razorpay (Ref: `rzp_txn_abc123`) → Status: `partial`
  - Payment 2: ₹7,000 on Feb 10 via cash → Status: `paid`
- **Financial Dashboard:** Total due vs. collected, collection rate %, breakdown by pending/partial/paid/overdue
- **Per-Student Ledger:** Complete chronological history of every invoice and payment for any child

---

## 🎮 GAMIFICATION ENGINE — How Streaks Actually Work

### The Login Streak Algorithm

```
Today's login:
  → Is this the FIRST login ever? → Create streak record: current=1, longest=1, total=1
  → Already logged in TODAY? → Do nothing (no double-counting)
  → Logged in YESTERDAY? → current_streak += 1 (streak continues!)
  → Missed yesterday? → current_streak = 1 (streak resets, but longest is preserved)
```

### 10 Achievement Badges

| Badge | Icon | Unlock Condition |
|---|---|---|
| First Login | 🏅 | Log in once |
| 3-Day Streak | ⚡ | 3 consecutive days |
| Week Warrior | 🔥 | 7 consecutive days |
| Fortnight Focus | 💪 | 14 consecutive days |
| 30-Day Scholar | ⭐ | 30 consecutive days |
| 100-Day Champion | 🏆 | 100 consecutive days |
| 10 Sessions | 📚 | 10 total study sessions |
| 50 Sessions | 🎓 | 50 total study sessions |
| Century Club | 💯 | 100 total study sessions |
| All-Time 30 Legend | 🌟 | Longest streak ever hits 30 |

---

## 🎓 ADMISSION PIPELINE — State Machine Workflow

### Application Lifecycle

```
Pending → Under Review → Accepted → Enrolled (auto-creates student account)
                       → Rejected (with notes)
```

- **Strict Transitions:** Can't jump from "Pending" to "Enrolled" — must go through review
- **Bulk Enrollment:** Select 50 accepted applications → One click → 50 student accounts + 50 class enrollments created in a single database transaction
- **Duplicate Protection:** If a student with the same email already exists, the system blocks enrollment and reports the duplicate
- **Statistics Dashboard:** Live counts: 120 pending, 45 reviewing, 30 accepted, 25 enrolled, 5 rejected

---

## 🚨 INCIDENT ESCALATION — The Reliability Chain

### What Happens When Something Breaks

1. **Alert fires** (e.g., "AI queue backlog exceeds 100 jobs")
2. **Incident created** → Status: `open`
3. **Route matched** → Checks severity filter → Delivers to configured channel:
   - **Slack Webhook** → Posts to #ops-alerts channel
   - **Email** → Sends formatted HTML email to admin
   - **SMS** → Sends text message to admin phone
   - **PagerDuty** → Creates P1 incident
   - **OpsGenie** → Creates alert
4. **No response in 15 minutes?** → **Auto-Escalation** kicks in → Sends to the escalation channel (SMS if primary was Slack)
5. **Admin acknowledges** → Status: `acknowledged` → Timer stops
6. **Admin resolves** → Status: `resolved` → Incident closed with resolution note

**Every step is permanently logged** as an `IncidentEvent` with timestamp, actor, and full payload.

---

## 📊 ANALYTICS ENGINE — Why Your Dashboard Is Fast

### Redis-Backed Hot Caching

- Every 15 minutes, a background job runs across all active tenants
- Calculates: total students, present today, absent today, pending fee amounts
- Stores results in Redis cache with 15-minute TTL
- Dashboard reads from Redis (microseconds) instead of running SQL queries against the full database (seconds)
- **Result:** Even with 10,000 students, the admin dashboard loads in under 200ms

---

## 🔐 SECURITY LAYERS — Indian Data Protection (DPDP Act 2023)

| Layer | What It Does |
|---|---|
| **SAML 2.0 SSO** | Google/Microsoft login — no separate VidyaOS password |
| **reCAPTCHA v3** | Invisible bot protection on login, registration, admission forms |
| **JWT Token Blacklisting** | Old refresh tokens are permanently killed on rotation (LRU cache + PostgreSQL) |
| **DOCX Macro Sanitization** | Every uploaded Word file is scanned and stripped of embedded macros |
| **Consent Management** | Ready for children's data consent requirements under DPDP Act |
| **Data Export** | Full school data downloadable as ZIP for compliance audits |
| **Multi-Tenant Isolation** | Every SQL query is scoped to `tenant_id` — impossible to leak data between schools |

---

## 🏛️ INFRASTRUCTURE

| Component | Technology | Purpose |
|---|---|---|
| Backend | FastAPI (Python) | REST API + WebSocket notifications |
| Database | PostgreSQL | All school data, audit logs, sessions |
| Cache | Redis | WhatsApp sessions, rate limits, analytics, AI job queue |
| AI Engine | Ollama / OpenAI / Anthropic (configurable) | Grading, tutoring, quiz generation |
| Vector Store | FAISS | Document search for AI-grounded answers |
| WhatsApp | Meta Cloud API | Two-way messaging, interactive lists, quick-reply buttons |
| AI Agent | LangGraph (StateGraph) | 4-node intent→tool→response→format pipeline |
| Frontend | Next.js + React | Student/Teacher/Parent/Admin dashboards |
| Deployment | Docker multi-stage build | 120MB production image (vs 800MB unoptimized) |

---

*VidyaOS — Har School Ke Liye, Har Budget Mein* 🇮🇳
