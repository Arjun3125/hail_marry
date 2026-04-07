"""Fee management API routes — structures, invoices, payments, reports."""
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session
from typing import Optional
from uuid import UUID

from auth.dependencies import require_role
from database import get_db
from src.domains.academic.models.core import Class
from src.domains.administrative.services.fee_management import (
    create_fee_structure,
    generate_invoices,
    get_fee_report,
    get_student_ledger,
    list_fee_structures,
    list_invoices,
    record_payment,
)

router = APIRouter(prefix="/api/fees", tags=["Fees"])


# ── Request schemas ──

class CreateFeeStructureRequest(BaseModel):
    fee_type: str
    amount: float
    frequency: str
    class_id: Optional[str] = None
    academic_year: str = "2025-26"
    description: Optional[str] = None


class GenerateInvoicesRequest(BaseModel):
    fee_structure_id: str
    due_date: str  # ISO format


class RecordPaymentRequest(BaseModel):
    invoice_id: str
    amount: float
    payment_method: str
    transaction_ref: Optional[str] = None


def _parse_uuid(value: str, field_name: str) -> UUID:
    try:
        return UUID(value)
    except (TypeError, ValueError):
        raise HTTPException(status_code=400, detail=f"Invalid {field_name}")


# ── Endpoints ──

@router.post("/structures")
def create_structure(
    body: CreateFeeStructureRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Create a fee structure. Admin only."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")

    class_uuid = _parse_uuid(body.class_id, "class_id") if body.class_id else None
    try:
        structure = create_fee_structure(
            db,
            user.tenant_id,
            body.fee_type,
            body.amount,
            body.frequency,
            class_id=class_uuid,
            academic_year=body.academic_year,
            description=body.description,
            class_model=Class,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {
        "id": str(structure.id),
        "fee_type": structure.fee_type,
        "amount": structure.amount,
        "frequency": structure.frequency,
    }


@router.get("/structures")
def get_structures(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """List fee structures. Admin only."""
    structures = list_fee_structures(db, user.tenant_id)
    return {
        "structures": [
            {
                "id": str(s.id),
                "fee_type": s.fee_type,
                "amount": s.amount,
                "frequency": s.frequency,
                "academic_year": s.academic_year,
                "description": s.description,
            }
            for s in structures
        ]
    }


@router.post("/generate-invoices")
def generate_fee_invoices(
    body: GenerateInvoicesRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Generate invoices for enrolled students. Admin only."""
    try:
        due = datetime.fromisoformat(body.due_date)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid due_date format (use ISO)")

    try:
        result = generate_invoices(
            db,
            user.tenant_id,
            _parse_uuid(body.fee_structure_id, "fee_structure_id"),
            due,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return result


@router.get("/invoices")
def get_invoices(
    status: Optional[str] = Query(None),
    student_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """List invoices with filters. Admin only."""
    sid = _parse_uuid(student_id, "student_id") if student_id else None
    invoices, total = list_invoices(db, user.tenant_id, status, sid, limit, offset)
    return {
        "invoices": [
            {
                "id": str(i.id),
                "student_id": str(i.student_id),
                "amount_due": i.amount_due,
                "amount_paid": i.amount_paid,
                "status": i.status,
                "due_date": i.due_date.isoformat() if i.due_date else None,
            }
            for i in invoices
        ],
        "total": total,
    }


@router.post("/payments")
def make_payment(
    body: RecordPaymentRequest,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Record a fee payment. Admin only."""
    if body.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be positive")
    try:
        payment = record_payment(
            db,
            _parse_uuid(body.invoice_id, "invoice_id"),
            body.amount,
            body.payment_method,
            user.id, body.transaction_ref,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"payment_id": str(payment.id), "amount": payment.amount, "method": payment.payment_method}


@router.get("/report")
def fee_report(
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Financial report. Admin only."""
    return {"report": get_fee_report(db, user.tenant_id)}


@router.get("/student/{student_id}/ledger")
def student_ledger(
    student_id: str,
    user=Depends(require_role("admin")),
    db: Session = Depends(get_db),
):
    """Student fee ledger. Admin only."""
    ledger = get_student_ledger(db, user.tenant_id, _parse_uuid(student_id, "student_id"))
    return {"ledger": ledger}
