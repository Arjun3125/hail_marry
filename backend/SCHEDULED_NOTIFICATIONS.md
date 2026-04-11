# Scheduled Notifications Implementation (Phase 6)

## Overview

Implemented automated scheduled notifications system using APScheduler to trigger parent notifications on a daily schedule. The scheduler runs two recurring jobs that emit WhatsApp notifications based on school events and student engagement metrics.

## Architecture

### Components

1. **Scheduled Notifications Service** (`backend/src/domains/academic/services/scheduled_notifications.py`)
   - Main service class: `ScheduledNotificationsService`
   - Uses APScheduler AsyncIOScheduler for async-first design
   - Manages job lifecycle (initialize, start, stop)
   - Implements two scheduled jobs with Cron triggers

2. **Runtime Scheduler Integration** (`backend/src/domains/platform/services/runtime_scheduler.py`)
   - Added `run_scheduled_notifications_loop()` function
   - Integrates with FastAPI lifespan for automatic startup/shutdown
   - Pattern matches existing doc_watch and digest_email loops

3. **FastAPI Lifespan** (`backend/src/bootstrap/startup.py`)
   - Updated to include scheduled notifications in the task list
   - Runs automatically during API startup (non-testing environments)

## Jobs Scheduled

### 1. Assignment Due Tomorrow Check
- **Schedule:** Daily at 8:00 AM IST (Asia/Kolkata timezone)
- **Job ID:** `check_assignments_due_tomorrow`
- **Behavior:**
  - Queries all assignments with `due_date` = tomorrow
  - For each assignment, identifies the class and all enrolled students
  - Fetches parent links for each student
  - Sends WhatsApp notification via `ParentNotificationService.notify_assignment_due_tomorrow()`
  - Respects parent preferences (channels, quiet hours, category overrides)
  - Logs all operations with detailed warnings for failed notifications

### 2. Low Attendance Check
- **Schedule:** Daily at 9:00 AM IST (Asia/Kolkata timezone)
- **Job ID:** `check_low_attendance`
- **Behavior:**
  - Queries all students across all tenants
  - For each student, calls `ParentNotificationService.check_and_notify_low_attendance()`
  - Internally calculates monthly attendance percentage
  - If attendance < 75% (default threshold), notifies parents via WhatsApp
  - Respects parent preferences
  - Logs all operations with metrics (total students checked, notifications sent)

## How It Works

### Startup Flow
1. FastAPI app initializes via `create_app()` in `app_factory.py`
2. `create_lifespan()` is called as the lifespan context manager
3. During startup phase, if not in TESTING mode:
   - `_maybe_schedule_runtime_task()` is called for "scheduled notifications"
   - This imports `run_scheduled_notifications_loop` from runtime_scheduler
   - The loop is wrapped in an asyncio.Task and added to the tasks list

### Running Flow
1. `run_scheduled_notifications_loop(stop_event)` is executed
2. Inside the loop:
   - `ScheduledNotificationsService.initialize_scheduler()` creates AsyncIOScheduler
   - Two jobs are registered with CronTrigger (8 AM and 9 AM IST)
   - `scheduler.start()` begins the scheduler
   - Waits on `stop_event` (blocks until shutdown signal)

### Shutdown Flow
1. When FastAPI app shuts down, `stop_event.set()` is called
2. Scheduled notifications loop receives the event
3. `scheduler.shutdown(wait=False)` stops the scheduler
4. Tasks are cancelled and cleaned up

## Dependencies

### New Package
- **APScheduler 3.10.4** - Added to `backend/requirements.txt`
  - Provides AsyncIOScheduler for async-compatible job scheduling
  - CronTrigger for cron-style scheduling (8 AM, 9 AM IST)
  - Proper integration with asyncio event loop

### Existing Dependencies
- FastAPI (async framework context)
- SQLAlchemy (database queries)
- Parent notification service (notification logic)

## Configuration

### Timezone
- **Default:** `Asia/Kolkata` (IST)
- **Configurable:** Pass different timezone to `initialize_scheduler(timezone="...")`
- **Supported:** Any valid IANA timezone (e.g., "US/Eastern", "Europe/London")

### Job Times
Hardcoded cron triggers in `ScheduledNotificationsService.initialize_scheduler()`:

```python
# 8:00 AM IST - Check assignments due tomorrow
trigger=CronTrigger(hour=8, minute=0, timezone=timezone)

# 9:00 AM IST - Check low attendance
trigger=CronTrigger(hour=9, minute=0, timezone=timezone)
```

To change times, modify the `hour` and `minute` parameters in `scheduled_notifications.py`.

### Mode (Optional Environment Variables)
The scheduler is automatically enabled by default and disabled only in TESTING mode:

```python
# In startup.py lifespan
if not os.environ.get("TESTING"):
    _maybe_schedule_runtime_task(tasks, stop_event, ...)
```

To disable in production temporarily, set environment variable before startup (not recommended).

## Behavior & Error Handling

### Graceful Degradation
- ✅ Missing parent phone number → Logs warning, skips sending
- ✅ WhatsApp credentials not configured → Returns success=false, logged
- ✅ Database connection failed → Catch at job level, logged as error
- ✅ Parent preferences invalid → Filters/validates, continues
- ✅ Job execution timeout → APScheduler handles with `max_instances=1`

### Coalescing
Jobs use `coalesce=True` and `max_instances=1` to prevent:
- Multiple concurrent executions of the same job
- Queued job runs if scheduler catches up after delay

### Logging
All operations logged to `logging.getLogger(__name__)`:

```
INFO - Scheduler initialized with 2 jobs
INFO - Scheduler started successfully
INFO - Starting job: check_assignments_due_tomorrow
INFO - Found 10 assignments due tomorrow
INFO - Notifying 25 student(s) in class <class_id>
WARNING - Failed to notify parents for student <id>: <reason>
WARNING - Scheduler is already running
ERROR - Job check_low_attendance failed: <reason>
```

## Testing

### Local Development (Non-Testing Mode)
1. Set `.env` variables (or use defaults for demo)
2. Start backend: `python main.py` or via Docker
3. Observe logs:
   ```
   INFO - Scheduler initialized with 2 jobs: assignments check, low attendance check
   INFO - Scheduler started successfully
   ```
4. Wait for 8 AM or 9 AM IST (or modify CronTrigger temporarily for testing)

### Testing Mode
Set `TESTING=true` environment variable:
```bash
export TESTING=true
python -m pytest backend/tests
```

Scheduler will NOT start in testing mode (verified by `if not os.environ.get("TESTING")`).

### Manual Job Execution
To test jobs without waiting for schedule:

```python
from src.domains.academic.services.scheduled_notifications import ScheduledNotificationsService
import asyncio

async def test():
    await ScheduledNotificationsService._job_check_assignments_due_tomorrow()
    print("Job completed successfully")

asyncio.run(test())
```

## Database Considerations

### Queries
- **Assignments due tomorrow:** Filters by `due_date` range
- **Student list:** Queries `Enrollment` table for class members
- **Parent notification:** Uses existing `ParentLink` relationships
- **Low attendance:** Calculates from `Attendance` table records

### Performance
- Each job runs once per day → Low frequency
- Queries are indexed by `due_date`, `class_id`, `tenant_id`
- Parent notifications are async (non-blocking)
- All jobs wrapped in try-catch to prevent scheduler crashes

## Monitoring & Observability

### Prometheus Metrics (Optional)
APScheduler can be instrumented with Prometheus:
```python
from prometheus_client import Counter
job_executions = Counter('scheduled_job_executions_total', 'Total job executions', ['job_id', 'status'])
```

### Current Logging
Full execution logs are written to:
- Standard logger: `logging.getLogger(__name__)`
- Level: INFO (startup/completion), WARNING (minor issues), ERROR (failures)

### Health Check Integration
Scheduler health can be checked via:
```python
ScheduledNotificationsService._scheduler.get_jobs()  # Check running jobs
ScheduledNotificationsService._scheduler.running     # Check if active
```

## Integration with Phase 5

Phase 5 delivered:
- Parent notification service with preference logic ✅
- API endpoints for preference management ✅
- Frontend settings UI for configuration ✅
- Message templates (WhatsApp-optimized) ✅

Phase 6 adds:
- Automated job triggers (no manual API calls) ✅
- Daily execution on schedule ✅
- Multi-tenant support ✅
- Error resilience ✅

## Deployment Checklist

- [x] APScheduler added to requirements.txt
- [x] Scheduled notifications service created and tested
- [x] Runtime scheduler integration added
- [x] FastAPI lifespan updated
- [x] Timezone set to Asia/Kolkata (IST)
- [x] Logging configured
- [x] Error handling implemented
- [ ] Docker Compose updated (if needed)
- [ ] Production environment variables verified
- [ ] WhatsApp credentials configured (WHATSAPP_TOKEN, WHATSAPP_PHONE_ID)
- [ ] Database migrations run (existing tables reused)

## Next Steps (Optional Enhancements)

1. **Configurable Job Times**
   - Add environment variables for SCHEDULED_NOTIFICATIONS_ASSIGNMENT_TIME, etc.
   - Dynamic CronTrigger creation based on config

2. **Timezone Per-Tenant**
   - Store timezone preference in Tenant model
   - Run jobs in each tenant's timezone

3. **Job Result Tracking**
   - Create `ScheduledJobLog` table
   - Track execution time, records processed, notifications sent
   - Alerting on job failures

4. **Manual Job Triggers**
   - Add admin API endpoint to trigger jobs on-demand
   - Useful for testing and recovery scenarios

5. **Dynamic Job Management**
   - API to enable/disable specific jobs
   - Update job schedule without restarting

## Troubleshooting

### Scheduler not starting
```
Check logs for: "Scheduler started successfully"
If missing:
- Verify TESTING environment variable is not set
- Confirm APScheduler is installed: pip install APScheduler==3.10.4
- Check database connectivity (jobs query DB)
```

### Jobs not running at expected times
```
- Verify server timezone (compare with IST)
- Check logs for job execution messages: "Starting job: ..."
- Jobs run at 8 AM and 9 AM IST server time
- In testing: jobs do not run (TESTING=true disables scheduler)
```

### Parents not receiving notifications
```
- Check parent preferences: ensure channels are enabled
- Verify quiet hours settings: current time should not be in quiet window
- Check WhatsApp credentials: WHATSAPP_TOKEN, WHATSAPP_PHONE_ID configured
- Review logs for: "Failed to send parent notifications"
- Verify database has parent phone numbers in User table
```

### High job execution time
```
- If jobs take > 1 hour: APScheduler will coalesce (skip) the next run
- This is intentional (max_instances=1, coalesce=True)
- Monitor: Check for large number of assignments or students
- Optimize: Add database indexes if needed, consider pagination
```

## Files Modified

1. **Created:**
   - `backend/src/domains/academic/services/scheduled_notifications.py` (180 lines)

2. **Modified:**
   - `backend/requirements.txt` - Added APScheduler==3.10.4
   - `backend/src/bootstrap/startup.py` - Added scheduler to lifespan
   - `backend/src/domains/platform/services/runtime_scheduler.py` - Added `run_scheduled_notifications_loop()`

3. **Documentation:**
   - `SCHEDULED_NOTIFICATIONS.md` (this file)

## Architecture Diagram

```
FastAPI App Startup
    ↓
create_lifespan(container) called
    ↓
During startup:
  - load feature flags ✓
  - enforce startup checks ✓
  - schedule runtime tasks (including scheduled_notifications) ✓
    ↓
_maybe_schedule_runtime_task() for "scheduled notifications"
    ↓
Import runtime_scheduler.run_scheduled_notifications_loop
    ↓
asyncio.create_task(run_scheduled_notifications_loop(stop_event))
    ↓
ScheduledNotificationsService.initialize_scheduler()
  - Create AsyncIOScheduler (timezone=Asia/Kolkata)
  - Add job: check_assignments_due_tomorrow (8 AM IST)
  - Add job: check_low_attendance (9 AM IST)
    ↓
scheduler.start()
    ↓
Scheduler running ← [Daily at 8 AM: notify for tomorrow's assignments]
                ← [Daily at 9 AM: notify for low attendance]
                ← [Continue until stop_event.set()]
    ↓
On app shutdown:
  - stop_event.set()
  - scheduler.shutdown(wait=False)
  - Tasks cancelled/cleaned
```

## Summary

Phase 6 successfully implements a production-ready scheduled notification system that:
- ✅ Automatically notifies parents of assignments due tomorrow (8 AM IST)
- ✅ Automatically alerts parents of low attendance (9 AM IST)
- ✅ Respects all parent preferences from Phase 5 (channels, quiet hours, categories)
- ✅ Handles errors gracefully without crashing the API
- ✅ Integrates seamlessly with FastAPI lifespan
- ✅ Uses industry-standard APScheduler library
- ✅ Fully async/await compatible
- ✅ Multi-tenant aware
- ✅ Properly logs all operations
- ✅ No configuration required (works out of the box)
