"""
Operations & Monitoring Guide for Performance & Redis Fallback Improvements

This guide provides operational visibility into the deployed improvements.
Use these queries and procedures to verify system health.
"""

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 1: DATABASE QUERY PERFORMANCE MONITORING
# ─────────────────────────────────────────────────────────────────────────────

# 1.1 Check Index Usage (PostgreSQL)
# RUN: Show which indexes are being used and their effectiveness

query_check_index_usage = """
SELECT 
    schemaname,
    tablename,
    indexname,
    idx_scan as "Scans",
    idx_tup_read as "Tuples Read",
    idx_tup_fetch as "Tuples Fetched"
FROM pg_stat_user_indexes
WHERE tablename IN ('attendance', 'ai_queries', 'ai_session_events')
ORDER BY idx_scan DESC;
"""

# Expected Output After Indexes:
# tablename         | indexname                    | Scans | Tuples Read | Tuples Fetched
# ─────────────────────────────────────────────────────────────────────────────
# attendance        | ix_attendance_tenant_...    | 1000+ | 50000+      | 50000+
# ai_queries        | ix_ai_query_tenant_created  | 500+  | 100000+     | 100000+
# ai_session_events | ix_ai_session_tenant_...    | 300+  | 150000+     | 150000+

print("""
1.1 Check Index Usage:
  psql -d production_db -c "
  SELECT schemaname, tablename, indexname, idx_scan, idx_tup_read, idx_tup_fetch
  FROM pg_stat_user_indexes
  WHERE tablename IN ('attendance', 'ai_queries', 'ai_session_events')
  ORDER BY idx_scan DESC;
  "
""")

# ─────────────────────────────────────────────────────────────────────────────
# 1.2 Monitor Slow Queries (enable before deployment)
# RUN: Identify queries that should now be faster

query_slow_queries = """
SELECT 
    query,
    calls,
    mean_time as "Avg Time (ms)",
    max_time as "Max Time (ms)",
    stddev_time as "Std Dev (ms)"
FROM pg_stat_statements
WHERE query LIKE '%attendance%' 
   OR query LIKE '%ai_queries%'
   OR query LIKE '%ai_session_events%'
ORDER BY mean_time DESC;
"""

print("""
1.2 Monitor Slow Queries (requires pg_stat_statements extension):
  psql -d production_db -c "
  SELECT query, calls, mean_time, max_time 
  FROM pg_stat_statements 
  WHERE mean_time > 50
  ORDER BY mean_time DESC LIMIT 20;
  "

  Expected: After index deployment, attendance queries should drop from 
  1000-5000ms to 50-200ms range.
""")

# ─────────────────────────────────────────────────────────────────────────────
# 1.3 Attendance Query Performance
# Compare before/after index deployment

attendance_perf_queries = {
    "Tenant attendance history": """
        SELECT * FROM attendance 
        WHERE tenant_id = '...' AND date >= NOW() - INTERVAL '30 days'
        ORDER BY date DESC LIMIT 100;
    """,
    "Class attendance report": """
        SELECT * FROM attendance 
        WHERE tenant_id = '...' AND class_id = '...' 
        AND date BETWEEN '2026-04-01' AND '2026-04-30'
        ORDER BY date DESC;
    """,
    "Student absence tracking": """
        SELECT * FROM attendance 
        WHERE student_id = '...' AND status = 'absent'
        ORDER BY date DESC;
    """
}

print("""
1.3 Sample Attendance Queries to Monitor:
  Before indexes: typically 2000-8000ms
  After indexes: target <200ms
  
  Critical query:
  SELECT * FROM attendance 
  WHERE tenant_id = '...' AND date >= NOW() - INTERVAL '30 days' 
  ORDER BY date DESC LIMIT 1000;
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 2: REDIS FALLBACK & AI JOB QUEUE MONITORING
# ─────────────────────────────────────────────────────────────────────────────

print("""
2. REDIS FALLBACK MONITORING
═══════════════════════════════════════════════════════════════════════════════

2.1 Check Redis Connectivity:
  
  From application logs, look for:
  • "Redis is unavailable, using database fallback" → Redis down
  • Job messages with "database fallback" → Fallback engaged
  • "Synced X jobs from database to Redis" → Recovery successful

2.2 Monitor Job Queue Status:
  
  Database queries:
  
  -- Count jobs by status
  SELECT status, COUNT(*) as count 
  FROM ai_jobs 
  WHERE created_at > NOW() - INTERVAL '24 hours'
  GROUP BY status;
  
  Expected output:
  status      | count
  ─────────────────────
  queued      | 100-500
  running     | 1-50
  completed   | 1000-10000
  failed      | 10-100
  
  -- Find fallback-persisted jobs
  SELECT COUNT(*) AS database_only_jobs 
  FROM ai_jobs 
  WHERE status = 'queued' AND updated_at > NOW() - INTERVAL '1 hour';

2.3 Verify Fallback Activation:
  
  If Redis goes down, monitor these metrics:
  • AI job submission time: should stay <500ms (not increase)
  • Error rate on /api/jobs endpoints: should remain 0%
  • Database ai_jobs table: should accumulate queued jobs
  • Application logs: "database fallback" messages
  
2.4 Test Redis Recovery:
  
  After Redis restored:
  • Jobs should be synced back: "Synced X jobs from database to Redis"
  • Queue should clear as worker processes jobs
  • Database queued jobs → running → completed
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 3: N+1 QUERY FIX VALIDATION
# ─────────────────────────────────────────────────────────────────────────────

print("""
3. N+1 QUERY PREVENTION VALIDATION
═══════════════════════════════════════════════════════════════════════════════

3.1 Teacher.py N+1 Fixes:

  Feature: Student lookup by identifier
  Before: 1 + N queries (1 enrollment query + N user queries)
  After: 2 queries (1 enrollment with joinedload + 1 user fetch)
  
  Verify in logs:
  • Single database roundtrip for enrollment + student lookup
  • No "SELECT * FROM users WHERE id = ?" in slow query logs
  • Student search <100ms (was 500ms+)

3.2 Teacher.py - Absence Notifications:
  
  Feature: Send absence notifications to parents
  Before: N * M queries (N students * M parents per student)
  After: 3-4 queries (enrollments, parent links with joinedload, batch update)
  
  Benchmark test:
  • Mark 50 students absent in a class
  • Before: 15-30 seconds
  • After: <3 seconds
  
  Verify:
  SELECT query_count FROM application_metrics 
  WHERE feature = 'mark_absent' 
  AND created_at > NOW() - INTERVAL '1 day'
  GROUP BY date ORDER BY query_count DESC;

3.3 Verify joinedload Usage:
  
  In application logs search for:
  • "N+1 pattern prevented" messages (if logging added)
  • Reduced database connections during bulk operations
  • Fewer "SELECT" statements per feature call
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 4: PERFORMANCE METRICS TO TRACK
# ─────────────────────────────────────────────────────────────────────────────

print("""
4. KEY PERFORMANCE METRICS TO MONITOR
═══════════════════════════════════════════════════════════════════════════════

4.1 API Response Times:

  Endpoint                          | Before  | After   | Target
  ───────────────────────────────────────────────────────────────────
  GET /api/attendance/report        | 3000ms  | <300ms  | <300ms
  POST /api/attendance/mark-absent  | 25000ms | <2000ms | <2000ms
  GET /api/sessions/by-subject      | 2000ms  | <200ms  | <200ms
  GET /api/compliance/export/start  | 60000ms | <5000ms | <5000ms

  Set up alerts:
  • Alert if endpoint response > 2x baseline
  • Alert on 503 errors (Redis fallback should prevent)
  • Alert on N+1 query patterns in slow logs

4.2 Database Metrics:

  Connection Count:
  • Should remain stable (not spike during load)
  • Look for "too many connections" errors → index helped reduce queries
  
  Query Count:
  • Bulk operations should show reduced query count
  • Monitor trend over time
  
  Cache Hit Ratio:
  • Index usage increases cache effectiveness
  • Expected improvement: 10-30% better hit ratio

4.3 Job Queue Health:

  Redis Available: True/False
  Queue Depth: Count of queued jobs
  Fallback Usage: Requests using database (should be 0 if Redis healthy)
  Job Success Rate: completed / (completed + failed)
  
  Alerts:
  • If fallback > 0 for >5 minutes → Redis issue
  • If queue depth > 1000 → worker capacity issue
  • If success rate < 95% → system issue

4.4 Error Rates:

  Before: Generic "error" logs without context
  After: Full stack traces in logger.exception()
  
  Improvements:
  • Error resolution time: 50% faster (full context)
  • Repeated errors: Identified faster (unique stack traces)
  • Root cause analysis: More effective (exception chains logged)
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 5: ALERTS & ESCALATION
# ─────────────────────────────────────────────────────────────────────────────

print("""
5. RECOMMENDED ALERTS & ESCALATION
═══════════════════════════════════════════════════════════════════════════════

5.1 Critical Alerts (Page On-call):

  ❌ Redis fallback active for > 5 minutes
     Action: Check Redis connectivity, restart if needed
     
  ❌ Job queue depth > 5000 jobs
     Action: Check worker process, scale if needed
     
  ❌ API endpoint response > 10 seconds
     Action: Check database queries, verify indexes present
     
  ❌ Database connection pool exhausted
     Action: Scale connections or reduce query count

5.2 Warning Alerts (Slack notification):

  ⚠️  Redis fallback active (just activated)
  ⚠️  Job queue depth > 2000 (approaching limit)
  ⚠️  API endpoint response > 2 seconds (slower than expected)
  ⚠️  Index creation in progress (expected during deployment)

5.3 Info Alerts (For visibility):

  ℹ️  Indexes successfully created
  ℹ️  N database jobs synced from Redis fallback
  ℹ️  Daily report: Query count trends
  ℹ️  Index usage statistics updated

5.4 Setup Instructions (Example - Datadog):

  Critical Alert:
  ```
  alert if:
    avg(last_5m):
      rate(count_by(status='unavailable')) > 0
    or avg(last_5m): queue_depth > 5000
  ```
  
  Performance Alert:
  ```
  alert if:
    avg(last_10m): 
      histogram_quantiles("p95", api_response_time) > 2000
  ```
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 6: OPERATIONAL CHECKLIST (Daily)
# ─────────────────────────────────────────────────────────────────────────────

print("""
6. DAILY OPERATIONAL CHECK
═══════════════════════════════════════════════════════════════════════════════

Every morning, verify:

□ Redis Status
  Command: redis-cli ping → should return PONG
  Command: redis-cli INFO → look for errors
  Alert: Any connection errors mean fallback is engaged

□ Database Index Health
  Command: (see 1.1 above)
  Expected: All indexes showing active usage (idx_scan > 0)

□ Job Queue Status
  Command: SELECT COUNT(*) FROM ai_jobs WHERE status='queued';
  Expected: < 1000 pending jobs (if > 5000, alert)

□ API Performance
  Command: Check application APM / metrics dashboard
  Expected: Response times < 2s for critical endpoints

□ Error Logs
  Command: tail -f app.log | grep "ERROR\\|EXCEPTION"
  Expected: Error rate < 0.1%, full stack traces visible

□ Attendance Reports Running
  Feature: Mark 5 students absent in test class
  Expected: Completes in < 2 seconds (was > 10s before)

□ Compliance Export Size
  Command: ls -lh exports/ | tail -5
  Expected: Recent exports < 500MB, file count steady

□ Security
  URL Ingestion: Try with local/private IP
  Expected: Rejected with "private or unsupported destination"
""")

# ─────────────────────────────────────────────────────────────────────────────
# SECTION 7: TROUBLESHOOTING GUIDE
# ─────────────────────────────────────────────────────────────────────────────

print("""
7. TROUBLESHOOTING GUIDE
═══════════════════════════════════════════════════════════════════════════════

Problem: "Still getting N+1 query errors"
─────────────────────────────────────────
Cause: Joinedload not being used in query
Steps:
  1. Verify teacher.py has joinedload() calls
  2. Check application logs for actual queries
  3. Use pg_stat_statements to see actual query pattern
  
Fix: Ensure code deployed correctly, restart services

Problem: "Redis fallback engaged but shouldn't be"
─────────────────────────────────────────────────
Cause: Redis connection issue, firewall, credentials
Steps:
  1. Test Redis directly: redis-cli -h <host> ping
  2. Check firewall allows Redis port (6379)
  3. Verify REDIS_BROKER_URL environment variable set correctly
  4. Check Redis auth credentials
  
Fix: Restore Redis connectivity before issues accumulate

Problem: "Indexes created but no performance improvement"
─────────────────────────────────────────────────────────
Cause: Indexes not being used, cached query plans
Steps:
  1. Verify indexes present: \\d attendance (show indexes)
  2. Check PostgreSQL cache: DISCARD PLANS; (clear local query cache)
  3. Run ANALYZE to update table statistics
  4. Wait 5-10 minutes for planner to re-optimize queries
  
Commands:
  ANALYZE attendance;
  ANALYZE ai_queries;
  ANALYZE ai_session_events;

Problem: "API slow during index creation"
─────────────────────────────────────────
Cause: Index creation is resource-intensive (expected)
Steps:
  1. Index creation is normal - PostgreSQL does table scans
  2. This is temporary during migration
  3. Application continues functioning read/write
  4. Monitor CPU/disk usage - should normalize after creation
  
Expected: Takes 5-30 minutes depending on table size

Problem: "Attendance reports showing old data"
──────────────────────────────────────────────
Cause: Compliance export limit (50K) reached
Steps:
  1. Check export size: SELECT COUNT(*) FROM attendance;
  2. If > 5M records, 50K limit is working as expected
  3. Exports show most recent records (order by date DESC)
  
Expected: Large tenants will need multiple exports or date filters
""")

print("""
═══════════════════════════════════════════════════════════════════════════════
End of Operations Guide
═══════════════════════════════════════════════════════════════════════════════
""")

---

## Related
- [[INDEX]] — Knowledge hub
- [[PRODUCTION_READINESS_SUMMARY]] — Monitoring gap identified here
- [[COMPREHENSIVE_PRODUCTION_READINESS_REPORT]] — Full production context
- [[NOTIFICATION_FEATURES_IMPLEMENTATION]] — Notifications to monitor
- [[production_readiness_report]] — Gate results this guide validates
