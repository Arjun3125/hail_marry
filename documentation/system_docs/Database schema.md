# Database Schema

**Project:** AIaaS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Phase 1 — Pilot)  
**Database:** PostgreSQL 15+  
**Architecture:** Multi-Tenant (Shared DB, Logical Isolation)

---

## 1. Design Principles

1. All core tables include `tenant_id` — no exceptions
2. No cross-tenant queries allowed at the application or DB level
3. ERP data is authoritative — AI layer reads but never mutates
4. Auditability built into every write operation
5. Scalable to 10k–50k students with indexing strategy
6. Foreign key enforcement + NOT NULL on critical fields
7. Soft delete strategy (`is_deleted` flag) to prevent accidental data loss

---

## 2. Core Multi-Tenant Model

### 2.1 Tenants

```sql
CREATE TABLE tenants (
    id UUID PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    plan_tier VARCHAR(50),           -- 'basic', 'pro', 'advanced', 'enterprise'
    max_students INT,
    ai_daily_limit INT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

Each school = one tenant. All system data references back to this table.

---

## 3. User & Role System

### 3.1 Users

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    google_id VARCHAR(255) UNIQUE,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) CHECK (role IN ('student', 'teacher', 'admin', 'parent')),
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

**Design decision:** `parent` role added for Phase 2 parent portal access. `is_deleted` enables soft delete.

---

## 4. Academic Structure

### 4.1 Classes

```sql
CREATE TABLE classes (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(100),
    grade_level VARCHAR(50),
    academic_year VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.2 Subjects

```sql
CREATE TABLE subjects (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(100),
    class_id UUID REFERENCES classes(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 4.3 Student Enrollment

```sql
CREATE TABLE enrollments (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    student_id UUID REFERENCES users(id),
    class_id UUID REFERENCES classes(id),
    roll_number VARCHAR(50),
    academic_year VARCHAR(20),
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 5. Attendance Module

```sql
CREATE TABLE attendance (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    student_id UUID REFERENCES users(id),
    class_id UUID REFERENCES classes(id),
    date DATE,
    status VARCHAR(20) CHECK (status IN ('present', 'absent', 'late')),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_attendance_student_date ON attendance(student_id, date);
CREATE INDEX idx_attendance_tenant ON attendance(tenant_id);
```

---

## 6. Marks & Results

### 6.1 Exams

```sql
CREATE TABLE exams (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(100),
    subject_id UUID REFERENCES subjects(id),
    max_marks INT,
    exam_date DATE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 6.2 Marks

```sql
CREATE TABLE marks (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    student_id UUID REFERENCES users(id),
    exam_id UUID REFERENCES exams(id),
    marks_obtained INT,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_marks_student ON marks(student_id);
CREATE INDEX idx_marks_tenant_student ON marks(tenant_id, student_id);
```

---

## 7. Assignments

### 7.1 Assignment Table

```sql
CREATE TABLE assignments (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    subject_id UUID REFERENCES subjects(id),
    title VARCHAR(255),
    description TEXT,
    due_date TIMESTAMP,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 7.2 Assignment Submissions

```sql
CREATE TABLE assignment_submissions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    assignment_id UUID REFERENCES assignments(id),
    student_id UUID REFERENCES users(id),
    submission_url TEXT,
    submitted_at TIMESTAMP,
    grade INT,
    feedback TEXT
);
```

---

## 8. Timetable Module

```sql
CREATE TABLE timetable (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    class_id UUID REFERENCES classes(id),
    subject_id UUID REFERENCES subjects(id),
    teacher_id UUID REFERENCES users(id),
    day_of_week INT CHECK (day_of_week BETWEEN 0 AND 6),
    start_time TIME,
    end_time TIME
);
```

---

## 9. Complaint Portal

```sql
CREATE TABLE complaints (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    student_id UUID REFERENCES users(id),
    category VARCHAR(100),
    description TEXT,
    status VARCHAR(50) CHECK (status IN ('open', 'in_review', 'resolved')),
    resolved_by UUID REFERENCES users(id),
    resolution_note TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    resolved_at TIMESTAMP
);
```

---

## 10. Lecture Library

```sql
CREATE TABLE lectures (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    subject_id UUID REFERENCES subjects(id),
    title VARCHAR(255),
    youtube_url TEXT,
    transcript_ingested BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 11. AI-Related Metadata (ERP-Side)

AI vector storage lives separately (FAISS/Qdrant), but ERP tracks document metadata.

### 11.1 Documents

```sql
CREATE TABLE documents (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    subject_id UUID REFERENCES subjects(id),
    uploaded_by UUID REFERENCES users(id),
    file_name VARCHAR(255),
    file_type VARCHAR(50),
    storage_path TEXT,
    ingestion_status VARCHAR(50) CHECK (ingestion_status IN ('pending', 'processing', 'completed', 'failed')),
    chunk_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);
```

### 11.2 AI Query Logs

```sql
CREATE TABLE ai_queries (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    query_text TEXT,
    mode VARCHAR(50) CHECK (mode IN ('qa', 'study_guide', 'quiz', 'concept_map', 'weak_topic')),
    response_text TEXT,
    token_usage INT,
    response_time_ms INT,
    trace_id VARCHAR(64),              -- For AI query tracing/debugging
    citation_count INT DEFAULT 0,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_ai_queries_user ON ai_queries(user_id);
CREATE INDEX idx_ai_queries_tenant_date ON ai_queries(tenant_id, created_at);
```

Used for: Billing, rate limiting, analytics, AI quality review, and trace debugging.

---

## 12. Weak Topic Intelligence

Precomputed performance aggregation for AI personalization:

```sql
CREATE TABLE subject_performance (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    student_id UUID REFERENCES users(id),
    subject_id UUID REFERENCES subjects(id),
    average_score FLOAT,
    exam_count INT DEFAULT 0,
    last_updated TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_perf_student ON subject_performance(student_id);
```

AI reads this table to identify weak topics and generate targeted study material.

---

## 13. Audit Logs

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,       -- e.g. 'user.created', 'role.changed', 'ai.quota.reset'
    entity_type VARCHAR(100),           -- e.g. 'user', 'document', 'complaint'
    entity_id UUID,
    metadata JSONB,                     -- Additional context (old_value, new_value, etc.)
    ip_address VARCHAR(45),
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant_date ON audit_logs(tenant_id, created_at);
```

**Design decision:** `metadata` stored as JSONB for flexibility — different action types carry different context data.

---

## 14. Webhook Events (Phase 2)

```sql
CREATE TABLE webhook_subscriptions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    event_type VARCHAR(100) NOT NULL,   -- e.g. 'student.enrolled', 'exam.results.published'
    target_url TEXT NOT NULL,
    secret VARCHAR(255),                -- For signature verification
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY,
    subscription_id UUID REFERENCES webhook_subscriptions(id),
    event_type VARCHAR(100),
    payload JSONB,
    status VARCHAR(20) CHECK (status IN ('pending', 'delivered', 'failed')),
    attempts INT DEFAULT 0,
    last_attempt_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW()
);
```

---

## 15. Vector DB (Separate System)

Vector DB is NOT inside PostgreSQL. It stores:

| Field | Description |
|---|---|
| `namespace` | `tenant_{tenant_id}` — isolates each school |
| `document_id` | Reference to ERP `documents` table |
| `chunk_id` | Unique chunk identifier |
| `embedding_vector` | 768-dim float array |
| `metadata` | JSON: page_number, section_title, subject, class, teacher, academic_year |

---

## 16. Indexing Strategy

Critical indexes for performance at 10k+ students:

| Column(s) | Table | Purpose |
|---|---|---|
| `tenant_id` | All tables | Tenant isolation |
| `student_id` | marks, attendance | Student data queries |
| `student_id, date` | attendance | Date-range attendance |
| `user_id` | ai_queries | Usage tracking |
| `tenant_id, created_at` | ai_queries, audit_logs | Time-series analytics |
| `tenant_id, student_id` | marks | Composite for joins |

---

## 17. Scaling Considerations

When reaching 10k+ students:
- Enable PostgreSQL read replicas
- Partition tables by `tenant_id`
- Implement archival strategy for old academic years
- Consider Row-Level Security (RLS) at DB level
- Move to cursor-based pagination for large queries

---

## 18. Backup Strategy

| Action | Frequency |
|---|---|
| PostgreSQL dump | Daily (automated) |
| Offsite cloud storage | Daily (S3-compatible) |
| Restore test | Weekly |
| Versioned backups | Retained 30 days |
