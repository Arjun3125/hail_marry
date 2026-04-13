"""Student risk-flag cron helpers."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any
from uuid import UUID

from database import SessionLocal
from src.domains.academic.models.student_profile import StudentProfile
from src.domains.administrative.models.fee import FeeInvoice
from src.domains.platform.services.telemetry_events import record_business_event

logger: logging.Logger = logging.getLogger(__name__)


def _normalize_datetime(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value


def _review_gap_days(profile: StudentProfile, *, now: datetime) -> int | None:
    last_review_at: datetime | None = _normalize_datetime(profile.last_review_at)
    if last_review_at is None:
        return None
    return max((now - last_review_at).days, 0)


def _compute_dropout_risk(profile: StudentProfile, *, now: datetime) -> str:
    attendance_pct = float(profile.attendance_pct or 0.0)
    absent_streak = int(profile.absent_streak or 0)
    current_streak_days = int(profile.current_streak_days or 0)
    review_gap_days: int | None = _review_gap_days(profile, now=now)

    if absent_streak >= 5 or attendance_pct < 60.0:
        return "high"
    if absent_streak >= 3 or attendance_pct < 75.0:
        return "medium"
    if review_gap_days is not None and review_gap_days >= 21 and current_streak_days == 0:
        return "medium"
    return "low"


def _compute_academic_risk(profile: StudentProfile, *, now: datetime) -> str:
    score = profile.overall_score_pct
    total_reviews_completed = int(profile.total_reviews_completed or 0)
    review_gap_days: int | None = _review_gap_days(profile, now=now)

    if score is None:
        if review_gap_days is not None and review_gap_days >= 30 and total_reviews_completed == 0:
            return "medium"
        return "low"

    if score < 40.0:
        return "high"
    if score < 50.0 and (review_gap_days is None or review_gap_days >= 14 or total_reviews_completed == 0):
        return "high"
    if score < 60.0:
        return "medium"
    if score < 70.0 and review_gap_days is not None and review_gap_days >= 21:
        return "medium"
    return "low"


def _compute_fee_risk(*, db, profile: StudentProfile, now: datetime) -> tuple[str, int, float]:
    overdue_rows = (
        db.query(FeeInvoice)
        .filter(
            FeeInvoice.student_id == profile.user_id,
            FeeInvoice.status.in_(("pending", "partial", "overdue")),
        )
        .all()
    )
    overdue_rows = [
        invoice
        for invoice in overdue_rows
        if (_normalize_datetime(invoice.due_date) or now) < now
    ]
    overdue_count: int = len(overdue_rows)
    overdue_amount: float = round(
        sum(
            max(float(invoice.amount_due or 0.0) - float(invoice.amount_paid or 0.0), 0.0)
            for invoice in overdue_rows
        ),
        2,
    )

    if overdue_count >= 2 or overdue_amount >= 10000.0:
        return "high", overdue_count, overdue_amount
    if overdue_count >= 1 or overdue_amount > 0.0:
        return "medium", overdue_count, overdue_amount
    return "low", overdue_count, overdue_amount


def compute_student_risks(tenant_id: UUID | None = None) -> int:
    """Scan student profiles and compute actionable risk flags."""
    db = SessionLocal()
    updated_count = 0
    now: datetime = datetime.now(timezone.utc)

    try:
        query = db.query(StudentProfile)
        if tenant_id is not None:
            query = query.filter(StudentProfile.tenant_id == tenant_id)

        profiles = query.all()
        for profile in profiles:
            prior_risks: dict[str, Any | str] = {
                "dropout_risk": profile.dropout_risk or "low",
                "academic_risk": profile.academic_risk or "low",
                "fee_risk": profile.fee_risk or "low",
            }
            dropout_risk: str = _compute_dropout_risk(profile, now=now)
            academic_risk: str = _compute_academic_risk(profile, now=now)
            fee_risk, overdue_count, overdue_amount = _compute_fee_risk(db=db, profile=profile, now=now)

            profile.dropout_risk = dropout_risk
            profile.academic_risk = academic_risk
            profile.fee_risk = fee_risk
            profile.last_computed_at = now

            changed: bool = prior_risks != {
                "dropout_risk": dropout_risk,
                "academic_risk": academic_risk,
                "fee_risk": fee_risk,
            }
            if changed:
                updated_count += 1

            record_business_event(
                "student_risk_recomputed",
                db=db,
                tenant_id=str(profile.tenant_id),
                user_id=str(profile.user_id),
                event_family="risk",
                surface="risk_cron",
                target="student_profile",
                channel="system",
                metadata={
                    "changed": changed,
                    "dropout_risk": dropout_risk,
                    "academic_risk": academic_risk,
                    "fee_risk": fee_risk,
                    "prior_dropout_risk": prior_risks["dropout_risk"],
                    "prior_academic_risk": prior_risks["academic_risk"],
                    "prior_fee_risk": prior_risks["fee_risk"],
                    "attendance_pct": float(profile.attendance_pct or 0.0),
                    "absent_streak": int(profile.absent_streak or 0),
                    "overall_score_pct": profile.overall_score_pct,
                    "overdue_invoice_count": overdue_count,
                    "overdue_amount": overdue_amount,
                },
            )

        db.commit()
        logger.info("Computed risk flags: updated %d student profiles", updated_count)
    except Exception:
        db.rollback()
        logger.exception("Error computing student risks")
    finally:
        db.close()

    return updated_count
