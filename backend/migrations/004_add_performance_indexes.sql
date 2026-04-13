-- Migration: Add performance indexes for analytics and reporting queries
-- Date: 2026-04-12
-- Fixes: P2 performance issues - missing indexes on attendance, ai_queries, ai_session_events

-- ─────────────────────────────────────────────────────────────────────────────
-- ATTENDANCE TABLE INDEXES (Query optimization for attendance reports)
-- ─────────────────────────────────────────────────────────────────────────────

-- Composite index: Tenant + Student + Date (for user attendance history)
CREATE INDEX IF NOT EXISTS ix_attendance_tenant_student_date 
ON attendance(tenant_id, student_id, date DESC)
WHERE deleted_at IS NULL;

-- Composite index: Tenant + Class + Date (for class attendance reports)
CREATE INDEX IF NOT EXISTS ix_attendance_tenant_class_date 
ON attendance(tenant_id, class_id, date DESC);

-- Index: Student + Date (for cross-tenant lookups if needed)
CREATE INDEX IF NOT EXISTS ix_attendance_student_date 
ON attendance(student_id, date DESC);

-- Index: Status lookup for absent students reports
CREATE INDEX IF NOT EXISTS ix_attendance_status 
ON attendance(tenant_id, status, date DESC)
WHERE status = 'absent';

-- ─────────────────────────────────────────────────────────────────────────────
-- AI_QUERIES TABLE INDEXES (Query optimization for analytics)
-- ─────────────────────────────────────────────────────────────────────────────

-- Composite index: Tenant + Created timestamp (for tenant usage analytics)
CREATE INDEX IF NOT EXISTS ix_ai_query_tenant_created 
ON ai_queries(tenant_id, created_at DESC)
WHERE deleted_at IS NULL;

-- Composite index: User + Created timestamp (for user query history)
CREATE INDEX IF NOT EXISTS ix_ai_query_user_created 
ON ai_queries(user_id, created_at DESC)
WHERE deleted_at IS NULL;

-- Composite index: Tenant + Mode (for query distribution analysis)
CREATE INDEX IF NOT EXISTS ix_ai_query_tenant_mode 
ON ai_queries(tenant_id, mode, created_at DESC);

-- Index: Notebook-level query tracking
CREATE INDEX IF NOT EXISTS ix_ai_query_notebook_created 
ON ai_queries(notebook_id, created_at DESC)
WHERE notebook_id IS NOT NULL AND deleted_at IS NULL;

-- ─────────────────────────────────────────────────────────────────────────────
-- AI_SESSION_EVENTS TABLE INDEXES (Learning path analytics)
-- ─────────────────────────────────────────────────────────────────────────────

-- Composite index: Tenant + User + Subject (for learning path dashboards)
CREATE INDEX IF NOT EXISTS ix_ai_session_tenant_user_subject 
ON ai_session_events(tenant_id, user_id, subject, created_at DESC)
WHERE subject IS NOT NULL;

-- Composite index: User + Created timestamp (for user session history)
CREATE INDEX IF NOT EXISTS ix_ai_session_user_created 
ON ai_session_events(user_id, created_at DESC);

-- Composite index: Tenant + Created timestamp (for global session pagination)
CREATE INDEX IF NOT EXISTS ix_ai_session_tenant_created 
ON ai_session_events(tenant_id, created_at DESC);

-- Index: Session tracking by ID (for browser session recovery)
CREATE INDEX IF NOT EXISTS ix_ai_session_id 
ON ai_session_events(session_id, tenant_id, created_at DESC);

-- Index: Tool mode distribution (for feature usage analytics)
CREATE INDEX IF NOT EXISTS ix_ai_session_mode 
ON ai_session_events(tenant_id, tool_mode, created_at DESC);

-- ─────────────────────────────────────────────────────────────────────────────
-- ANALYZE TABLES (Update planner statistics)
-- ─────────────────────────────────────────────────────────────────────────────

ANALYZE attendance;
ANALYZE ai_queries;
ANALYZE ai_session_events;

-- ─────────────────────────────────────────────────────────────────────────────
-- ROLLBACK INSTRUCTIONS
-- ─────────────────────────────────────────────────────────────────────────────

/*
DROP INDEX IF EXISTS ix_attendance_tenant_student_date;
DROP INDEX IF EXISTS ix_attendance_tenant_class_date;
DROP INDEX IF EXISTS ix_attendance_student_date;
DROP INDEX IF EXISTS ix_attendance_status;
DROP INDEX IF EXISTS ix_ai_query_tenant_created;
DROP INDEX IF EXISTS ix_ai_query_user_created;
DROP INDEX IF EXISTS ix_ai_query_tenant_mode;
DROP INDEX IF EXISTS ix_ai_query_notebook_created;
DROP INDEX IF EXISTS ix_ai_session_tenant_user_subject;
DROP INDEX IF EXISTS ix_ai_session_user_created;
DROP INDEX IF EXISTS ix_ai_session_tenant_created;
DROP INDEX IF EXISTS ix_ai_session_id;
DROP INDEX IF EXISTS ix_ai_session_mode;
*/
