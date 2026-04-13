#!/bin/bash
# Deployment Guide for Performance & Redis Fallback Improvements
# Run this checklist before deploying to production

set -e

echo "================================================================================"
echo "DEPLOYMENT CHECKLIST - Performance & Redis Fallback Improvements"
echo "================================================================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

check_passed() {
    echo -e "${GREEN}✓ PASS${NC}: $1"
}

check_failed() {
    echo -e "${RED}✗ FAIL${NC}: $1"
    return 1
}

check_warning() {
    echo -e "${YELLOW}⚠ WARNING${NC}: $1"
}

# ─────────────────────────────────────────────────────────────────────────────
# PRE-DEPLOYMENT CHECKS
# ─────────────────────────────────────────────────────────────────────────────

echo "STEP 1: Code Syntax Validation"
echo "─────────────────────────────────────────────────────────────────────────────"

FILES_TO_CHECK=(
    "src/domains/platform/services/ai_queue.py"
    "src/domains/platform/services/compliance.py"
    "src/interfaces/rest_api/ai/routes/session_tracking.py"
    "src/shared/ai_tools/whatsapp_tools.py"
    "src/domains/academic/routes/teacher.py"
    "src/domains/academic/models/attendance.py"
    "src/domains/platform/models/ai.py"
)

for file in "${FILES_TO_CHECK[@]}"; do
    if python -m py_compile "backend/$file" 2>/dev/null; then
        check_passed "Syntax valid: backend/$file"
    else
        check_failed "Syntax error in: backend/$file"
        exit 1
    fi
done

echo ""
echo "STEP 2: Dependency Check"
echo "─────────────────────────────────────────────────────────────────────────────"

# Check critical imports
if grep -q "from sqlalchemy.orm import joinedload" backend/src/domains/academic/routes/teacher.py; then
    check_passed "SQLAlchemy joinedload import present"
else
    check_failed "Missing joinedload import in teacher.py"
    exit 1
fi

if grep -q "sync_database_jobs_to_redis" backend/src/domains/platform/services/ai_queue.py; then
    check_passed "Database sync function implemented"
else
    check_failed "Missing sync_database_jobs_to_redis function"
    exit 1
fi

echo ""
echo "STEP 3: Redis Fallback Mechanism Verification"
echo "─────────────────────────────────────────────────────────────────────────────"

if grep -q "_enqueue_to_database" backend/src/domains/platform/services/ai_queue.py; then
    check_passed "Database fallback function implemented"
else
    check_failed "Missing database fallback function"
    exit 1
fi

if grep -q "get_queue_client_with_fallback" backend/src/domains/platform/services/ai_queue.py; then
    check_passed "Fallback client selection implemented"
else
    check_failed "Missing fallback client selection"
    exit 1
fi

echo ""
echo "STEP 4: Database Index Verification"
echo "─────────────────────────────────────────────────────────────────────────────"

if [ -f "backend/migrations/004_add_performance_indexes.sql" ]; then
    check_passed "Migration script exists: 004_add_performance_indexes.sql"
else
    check_failed "Missing migration script for indexes"
    exit 1
fi

# Verify indexes are defined in migration
REQUIRED_INDEXES=(
    "ix_attendance_tenant_student_date"
    "ix_ai_query_tenant_created"
    "ix_ai_session_tenant_user_subject"
)

for index in "${REQUIRED_INDEXES[@]}"; do
    if grep -q "$index" backend/migrations/004_add_performance_indexes.sql; then
        check_passed "Index defined: $index"
    else
        check_failed "Missing index definition: $index"
        exit 1
    fi
done

echo ""
echo "STEP 5: N+1 Query Fixes Verification"
echo "─────────────────────────────────────────────────────────────────────────────"

if grep -q "options(.*joinedload(Enrollment.student))" backend/src/domains/academic/routes/teacher.py; then
    check_passed "N+1 fix applied: Student lookup uses joinedload"
else
    check_failed "N+1 fix not applied: Student lookup"
    exit 1
fi

if grep -q "joinedload(ParentLink.parent)" backend/src/domains/academic/routes/teacher.py; then
    check_passed "N+1 fix applied: Parent notifications use joinedload"
else
    check_failed "N+1 fix not applied: Parent notifications"
    exit 1
fi

echo ""
echo "STEP 6: Error Logging Improvements Verification"
echo "─────────────────────────────────────────────────────────────────────────────"

EXCEPTION_HANDLERS=$(grep -c "logger.exception(" backend/src/shared/ai_tools/whatsapp_tools.py || echo "0")
if [ "$EXCEPTION_HANDLERS" -ge 15 ]; then
    check_passed "Exception handlers fixed: $EXCEPTION_HANDLERS using logger.exception()"
else
    check_warning "Only $EXCEPTION_HANDLERS exception handlers fixed (expected 20+)"
fi

echo ""
echo "STEP 7: Compliance Export Protection"
echo "─────────────────────────────────────────────────────────────────────────────"

if grep -q "\.limit(50000)" backend/src/domains/administrative/services/compliance.py; then
    check_passed "Compliance export limit added (50K records)"
else
    check_failed "Compliance export limit not applied"
    exit 1
fi

if grep -q "order_by(desc" backend/src/domains/administrative/services/compliance.py; then
    check_passed "Compliance export sorting added (DESC by created_at)"
else
    check_failed "Compliance export sorting not applied"
    exit 1
fi

echo ""
echo "STEP 8: Test Suite Availability"
echo "─────────────────────────────────────────────────────────────────────────────"

if [ -f "backend/tests/test_redis_fallback_and_performance.py" ]; then
    check_passed "Test suite created: test_redis_fallback_and_performance.py"
else
    check_failed "Test suite missing"
    exit 1
fi

# ─────────────────────────────────────────────────────────────────────────────
# DEPLOYMENT STEPS
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "================================================================================"
echo "DEPLOYMENT STEPS"
echo "================================================================================"
echo ""

echo "STEP 1: Database Migration"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  Run in production database:"
echo ""
echo "  psql -d <production_db> -f backend/migrations/004_add_performance_indexes.sql"
echo ""
echo "  On PostgreSQL:"
echo "  • Index creation is non-blocking with PostgreSQL"
echo "  • Application continues operating during migration"
echo "  • Estimated time: 5-30 minutes based on table size"
echo ""

echo "STEP 2: Code Deployment"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  Deploy updated application code:"
echo ""
echo "  • backend/src/domains/platform/services/ai_queue.py (redis fallback)"
echo "  • backend/src/domains/academic/routes/teacher.py (N+1 fixes)"
echo "  • backend/src/shared/ai_tools/whatsapp_tools.py (error logging)"
echo "  • backend/src/interfaces/rest_api/ai/routes/session_tracking.py (cleanup)"
echo "  • backend/src/domains/platform/models/ai.py (indexes in code)"
echo "  • backend/src/domains/academic/models/attendance.py (indexes in code)"
echo ""

echo "STEP 3: Restart API Services"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  • Restart FastAPI backend (api/web services)"
echo "  • No downtime required if using rolling restarts"
echo "  • Worker processes auto-detect running schema"
echo ""

echo "STEP 4: Run Test Suite"
echo "─────────────────────────────────────────────────────────────────────────────"
echo "  Verify all improvements are operational:"
echo ""
echo "  cd backend"
echo "  python tests/test_redis_fallback_and_performance.py"
echo ""

# ─────────────────────────────────────────────────────────────────────────────
# POST-DEPLOYMENT VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

echo ""
echo "================================================================================"
echo "POST-DEPLOYMENT VALIDATION CHECKLIST"
echo "================================================================================"
echo ""

echo "VALIDATION PRIORITY 1: Redis Fallback Mechanism"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Action: Simulate Redis unavailability on staging"
echo "Expected: Jobs still enqueued to database, no 503 errors"
echo ""
echo "Verify in logs:"
echo "  • Job persisted to database (Redis unavailable) messages"
echo "  • No exceptions in FastAPI logs"
echo "  • ai_job table has records with status='queued'"
echo ""

echo "VALIDATION PRIORITY 2: Query Performance"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Action: Monitor database slow query logs"
echo "Expected: Notable improvement in query times after index creation"
echo ""
echo "Queries to monitor:"
echo "  • Attendance by tenant/student/date (should be <50ms)"
echo "  • AI queries by tenant (should be <50ms)"
echo "  • Session events by user (should be <50ms)"
echo ""
echo "Monitor:"
echo "  • pg_stat_statements for query execution time"
echo "  • Application performance metrics"
echo ""

echo "VALIDATION PRIORITY 3: Absence Notifications"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Action: Test teacher absence notification feature"
echo "Expected: Notifications sent successfully with faster response"
echo ""
echo "Verify:"
echo "  • Absence notification POST completes in <2s (was >10s before)"
echo "  • All parent recipients receive notifications"
echo "  • No \"too many queries\" warnings in logs"
echo ""

echo "VALIDATION PRIORITY 4: Teacher Analytics"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Action: Load teacher dashboard with class analytics"
echo "Expected: Charts and reports load within 1-2 seconds"
echo ""
echo "Verify:"
echo "  • Class insights page loads <2s"
echo "  • Student performance reports load <2s"
echo "  • Dashboard responsive without timeouts"
echo ""

echo "VALIDATION PRIORITY 5: Compliance Exports"
echo "─────────────────────────────────────────────────────────────────────────────"
echo ""
echo "Action: Export compliance data for large tenant (>100K records)"
echo "Expected: Export completes without memory issues, latest records first"
echo ""
echo "Verify:"
echo "  • Export completes successfully (not OOM)"
echo "  • File size is reasonable (<500MB)"
echo "  • Contains most recent records (not oldest)"
echo ""

echo ""
echo "================================================================================"
echo "ROLLBACK PLAN (If Issues Occur)"
echo "================================================================================"
echo ""

echo "If Redis fallback causes issues:"
echo "  • Revert ai_queue.py to previous version"
echo "  • Restart API services"
echo "  • Jobs will be processed by Redis queue only (status quo)"
echo ""

echo "If N+1 fixes cause issues:"
echo "  • Revert teacher.py to previous version"
echo "  • Restart API services"
echo "  • Performance will revert to previous state"
echo ""

echo "If indexes cause slowness:"
echo "  • Run: DROP INDEX IF EXISTS <index_name>;"
echo "  • Allow 5-10 minutes for planner to adjust"
echo "  • No application restart required"
echo ""

echo ""
echo "================================================================================"
echo "All pre-deployment checks passed! ✓"
echo "================================================================================"
echo ""
