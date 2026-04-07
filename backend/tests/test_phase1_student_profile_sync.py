"""Phase 1 integration tests for unified learner-profile synchronization."""

from __future__ import annotations

from datetime import date
import os
import sys
import uuid
from pathlib import Path
from unittest.mock import MagicMock


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from src.domains.academic.models.attendance import Attendance
from src.domains.academic.models.batch import Batch, BatchEnrollment
from src.domains.academic.models.core import Class, Enrollment, Subject
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.academic.services.student_profile_sync import sync_student_profile_context
from src.domains.administrative.application.parent_links import (
    create_admin_parent_link,
    delete_admin_parent_link,
)
from src.domains.administrative.services.admission import bulk_enroll
from src.domains.administrative.models.admission import AdmissionApplication
from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.identity.services.onboarding import import_students_from_csv


def _student(tenant_id, email="student@example.com", full_name="Student One") -> User:
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        role="student",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )


def _parent(tenant_id, email="parent@example.com", full_name="Parent One") -> User:
    return User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        role="parent",
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )


def test_sync_student_profile_context_upserts_live_enrollment_and_guardian_data(db_session, active_tenant):
    school_class = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Class 9",
        grade_level="9",
    )
    maths = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        name="Mathematics",
    )
    science = Subject(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        class_id=school_class.id,
        name="Science",
    )
    student = _student(active_tenant.id)
    parent = _parent(active_tenant.id)
    batch = Batch(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Evening Batch",
        class_id=school_class.id,
        teacher_id=None,
    )
    db_session.add_all([school_class, maths, science, student, parent, batch])
    db_session.flush()
    db_session.add(
        Enrollment(
            tenant_id=active_tenant.id,
            student_id=student.id,
            class_id=school_class.id,
        )
    )
    db_session.add(
        BatchEnrollment(
            tenant_id=active_tenant.id,
            batch_id=batch.id,
            student_id=student.id,
            status="active",
        )
    )
    db_session.add(
        ParentLink(
            tenant_id=active_tenant.id,
            parent_id=parent.id,
            child_id=student.id,
        )
    )
    db_session.add_all(
        [
            Attendance(
                tenant_id=active_tenant.id,
                student_id=student.id,
                class_id=school_class.id,
                date=date(2026, 4, 4),
                status="present",
            ),
            Attendance(
                tenant_id=active_tenant.id,
                student_id=student.id,
                class_id=school_class.id,
                date=date(2026, 4, 5),
                status="absent",
            ),
            Attendance(
                tenant_id=active_tenant.id,
                student_id=student.id,
                class_id=school_class.id,
                date=date(2026, 4, 6),
                status="absent",
            ),
            SubjectPerformance(
                tenant_id=active_tenant.id,
                student_id=student.id,
                subject_id=maths.id,
                average_score=81.0,
                attendance_rate=90.0,
            ),
            SubjectPerformance(
                tenant_id=active_tenant.id,
                student_id=student.id,
                subject_id=science.id,
                average_score=63.0,
                attendance_rate=78.0,
            ),
        ]
    )
    db_session.commit()

    profile = sync_student_profile_context(
        db=db_session,
        tenant_id=active_tenant.id,
        student_id=student.id,
    )
    db_session.commit()

    stored = db_session.query(StudentProfile).filter(
        StudentProfile.tenant_id == active_tenant.id,
        StudentProfile.user_id == student.id,
    ).one()
    assert profile.id == stored.id
    assert stored.current_class_id == school_class.id
    assert stored.current_batch_id == batch.id
    assert stored.primary_parent_id == parent.id
    assert stored.guardian_count == 1
    assert stored.total_days == 3
    assert stored.present_days == 1
    assert stored.attendance_pct == 33.33
    assert stored.absent_streak == 2
    assert stored.overall_score_pct == 72.0
    assert stored.strongest_subject == "Mathematics"
    assert stored.weakest_subject == "Science"
    assert stored.subject_mastery_map == {
        "Mathematics": 81.0,
        "Science": 63.0,
    }


def test_create_admin_parent_link_syncs_student_profile_context(db_session, active_tenant):
    parent = _parent(active_tenant.id, email="parent-sync@example.com")
    child = _student(active_tenant.id, email="child-sync@example.com")
    db_session.add_all([parent, child])
    db_session.commit()

    sync_mock = MagicMock()
    payload = create_admin_parent_link(
        db=db_session,
        tenant_id=active_tenant.id,
        actor_user_id=uuid.uuid4(),
        parent_id=str(parent.id),
        child_id=str(child.id),
        parse_uuid_fn=lambda value, _field: uuid.UUID(str(value)),
        sync_student_profile_fn=sync_mock,
    )

    assert payload["success"] is True
    sync_mock.assert_called_once_with(
        db=db_session,
        tenant_id=active_tenant.id,
        student_id=child.id,
    )


def test_delete_admin_parent_link_syncs_student_profile_context(db_session, active_tenant):
    parent = _parent(active_tenant.id, email="parent-delete@example.com")
    child = _student(active_tenant.id, email="child-delete@example.com")
    link = ParentLink(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        parent_id=parent.id,
        child_id=child.id,
    )
    db_session.add_all([parent, child, link])
    db_session.commit()

    sync_mock = MagicMock()
    payload = delete_admin_parent_link(
        db=db_session,
        tenant_id=active_tenant.id,
        actor_user_id=uuid.uuid4(),
        link_id=str(link.id),
        parse_uuid_fn=lambda value, _field: uuid.UUID(str(value)),
        sync_student_profile_fn=sync_mock,
    )

    assert payload["success"] is True
    sync_mock.assert_called_once_with(
        db=db_session,
        tenant_id=active_tenant.id,
        student_id=child.id,
    )


def test_import_students_from_csv_syncs_each_imported_student(db_session, active_tenant):
    school_class = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Class 8A",
        grade_level="8",
    )
    db_session.add(school_class)
    db_session.commit()

    sync_mock = MagicMock()
    payload = import_students_from_csv(
        db=db_session,
        tenant_id=active_tenant.id,
        csv_content="full_name,email,class_name\nAsha,asha@example.com,Class 8A\n",
        sync_student_profile_fn=sync_mock,
    )

    assert payload["imported"] == 1
    assert sync_mock.call_count == 1


def test_bulk_enroll_syncs_new_student_profiles(db_session, active_tenant):
    school_class = Class(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        name="Class 10",
        grade_level="10",
    )
    application = AdmissionApplication(
        id=uuid.uuid4(),
        tenant_id=active_tenant.id,
        student_name="Applicant One",
        parent_email="applicant@example.com",
        applied_class_id=school_class.id,
        applied_class_name=school_class.name,
        status="accepted",
    )
    db_session.add_all([school_class, application])
    db_session.commit()

    sync_mock = MagicMock()
    payload = bulk_enroll(
        db=db_session,
        tenant_id=active_tenant.id,
        application_ids=[application.id],
        enrolled_by=uuid.uuid4(),
        sync_student_profile_fn=sync_mock,
    )

    assert payload["enrolled"] == 1
    assert sync_mock.call_count == 1
