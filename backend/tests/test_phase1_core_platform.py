"""Phase 1 model-contract tests for the Vidya OS transformation program."""

import os
import sys
from pathlib import Path


BACKEND_DIR = Path(__file__).resolve().parents[1]
if str(BACKEND_DIR) not in sys.path:
    sys.path.insert(0, str(BACKEND_DIR))

os.environ["DEBUG"] = "true"

from src.domains.academic.models.batch import BatchEnrollment
from src.domains.academic.models.core import Enrollment
from src.domains.academic.models.parent_link import ParentLink
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.academic.models.test_series import TestSeries as AssessmentSeriesModel
from src.domains.administrative.models.fee import FeeInvoice, FeePayment


def _unique_constraint_columns(model):
    return [
        tuple(constraint.columns.keys())
        for constraint in model.__table__.constraints
        if constraint.__class__.__name__ == "UniqueConstraint"
    ]


def _check_constraint_sql(model):
    return [
        str(constraint.sqltext)
        for constraint in model.__table__.constraints
        if constraint.__class__.__name__ == "CheckConstraint"
    ]


def test_student_profile_exposes_unified_parent_and_placement_fields():
    columns = StudentProfile.__table__.columns.keys()

    assert "current_class_id" in columns
    assert "current_batch_id" in columns
    assert "primary_parent_id" in columns
    assert "guardian_count" in columns


def test_parent_link_is_unique_per_tenant_parent_child_pair():
    assert ("tenant_id", "parent_id", "child_id") in _unique_constraint_columns(ParentLink)


def test_enrollment_is_unique_per_tenant_student_class_academic_year():
    assert (
        "tenant_id",
        "student_id",
        "class_id",
        "academic_year",
    ) in _unique_constraint_columns(Enrollment)


def test_batch_enrollment_is_unique_per_tenant_batch_student():
    assert (
        "tenant_id",
        "batch_id",
        "student_id",
    ) in _unique_constraint_columns(BatchEnrollment)


def test_fee_invoice_has_duplicate_prevention_and_non_negative_amount_guards():
    unique_constraints = _unique_constraint_columns(FeeInvoice)
    checks = _check_constraint_sql(FeeInvoice)

    assert (
        "tenant_id",
        "student_id",
        "fee_structure_id",
        "due_date",
    ) in unique_constraints
    assert any("amount_due >= 0" in check for check in checks)
    assert any("amount_paid >= 0" in check for check in checks)


def test_fee_payment_requires_positive_amount():
    checks = _check_constraint_sql(FeePayment)
    assert any("amount > 0" in check for check in checks)


def test_test_series_exposes_explicit_lifecycle_columns():
    columns = AssessmentSeriesModel.__table__.columns.keys()

    assert "assessment_kind" in columns
    assert "grading_mode" in columns
    assert "status" in columns
    assert "opens_at" in columns
    assert "closes_at" in columns
    assert "published_at" in columns


def test_test_series_has_positive_marks_and_duration_guards():
    checks = _check_constraint_sql(AssessmentSeriesModel)
    assert any("total_marks > 0" in check for check in checks)
    assert any("duration_minutes > 0" in check for check in checks)
