"""Convenience module to import all SQLAlchemy models so that
Base.metadata.create_all() can discover every table.

This file is imported by main.py during DEMO_MODE startup.
"""

# Identity
from src.domains.identity.models.user import User           # noqa: F401
from src.domains.identity.models.tenant import Tenant       # noqa: F401

# Academic
from src.domains.academic.models.core import Class, Subject, Enrollment  # noqa: F401
from src.domains.academic.models.batch import Batch, BatchEnrollment  # noqa: F401
from src.domains.academic.models.lecture import Lecture       # noqa: F401
from src.domains.academic.models.timetable import Timetable  # noqa: F401
from src.domains.academic.models.parent_link import ParentLink  # noqa: F401
from src.domains.academic.models.performance import SubjectPerformance  # noqa: F401
from src.domains.academic.models.attendance import Attendance  # noqa: F401
from src.domains.academic.models.assignment import Assignment, AssignmentSubmission  # noqa: F401
from src.domains.academic.models.marks import Exam, Mark     # noqa: F401
from src.domains.academic.models.test_series import TestSeries, MockTestAttempt  # noqa: F401
from src.domains.academic.models.student_profile import StudentProfile  # noqa: F401

# Administrative
from src.domains.administrative.models.admission import AdmissionApplication  # noqa: F401
from src.domains.administrative.models.complaint import Complaint  # noqa: F401
from src.domains.administrative.models.fee import FeeStructure, FeeInvoice, FeePayment  # noqa: F401

# Platform
from src.domains.platform.models.ai import AIQuery, AISessionEvent          # noqa: F401
from src.domains.platform.models.analytics_event import AnalyticsEvent  # noqa: F401
from src.domains.platform.models.document import Document    # noqa: F401
from src.domains.platform.models.audit import AuditLog       # noqa: F401
from src.domains.platform.models.feature_flag import FeatureFlag  # noqa: F401
from src.domains.platform.models.webhook import WebhookSubscription, WebhookDelivery  # noqa: F401
from src.domains.platform.models.spaced_repetition import ReviewSchedule  # noqa: F401
from src.domains.platform.models.notebook import Notebook  # noqa: F401
from src.domains.platform.models.generated_content import GeneratedContent  # noqa: F401
from src.domains.platform.models.topic_mastery import TopicMastery  # noqa: F401
from src.domains.platform.models.learner_profile import LearnerProfile  # noqa: F401
from src.domains.platform.models.study_path_plan import StudyPathPlan  # noqa: F401
from src.domains.platform.models.usage_counter import UsageCounter  # noqa: F401
from src.domains.platform.models.knowledge_graph import KGConcept, KGRelationship  # noqa: F401

# Mascot
from src.domains.mascot.models.conversation import MascotConversationTurn  # noqa: F401
from src.domains.mascot.models.mascot_memory import StudentMascotMemory  # noqa: F401
from src.domains.mascot.models.personality_profile import StudentPersonalityProfile  # noqa: F401
from src.domains.mascot.models.signals import ProfileSignal, ElicitationLog  # noqa: F401
