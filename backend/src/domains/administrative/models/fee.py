"""Fee management models — fee structures, invoices, and payments."""
import uuid
from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, String, func
from sqlalchemy.dialects.postgresql import UUID
from database import Base


class FeeStructure(Base):
    __tablename__ = "fee_structures"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    class_id = Column(UUID(as_uuid=True), ForeignKey("classes.id"), nullable=True)
    fee_type = Column(String(50), nullable=False)       # tuition, lab, transport, library, exam, other
    amount = Column(Float, nullable=False)               # per-student amount in INR
    frequency = Column(String(20), nullable=False)       # monthly, quarterly, yearly, one_time
    academic_year = Column(String(20), default="2025-26")
    description = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class FeeInvoice(Base):
    __tablename__ = "fee_invoices"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    student_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    fee_structure_id = Column(UUID(as_uuid=True), ForeignKey("fee_structures.id"), nullable=False)
    amount_due = Column(Float, nullable=False)
    amount_paid = Column(Float, default=0.0)
    status = Column(String(20), nullable=False, default="pending")  # pending, partial, paid, overdue, cancelled
    due_date = Column(DateTime(timezone=True), nullable=False)
    issued_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class FeePayment(Base):
    __tablename__ = "fee_payments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    invoice_id = Column(UUID(as_uuid=True), ForeignKey("fee_invoices.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    amount = Column(Float, nullable=False)
    payment_method = Column(String(30), nullable=False)  # cash, online, bank_transfer, razorpay
    transaction_ref = Column(String(200), nullable=True)
    recorded_by = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    paid_at = Column(DateTime(timezone=True), server_default=func.now())
