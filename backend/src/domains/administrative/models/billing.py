"""Billing models for Razorpay payment integration."""
import uuid
from sqlalchemy import Column, DateTime, Float, ForeignKey, Integer, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from database import Base


class BillingPlan(Base):
    __tablename__ = "billing_plans"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(50), unique=True, nullable=False)          # basic, standard, premium
    label = Column(String(100), nullable=False)                     # "Basic (ERP Only)"
    price_per_student_yearly = Column(Integer, nullable=False)      # in INR
    features = Column(JSONB, nullable=True)                         # {"ai_chat": true, ...}
    razorpay_plan_id = Column(String(100), nullable=True)           # Razorpay plan reference
    is_active = Column(Integer, default=1)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class TenantSubscription(Base):
    __tablename__ = "tenant_subscriptions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    plan_id = Column(UUID(as_uuid=True), ForeignKey("billing_plans.id"), nullable=False)
    status = Column(String(20), nullable=False, default="active")   # active, past_due, cancelled, trialing
    razorpay_subscription_id = Column(String(100), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=True)
    current_period_end = Column(DateTime(timezone=True), nullable=True)
    student_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class PaymentRecord(Base):
    __tablename__ = "payment_records"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)                          # in INR
    currency = Column(String(10), default="INR")
    razorpay_order_id = Column(String(100), nullable=True, unique=True)
    razorpay_payment_id = Column(String(100), nullable=True)
    razorpay_signature = Column(String(255), nullable=True)
    status = Column(String(20), nullable=False, default="created")  # created, captured, failed, refunded
    description = Column(String(500), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
