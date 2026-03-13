# Sitemap & Wireframe

**Project:** VidyaOS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Current Implementation)  
**Primary Platform:** Web (Next.js)  
**Roles:** Student / Teacher / Admin / Parent  
**Status:** Updated to match `frontend/src/app/` on 2026-03-12

**Current status note:** Admin queue operations, trace viewer, and observability alerts now have matching backend
endpoints. See `documentation/system_docs/Admin review dashboard.md` for the latest implementation notes.

---

## 1. Global Sitemap

```
/                       Landing Page (public)
/login                  Login (Google OAuth)
/demo                   Demo mode landing
│
├── /student            Student Portal (authenticated)
│   ├── /overview       Dashboard overview
│   ├── /attendance     Attendance records
│   ├── /results        Marks & performance
│   ├── /assignments    Assignment tracker
│   ├── /timetable      Weekly schedule
│   ├── /lectures       Lecture library
│   ├── /ai             AI Assistant
│   ├── /tools          Study tools (study guide, quiz, flashcards, etc.)
│   ├── /mind-map       Interactive mind map viewer
│   ├── /audio-overview Audio overview generation
│   ├── /video-overview Video overview generation
│   ├── /reviews        Spaced repetition review cards
│   ├── /upload         Student file upload
│   ├── /complaints     Complaint portal
│   └── /profile        Student profile
│
├── /teacher            Teacher Portal (authenticated)
│   ├── /dashboard      Class overview
│   ├── /classes        Class management
│   ├── /attendance     Attendance entry
│   ├── /marks          Marks entry
│   ├── /assignments    Assignment management
│   ├── /upload         Lecture / PDF upload
│   ├── /insights       AI class analytics
│   ├── /discover       Source discovery search
│   ├── /generate-assessment  AI assessment generation
│   ├── /doubt-heatmap  Student doubt aggregation
│   └── /profile        Teacher profile
│
├── /admin              Admin Portal (authenticated)
│   ├── /dashboard      KPI overview
│   ├── /users          User management
│   ├── /classes        Class & subject setup
│   ├── /timetable      Timetable management
│   ├── /reports        Report generation + CSV exports
│   ├── /ai-usage       AI usage analytics
│   ├── /ai-review      AI quality review
│   ├── /queue          Queue operations (cancel, retry, dead-letter)
│   ├── /traces         Trace viewer
│   ├── /webhooks       Webhook subscription management
│   ├── /complaints     Complaint oversight
│   ├── /billing        Plan & usage billing
│   ├── /security       Security monitoring
│   └── /settings       Tenant settings
│
└── /parent             Parent Portal (authenticated)
    ├── /dashboard      Child's performance summary
    ├── /attendance     Child's attendance
    ├── /results        Child's marks
    └── /reports        Downloadable reports + audio report
```

---

## 2. Public Pages

### 2.1 Landing Page (`/`)
- Hero section: "AI-Powered Learning for Schools"
- Features overview (6 tiles)
- Demo video embed
- Pricing tiers display
- Contact / Book Demo form
- Footer: links, legal, social

### 2.2 Login Page (`/login`)
- Google Sign-In button
- Tenant detection (based on email domain)
- Error state handling (invalid email, inactive account)

### 2.3 Demo Mode (`/demo`)
- Role switching between student, teacher, admin, parent
- Guided walkthrough
- Data reset capability

---

## 3. Student Portal Wireframes

### 3.1 Student Dashboard (`/student/overview`)
```
┌─────────────────────────────────────────────────────┐
│ Top Nav: Logo | Notifications | Profile              │
├──────────┬──────────────────────────────────────────┤
│ Sidebar  │  Quick Stats Cards                        │
│          │  ┌────────┐ ┌────────┐ ┌────────┐        │
│ Overview │  │Attend%  │ │Avg Mark│ │Due Assg│        │
│ Attend.  │  │  92%    │ │  78%   │ │   3    │        │
│ Results  │  └────────┘ └────────┘ └────────┘        │
│ Assign.  │                                           │
│ Schedule │  Upcoming Classes (today)                 │
│ Lectures │  ┌─────────────────────────────────┐      │
│ AI Asst. │  │ 10:00 - Math │ 11:00 - Science │      │
│ Tools    │  └─────────────────────────────────┘      │
│ Reviews  │                                           │
│ Upload   │  AI Insight Panel                         │
│ Complain │  "Your Algebra scores dropped 15%.        │
│          │   Review Chapter 3."                      │
└──────────┴──────────────────────────────────────────┘
```

### 3.2 AI Assistant (`/student/ai`)
```
┌─────────────────────────────────────────────┐
│ AI Study Assistant                           │
│                                              │
│ ┌──────────────────────────────────────┐     │
│ │ Ask about your notes...              │     │
│ └──────────────────────────────────────┘     │
│                                              │
│ Mode: [Q&A] [Study Guide] [Quiz] [Concept]  │
│       [Flowchart] [Mind Map] [Flashcards]   │
│       [Socratic] [Perturbation] [Debate]    │
│       [Essay Review] [Career Simulation]    │
│                                              │
│ ┌──────────────────────────────────────┐     │
│ │ AI Response                          │     │
│ │                                      │     │
│ │ Photosynthesis occurs in the         │     │
│ │ chloroplasts of plant cells.         │     │
│ │                                      │     │
│ │ Citations:                           │     │
│ │ [Biology_Ch3_p12] [Biology_Ch3_p14] │     │
│ └──────────────────────────────────────┘     │
│                                              │
│ Token usage: 42/100 today                    │
│ ████████████████░░░░░░░░                     │
└─────────────────────────────────────────────┘
```

### 3.3 Results Page (`/student/results`)
- Subject cards with exam list (Midterm, Final)
- Performance trend graph (line chart over time)
- AI Insight Panel: "Your performance dropped in Algebra. Review Chapter 3."

### 3.4 Assignments Page (`/student/assignments`)
- Tabs: [Pending] [Submitted] [Graded]
- Assignment card: Title, Subject, Due Date, Upload Button, AI Help Button

### 3.5 Lecture Library (`/student/lectures`)
- Subject filter dropdown
- Lecture cards: thumbnail, title, description, transcript badge
- "Ask AI about this lecture" button per card

### 3.6 Study Tools (`/student/tools`)
- Study tool generation interface
- Supports all 13 text modes via queued or synchronous execution
- Structured output rendering for each mode

### 3.7 Audio & Video Overview
- `/student/audio-overview`: generates podcast-style dialogue overview from study materials
- `/student/video-overview`: generates narrated slide presentation from study materials

### 3.8 Spaced Repetition Reviews (`/student/reviews`)
- Due and upcoming review cards
- SM-2 algorithm for scheduling
- Quality self-rating (1=Again to 5=Perfect)
- Topic and subject-scoped cards

### 3.9 Student Upload (`/student/upload`)
- Upload PDF/DOCX study materials
- Files ingested into RAG pipeline
- Upload history with pagination

---

## 4. Teacher Portal Wireframes

### 4.1 Teacher Dashboard (`/teacher/dashboard`)
```
┌────────────────────────────────────────────┐
│ Class Overview Cards                        │
│  ┌──────────┐ ┌──────────┐                 │
│  │ Class 5A  │ │ Class 6B  │                │
│  │ 32 studs  │ │ 28 studs  │                │
│  └──────────┘ └──────────┘                 │
│                                             │
│ Recent Submissions (5 latest)               │
│                                             │
│ AI Class Analytics                          │
│ "30% of students weak in Algebra."          │
└────────────────────────────────────────────┘
```

### 4.2 Marks Entry (`/teacher/marks`)
- Select: Class → Subject → Exam
- Student list with inline marks input field
- Save button with validation

### 4.3 Upload Page (`/teacher/upload`)
- Upload PDF or Paste YouTube URL
- Ingestion status: Pending → Processing → Completed

### 4.4 AI Class Insights (`/teacher/insights`)
- Class performance chart
- Weak topics breakdown (bar chart)
- "Generate Class-Level Study Guide" button

### 4.5 Source Discovery (`/teacher/discover`)
- DuckDuckGo-powered educational resource search
- URL ingestion for discovered sources
- Results include NCERT, Wikipedia, PDF sources

### 4.6 Assessment Generator (`/teacher/generate-assessment`)
- Subject and topic selection
- NCERT-aligned formative assessment generation via RAG + LLM
- Configurable number of questions

### 4.7 Doubt Heatmap (`/teacher/doubt-heatmap`)
- Aggregated student AI queries by subject
- Identifies doubt hotspots across classes
- Helps teachers prioritize revision topics

---

## 5. Admin Portal Wireframes

### 5.1 Admin Dashboard (`/admin/dashboard`)
```
KPI Cards:
┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│Students│ │Active  │ │AI Quer.│ │Avg     │ │Avg     │ │Open    │
│  420   │ │Today 89│ │Today 56│ │Attend. │ │Perform.│ │Complnt.│
│        │ │        │ │        │ │  92%   │ │  78%   │ │   4    │
└────────┘ └────────┘ └────────┘ └────────┘ └────────┘ └────────┘

Performance Heatmap:
Subjects × Classes grid, color-coded by average score.
```

### 5.2 AI Usage Analytics (`/admin/ai-usage`)
- Query count by day (line graph)
- AI usage by role (pie chart: Students 85%, Teachers 10%, Admin 5%)
- Top queried subjects (bar chart)
- Heavy users table with flag system

### 5.3 AI Quality Review (`/admin/ai-review`)
- Random sample AI responses with: Query, Response, Citations, Response Time
- Actions: Approve, Flag
- Detailed review with trace context

### 5.4 Queue Operations (`/admin/queue`)
- Queue metrics (pending, processing, completed, failed, dead-letter counts)
- Job list with status filtering
- Per-job actions: Cancel, Retry, Dead-letter
- Audit history for queue actions

### 5.5 Trace Viewer (`/admin/traces`)
- Trace lookup by `trace_id`
- Per-request event timeline
- Cross-service trace propagation view

### 5.6 Webhook Management (`/admin/webhooks`)
- Webhook subscription list
- Create / toggle / delete subscriptions
- Delivery logs per subscription

### 5.7 Reports (`/admin/reports`)
- Attendance, performance, and AI usage reports
- CSV export for attendance, performance, AI usage

---

## 6. Parent Portal

### 6.1 Parent Dashboard (`/parent/dashboard`)
- Child's performance summary
- Attendance overview
- Recent results
- Audio report generation (TTS-ready text summary)

### 6.2 Child's Attendance (`/parent/attendance`)
### 6.3 Child's Results (`/parent/results`)
### 6.4 Reports (`/parent/reports`)
- Downloadable progress reports

---

## 7. Navigation Structure (Role-Based Sidebar)

| Student | Teacher | Admin | Parent |
|---|---|---|---|
| Overview | Dashboard | Dashboard | Dashboard |
| Attendance | Classes | Users | Attendance |
| Results | Attendance | Classes | Results |
| Assignments | Marks | Timetable | Reports |
| Timetable | Assignments | Reports | |
| Lectures | Upload | AI Analytics | |
| AI Assistant | Insights | AI Review | |
| Tools | Discover | Queue | |
| Reviews | Assessment | Traces | |
| Upload | Doubt Heatmap | Webhooks | |
| Complaints | Profile | Complaints | |
| Profile | | Billing | |
| | | Security | |
| | | Settings | |
