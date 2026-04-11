"""
EVENT HOOKS INTEGRATION GUIDE FOR WHATSAPP NOTIFICATIONS

This document shows where to add event hooks for triggering parent notifications
in the teacher workflow.

═══════════════════════════════════════════════════════════════════════════════

LOCATION 1: Assignment Creation Hook
─────────────────────────────────────
File: backend/src/domains/academic/routes/teacher.py
Endpoint: POST /teacher/assignments (create_assignment)

Current code:
    @router.post("/assignments")
    async def create_assignment(
        data: AssignmentCreate,
        current_user: User = Depends(require_role("teacher", "admin")),
        teacher_class_ids: list = Depends(get_teacher_class_ids),
        db: Session = Depends(get_db),
    ):
        # ... existing code ...
        return _build_created_assignment_response_impl(...)

ADD THIS HOOK after assignment is created:
────────────────────────────────────────
    # After creating assignment, check if due date is tomorrow
    import asyncio
    from datetime import datetime, timedelta, timezone
    from src.domains.academic.services.parent_notification_service import ParentNotificationService
    
    response = _build_created_assignment_response_impl(...)
    
    # Extract assignment ID from response
    assignment_id = response.get("id")  # Assuming response is dict with 'id' field
    
    # Get all students in the class
    from src.domains.academic.models.core import Enrollment
    enrollments = db.query(Enrollment).filter(
        Enrollment.class_id == <extracted from subject>
    ).all()
    
    # Trigger notifications for each student if due date is nearby
    task = asyncio.create_task(
        ParentNotificationService.notify_assignment_due_tomorrow(
            db=db,
            tenant_id=current_user.tenant_id,
            student_id=enrollment.student_id,
            assignment_id=assignment_id,
        )
    )
    
    return response

═══════════════════════════════════════════════════════════════════════════════

LOCATION 2: Attendance Marking Hook
───────────────────────────────────
File: backend/src/domains/academic/routes/teacher.py
Endpoint: POST /teacher/attendance (submit_attendance)

Hook for: Notifying parents when their child is marked absent

Current infrastructure already exists!
File: backend/src/domains/academic/services/attendance_notifier.py
Function: notify_parents_on_absence()

This is already integrated and working. No additional hooks needed.

═══════════════════════════════════════════════════════════════════════════════

LOCATION 3: Marks Submission Hook
──────────────────────────────────
File: backend/src/domains/academic/routes/teacher.py
Endpoint: POST /teacher/marks (submit_marks)

Current code:
    @router.post("/marks")
    async def submit_marks(
        data: MarksBulk,
        current_user: User = Depends(require_role("teacher", "admin")),
        ...
    ):
        # ... existing code ...
        return response

ADD THIS HOOK after marks are submitted:
───────────────────────────────────────
    import asyncio
    from src.domains.academic.services.parent_notification_service import ParentNotificationService
    
    # After marks are saved to DB
    for student_id, mark_id in list_of_submitted_marks:
        task = asyncio.create_task(
            ParentNotificationService.notify_assessment_results(
                db=db,
                tenant_id=current_user.tenant_id,
                student_id=student_id,
                mark_id=mark_id,
            )
        )

═══════════════════════════════════════════════════════════════════════════════

ASYNC BACKGROUND TASKS (Recommended Implementation)
────────────────────────────────────────────────────

Instead of synchronous hooks, create scheduled background tasks:

File: backend/src/domains/academic/services/scheduled_notifications.py (NEW)

    import asyncio
    from datetime import datetime, timedelta, timezone
    from database import SessionLocal
    from src.domains.academic.models.assignment import Assignment
    from src.domains.academic.services.parent_notification_service import ParentNotificationService
    
    async def check_and_notify_assignments_due_tomorrow():
        db = SessionLocal()
        try:
            tomorrow = (datetime.now(timezone.utc) + timedelta(days=1)).date()
            
            # Find all assignments due tomorrow
            assignments = db.query(Assignment).filter(
                Assignment.due_date == tomorrow
            ).all()
            
            for assignment in assignments:
                # Get all students in the class
                from src.domains.academic.models.core import Enrollment
                
                enrollments = db.query(Enrollment).filter(
                    Enrollment.class_id == assignment.class_id
                ).all()
                
                for enrollment in enrollments:
                    await ParentNotificationService.notify_assignment_due_tomorrow(
                        db=db,
                        tenant_id=assignment.tenant_id,
                        student_id=enrollment.student_id,
                        assignment_id=assignment.id,
                    )
        finally:
            db.close()
    
    async def check_and_notify_low_attendance():
        db = SessionLocal()
        try:
            # Get all students
            from src.domains.identity.models.user import User
            from src.domains.academic.models.attendance import Attendance
            
            students = db.query(User).filter(User.role == "student").all()
            
            for student in students:
                ParentNotificationService.check_and_notify_low_attendance(
                    db=db,
                    tenant_id=student.tenant_id,
                    student_id=student.id,
                    threshold=75,  # Configurable
                )
        finally:
            db.close()

Then schedule these via APScheduler or Celery:

File: backend/main.py

    from apscheduler.schedulers.background import BackgroundScheduler
    
    scheduler = BackgroundScheduler()
    
    # Run every day at 8 AM IST
    scheduler.add_job(
        check_and_notify_assignments_due_tomorrow,
        'cron',
        hour=2,  # 8 AM IST = 2:30 UTC (approximate)
        minute=30,
    )
    
    # Run every day at 9 AM IST
    scheduler.add_job(
        check_and_notify_low_attendance,
        'cron',
        hour=3,
        minute=30,
    )
    
    scheduler.start()

═══════════════════════════════════════════════════════════════════════════════

TESTING THE HOOKS
─────────────────

1. Trigger assignment creation:
   curl -X POST http://localhost:8000/api/teacher/assignments \
     -H "Authorization: Bearer <token>" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Test Assignment",
       "subject_id": "...",
       "due_date": "2026-04-12"
     }'

2. Check if parent received WhatsApp notification (if credentials configured)

3. If not configured, check database:
   SELECT * FROM notifications
   WHERE category = 'assignment_reminder'
   AND created_at > NOW() - INTERVAL 1 MINUTE;

═══════════════════════════════════════════════════════════════════════════════

PARENT NOTIFICATION PREFERENCES API
────────────────────────────────────

GET /api/parent/notification-preferences
  Returns current parent's notification settings

PUT /api/parent/notification-preferences
  Updates notification settings
  
  Example payload:
  {
    "whatsapp_enabled": true,
    "email_enabled": false,
    "push_enabled": true,
    "quiet_hours_start": "22:00",
    "quiet_hours_end": "07:00",
    "category_overrides": {
      "assignment_reminder": true,
      "low_attendance": true,
      "assessment_results": false
    }
  }

═══════════════════════════════════════════════════════════════════════════════
"""
