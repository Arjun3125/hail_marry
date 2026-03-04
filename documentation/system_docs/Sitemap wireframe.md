# Sitemap & Wireframe

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot UX Blueprint)  
**Primary Platform:** Web (Next.js)  
**Roles:** Student / Teacher / Admin / Parent (Phase 2)

---

## 1. Global Sitemap

```
/                       Landing Page (public)
/login                  Login (Google OAuth)
│
├── /student            Student Portal (authenticated)
│   ├── /overview       Dashboard overview
│   ├── /attendance     Attendance records
│   ├── /results        Marks & performance
│   ├── /assignments    Assignment tracker
│   ├── /timetable      Weekly schedule
│   ├── /lectures       Lecture library
│   ├── /ai             AI Assistant
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
│   └── /profile        Teacher profile
│
├── /admin              Admin Portal (authenticated)
│   ├── /dashboard      KPI overview
│   ├── /users          User management
│   ├── /classes        Class & subject setup
│   ├── /timetable      Timetable management
│   ├── /reports        Report generation
│   ├── /ai-usage       AI usage analytics
│   ├── /ai-review      AI quality review
│   ├── /complaints     Complaint oversight
│   ├── /billing        Plan & usage billing
│   ├── /security       Security monitoring
│   └── /settings       Tenant settings
│
└── /parent             Parent Portal (Phase 2)
    ├── /dashboard      Child's performance summary
    ├── /attendance     Child's attendance
    ├── /results        Child's marks
    └── /reports        Downloadable reports
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
│ Complain │  └─────────────────────────────────┘      │
│          │                                           │
│          │  AI Insight Panel                         │
│          │  "Your Algebra scores dropped 15%.        │
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
```

### 5.2 AI Usage Analytics (`/admin/ai-usage`)
- Query count by day (line graph)
- AI usage by role (pie chart: Students 85%, Teachers 10%, Admin 5%)
- Top queried subjects (bar chart)
- Heavy users table with flag system

### 5.3 AI Quality Review (`/admin/ai-review`)
- Random sample AI responses with: Query, Response, Citations, Response Time
- Actions: Approve, Flag, Mark Incorrect
- Flagged responses list with Review/Dismiss/Escalate

---

## 6. Navigation Structure (Role-Based Sidebar)

| Student | Teacher | Admin |
|---|---|---|
| Overview | Dashboard | Dashboard |
| Attendance | Classes | Users |
| Results | Assignments | Reports |
| Assignments | Upload | AI Analytics |
| Timetable | Insights | AI Review |
| AI Assistant | Profile | Complaints |
| Complaints | | Billing |
| Profile | | Settings |

---

## 7. MVP Wireframe Scope

**Pilot — implement only:**
- Login
- Student Dashboard + Attendance + Results
- AI Assistant (Q&A mode only)
- Teacher Upload + Marks Entry
- Admin User Management + AI Usage

**Defer to Phase 2:**
- Billing UI (manual billing initially)
- Advanced analytics dashboards
- Concept map visualization
- Parent portal
