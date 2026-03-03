# Admin Review Dashboard

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Pilot → Scale)  
**Role:** Tenant Admin (School-Level)  
**Access Level:** Highest within Tenant

---

## 1. Dashboard Purpose

The Admin Dashboard is the institutional governance control center. It must allow:

1. **Visibility** — see institutional performance at a glance
2. **Monitoring** — track AI usage and operational cost
3. **Quality Control** — review and audit AI responses
4. **Governance** — manage users, roles, and quotas
5. **Risk Detection** — spot anomalies, abuse, and security events

> Admin must feel in control. This is not a chatbot interface — it is an operations center.

---

## 2. Overview Panel (Default View)

### KPI Cards (top row, real-time)

| Metric | Description | Refresh Rate |
|---|---|---|
| Total Students | Active student accounts | 60s |
| Active Users Today | Logged in today | 60s |
| AI Queries Today | Total AI requests | 5 min |
| Avg Attendance | Across all classes | Daily |
| Avg Performance | Aggregated score | Daily |
| Open Complaints | Pending resolution | 60s |

Cards must be filterable by date range.

---

## 3. Academic Insights Panel

### 3.1 Performance Heatmap
Grid: Subjects → (columns), Classes ↓ (rows)  
Color-coded: Green (>80%), Yellow (60-80%), Red (<60%)  
Data source: `subject_performance` table

### 3.2 Weak Topic Distribution
Bar chart showing percentage breakdown of weakest topics across all students.  
Allows admin to identify curriculum gaps and allocate teacher attention.

### 3.3 Attendance Trends
Line graph: monthly attendance % with class-level breakdown.  
Absence spike detection with visual alerts.

---

## 4. AI Usage Panel

### 4.1 Daily AI Query Graph
Line graph: queries per day, peak hours, query spikes.

### 4.2 AI Usage by Role

| Role | Typical % |
|---|---|
| Students | ~85% |
| Teachers | ~10% |
| Admin | ~5% |

### 4.3 Top Queried Subjects
Bar chart: Math, Science, English, etc.  
Helps understand academic demand patterns.

### 4.4 Heavy Users Table

| Column | Description |
|---|---|
| Student Name | Student identifier |
| Queries Today | Count for current day |
| Flag | ⚠️ if exceeding threshold |

Admin can: temporarily restrict user, reset AI quota.

---

## 5. AI Quality Review Panel

### 5.1 Random Sample Responses
Display: Query, AI Response, Citations, Response Time  
Admin can: Approve, Flag, Mark Incorrect

### 5.2 Flagged AI Responses
Students can report: incorrect answer, inappropriate content  
Admin actions: Review, Dismiss, Escalate

### 5.3 AI Query Trace Viewer
For any specific query, admin can view:
- Query text → embedding → retrieved chunks → reranked context → LLM prompt → response
- Trace ID for debugging
- Token usage breakdown

---

## 6. User Management Panel

### User Table
Filters: Role, Class, Active/Inactive, AI Usage Level  
Columns: Name, Role, Class, Status, Last Login, AI Queries (30d)

### Actions
- Activate / Deactivate user
- Reset password (if applicable)
- Change role
- Reset AI quota
- All actions logged in `audit_logs`

---

## 7. Complaints Review Panel

Filters: Open, In Review, Resolved, Category  
Detail view: Student, Description, Status, Resolution Timeline  
Admin can: Assign to teacher, Mark resolved, Add resolution note

---

## 8. Reports Panel

Exportable reports:
- Student performance report (PDF)
- Class performance summary (CSV)
- AI usage summary (CSV)
- Attendance report (PDF/CSV)

All reports respect tenant isolation.

---

## 9. Billing Panel

Shows: Current plan, AI credit usage, Estimated cost, Upgrade option  
For pilot: informational only (manual billing).

---

## 10. Security Monitoring Panel

Admin must see:
- Failed login attempts (count + user)
- Role changes (who changed whom)
- Suspicious activity (excessive queries, unusual hours)
- Cross-tenant attempts (should always be zero)

Data source: `audit_logs` table.

---

## 11. Permission Matrix

| Feature | Student | Teacher | Admin |
|---|---|---|---|
| View own performance | ✅ | ❌ | ✅ |
| View class performance | ❌ | ✅ | ✅ |
| View AI usage analytics | ❌ | ❌ | ✅ |
| Manage users | ❌ | ❌ | ✅ |
| Review AI responses | ❌ | Limited | ✅ |
| Export reports | ❌ | Own class | ✅ |
| Reset AI quotas | ❌ | ❌ | ✅ |
| View security logs | ❌ | ❌ | ✅ |

---

## 12. Critical Governance Rules

Admin must always be able to:
- Disable AI for a specific class
- Reduce AI quota for any user
- Temporarily disable any user
- Export all tenant data
- View full audit trail

**Control is non-negotiable.**

---

## 13. Data Refresh Strategy

| Data | Refresh Rate |
|---|---|
| KPI cards | Every 60 seconds |
| AI usage metrics | Every 5 minutes |
| Academic stats | Daily recalculation (cron) |
| Reports | On-demand generation |

Use precomputed aggregation tables and cached statistics. Avoid real-time heavy joins.
