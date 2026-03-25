# Database Schema

**Project:** VidyaOS – AI Infrastructure for Educational Institutions  
**Version:** v0.1 (Current Implementation)  
**Database:** PostgreSQL 15+  
**Architecture:** Multi-Tenant (Shared DB, Logical Isolation)  
**Status:** Updated to match the repository models on 2026-03-25

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
    domain VARCHAR(255) UNIQUE,
    plan_tier VARCHAR(50) DEFAULT 'basic',
    max_students INT DEFAULT 100,
    ai_daily_limit INT DEFAULT 50,
    is_active INT DEFAULT 1,

    -- SAML SSO configuration
    saml_enabled BOOLEAN NOT NULL DEFAULT FALSE,
    saml_entity_id VARCHAR(500),
    saml_metadata_url VARCHAR(1000),
    saml_metadata_xml TEXT,
    saml_idp_entity_id VARCHAR(500),
    saml_idp_sso_url VARCHAR(1000),
    saml_idp_slo_url VARCHAR(1000),
    saml_x509_cert TEXT,
    saml_attribute_email VARCHAR(255) NOT NULL DEFAULT 'email',
    saml_attribute_name VARCHAR(255) NOT NULL DEFAULT 'full_name',

    -- Compliance controls
    data_retention_days INT NOT NULL DEFAULT 365,
    export_retention_days INT NOT NULL DEFAULT 30,

    -- White-label branding
    logo_url TEXT,
    primary_color VARCHAR(7),
    secondary_color VARCHAR(7),
    accent_color VARCHAR(7),
    font_family VARCHAR(100),
    theme_style VARCHAR(50) DEFAULT 'modern',

    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    hashed_password VARCHAR(255),
    full_name VARCHAR(255),
    role VARCHAR(50) CHECK (role IN ('student', 'teacher', 'admin', 'parent')),
    is_active BOOLEAN DEFAULT TRUE,
    is_deleted BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_users_tenant ON users(tenant_id);
CREATE INDEX idx_users_email ON users(email);
```

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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 4.2 Subjects

```sql
CREATE TABLE subjects (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    name VARCHAR(100),
    class_id UUID REFERENCES classes(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
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
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 11.2 AI Query Logs

```sql
CREATE TABLE ai_queries (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    user_id UUID REFERENCES users(id) NOT NULL,
    query_text TEXT NOT NULL,
    mode VARCHAR(50) NOT NULL DEFAULT 'qa',
    response_text TEXT,
    token_usage INT,
    response_time_ms INT,
    trace_id VARCHAR(64),
    citation_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_ai_queries_user ON ai_queries(user_id);
CREATE INDEX idx_ai_queries_tenant_date ON ai_queries(tenant_id, created_at);
```

Supported `mode` values: `qa`, `study_guide`, `quiz`, `concept_map`, `weak_topic`, `flowchart`, `mind_map`, `flashcards`, `socratic`, `perturbation`, `debate`, `essay_review`, `career_simulation`.

Used for: billing, rate limiting, analytics, AI quality review, trace debugging, and doubt heatmap aggregation.

---

## 12. AI Job Queue (Persistent State)

### 12.1 AI Jobs

Mirrors Redis live queue state into relational storage for durability and admin operations.

```sql
CREATE TABLE ai_jobs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    user_id UUID REFERENCES users(id),
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    trace_id VARCHAR(255),
    priority INT,
    attempts INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 0,
    worker_id VARCHAR(255),
    error TEXT,
    request_payload JSONB,
    result_payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_ai_jobs_tenant ON ai_jobs(tenant_id);
CREATE INDEX idx_ai_jobs_status ON ai_jobs(status);
CREATE INDEX idx_ai_jobs_type ON ai_jobs(job_type);
CREATE INDEX idx_ai_jobs_trace ON ai_jobs(trace_id);
```

### 12.2 AI Job Events

Per-job event timeline for observability.

```sql
CREATE TABLE ai_job_events (
    id UUID PRIMARY KEY,
    ai_job_id UUID REFERENCES ai_jobs(id) NOT NULL,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    stage VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    detail TEXT,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_ai_job_events_job ON ai_job_events(ai_job_id);
CREATE INDEX idx_ai_job_events_stage ON ai_job_events(stage);
```

---

## 13. Weak Topic Intelligence

Precomputed performance aggregation for AI personalization:

```sql
CREATE TABLE subject_performance (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    student_id UUID REFERENCES users(id),
    subject_id UUID REFERENCES subjects(id),
    average_score FLOAT,
    exam_count INT DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_perf_student ON subject_performance(student_id);
```

AI reads this table to identify weak topics and generate targeted study material.

---

## 14. Spaced Repetition Reviews

SM-2 algorithm-backed review cards for student study scheduling.

```sql
CREATE TABLE review_schedules (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    student_id UUID REFERENCES users(id) NOT NULL,
    subject_id UUID,
    topic VARCHAR NOT NULL,
    next_review_at TIMESTAMP WITH TIME ZONE NOT NULL,
    interval_days INT DEFAULT 1,
    ease_factor FLOAT DEFAULT 2.5,
    review_count INT DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

---

## 15. Parent-Child Links

```sql
CREATE TABLE parent_links (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    parent_id UUID REFERENCES users(id) NOT NULL,
    child_id UUID REFERENCES users(id) NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE (tenant_id, parent_id, child_id)
);

CREATE INDEX idx_parent_links_parent ON parent_links(parent_id);
CREATE INDEX idx_parent_links_child ON parent_links(child_id);
```

---

## 16. Audit Logs

```sql
CREATE TABLE audit_logs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    action VARCHAR(255) NOT NULL,
    entity_type VARCHAR(100),
    entity_id UUID,
    metadata JSONB,
    ip_address VARCHAR(45),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_audit_tenant_date ON audit_logs(tenant_id, created_at);
CREATE INDEX idx_audit_tenant_action ON audit_logs(tenant_id, action);
```

---

### 16.2 Notifications

```sql
CREATE TABLE notifications (
    id UUID PRIMARY KEY,
    user_id UUID REFERENCES users(id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    body TEXT NOT NULL,
    category VARCHAR(50) NOT NULL DEFAULT 'info',
    data JSONB,
    read BOOLEAN NOT NULL DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_notifications_user ON notifications(user_id);
CREATE INDEX idx_notifications_user_read ON notifications(user_id, read);
CREATE INDEX idx_notifications_created ON notifications(created_at);
```

---

## 17. Webhook Subscriptions & Deliveries

```sql
CREATE TABLE webhook_subscriptions (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    target_url VARCHAR(500) NOT NULL,
    secret VARCHAR(128) NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_webhooks_tenant ON webhook_subscriptions(tenant_id);
CREATE INDEX idx_webhooks_event ON webhook_subscriptions(event_type);

CREATE TABLE webhook_deliveries (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    subscription_id UUID REFERENCES webhook_subscriptions(id) NOT NULL,
    event_type VARCHAR(100) NOT NULL,
    payload JSONB NOT NULL,
    status VARCHAR(50) NOT NULL DEFAULT 'pending',
    status_code INT,
    response_body TEXT,
    attempt_count INT NOT NULL DEFAULT 0,
    last_attempt_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_deliveries_subscription ON webhook_deliveries(subscription_id);
CREATE INDEX idx_deliveries_event ON webhook_deliveries(event_type);
```

Supported event types: `student.enrolled`, `document.ingested`, `ai.query.completed`, `exam.results.published`, `attendance.marked`, `complaint.status.changed`, `observability.alert.raised`.

---

## 18. Observability Persistence

### 18.1 Trace Event Records

Persistent trace events for admin trace viewer.

```sql
CREATE TABLE trace_event_records (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    trace_id VARCHAR(255) NOT NULL,
    user_id UUID REFERENCES users(id),
    source VARCHAR(100) NOT NULL,
    stage VARCHAR(100) NOT NULL,
    status VARCHAR(50),
    detail TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_traces_tenant ON trace_event_records(tenant_id);
CREATE INDEX idx_traces_trace_id ON trace_event_records(trace_id);
CREATE INDEX idx_traces_source ON trace_event_records(source);
CREATE INDEX idx_traces_stage ON trace_event_records(stage);
```

### 18.2 Observability Alert Records

```sql
CREATE TABLE observability_alert_records (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    alert_code VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'active',
    message TEXT NOT NULL,
    first_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_seen_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
    last_dispatched_at TIMESTAMP WITH TIME ZONE,
    delivery_count INT NOT NULL DEFAULT 0,
    occurrence_count INT NOT NULL DEFAULT 1,
    active BOOLEAN NOT NULL DEFAULT TRUE,
    trace_id VARCHAR(255),
    latest_payload JSONB,
    latest_metrics JSONB
);

CREATE INDEX idx_obs_alerts_tenant ON observability_alert_records(tenant_id);
CREATE INDEX idx_obs_alerts_active ON observability_alert_records(active);
CREATE INDEX idx_obs_alerts_code ON observability_alert_records(alert_code);
```

### 18.3 Observability Alert Events

```sql
CREATE TABLE observability_alert_events (
    id UUID PRIMARY KEY,
    alert_record_id UUID REFERENCES observability_alert_records(id) NOT NULL,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    event_type VARCHAR(50) NOT NULL,
    detail TEXT,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_obs_alert_events_record ON observability_alert_events(alert_record_id);
CREATE INDEX idx_obs_alert_events_type ON observability_alert_events(event_type);
```

---

## 19. Compliance & Deletion Tracking

### 19.1 Compliance Exports

```sql
CREATE TABLE compliance_exports (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    requested_by UUID REFERENCES users(id),
    export_type VARCHAR(50) NOT NULL DEFAULT 'tenant_bundle',
    scope_type VARCHAR(50) NOT NULL DEFAULT 'tenant',
    scope_user_id UUID REFERENCES users(id),
    format VARCHAR(20) NOT NULL DEFAULT 'zip',
    status VARCHAR(30) NOT NULL DEFAULT 'pending',
    file_path TEXT,
    file_size INT,
    checksum VARCHAR(128),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_exports_tenant ON compliance_exports(tenant_id);
```

### 19.2 Deletion Requests

```sql
CREATE TABLE deletion_requests (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    requested_by UUID REFERENCES users(id),
    target_user_id UUID REFERENCES users(id),
    status VARCHAR(30) NOT NULL DEFAULT 'requested',
    reason TEXT,
    resolution_note TEXT,
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    resolved_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_deletions_tenant ON deletion_requests(tenant_id);
```

---

## 20. Incident Management

### 20.1 Incident Routes

Configurable routing targets for incident dispatch.

```sql
CREATE TABLE incident_routes (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    name VARCHAR(255) NOT NULL,
    channel_type VARCHAR(50) NOT NULL,      -- 'webhook', 'slack_webhook', 'pagerduty', 'opsgenie'
    target VARCHAR(1000) NOT NULL,
    secret VARCHAR(255),
    severity_filter VARCHAR(50) NOT NULL DEFAULT 'all',
    escalation_channel_type VARCHAR(50),
    escalation_target VARCHAR(1000),
    escalation_after_minutes INT NOT NULL DEFAULT 30,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_incident_routes_tenant ON incident_routes(tenant_id);
```

### 20.2 Incidents

```sql
CREATE TABLE incidents (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    alert_code VARCHAR(100) NOT NULL,
    severity VARCHAR(30) NOT NULL,
    status VARCHAR(30) NOT NULL DEFAULT 'open',
    title VARCHAR(255) NOT NULL,
    summary TEXT NOT NULL,
    trace_id VARCHAR(255),
    source_payload JSONB,
    acknowledged_by UUID REFERENCES users(id),
    acknowledged_at TIMESTAMP WITH TIME ZONE,
    resolved_by UUID REFERENCES users(id),
    resolved_at TIMESTAMP WITH TIME ZONE,
    last_notified_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_incidents_tenant ON incidents(tenant_id);
CREATE INDEX idx_incidents_alert_code ON incidents(alert_code);
CREATE INDEX idx_incidents_trace ON incidents(trace_id);
```

### 20.3 Incident Events

```sql
CREATE TABLE incident_events (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id) NOT NULL,
    incident_id UUID REFERENCES incidents(id) NOT NULL,
    actor_user_id UUID REFERENCES users(id),
    event_type VARCHAR(50) NOT NULL,
    detail TEXT,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_incident_events_incident ON incident_events(incident_id);
```

---

## 21. Vector DB (Separate System)

Vector DB is NOT inside PostgreSQL. It stores:

| Field | Description |
|---|---|
| `namespace` | `tenant_{tenant_id}` — isolates each school |
| `document_id` | Reference to ERP `documents` table |
| `chunk_id` | Unique chunk identifier |
| `embedding_vector` | 768-dim float array |
| `metadata` | JSON: page_number, section_title, subject, class, teacher, academic_year |

---

## 21.1 Additional Implemented Tables (Current Codebase)

These tables are implemented in `backend/models/` but are not fully expanded above:

- `admission_applications` — admission workflow pipeline
- `fee_structures`, `fee_invoices`, `fee_payments` — fee management
- `billing_plans`, `tenant_subscriptions`, `payment_records` — Razorpay billing
- `library_books`, `library_lendings` — library catalog and lending
- `login_streaks` — student streak tracking
- `test_series`, `mock_test_attempts` — leaderboard/test series
- `kg_concepts`, `kg_relationships` — knowledge graph index
- `blacklisted_tokens` — refresh token blacklist (enforced during refresh/logout)
- `feature_flags` — runtime feature toggles with `module` and `ai_intensity` classification

### Feature Flags Table

```sql
CREATE TABLE feature_flags (
    id VARCHAR(100) PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    description TEXT,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    module VARCHAR(100),           -- ERP module grouping (e.g. 'Student Management', 'Finance')
    ai_intensity VARCHAR(50),      -- AI usage level ('heavy_ai', 'medium_ai', 'low_ai', 'no_ai')
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

Used by the `require_feature()` FastAPI dependency to gate route access at runtime.

If you need full SQL for these, generate it from the SQLAlchemy models.

---

## 22. Indexing Strategy

Critical indexes for performance at 10k+ students:

| Column(s) | Table | Purpose |
|---|---|---|
| `tenant_id` | All tables | Tenant isolation |
| `student_id` | marks, attendance | Student data queries |
| `student_id, date` | attendance | Date-range attendance |
| `user_id` | ai_queries | Usage tracking |
| `tenant_id, created_at` | ai_queries, audit_logs | Time-series analytics |
| `tenant_id, student_id` | marks | Composite for joins |
| `status` | ai_jobs | Queue filtering |
| `trace_id` | ai_jobs, trace_event_records, incidents | Cross-service trace lookup |
| `alert_code` | observability_alert_records, incidents | Alert aggregation |

---

## 23. Scaling Considerations

When reaching 10k+ students:
- Enable PostgreSQL read replicas
- Partition tables by `tenant_id`
- Implement archival strategy for old academic years
- Consider Row-Level Security (RLS) at DB level
- Move to cursor-based pagination for large queries

---

## 24. Backup Strategy

| Action | Frequency |
|---|---|
| PostgreSQL dump | Daily (automated) |
| Offsite cloud storage | Daily (S3-compatible) |
| Restore test | Weekly |
| Versioned backups | Retained 30 days |

---

## 25. Persistent Queues & Jobs

### 25.1 AI Jobs

```sql
CREATE TABLE ai_jobs (
    id UUID PRIMARY KEY,
    tenant_id UUID REFERENCES tenants(id),
    user_id UUID REFERENCES users(id),
    job_type VARCHAR(100) NOT NULL,
    status VARCHAR(30) NOT NULL,
    trace_id VARCHAR(255),
    priority INT,
    attempts INT DEFAULT 0,
    max_retries INT DEFAULT 0,
    worker_id VARCHAR(255),
    error TEXT,
    request_payload JSONB,
    result_payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);
```

### 25.2 AI Job Events

```sql
CREATE TABLE ai_job_events (
    id UUID PRIMARY KEY,
    ai_job_id UUID REFERENCES ai_jobs(id),
    tenant_id UUID REFERENCES tenants(id),
    stage VARCHAR(100) NOT NULL,
    source VARCHAR(100) NOT NULL,
    detail TEXT,
    event_timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    payload JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```
