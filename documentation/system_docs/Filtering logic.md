# Filtering Logic

**Project:** VidyaOS – AI Infrastructure for Educational Institutions  
**Version:** v0.1  
**Applies To:** ERP + AI Layer  
**Database:** PostgreSQL  
**Vector DB:** Namespace-Isolated  
**Status:** Updated to match the repository on 2026-03-06

---

## 1. Filtering Philosophy

Filtering exists at **4 independent layers**. All 4 must be enforced. Never rely on frontend filtering alone.

| Layer | Purpose |
|---|---|
| **Tenant Isolation** | Prevent cross-school data access |
| **Role-Based Access (RBAC)** | Control what each role can see |
| **Data Scope Filtering** | Filter by year, class, subject, date |
| **AI Context Filtering** | Restrict AI retrieval by namespace + metadata |

---

## 2. Layer 1 — Tenant-Level Filtering

Every database query must include:

```sql
WHERE tenant_id = :tenant_id
```

**Middleware enforcement flow:**
1. Extract JWT from request
2. Parse `tenant_id` from token claims
3. Inject `tenant_id` into request context via `TenantMiddleware`
4. Enforce in repository/query layer

**Hard rules:**
- Never allow `tenant_id` from client body or query params
- Always derive from JWT
- Automated tests must detect missing tenant filters

---

## 3. Layer 2 — Role-Based Filtering

### Student
- View only their own: attendance, marks, assignments, AI queries, uploads, review cards
```sql
WHERE tenant_id = :tenant_id AND student_id = :user_id
```
- Student must never query other students' data

### Teacher
- View students in assigned classes only
```sql
WHERE tenant_id = :tenant_id
AND class_id IN (
    SELECT class_id FROM timetable
    WHERE teacher_id = :user_id
)
```
- Cannot access admin-level analytics or financial data
- Teacher class access derived via `get_teacher_class_ids` dependency

### Admin
- Access all data within own tenant
- Manage users, view AI usage, export reports, operate queue
- Still constrained by `tenant_id`

### Parent
- View only linked child's data
```sql
WHERE tenant_id = :tenant_id
AND student_id IN (
    SELECT child_id FROM parent_links
    WHERE parent_id = :user_id
    AND tenant_id = :tenant_id
)
```
- Parent-child links managed by admin through `parent_links` table

---

## 4. Layer 3 — Data Scope Filtering

All queries should support filtering by:
- **Academic year** — prevent cross-year contamination
- **Class** — scope to specific class
- **Subject** — scope to specific subject
- **Date range** — time-bounded queries

Example:
```sql
WHERE tenant_id = :tenant_id
AND student_id = :user_id
AND academic_year = :current_year
AND date BETWEEN :start_date AND :end_date
```

---

## 5. Layer 4 — AI Context Filtering

### 5.1 Vector Namespace Isolation
Each tenant's vectors stored in separate namespace:
```python
vector_db.search(
    namespace=f"tenant_{tenant_id}",
    query_embedding=embedding,
    top_k=8
)
```
No global search allowed.

### 5.2 Subject-Based Filtering
Filter vector retrieval by subject metadata:
```python
filter={"subject_id": current_subject_id}
```
Prevents retrieval from unrelated subjects.

### 5.3 Class-Level Restriction (Optional)
Students retrieve only documents tagged to their class:
```python
filter={"class_id": student_class_id}
```

### 5.4 AI Personalization Filtering
For weak-topic insights, combine all filters:
1. Fetch student performance from ERP
2. Identify lowest-performing subject
3. Retrieve documents for that subject only (tenant + subject + class)
4. Generate targeted study material

---

## 6. AI Usage Rate Limiting

Before processing any AI query:
```python
daily_count = count_ai_queries(user_id, today)
if daily_count >= plan_limit:
    reject_request()
```
Plan-based filtering must execute **before** GPU call.

Additional rate limiting is enforced by `RateLimitMiddleware` (disabled in demo mode).

---

## 7. Middleware Stack

The API enforces filtering through a middleware chain (last added executes first):

| Middleware | Purpose | Demo Mode |
|---|---|---|
| `ObservabilityMiddleware` | Structured logging and metrics | Active |
| `CORSMiddleware` | Cross-origin request control | Active |
| `CSRFMiddleware` | State-changing request protection | Disabled |
| `TenantMiddleware` | Tenant context injection | Active |
| `RateLimitMiddleware` | Request throttling | Disabled |

---

## 8. Pagination

Large datasets must use pagination:
```sql
LIMIT 20 OFFSET :offset
```
Or cursor-based pagination for large, frequently-updated tables. 

Never allow unbounded `SELECT *` queries.

---

## 9. Data Sanitization

Before returning any API response:
- Remove internal UUIDs where appropriate
- Remove sensitive system fields
- Mask unnecessary metadata
- Students should not see other student UUIDs or internal audit data

---

## 10. AI Output Filtering

Before returning AI response, validate:
- Citation present (for Q&A mode)
- No student names from other students
- No database dumps
- No system configuration leakage
- No file paths or API keys

If violation detected → block response.

---

## 11. API-Level Filtering Flow

```
Request
  ↓
ObservabilityMiddleware (logging)
  ↓
CORSMiddleware
  ↓
CSRFMiddleware (if not demo)
  ↓
TenantMiddleware (inject tenant_id)
  ↓
RateLimitMiddleware (if not demo)
  ↓
JWT Validation
  ↓
Extract tenant_id + role
  ↓
Apply role-based filter
  ↓
Apply scope filters (class/year/date)
  ↓
Execute DB query
  ↓
Sanitize response
  ↓
Return to client
```

---

## 12. Common Filtering Vulnerabilities

| ❌ Avoid | Why |
|---|---|
| Filtering only in frontend | Backend must enforce independently |
| Trusting client-provided `tenant_id` | Must derive from JWT |
| Missing `tenant_id` in JOIN queries | Both sides of join need tenant filter |
| Cross-tenant vector search | Namespace isolation is mandatory |
| Unbounded AI query history fetch | Always paginate |

---

## 13. Performance Optimization

Index these columns for fast filtering at scale:

```sql
CREATE INDEX idx_marks_tenant_student ON marks(tenant_id, student_id);
CREATE INDEX idx_attendance_tenant_date ON attendance(tenant_id, student_id, date);
CREATE INDEX idx_ai_queries_tenant_date ON ai_queries(tenant_id, created_at);
```
