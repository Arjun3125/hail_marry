"""Smart weakness alert generation based on subject performance thresholds."""
from __future__ import annotations

from typing import Any, List
from uuid import UUID

from sqlalchemy import Column
from sqlalchemy.orm import Session

from src.domains.academic.models.performance import SubjectPerformance
from src.domains.academic.models.core import Subject
from src.domains.platform.models.topic_mastery import TopicMastery


from constants import WEAK_TOPIC_THRESHOLD_PCT as WEAK_THRESHOLD_PCT


def generate_weakness_alerts(
    db: Session,
    *,
    user_id: UUID,
    tenant_id: UUID,
) -> list[dict[str, Any]]:
    """Scan subject performances and generate alerts for subjects below threshold."""
    performances: List[SubjectPerformance] = db.query(SubjectPerformance).filter(
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

        subject: Subject | None = db.query(Subject).filter(Subject.id == perf.subject_id).first()
        subject_name: Column[str] | str = subject.name if subject else "Unknown Subject"

        severity: str = "critical" if avg < 40 else "warning"
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

    # Scan Topic Mastery for granular conceptual gaps
    mastery_risks: List[TopicMastery] = db.query(TopicMastery).filter(
        TopicMastery.user_id == user_id,
        TopicMastery.tenant_id == tenant_id,
        TopicMastery.concept == "core",
        TopicMastery.mastery_score < 45,
        TopicMastery.confidence_score > 0.2, # Only alert on topics we are somewhat sure about
    ).all()

    for risk in mastery_risks:
        alerts.append({
            "subject_id": str(risk.subject_id) if risk.subject_id else None,
            "topic": risk.topic,
            "mastery_score": round(risk.mastery_score, 1),
            "severity": "critical" if risk.mastery_score < 35 else "warning",
            "type": "mastery_gap",
            "message": f"Struggling with {risk.topic}: Your mastery score is {round(risk.mastery_score)}%.",
            "recommendation": f"Focus on {risk.topic} in the AI Studio to rebuild confidence.",
            "action": {
                "type": "open_ai_studio",
                "label": f"Study {risk.topic}",
                "topic": risk.topic,
                "subject_id": str(risk.subject_id) if risk.subject_id else None,
            },
        })

    return sorted(alerts, key=lambda a: a.get("average_score", a.get("mastery_score", 100)))
