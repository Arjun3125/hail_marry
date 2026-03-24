"""Smart weakness alert generation based on subject performance thresholds."""
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy.orm import Session

from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.models.core import Subject


from constants import WEAK_TOPIC_THRESHOLD_PCT as WEAK_THRESHOLD_PCT


def generate_weakness_alerts(
    db: Session,
    *,
    user_id: UUID,
    tenant_id: UUID,
) -> list[dict[str, Any]]:
    """Scan subject performances and generate alerts for subjects below threshold."""
    performances = db.query(SubjectPerformance).filter(
        SubjectPerformance.student_id == user_id,
        SubjectPerformance.tenant_id == tenant_id,
    ).all()

    alerts: list[dict[str, Any]] = []
    for perf in performances:
        if perf.average_score is None:
            continue
        avg = float(perf.average_score)
        if avg >= WEAK_THRESHOLD_PCT:
            continue

        subject = db.query(Subject).filter(Subject.id == perf.subject_id).first()
        subject_name = subject.name if subject else "Unknown Subject"

        severity = "critical" if avg < 40 else "warning"
        alerts.append({
            "subject_id": str(perf.subject_id),
            "subject_name": subject_name,
            "average_score": round(avg, 1),
            "threshold": WEAK_THRESHOLD_PCT,
            "severity": severity,
            "message": f"Your {subject_name} average is {round(avg)}% — below the {WEAK_THRESHOLD_PCT}% target.",
            "recommendation": f"Try reviewing {subject_name} flashcards using spaced repetition to strengthen weak areas.",
            "action": {
                "type": "create_review",
                "label": f"Start {subject_name} Review",
                "topic": subject_name,
                "subject_id": str(perf.subject_id),
            },
        })

    return sorted(alerts, key=lambda a: a["average_score"])
