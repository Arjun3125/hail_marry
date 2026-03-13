"""Fee management service — structures, invoicing, payments, reports."""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from constants import FEE_INVOICE_STATUSES
from models.academic import Enrollment
from models.fee import FeeInvoice, FeePayment, FeeStructure
from models.user import User


def create_fee_structure(
    db: Session,
    tenant_id: UUID,
    fee_type: str,
    amount: float,
    frequency: str,
    class_id: Optional[UUID] = None,
    academic_year: str = "2025-26",
    description: Optional[str] = None,
) -> FeeStructure:
    """Create a new fee structure for a class or school-wide."""
    structure = FeeStructure(
        tenant_id=tenant_id,
        class_id=class_id,
        fee_type=fee_type,
        amount=amount,
        frequency=frequency,
        academic_year=academic_year,
        description=description,
    )
    db.add(structure)
    db.commit()
    db.refresh(structure)
    return structure


def list_fee_structures(db: Session, tenant_id: UUID) -> list[FeeStructure]:
    """List all active fee structures for a tenant."""
    return (
        db.query(FeeStructure)
        .filter(FeeStructure.tenant_id == tenant_id, FeeStructure.is_active == 1)
        .order_by(FeeStructure.created_at.desc())
        .all()
    )


def generate_invoices(
    db: Session, tenant_id: UUID, fee_structure_id: UUID, due_date: datetime
) -> dict:
    """Generate invoices for all enrolled students in the fee structure's class."""
    structure = db.query(FeeStructure).filter(
        FeeStructure.id == fee_structure_id, FeeStructure.tenant_id == tenant_id
    ).first()
    if not structure:
        raise ValueError("Fee structure not found")

    # Get enrolled students for this class
    if structure.class_id:
        enrollments = db.query(Enrollment).filter(
            Enrollment.tenant_id == tenant_id,
            Enrollment.class_id == structure.class_id,
        ).all()
        student_ids = [e.student_id for e in enrollments]
    else:
        # School-wide fee — apply to all students
        students = db.query(User).filter(
            User.tenant_id == tenant_id, User.role == "student", User.is_active == True
        ).all()
        student_ids = [s.id for s in students]

    generated = 0
    skipped = 0
    for sid in student_ids:
        # Skip if invoice already exists for this structure + student + due_date
        existing = db.query(FeeInvoice).filter(
            FeeInvoice.tenant_id == tenant_id,
            FeeInvoice.student_id == sid,
            FeeInvoice.fee_structure_id == fee_structure_id,
            FeeInvoice.due_date == due_date,
        ).first()
        if existing:
            skipped += 1
            continue

        invoice = FeeInvoice(
            tenant_id=tenant_id,
            student_id=sid,
            fee_structure_id=fee_structure_id,
            amount_due=structure.amount,
            amount_paid=0.0,
            status="pending",
            due_date=due_date,
        )
        db.add(invoice)
        generated += 1

    db.commit()
    return {"generated": generated, "skipped": skipped, "total_students": len(student_ids)}


def record_payment(
    db: Session,
    invoice_id: UUID,
    amount: float,
    payment_method: str,
    recorded_by: UUID,
    transaction_ref: Optional[str] = None,
) -> FeePayment:
    """Record a payment against an invoice and update invoice status."""
    invoice = db.query(FeeInvoice).filter(FeeInvoice.id == invoice_id).first()
    if not invoice:
        raise ValueError("Invoice not found")

    payment = FeePayment(
        invoice_id=invoice_id,
        tenant_id=invoice.tenant_id,
        amount=amount,
        payment_method=payment_method,
        transaction_ref=transaction_ref,
        recorded_by=recorded_by,
    )
    db.add(payment)

    # Update invoice paid amount and status
    invoice.amount_paid = (invoice.amount_paid or 0) + amount
    if invoice.amount_paid >= invoice.amount_due:
        invoice.status = "paid"
    elif invoice.amount_paid > 0:
        invoice.status = "partial"

    db.commit()
    db.refresh(payment)
    return payment


def list_invoices(
    db: Session,
    tenant_id: UUID,
    status_filter: Optional[str] = None,
    student_id: Optional[UUID] = None,
    limit: int = 50,
    offset: int = 0,
) -> tuple[list[FeeInvoice], int]:
    """List invoices with optional filters."""
    query = db.query(FeeInvoice).filter(FeeInvoice.tenant_id == tenant_id)
    if status_filter and status_filter in FEE_INVOICE_STATUSES:
        query = query.filter(FeeInvoice.status == status_filter)
    if student_id:
        query = query.filter(FeeInvoice.student_id == student_id)
    total = query.count()
    invoices = query.order_by(FeeInvoice.due_date.desc()).offset(offset).limit(limit).all()
    return invoices, total


def get_fee_report(db: Session, tenant_id: UUID) -> dict:
    """Financial summary: total due, total collected, outstanding, by status."""
    totals = (
        db.query(
            func.sum(FeeInvoice.amount_due).label("total_due"),
            func.sum(FeeInvoice.amount_paid).label("total_paid"),
        )
        .filter(FeeInvoice.tenant_id == tenant_id)
        .first()
    )
    total_due = totals.total_due or 0
    total_paid = totals.total_paid or 0

    status_counts = (
        db.query(FeeInvoice.status, func.count(FeeInvoice.id))
        .filter(FeeInvoice.tenant_id == tenant_id)
        .group_by(FeeInvoice.status)
        .all()
    )

    return {
        "total_due": total_due,
        "total_collected": total_paid,
        "outstanding": total_due - total_paid,
        "collection_rate": round((total_paid / total_due * 100), 1) if total_due > 0 else 0,
        "by_status": {status: count for status, count in status_counts},
    }


def get_student_ledger(db: Session, tenant_id: UUID, student_id: UUID) -> list[dict]:
    """Get full fee ledger for a student."""
    invoices = (
        db.query(FeeInvoice)
        .filter(FeeInvoice.tenant_id == tenant_id, FeeInvoice.student_id == student_id)
        .order_by(FeeInvoice.due_date.desc())
        .all()
    )
    ledger = []
    for inv in invoices:
        payments = (
            db.query(FeePayment)
            .filter(FeePayment.invoice_id == inv.id)
            .order_by(FeePayment.paid_at.asc())
            .all()
        )
        ledger.append({
            "invoice_id": str(inv.id),
            "amount_due": inv.amount_due,
            "amount_paid": inv.amount_paid,
            "status": inv.status,
            "due_date": inv.due_date.isoformat() if inv.due_date else None,
            "payments": [
                {
                    "amount": p.amount,
                    "method": p.payment_method,
                    "ref": p.transaction_ref,
                    "date": p.paid_at.isoformat() if p.paid_at else None,
                }
                for p in payments
            ],
        })
    return ledger
