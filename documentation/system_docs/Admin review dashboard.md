# Admin Review Dashboard

**Project:** VidyaOS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Current Implementation)  
**Role:** Tenant Admin (School-Level)  
**Access Level:** Highest within Tenant  
**Status:** Updated to match backend routes and frontend pages on 2026-03-25

---

## 1. Dashboard Purpose

The Admin Dashboard is the institutional governance control center. It provides:

1. **Visibility** — institutional performance at a glance via KPI cards and performance heatmap
2. **Monitoring** — AI usage analytics, queue metrics, and trace inspection
3. **Quality Control** — AI response review with approve / flag actions
4. **Governance** — user, class, timetable, parent link, and webhook management
5. **Operations** — queue controls, incident lifecycle, CSV exports
6. **Risk Detection** — security logs, audit trail, observability alerts
7. **Feature Management** — toggle 61 features individually or apply system profiles
8. **Branding** — white-label customization with logo upload and automated color extraction

> Admin must feel in control. This is not a chatbot interface — it is an operations center.

---

## 2. Overview Panel (`/admin/dashboard`)

### KPI Cards (top row)

| Metric | Description |
|---|---|
| Total Students | Active student accounts |
| Active Users Today | Logged in today |
| AI Queries Today | Total AI requests |
| Avg Attendance | Across all classes |
| Avg Performance | Aggregated score |
| Open Complaints | Pending resolution |

### Performance Heatmap

Grid: Subjects → (columns), Classes ↓ (rows)  
Color-coded: Green (>80%), Yellow (60-80%), Red (<60%)  
Data source: `subject_performance` table, served by `/api/admin/performance-heatmap`.

---

## 3. AI Usage Panel (`/admin/ai-usage`)

### Daily AI Query Stats
- Total queries, queries by mode, top queried subjects
- Usage breakdown by role

### Heavy Users
- Flag system for users exceeding threshold

---

## 4. AI Quality Review Panel (`/admin/ai-review`)

### Sample Responses
Display: Query, AI Response, Citations, Response Time, Mode  
Admin can: **Approve** or **Flag**

### Review Detail
For any specific query, admin can view:
- Query text, response text, citations, response time
- Trace ID for debugging
- Token usage
- Review state (approved / flagged / unreviewed)

All review actions logged in `audit_logs`.

---

## 5. Queue Operations Panel (`/admin/queue`)

### Queue Metrics
- Pending, processing, completed, failed, dead-letter, cancelled counts
- Queue depth and throughput

### Job List
- Filterable by status and job type
- Per-job detail view with request/result payloads and event timeline

### Job Actions
- **Cancel** — stop a pending or processing job
- **Retry** — re-enqueue a failed job
- **Dead-letter** — move a failed job to dead-letter queue

### Audit History
- Chronological audit trail of all queue operations
- Records who performed what action and when

---

## 6. Trace Viewer (`/admin/traces`)

Trace lookup by `trace_id`:
- Per-request event timeline across API, queue, worker, and AI service
- Stage, source, status, and detail for each event
- Cross-service trace propagation

---

## 7. User Management Panel (`/admin/users`)

### User Table
Columns: Name, Email, Role, Status, Created At

### Actions
- Change role
- Deactivate user
- All actions logged in `audit_logs`

---

## 8. Class & Subject Management (`/admin/classes`)

- List all classes with enrolled students, subjects, and exam counts
- Create new classes and subjects
- Tenant-scoped

---

## 9. Timetable Management (`/admin/timetable`)

- View timetable grid per class (day × time slots)
- Create and delete timetable slots
- Teacher assignment to slots

---

## 10. Parent Link Management

Managed through admin routes:
- List all parent-child links
- Create new links (parent user ↔ child user)
- Delete links
- All mutations logged in `audit_logs`

---

## 11. Complaints Review Panel (`/admin/complaints`)

Filters: Open, In Review, Resolved  
Admin can: Update status, add resolution note  
Status transitions logged in `audit_logs`.

---

## 12. Reports Panel (`/admin/reports`)

Summary reports:
- Attendance summary grouped by class
- Performance summary grouped by subject
- AI usage report

CSV exports:
- `/api/admin/export/attendance` — attendance data as CSV
- `/api/admin/export/performance` — student performance as CSV
- `/api/admin/export/ai-usage` — AI usage data as CSV

All reports respect tenant isolation.

---

## 13. Webhook Management (`/admin/webhooks`)

### Subscription Management
- Create, toggle active/inactive, and delete webhook subscriptions
- Supported events: `student.enrolled`, `document.ingested`, `ai.query.completed`, `exam.results.published`, `attendance.marked`, `complaint.status.changed`, `observability.alert.raised`

### Delivery Logs
- Per-subscription delivery history
- Status, attempt count, status code, response body

---

## 14. Observability Alerts

- Alert evaluation based on queue metrics and system state
- Dispatch alerts through configured webhook subscriptions
- Incident auto-sync from active alerts

---

## 15. Billing Panel (`/admin/billing`)

Shows: Current plan tier, student count, AI daily limit, plan features  
Informational only for pilot (manual billing).

---

## 16. Security Monitoring (`/admin/security`)

Admin can see:
- Recent audit log entries
- Action history for admin operations
- Queue operation audit trail

Data source: `audit_logs` table.

---

## 17. Settings Panel (`/admin/settings`)

- View and update tenant name
- Configure AI daily limit
- Tenant-scoped settings

---

## 18. Feature Management Panel (`/admin/feature-flags`)

### Feature Catalog
- Lists all 61 platform features with toggle switches
- Each feature displays color-coded badges for:
  - **AI Intensity:** Heavy AI (red), Medium AI (orange), Low AI (yellow), No AI (green)
  - **ERP Module:** Student Management, Learning, Finance, Admissions, etc.

### System Configuration Profiles
Quick-apply buttons at the top of the dashboard:
- **AI Tutor Mode** — maximizes generative AI features
- **AI Helper Mode** — balanced ERP + ambient AI
- **Full ERP Mode** — disables heavy AI, pure admin mode

Profile application triggers `POST /api/features/profile/{profile_name}` which bulk-updates all feature flags.

---

## 19. White-Label Branding Panel (`/admin/branding`)

### Branding Configuration
- **Logo Upload:** Drag-and-drop file zone with preview
- **Color Extraction:** Automated palette generation from uploaded logo via `colorthief`
- **Manual Overrides:** Hex color pickers for primary, secondary, accent colors
- **Font Selection:** Font family dropdown
- **Live Preview:** Real-time iframe showing how the theme will appear
- **Save & Apply:** Persists to tenant record, injected as CSS custom properties via `BrandingProvider`

---

## 20. Permission Matrix

| Feature | Student | Teacher | Admin | Parent |
|---|---|---|---|---|
| View own performance | ✅ | ❌ | ✅ | ✅ (child) |
| View class performance | ❌ | ✅ | ✅ | ❌ |
| View AI usage analytics | ❌ | ❌ | ✅ | ❌ |
| Manage users | ❌ | ❌ | ✅ | ❌ |
| Review AI responses | ❌ | ❌ | ✅ | ❌ |
| Export reports / CSV | ❌ | ❌ | ✅ | ❌ |
| Queue operations | ❌ | ❌ | ✅ | ❌ |
| View traces | ❌ | ❌ | ✅ | ❌ |
| Manage webhooks | ❌ | ❌ | ✅ | ❌ |
| View security logs | ❌ | ❌ | ✅ | ❌ |
| Manage feature flags | ❌ | ❌ | ✅ | ❌ |
| Configure branding | ❌ | ❌ | ✅ | ❌ |
| Upload materials | ✅ | ✅ | ❌ | ❌ |
| Discover sources | ❌ | ✅ | ✅ | ❌ |
