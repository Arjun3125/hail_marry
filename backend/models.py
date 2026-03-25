"""Convenience module to import all SQLAlchemy models so that
Base.metadata.create_all() can discover every table.

This file is imported by main.py during DEMO_MODE startup.
"""

# Identity
from src.domains.identity.models.user import User           # noqa: F401
from src.domains.identity.models.tenant import Tenant       # noqa: F401

# Academic
from src.domains.academic.models.core import Class, Subject, Enrollment  # noqa: F401
from src.domains.academic.models.lecture import Lecture       # noqa: F401
from src.domains.academic.models.timetable import Timetable  # noqa: F401
from src.domains.academic.models.parent_link import ParentLink  # noqa: F401
from src.domains.academic.models.performance import SubjectPerformance  # noqa: F401
from src.domains.academic.models.attendance import Attendance  # noqa: F401
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission  # noqa: F401
from src.domains.academic.models.marks import Exam, Mark     # noqa: F401
from src.domains.academic.models.test_series import TestSeries, MockTestAttempt  # noqa: F401

# Administrative
from src.domains.administrative.models.complaint import Complaint  # noqa: F401

# Platform
from src.domains.platform.models.ai import AIQuery          # noqa: F401
from src.domains.platform.models.document import Document    # noqa: F401
from src.domains.platform.models.audit import AuditLog       # noqa: F401
from src.domains.platform.models.webhook import WebhookSubscription, WebhookDelivery  # noqa: F401
from src.domains.platform.models.spaced_repetition import ReviewSchedule  # noqa: F401
