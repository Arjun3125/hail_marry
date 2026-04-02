"""Learner profile inference from existing study signals."""
from __future__ import annotations

import re
from collections import Counter
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.domains.academic.models.core import Subject
from src.domains.academic.models.performance import SubjectPerformance
from src.domains.platform.models.ai import AIQuery
from src.domains.platform.models.generated_content import GeneratedContent
from src.domains.platform.models.learner_profile import LearnerProfile
from src.domains.platform.models.study_session import StudySession
from src.domains.platform.models.topic_mastery import TopicMastery

_BRIEF_HINTS = ("brief", "short", "quick", "summary", "summarize", "bullet", "points")
_DETAILED_HINTS = ("detailed", "detail", "deep", "in depth", "thorough", "elaborate", "step by step")
_ADVANCED_MODES = {"debate", "essay_review", "concept_map"}
_GUIDED_MODES = {"study_guide", "socratic", "qa"}


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


def _coerce_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _profile_to_dict(profile: LearnerProfile | None) -> dict[str, Any] | None:
    if profile is None:
        return None
    return {
        "preferred_language": profile.preferred_language,
        "inferred_expertise_level": profile.inferred_expertise_level,
        "preferred_response_length": profile.preferred_response_length,
        "primary_subjects": list(profile.primary_subjects or []),
        "engagement_score": round(float(profile.engagement_score or 0.0), 1),
        "consistency_score": round(float(profile.consistency_score or 0.0), 1),
        "signal_summary": dict(profile.signal_summary or {}),
        "last_recomputed_at": profile.last_recomputed_at.isoformat() if profile.last_recomputed_at else None,
    }


def _detect_language(queries: list[AIQuery]) -> str:
    if not queries:
        return "english"

    has_latin = False
    has_devanagari = False
    marathi_markers = {"काय", "आहे", "नाही", "मला", "समजाव", "सांग"}
    hindi_markers = {"क्या", "है", "नहीं", "मुझे", "समझाओ", "बताओ"}
    marker_counts = Counter()

    for query in queries:
        text = (query.query_text or "").strip()
        if re.search(r"[A-Za-z]", text):
            has_latin = True
        if re.search(r"[\u0900-\u097F]", text):
            has_devanagari = True
            tokens = set(text.split())
            if tokens & marathi_markers:
                marker_counts["marathi"] += 1
            if tokens & hindi_markers:
                marker_counts["hindi"] += 1

    if has_latin and has_devanagari:
        return "mixed"
    if marker_counts["marathi"] > marker_counts["hindi"]:
        return "marathi"
    if has_devanagari:
        return "hindi"
    return "english"


def _infer_response_length(queries: list[AIQuery]) -> str:
    brief_hits = 0
    detailed_hits = 0
    for query in queries:
        text = (query.query_text or "").lower()
        if any(hint in text for hint in _BRIEF_HINTS):
            brief_hits += 1
        if any(hint in text for hint in _DETAILED_HINTS):
            detailed_hits += 1

    if detailed_hits > brief_hits and detailed_hits >= 1:
        return "detailed"
    if brief_hits > detailed_hits and brief_hits >= 1:
        return "brief"
    return "default"


def _infer_primary_subjects(db: Session, tenant_id: UUID, user_id: UUID) -> list[str]:
    try:
        query = (
            db.query(Subject.name, SubjectPerformance.average_score)
            .join(Subject, Subject.id == SubjectPerformance.subject_id)
            .filter(
                SubjectPerformance.tenant_id == tenant_id,
                SubjectPerformance.student_id == user_id,
                Subject.tenant_id == tenant_id,
            )
        )
    except TypeError:
        return []
    if hasattr(query, "order_by"):
        query = query.order_by(SubjectPerformance.average_score.asc().nullslast(), Subject.name.asc())
    if hasattr(query, "limit"):
        query = query.limit(3)
    rows = query.all() if hasattr(query, "all") else []
    return [row[0] for row in rows if row[0]]


def _infer_expertise_level(
    *,
    average_subject_score: float | None,
    average_mastery_score: float | None,
    queries: list[AIQuery],
    generated_types: list[str],
) -> str:
    advanced_signals = sum(1 for query in queries if query.mode in _ADVANCED_MODES)
    guided_signals = sum(1 for query in queries if query.mode in _GUIDED_MODES)
    advanced_signals += sum(1 for tool in generated_types if tool in {"concept_map", "flowchart"})
    low_score = average_subject_score is not None and average_subject_score < 55
    low_mastery = average_mastery_score is not None and average_mastery_score < 45
    high_score = average_subject_score is not None and average_subject_score >= 75
    high_mastery = average_mastery_score is not None and average_mastery_score >= 75

    if (low_score or low_mastery) and guided_signals >= advanced_signals:
        return "simple"
    if high_score or high_mastery or advanced_signals >= 2:
        return "advanced"
    return "standard"


def recompute_learner_profile(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
) -> LearnerProfile:
    now = _utcnow()
    since = now - timedelta(days=90)

    queries_query = (
        db.query(AIQuery)
        .filter(
            AIQuery.tenant_id == tenant_id,
            AIQuery.user_id == user_id,
            AIQuery.deleted_at.is_(None),
            AIQuery.created_at >= since,
        )
    )
    if hasattr(queries_query, "order_by"):
        queries_query = queries_query.order_by(AIQuery.created_at.desc())
    if hasattr(queries_query, "limit"):
        queries_query = queries_query.limit(50)
    queries = queries_query.all() if hasattr(queries_query, "all") else []

    sessions_query = (
        db.query(StudySession)
        .filter(
            StudySession.tenant_id == tenant_id,
            StudySession.user_id == user_id,
            StudySession.last_active_at >= since,
        )
    )
    sessions = sessions_query.all() if hasattr(sessions_query, "all") else []

    generated_query = (
        db.query(GeneratedContent.type)
        .filter(
            GeneratedContent.tenant_id == tenant_id,
            GeneratedContent.user_id == user_id,
            GeneratedContent.is_archived.is_(False),
        )
    )
    if hasattr(generated_query, "order_by"):
        generated_query = generated_query.order_by(GeneratedContent.created_at.desc())
    if hasattr(generated_query, "limit"):
        generated_query = generated_query.limit(50)
    generated = generated_query.all() if hasattr(generated_query, "all") else []

    subject_average_query = (
        db.query(func.avg(SubjectPerformance.average_score))
        .filter(
            SubjectPerformance.tenant_id == tenant_id,
            SubjectPerformance.student_id == user_id,
            SubjectPerformance.average_score.isnot(None),
        )
    )
    subject_average = subject_average_query.scalar() if hasattr(subject_average_query, "scalar") else None

    mastery_average_query = (
        db.query(func.avg(TopicMastery.mastery_score))
        .filter(
            TopicMastery.tenant_id == tenant_id,
            TopicMastery.user_id == user_id,
            TopicMastery.concept == "core",
        )
    )
    mastery_average = mastery_average_query.scalar() if hasattr(mastery_average_query, "scalar") else None

    total_study_seconds = sum(int(session.duration_seconds or 0) for session in sessions)
    query_days = {query.created_at.date() for query in queries if query.created_at}
    session_days = {session.last_active_at.date() for session in sessions if session.last_active_at}
    active_days = len(query_days | session_days)

    generated_types = [row[0] for row in generated if row[0]]
    preferred_language = _detect_language(queries)
    preferred_response_length = _infer_response_length(queries)
    primary_subjects = _infer_primary_subjects(db, tenant_id, user_id)
    engagement_score = min(100.0, len(queries) * 4.0 + len(sessions) * 6.0 + len(generated_types) * 3.0 + (total_study_seconds / 3600.0) * 12.0)
    consistency_score = min(100.0, active_days / 14.0 * 100.0)
    inferred_expertise_level = _infer_expertise_level(
        average_subject_score=float(subject_average) if subject_average is not None else None,
        average_mastery_score=float(mastery_average) if mastery_average is not None else None,
        queries=queries,
        generated_types=generated_types,
    )

    profile = (
        db.query(LearnerProfile)
        .filter(
            LearnerProfile.tenant_id == tenant_id,
            LearnerProfile.user_id == user_id,
        )
        .first()
    )
    if profile is None:
        profile = LearnerProfile(tenant_id=tenant_id, user_id=user_id)
        db.add(profile)

    profile.preferred_language = preferred_language
    profile.preferred_response_length = preferred_response_length
    profile.inferred_expertise_level = inferred_expertise_level
    profile.primary_subjects = primary_subjects
    profile.engagement_score = round(engagement_score, 1)
    profile.consistency_score = round(consistency_score, 1)
    profile.signal_summary = {
        "recent_query_count": len(queries),
        "study_session_count": len(sessions),
        "generated_content_count": len(generated_types),
        "average_subject_score": round(float(subject_average), 1) if subject_average is not None else None,
        "average_mastery_score": round(float(mastery_average), 1) if mastery_average is not None else None,
        "active_days_14d": active_days,
        "total_study_seconds_90d": total_study_seconds,
    }
    profile.last_recomputed_at = now
    profile.updated_at = now
    if hasattr(db, "flush"):
        db.flush()
    return profile


def get_or_recompute_learner_profile(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    max_age_hours: int = 24,
) -> LearnerProfile:
    profile = (
        db.query(LearnerProfile)
        .filter(
            LearnerProfile.tenant_id == tenant_id,
            LearnerProfile.user_id == user_id,
        )
        .first()
    )
    if profile and profile.last_recomputed_at:
        last_recomputed_at = _coerce_utc(profile.last_recomputed_at)
        age = _utcnow() - last_recomputed_at if last_recomputed_at else timedelta.max
        if age <= timedelta(hours=max_age_hours):
            return profile
    return recompute_learner_profile(db, tenant_id=tenant_id, user_id=user_id)


def get_learner_profile_dict(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    force_recompute: bool = False,
) -> dict[str, Any]:
    profile = recompute_learner_profile(db, tenant_id=tenant_id, user_id=user_id) if force_recompute else get_or_recompute_learner_profile(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
    )
    return _profile_to_dict(profile) or {}
