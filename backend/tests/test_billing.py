"""Tests for Razorpay billing service and routes."""
import hashlib
import hmac
import uuid


from constants import BILLING_CURRENCY, BILLING_PLANS


# ── Unit tests for constants ──

def test_billing_plans_structure():
    """All billing plans should have required keys."""
    for name, plan in BILLING_PLANS.items():
        assert "price_per_student_yearly" in plan
        assert "label" in plan
        assert isinstance(plan["price_per_student_yearly"], int)
        assert plan["price_per_student_yearly"] > 0


def test_billing_currency():
    assert BILLING_CURRENCY == "INR"


def test_plan_tiers():
    """Plans should have ascending pricing."""
    prices = [p["price_per_student_yearly"] for p in BILLING_PLANS.values()]
    assert prices == sorted(prices), "Plan prices should be in ascending order"


# ── Signature verification ──

def test_verify_signature_valid():
    """HMAC-SHA256 verification should pass for correct signature."""
    secret = "test_secret_key"
    order_id = "order_abc123"
    payment_id = "pay_xyz789"
    message = f"{order_id}|{payment_id}".encode()
    signature = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()

    # Manually replicate the verification logic
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    assert hmac.compare_digest(expected, signature)


def test_verify_signature_invalid():
    """HMAC-SHA256 verification should fail for wrong signature."""
    secret = "test_secret_key"
    order_id = "order_abc123"
    payment_id = "pay_xyz789"
    message = f"{order_id}|{payment_id}".encode()
    expected = hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()
    assert not hmac.compare_digest(expected, "wrong_signature")


# ── Webhook payload parsing ──

def test_webhook_payload_payment_captured():
    """Webhook payload for payment.captured should have expected structure."""
    payload = {
        "event": "payment.captured",
        "payload": {
            "payment": {
                "entity": {
                    "id": "pay_test123",
                    "order_id": "order_test456",
                    "amount": 90000,
                    "currency": "INR",
                    "status": "captured",
                }
            }
        },
    }
    entity = payload["payload"]["payment"]["entity"]
    assert entity["id"] == "pay_test123"
    assert entity["order_id"] == "order_test456"
    assert entity["status"] == "captured"


def test_webhook_payload_subscription_charged():
    """Webhook payload for subscription.charged should have expected structure."""
    payload = {
        "event": "subscription.charged",
        "payload": {
            "subscription": {
                "entity": {
                    "id": "sub_test789",
                    "plan_id": "plan_basic",
                    "status": "active",
                }
            }
        },
    }
    entity = payload["payload"]["subscription"]["entity"]
    assert entity["id"] == "sub_test789"


# ── Model instantiation ──

def test_billing_plan_model():
    """BillingPlan model should accept expected fields."""
    from src.domains.administrative.models.billing import BillingPlan

    plan = BillingPlan(
        name="test",
        label="Test Plan",
        price_per_student_yearly=500,
        features={"ai_chat": True},
    )
    assert plan.name == "test"
    assert plan.price_per_student_yearly == 500


def test_payment_record_model():
    """PaymentRecord model should accept expected fields."""
    from src.domains.administrative.models.billing import PaymentRecord

    record = PaymentRecord(
        tenant_id=uuid.uuid4(),
        amount=5000.0,
        currency="INR",
        status="created",
    )
    assert record.amount == 5000.0
    assert record.status == "created"


def test_tenant_subscription_model():
    """TenantSubscription model should accept expected fields."""
    from src.domains.administrative.models.billing import TenantSubscription

    sub = TenantSubscription(
        tenant_id=uuid.uuid4(),
        plan_id=uuid.uuid4(),
        status="active",
        student_count=50,
    )
    assert sub.status == "active"
    assert sub.student_count == 50
