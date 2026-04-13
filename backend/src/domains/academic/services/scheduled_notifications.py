"""Scheduled notification jobs using APScheduler for parent notifications."""
import asyncio
import importlib
import logging
from datetime import datetime, timedelta
from typing import Any

try:
    _apscheduler = importlib.import_module("apscheduler")
    AsyncIOScheduler: Any = getattr(_apscheduler.schedulers.asyncio, "AsyncIOScheduler")
    CronTrigger: Any = getattr(_apscheduler.triggers.cron, "CronTrigger")
except (ModuleNotFoundError, AttributeError):
    AsyncIOScheduler = object
    CronTrigger = object

from database import SessionLocal
from src.domains.academic.models.assignment import Assignment
from src.domains.academic.models.core import Enrollment
from src.domains.identity.models.user import User
from src.domains.academic.services.parent_notification_service import ParentNotificationService

logger: logging.Logger = logging.getLogger(__name__)


class ScheduledNotificationsService:
    """Service for managing scheduled parent notifications via APScheduler."""

    _scheduler: Any = None

    @classmethod
    def initialize_scheduler(cls, timezone: str = "Asia/Kolkata") -> Any:
        """Initialize the APScheduler instance with configured jobs.

        Args:
            timezone: Timezone for cron jobs (default: Asia/Kolkata for IST)

        Returns:
            Configured AsyncIOScheduler instance
        """
        if cls._scheduler is not None:
            logger.warning("Scheduler already initialized, returning existing instance")
            return cls._scheduler

        cls._scheduler = AsyncIOScheduler(timezone=timezone)

        # Add scheduled jobs
        cls._scheduler.add_job(
            cls._job_check_assignments_due_tomorrow,
            trigger=CronTrigger(hour=8, minute=0, timezone=timezone),
            id="check_assignments_due_tomorrow",
            name="Check assignments due tomorrow and notify parents",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        cls._scheduler.add_job(
            cls._job_check_low_attendance,
            trigger=CronTrigger(hour=9, minute=0, timezone=timezone),
            id="check_low_attendance",
            name="Check and notify low attendance alerts",
            replace_existing=True,
            coalesce=True,
            max_instances=1,
        )

        logger.info("Scheduler initialized with 2 jobs: assignments check, low attendance check")
        return cls._scheduler

    @classmethod
    async def start_scheduler(cls) -> None:
        """Start the scheduler."""
        if cls._scheduler is None:
            cls.initialize_scheduler()

        if not cls._scheduler.running:
            cls._scheduler.start()
            logger.info("Scheduler started successfully")
        else:
            logger.warning("Scheduler is already running")

    @classmethod
    async def stop_scheduler(cls) -> None:
        """Stop the scheduler."""
        if cls._scheduler and cls._scheduler.running:
            cls._scheduler.shutdown(wait=False)
            logger.info("Scheduler stopped")

    @classmethod
    async def _job_check_assignments_due_tomorrow(cls) -> None:
        """Check for assignments due tomorrow and notify parents.

        This job runs daily at 8 AM IST and:
        1. Queries all assignments with due_date = tomorrow
        2. For each assignment, gets the class and all students in that class
        3. Fetches parent links for each student
        4. Sends WhatsApp notification to each parent (respecting preferences)
        """
        logger.info("Starting job: check_assignments_due_tomorrow")
        db = SessionLocal()

        try:
            # Calculate tomorrow's date range
            tomorrow_start: datetime = (
                datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
            )
            tomorrow_end: datetime = tomorrow_start + timedelta(days=1)

            # Query assignments due tomorrow (eagerly load subject to avoid N+1)
            from sqlalchemy.orm import joinedload
            assignment_subject_attr: Any = getattr(Assignment, "subject", None)
            assignment_due_date_attr: Any = getattr(Assignment, "due_date", None)
            assignments = (
                db.query(Assignment)
                .options(joinedload(assignment_subject_attr))
                .filter(assignment_due_date_attr >= tomorrow_start, assignment_due_date_attr < tomorrow_end)
                .all()
            )

            if not assignments:
                logger.info("No assignments due tomorrow found")
                return

            logger.info(f"Found {len(assignments)} assignments due tomorrow")

            # For each assignment, notify parents of students in that assignment's class
            for assignment in assignments:
                try:
                    assignment_subject = getattr(assignment, "subject", None)
                    assignment_class_id = getattr(assignment_subject, "class_id", None)
                    if not assignment_subject or not assignment_class_id:
                        logger.warning(f"Assignment {assignment.id} has no related subject/class")
                        continue

                    # Get all students enrolled in the class
                    enrollments = (
                        db.query(Enrollment)
                        .filter(Enrollment.class_id == assignment_class_id)
                        .all()
                    )

                    if not enrollments:
                        logger.info(
                            f"No students found in class {assignment_class_id} for assignment {assignment.id}"
                        )
                        continue

                    logger.info(
                        f"Notifying {len(enrollments)} student(s) in class {assignment_class_id}"
                    )

                    # Notify each student's parents
                    for enrollment in enrollments:
                        try:
                            await ParentNotificationService.notify_assignment_due_tomorrow(
                                db=db,
                                tenant_id=assignment.tenant_id,
                                student_id=enrollment.student_id,
                                assignment_id=assignment.id,
                            )
                        except Exception as e:
                            logger.warning(
                                f"Failed to notify parents for student {enrollment.student_id}: {type(e).__name__}: {str(e)}",
                                exc_info=True
                            )

                except Exception as e:
                    logger.error(f"Error processing assignment {assignment.id}: {type(e).__name__}: {str(e)}", exc_info=True)

        except Exception as e:
            logger.error(f"Job check_assignments_due_tomorrow failed: {type(e).__name__}: {str(e)}", exc_info=True)

        finally:
            db.close()

    @classmethod
    async def _job_check_low_attendance(cls) -> None:
        """Check for low attendance and notify parents.

        This job runs daily at 9 AM IST and:
        1. For each student, calculates monthly attendance percentage
        2. If attendance < threshold (default 75%), notifies parents
        3. Respects parent preferences for notifications
        """
        logger.info("Starting job: check_low_attendance")
        db = SessionLocal()

        try:
            # Query all students across all tenants
            students = db.query(User).filter(User.role == "student").all()

            if not students:
                logger.info("No students found")
                return

            logger.info(f"Checking attendance for {len(students)} student(s)")
            notified_count = 0

            for student in students:
                try:
                    # Check low attendance (this method queries and calculates internally)
                    ParentNotificationService.check_and_notify_low_attendance(
                        db=db,
                        tenant_id=student.tenant_id,
                        student_id=student.id,
                        threshold=75,  # Default 75% threshold
                    )
                    notified_count += 1

                except Exception as e:
                    logger.warning(f"Failed to check attendance for student {student.id}: {type(e).__name__}: {str(e)}", exc_info=True)

            logger.info(f"Low attendance check completed for {notified_count} students")

        except Exception as e:
            logger.error(f"Job check_low_attendance failed: {type(e).__name__}: {str(e)}", exc_info=True)

        finally:
            db.close()


async def run_scheduled_notifications_loop(stop_event: asyncio.Event) -> None:
    """Main async loop for running the scheduler.

    This function is called during FastAPI lifespan startup and runs until stop_event is set.

    Args:
        stop_event: asyncio.Event to signal scheduler shutdown
    """
    try:
        logger.info("Initializing scheduled notifications service")
        service = ScheduledNotificationsService()
        service.initialize_scheduler()
        await service.start_scheduler()

        # Keep the scheduler running until stop_event is set
        await stop_event.wait()

        logger.info("Stop event received, shutting down scheduler")
        await service.stop_scheduler()

    except Exception as e:
        logger.error(f"Scheduled notifications loop failed: {str(e)}")
        raise
