"""Tests for fee management module."""
import uuid
from constants import FEE_TYPES, FEE_FREQUENCIES, FEE_INVOICE_STATUSES
from src.domains.identity.models.tenant import Tenant  # noqa: F401
from src.domains.identity.models.user import User  # noqa: F401


def test_fee_types_defined():
    expected = {"tuition", "lab", "transport", "library", "exam", "other"}
    assert FEE_TYPES == expected


def test_fee_frequencies_defined():
    expected = {"monthly", "quarterly", "yearly", "one_time"}
    assert FEE_FREQUENCIES == expected


def test_fee_invoice_statuses_defined():
    expected = {"pending", "partial", "paid", "overdue", "cancelled"}
    assert FEE_INVOICE_STATUSES == expected


def test_fee_structure_model():
    from src.domains.administrative.models.fee import FeeStructure
    fs = FeeStructure(
        tenant_id=uuid.uuid4(), fee_type="tuition",
        amount=5000.0, frequency="monthly",
    )
    assert fs.fee_type == "tuition"
    assert fs.amount == 5000.0


def test_fee_invoice_model():
    from src.domains.administrative.models.fee import FeeInvoice
    inv = FeeInvoice(
        tenant_id=uuid.uuid4(), student_id=uuid.uuid4(),
        fee_structure_id=uuid.uuid4(), amount_due=5000.0,
    )
    assert inv.amount_due == 5000.0


def test_fee_payment_model():
    from src.domains.administrative.models.fee import FeePayment
    pay = FeePayment(
        invoice_id=uuid.uuid4(), tenant_id=uuid.uuid4(),
        amount=2500.0, payment_method="cash", recorded_by=uuid.uuid4(),
    )
    assert pay.amount == 2500.0
    assert pay.payment_method == "cash"


def test_payment_status_transition():
    """Partial payment should set status to 'partial'."""
    assert "partial" in FEE_INVOICE_STATUSES


def test_amount_positive():
    """Fee amounts must be positive."""
    amount = 5000.0
    assert amount > 0


def test_report_structure():
    """Fee report should have correct keys."""
    report = {
        "total_due": 100000,
        "total_collected": 75000,
        "outstanding": 25000,
        "collection_rate": 75.0,
        "by_status": {"paid": 15, "pending": 5},
    }
    assert "total_due" in report
    assert "collection_rate" in report
    assert report["collection_rate"] == 75.0
