"""Lightweight concept/topic mastery tracking and adaptive quiz planning."""
from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import or_
from sqlalchemy.orm import Session

from src.domains.academic.models.core import Subject
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.topic_mastery import TopicMastery

_STOPWORDS = {
    "a", "an", "and", "are", "as", "at", "be", "by", "for", "from", "how", "in", "into",
    "is", "it", "of", "on", "or", "the", "to", "using", "with", "what", "why", "does",
    "do", "about", "your", "you", "make", "create", "generate", "topic", "chapter",
}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def normalize_topic_name(topic: str) -> str:
    normalized = " ".join((topic or "").strip().split())
    return normalized[:255]


def extract_concepts(topic: str, *, limit: int = 5) -> list[str]:
    text = normalize_topic_name(topic)
    if not text:
        return []

    lowered = re.sub(r"[^a-zA-Z0-9\s-]", " ", text.lower())
    pieces = re.split(r"[\s,/:-]+", lowered)
    concepts: list[str] = []
    seen: set[str] = set()
    for piece in pieces:
        token = piece.strip()
        if len(token) < 4 or token in _STOPWORDS or token.isdigit():
            continue
        if token not in seen:
            seen.add(token)
            concepts.append(token)
        if len(concepts) >= limit:
            break
    return concepts


def _clip(value: float, *, low: float, high: float) -> float:
    return max(low, min(high, value))


def infer_topic_from_query(query: str) -> str:
    text = normalize_topic_name(query)
    if not text:
        return ""

    lowered = text.lower()
    prefixes = (
        "explain ",
        "what is ",
        "what are ",
        "tell me about ",
        "help me understand ",
        "summarize ",
        "summary of ",
        "create quiz for ",
        "generate quiz for ",
        "make quiz for ",
        "quiz on ",
        "quiz for ",
        "study guide for ",
        "flashcards for ",
        "why is ",
        "how does ",
        "how do ",
    )
    for prefix in prefixes:
        if lowered.startswith(prefix):
            text = text[len(prefix):].strip()
            break

    text = re.sub(r"[?.!]+$", "", text).strip()
    if text and text == text.lower():
        text = " ".join(part.capitalize() for part in text.split())
    if len(text) > 255:
        text = text[:255].strip()
    return normalize_topic_name(text)


def _subject_baseline(db: Session, tenant_id: UUID, user_id: UUID, subject_id: UUID | None) -> tuple[float, float]:
    if not subject_id:
        return 55.0, 0.18

    performance = (
        db.query(SubjectPerformance)
        .filter(
            SubjectPerformance.tenant_id == tenant_id,
            SubjectPerformance.student_id == user_id,
            SubjectPerformance.subject_id == subject_id,
        )
        .first()
    )
    if not performance or performance.average_score is None:
        return 55.0, 0.22

    average = float(performance.average_score)
    confidence = 0.45 if average < 60 else 0.35
    return _clip(average, low=20.0, high=92.0), confidence


def _get_or_create_mastery(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    subject_id: UUID | None,
    topic: str,
    concept: str,
) -> TopicMastery:
    record = (
        db.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == user_id,
            TopicMastery.topic == topic,
            TopicMastery.concept == concept,
        )
        .first()
    )
    if record:
        return record

    baseline_score, baseline_confidence = _subject_baseline(db, tenant_id, user_id, subject_id)
    record = TopicMastery(
        tenant_id=tenant_id,
        user_id=user_id,
        subject_id=subject_id,
        topic=topic,
        concept=concept,
        mastery_score=baseline_score,
        confidence_score=baseline_confidence,
    )
    db.add(record)
    if hasattr(db, "flush"):
        db.flush()
    return record


def ensure_topic_mastery_seed(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    subject_id: UUID | None = None,
    evidence_type: str = "topic_seen",
) -> list[TopicMastery]:
    normalized_topic = normalize_topic_name(topic)
    if not normalized_topic:
        return []

    concepts = ["core", *extract_concepts(normalized_topic)]
    records: list[TopicMastery] = []
    for concept in concepts:
        record = _get_or_create_mastery(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            subject_id=subject_id,
            topic=normalized_topic,
            concept=concept,
        )
        record.last_evidence_type = record.last_evidence_type or evidence_type
        record.updated_at = _utcnow()
        records.append(record)
    return records


def record_study_tool_activity(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    subject_id: UUID | None = None,
    tool: str,
) -> list[TopicMastery]:
    records = ensure_topic_mastery_seed(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=topic,
        subject_id=subject_id,
        evidence_type=f"{tool}_requested",
    )
    now = _utcnow()
    for record in records:
        record.evidence_count = int(record.evidence_count or 0) + 1
        record.last_evidence_type = f"{tool}_requested"
        record.last_evidence_score = None
        record.last_evidence_at = now
        record.confidence_score = _clip(record.confidence_score + 0.03, low=0.05, high=0.95)
        record.updated_at = now
    return records


def record_review_completion(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    rating: int,
    next_review_at: datetime | None,
    subject_id: UUID | None = None,
) -> list[TopicMastery]:
    records = ensure_topic_mastery_seed(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=topic,
        subject_id=subject_id,
        evidence_type="review_completed",
    )
    score_delta_map = {1: -18.0, 2: -8.0, 3: 4.0, 4: 10.0, 5: 15.0}
    confidence_delta_map = {1: 0.07, 2: 0.08, 3: 0.10, 4: 0.12, 5: 0.14}
    score_delta = score_delta_map.get(rating, 0.0)
    confidence_delta = confidence_delta_map.get(rating, 0.08)
    now = _utcnow()

    for record in records:
        record.mastery_score = _clip(record.mastery_score + score_delta, low=0.0, high=100.0)
        record.confidence_score = _clip(record.confidence_score + confidence_delta, low=0.05, high=0.98)
        record.evidence_count += 1
        record.last_evidence_type = "review_completed"
        record.last_evidence_score = float(rating)
        record.last_evidence_at = now
        record.review_due_at = next_review_at
        record.updated_at = now
    return records


def record_quiz_completion(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    total_questions: int,
    correct_answers: int,
    subject_id: UUID | None = None,
    difficulty_breakdown: dict[str, int] | None = None,
) -> list[TopicMastery]:
    if total_questions <= 0:
        return []

    records = ensure_topic_mastery_seed(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=topic,
        subject_id=subject_id,
        evidence_type="quiz_completed",
    )
    now = _utcnow()
    accuracy = _clip(float(correct_answers) / float(total_questions), low=0.0, high=1.0)
    difficulty_breakdown = difficulty_breakdown or {}
    weighted_total = (
        difficulty_breakdown.get("easy", 0) * 0.9
        + difficulty_breakdown.get("medium", 0) * 1.0
        + difficulty_breakdown.get("hard", 0) * 1.15
    )
    question_weight = weighted_total / total_questions if weighted_total > 0 else 1.0
    score_delta = (accuracy - 0.6) * 42.0 * question_weight
    confidence_delta = 0.08 + min(total_questions, 10) * 0.012
    review_days = 2 if accuracy < 0.5 else 5 if accuracy < 0.75 else 9

    for record in records:
        record.mastery_score = _clip(record.mastery_score + score_delta, low=0.0, high=100.0)
        record.confidence_score = _clip(record.confidence_score + confidence_delta, low=0.05, high=0.99)
        record.evidence_count += 1
        record.last_evidence_type = "quiz_completed"
        record.last_evidence_score = round(accuracy * 100.0, 1)
        record.last_evidence_at = now
        record.review_due_at = now + timedelta(days=review_days)
        record.updated_at = now
    return records


def count_recent_confusion_queries(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    since_days: int = 7,
) -> int:
    normalized_topic = infer_topic_from_query(topic)
    if not normalized_topic:
        return 0

    since = _utcnow() - timedelta(days=since_days)
    escaped_topic = normalized_topic.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    candidate_patterns = [f"%{escaped_topic}%"]
    for prefix in (
        "explain ",
        "what is ",
        "what are ",
        "tell me about ",
        "help me understand ",
        "summarize ",
        "summary of ",
        "create quiz for ",
        "generate quiz for ",
        "make quiz for ",
        "quiz on ",
        "quiz for ",
        "study guide for ",
        "flashcards for ",
        "why is ",
        "how does ",
        "how do ",
    ):
        candidate_patterns.append(f"{prefix}{escaped_topic}%")
    query = (
        db.query(AIQuery)
        .filter(
            AIQuery.tenant_id == tenant_id,
            AIQuery.user_id == user_id,
            AIQuery.deleted_at.is_(None),
            AIQuery.created_at >= since,
            AIQuery.mode.in_(("qa", "study_guide", "socratic")),
            or_(*(AIQuery.query_text.ilike(pattern, escape="\\") for pattern in candidate_patterns)),
        )
    )
    queries = query.all() if hasattr(query, "all") else []
    return sum(1 for query in queries if infer_topic_from_query(query.query_text).lower() == normalized_topic.lower())


def record_ai_confusion_pattern(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    query: str,
    repeated_count: int,
    subject_id: UUID | None = None,
) -> list[TopicMastery]:
    topic = infer_topic_from_query(query)
    if not topic or repeated_count < 2:
        return []

    records = ensure_topic_mastery_seed(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=topic,
        subject_id=subject_id,
        evidence_type="ai_confusion_pattern",
    )
    now = _utcnow()
    penalty = min(12.0, 3.5 * (repeated_count - 1))
    confidence_delta = 0.05 + min(repeated_count, 4) * 0.02

    for record in records:
        record.mastery_score = _clip(record.mastery_score - penalty, low=0.0, high=100.0)
        record.confidence_score = _clip(record.confidence_score + confidence_delta, low=0.05, high=0.99)
        record.evidence_count += 1
        record.last_evidence_type = "ai_confusion_pattern"
        record.last_evidence_score = float(repeated_count)
        record.last_evidence_at = now
        record.review_due_at = now + timedelta(days=2)
        record.updated_at = now
    return records


def get_topic_mastery_snapshot(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    subject_id: UUID | None = None,
) -> dict[str, Any]:
    normalized_topic = normalize_topic_name(topic)
    if not normalized_topic:
        baseline_score, baseline_confidence = _subject_baseline(db, tenant_id, user_id, subject_id)
        return {
            "topic": "",
            "mastery_score": baseline_score,
            "confidence_score": baseline_confidence,
            "concepts": [],
        }

    query = (
        db.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == user_id,
            TopicMastery.topic == normalized_topic,
        )
    )
    records = query.all() if hasattr(query, "all") else []
    if not records:
        baseline_score, baseline_confidence = _subject_baseline(db, tenant_id, user_id, subject_id)
        extracted_concepts = extract_concepts(normalized_topic)
        return {
            "topic": normalized_topic,
            "mastery_score": baseline_score,
            "confidence_score": baseline_confidence,
            "concepts": [
                {
                    "concept": concept,
                    "mastery_score": round(float(baseline_score), 1),
                    "confidence_score": round(float(baseline_confidence), 2),
                }
                for concept in extracted_concepts
            ],
        }

    topic_row = next((row for row in records if row.concept == "core"), records[0])
    concept_rows = [row for row in records if row.concept != "core"]
    return {
        "topic": normalized_topic,
        "mastery_score": round(float(topic_row.mastery_score), 1),
        "confidence_score": round(float(topic_row.confidence_score), 2),
        "concepts": [
            {
                "concept": row.concept,
                "mastery_score": round(float(row.mastery_score), 1),
                "confidence_score": round(float(row.confidence_score), 2),
            }
            for row in concept_rows[:5]
        ],
    }


def build_adaptive_quiz_profile(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    topic: str,
    subject_id: UUID | None = None,
) -> dict[str, Any]:
    snapshot = get_topic_mastery_snapshot(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        topic=topic,
        subject_id=subject_id,
    )
    mastery_score = float(snapshot["mastery_score"])
    confidence_score = float(snapshot["confidence_score"])

    if mastery_score < 45 or confidence_score < 0.35:
        difficulty_mix = {"easy": 3, "medium": 2, "hard": 0}
        label = "support"
        rationale = "Focus on foundational recall and scaffolded practice before harder inference."
    elif mastery_score >= 75 and confidence_score >= 0.65:
        difficulty_mix = {"easy": 1, "medium": 2, "hard": 2}
        label = "challenge"
        rationale = "Performance suggests the learner can handle deeper application and synthesis questions."
    else:
        difficulty_mix = {"easy": 2, "medium": 2, "hard": 1}
        label = "balanced"
        rationale = "Blend reinforcement with one stretch question to improve retention and transfer."

    focus_concepts = [item["concept"] for item in snapshot["concepts"][:3]]
    return {
        "label": label,
        "difficulty_mix": difficulty_mix,
        "mastery_score": mastery_score,
        "confidence_score": confidence_score,
        "focus_concepts": focus_concepts,
        "prompt_suffix": (
            "Adaptive quiz profile:\n"
            f"- learner_state: {label}\n"
            f"- mastery_score: {mastery_score}\n"
            f"- confidence_score: {confidence_score}\n"
            f"- required difficulty mix: {difficulty_mix['easy']} easy, {difficulty_mix['medium']} medium, {difficulty_mix['hard']} hard\n"
            f"- focus concepts: {', '.join(focus_concepts) if focus_concepts else normalize_topic_name(topic)}\n"
            f"- rationale: {rationale}\n"
            "Include a required 'difficulty' field on every question using only: easy, medium, hard."
        ),
    }


def build_profile_aware_recommendations(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    active_tool: str | None = None,
    notebook_id: UUID | None = None,
    current_surface: str | None = None,
    current_topic: str | None = None,
    current_query: str | None = None,
    learner_profile: dict[str, Any] | None = None,
    limit: int = 4,
) -> list[dict[str, Any]]:
    suggestions: list[dict[str, Any]] = []
    primary_subjects = list((learner_profile or {}).get("primary_subjects") or [])
    preferred_length = str((learner_profile or {}).get("preferred_response_length") or "default")
    expertise = str((learner_profile or {}).get("inferred_expertise_level") or "standard")
    topic_label = normalize_topic_name(current_topic or "")
    surface_label = (current_surface or "").strip().lower()

    if expertise == "simple":
        focus_label = topic_label or (primary_subjects[0] if primary_subjects else "my current topic")
        target_tool = "study_guide" if active_tool not in {"study_guide", "socratic"} else "flashcards"
        suggestions.append(
            {
                "id": f"profile-support-{focus_label.lower().replace(' ', '-')[:40]}",
                "label": f"Get a guided explanation for {focus_label}",
                "description": "Your recent signals suggest step-by-step reinforcement will work better than jumping straight into harder practice.",
                "prompt": f"Explain {focus_label} in simple step-by-step language, then give me one small practice question.",
                "target_tool": target_tool,
                "reason": "learner_profile",
                "priority": "high",
            }
        )
    elif expertise == "advanced":
        focus_label = topic_label or (primary_subjects[0] if primary_subjects else "my current topic")
        target_tool = "debate" if active_tool not in {"debate", "essay_review"} else "concept_map"
        suggestions.append(
            {
                "id": f"profile-advanced-{focus_label.lower().replace(' ', '-')[:40]}",
                "label": f"Push deeper on {focus_label}",
                "description": "Recent work suggests you are ready for a higher-order reasoning task instead of another basic recap.",
                "prompt": f"Challenge me on {focus_label} with a {target_tool.replace('_', ' ')} task that tests deeper understanding.",
                "target_tool": target_tool,
                "reason": "learner_profile",
                "priority": "medium",
            }
        )

    if surface_label == "ai_studio" and preferred_length == "brief":
        focus_label = topic_label or (primary_subjects[0] if primary_subjects else "this topic")
        suggestions.append(
            {
                "id": f"profile-brief-{focus_label.lower().replace(' ', '-')[:40]}",
                "label": f"Quick revision on {focus_label}",
                "description": "You usually prefer concise outputs, so start with a fast recap before expanding.",
                "prompt": f"Give me a brief revision summary for {focus_label} with only the most important points.",
                "target_tool": "flashcards" if active_tool != "flashcards" else "qa",
                "reason": "learner_profile",
                "priority": "medium",
            }
        )

    weak_subjects = (
        db.query(SubjectPerformance)
        .filter(
            SubjectPerformance.tenant_id == tenant_id,
            SubjectPerformance.student_id == user_id,
            SubjectPerformance.average_score.isnot(None),
            SubjectPerformance.average_score < 60,
        )
        .order_by(SubjectPerformance.average_score.asc())
        .limit(3)
        .all()
    )
    for performance in weak_subjects:
        subject_label = "this weak topic"
        subject = (
            db.query(Subject)
            .filter(Subject.id == performance.subject_id, Subject.tenant_id == tenant_id)
            .first()
        )
        if subject and subject.name:
            subject_label = subject.name
        target_tool = "quiz" if active_tool != "quiz" else "flashcards"
        suggestions.append(
            {
                "id": f"weak-{performance.subject_id}",
                "label": f"Practice weak topic: {subject_label}",
                "description": f"Recent performance is below target, so {target_tool} is the best next step.",
                "prompt": (
                    f"Create a {target_tool.replace('_', ' ')} for {subject_label} "
                    "focused on the fundamentals I keep missing."
                ),
                "target_tool": target_tool,
                "reason": "weak_topic",
                "priority": "high",
            }
        )
    existing_weak_topics = {
        item["label"].replace("Practice weak topic: ", "", 1).strip().lower()
        for item in suggestions
        if item.get("reason") == "weak_topic"
    }

    if topic_label:
        snapshot = get_topic_mastery_snapshot(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            topic=topic_label,
        )
        if float(snapshot["mastery_score"]) < 55:
            target_tool = "quiz" if active_tool != "quiz" else "flashcards"
            suggestions.append(
                {
                    "id": f"mastery-gap-{topic_label.lower().replace(' ', '-')[:40]}",
                    "label": f"Rebuild {topic_label}",
                    "description": "Current mastery is still shaky, so a short reinforcement loop is the safest next step.",
                    "prompt": f"Create a {target_tool.replace('_', ' ')} for {topic_label} that starts from the basics and checks understanding gradually.",
                    "target_tool": target_tool,
                    "reason": "mastery_gap",
                    "priority": "high",
                }
            )

    mastery_rows = (
        db.query(TopicMastery)
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == user_id,
            TopicMastery.concept == "core",
        )
        .order_by(TopicMastery.mastery_score.asc(), TopicMastery.updated_at.desc())
        .limit(3)
        .all()
    )
    for row in mastery_rows:
        if row.topic.lower() in existing_weak_topics:
            continue
        target_tool = "flashcards" if active_tool != "flashcards" else "quiz"
        suggestions.append(
            {
                "id": f"mastery-{row.id}",
                "label": f"Review due topic: {row.topic}",
                "description": "Mastery confidence is still forming here. A focused review is the fastest win.",
                "prompt": f"Help me review {row.topic} with {target_tool.replace('_', ' ')} and a short explanation.",
                "target_tool": target_tool,
                "reason": "mastery_gap",
                "priority": "medium",
            }
        )

    if notebook_id:
        suggestions.append(
            {
                "id": f"notebook-{notebook_id}",
                "label": "Continue in mascot workspace",
                "description": "Use the mascot to route this notebook into the right study tool without choosing manually.",
                "prompt": "Open the best next study workflow for my current notebook.",
                "target_tool": "mascot",
                "reason": "notebook_continuity",
                "priority": "medium",
            }
        )

    if not suggestions:
        default_tool = "quiz" if active_tool != "quiz" else "flashcards"
        suggestions.append(
            {
                "id": "default-ai-path",
                "label": "Start with a focused practice step",
                "description": "The fastest way to learn is to ask one focused question, then turn it into practice.",
                "prompt": f"Create a {default_tool} on the topic I want to study next.",
                "target_tool": default_tool,
                "reason": "default",
                "priority": "low",
            }
        )

    priority_rank = {"high": 0, "medium": 1, "low": 2}
    suggestions.sort(key=lambda item: (priority_rank.get(item.get("priority", "medium"), 1), item.get("label", "")))

    unique: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for item in suggestions:
        item_id = str(item.get("id"))
        if item_id in seen_ids:
            continue
        seen_ids.add(item_id)
        unique.append(item)
        if len(unique) >= limit:
            break
    return unique
