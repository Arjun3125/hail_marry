from __future__ import annotations

from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import MagicMock
from uuid import uuid4

import pytest

from src.domains.mascot.services.elicitation_scheduler import (
    get_next_elicitation,
    record_elicitation_answered,
    record_elicitation_asked,
)
from src.domains.mascot.services.memory_manager import (
    get_days_since_last_interaction,
    increment_interaction_count,
    update_memory,
)
from src.domains.mascot.services.profile_manager import (
    compute_completeness,
    promote_signals_to_profile,
)
from src.domains.mascot.services.prompt_builder import build_mascot_system_prompt
from src.domains.mascot.services.signal_extractor import (
    detect_emotional_state,
    extract_signals_from_text,
)


def test_extract_signals_detects_multiple_types_and_single_learning_style():
    text = "I am dumb in math, show me a diagram, and I want to be a doctor."
    signals = extract_signals_from_text(text)

    signal_types = [sig.signal_type for sig in signals]
    learning_style_signals = [sig for sig in signals if sig.signal_type == "learning_style_hint"]

    assert "negative_self_talk" in signal_types
    assert "career_aspiration" in signal_types
    assert len(learning_style_signals) == 1
    assert learning_style_signals[0].signal_value == "visual"


def test_detect_emotional_state_defaults_to_neutral_and_prefers_dominant_signal():
    assert detect_emotional_state("Can you explain this chapter?") == "neutral"

    text = "I hate this boring chapter and this is useless."
    assert detect_emotional_state(text) == "frustrated"


def test_build_mascot_system_prompt_includes_context_and_session_goals():
    context = SimpleNamespace(
        student_name="Aarav",
        current_streak_days=3,
        overall_score_pct=58.0,
        weakest_subject="Math",
        strongest_subject="Science",
        academic_risk="high",
        dropout_risk="medium",
        learning_style_detected="visual",
        primary_motivation_driver="achievement",
        mascot_tone_setting="encouraging",
        last_summary="Focused on fractions.",
        days_since_last_interaction=7,
        career_aspiration_text="Engineer",
        interest_tags=["cricket", "robotics"],
        topics_due_for_review=["Fractions", "Algebra"],
        exam_readiness_pct=55.0,
        to_prompt_context=lambda: "STUDENT: Aarav | Streak: 3 days",
    )

    prompt = build_mascot_system_prompt(context)

    assert "You are Vidya, a personal study companion for Aarav." in prompt
    assert "WHAT YOU KNOW ABOUT THIS STUDENT:" in prompt
    assert "SESSION GOAL:" in prompt
    assert "high academic risk" in prompt
    assert "Exam readiness is only 55%" in prompt


def test_get_next_elicitation_skips_answered_and_filled_fields():
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value = query
    query.all.return_value = [SimpleNamespace(question_key="learning_style_pref")]
    db.query.return_value = query

    profile = SimpleNamespace(
        learning_style_stated=None,
        peak_study_hour=21,
        career_aspiration_text=None,
        primary_motivation_driver=None,
        help_seeking_style=None,
        interest_tags=None,
        social_orientation=None,
    )

    question = get_next_elicitation(
        db=db,
        student_id=uuid4(),
        tenant_id=uuid4(),
        total_interactions=4,
        profile=profile,
    )
    assert question is not None
    assert question["key"] == "motivation_trigger"


def test_record_elicitation_asked_updates_existing_row():
    existing = SimpleNamespace(skipped_count=1)
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = existing
    db.query.return_value = query

    result = record_elicitation_asked(
        db=db,
        student_id=uuid4(),
        tenant_id=uuid4(),
        question={"key": "learning_style_pref"},
    )

    assert result is existing
    assert existing.skipped_count == 2
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(existing)


def test_record_elicitation_asked_creates_new_row_when_absent():
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value = query
    query.first.return_value = None
    db.query.return_value = query

    result = record_elicitation_asked(
        db=db,
        student_id=uuid4(),
        tenant_id=uuid4(),
        question={"key": "career_aspiration"},
    )

    assert result.question_key == "career_aspiration"
    db.add.assert_called_once()
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(result)


def test_record_elicitation_answered_updates_response_fields():
    db = MagicMock()
    query = MagicMock()
    query.filter.return_value = query
    db.query.return_value = query

    record_elicitation_answered(
        db=db,
        student_id=uuid4(),
        question_key="career_aspiration",
        response_text="I want to become an engineer.",
        response_time_ms=1200,
    )

    query.update.assert_called_once()
    payload = query.update.call_args.args[0]
    assert payload["response_text"] == "I want to become an engineer."
    assert payload["response_time_ms"] == 1200
    assert "answered_at" in payload
    db.commit.assert_called_once()


def test_update_memory_accepts_mapping_and_ignores_none_fields(monkeypatch):
    memory = SimpleNamespace(
        last_summary=None,
        last_emotional_state="neutral",
        preferred_explanation_style=None,
        mascot_tone_setting="encouraging",
        context_snapshot=None,
        updated_at=None,
    )
    db = MagicMock()
    monkeypatch.setattr(
        "src.domains.mascot.services.memory_manager.get_or_create_memory",
        lambda _db, _student_id, _tenant_id: memory,
    )

    result = update_memory(
        db=db,
        student_id=uuid4(),
        tenant_id=uuid4(),
        update={
            "last_summary": "Session focused on photosynthesis.",
            "mascot_tone_setting": "playful",
            "last_emotional_state": None,
        },
    )

    assert result is memory
    assert memory.last_summary == "Session focused on photosynthesis."
    assert memory.mascot_tone_setting == "playful"
    assert memory.last_emotional_state == "neutral"
    assert isinstance(memory.updated_at, datetime)
    db.commit.assert_called_once()
    db.refresh.assert_called_once_with(memory)


def test_increment_interaction_count_updates_tracking_fields(monkeypatch):
    memory = SimpleNamespace(total_interactions=2, last_interaction_at=None, updated_at=None)
    db = MagicMock()
    monkeypatch.setattr(
        "src.domains.mascot.services.memory_manager.get_or_create_memory",
        lambda _db, _student_id, _tenant_id: memory,
    )

    increment_interaction_count(db, uuid4(), uuid4())

    assert memory.total_interactions == 3
    assert isinstance(memory.last_interaction_at, datetime)
    assert isinstance(memory.updated_at, datetime)
    db.commit.assert_called_once()


def test_get_days_since_last_interaction_handles_missing_and_existing_records():
    student_id = uuid4()
    tenant_id = uuid4()

    db_missing = MagicMock()
    query_missing = MagicMock()
    query_missing.filter.return_value = query_missing
    query_missing.first.return_value = None
    db_missing.query.return_value = query_missing
    assert get_days_since_last_interaction(db_missing, student_id, tenant_id) is None

    db_present = MagicMock()
    query_present = MagicMock()
    query_present.filter.return_value = query_present
    query_present.first.return_value = SimpleNamespace(
        last_interaction_at=datetime.now(timezone.utc) - timedelta(days=4, hours=1)
    )
    db_present.query.return_value = query_present
    assert get_days_since_last_interaction(db_present, student_id, tenant_id) == 4


def test_compute_completeness_counts_non_null_profile_fields():
    profile = SimpleNamespace(
        learning_style_detected="visual",
        learning_style_stated=None,
        reasoning_type=None,
        primary_motivation_driver="achievement",
        stress_threshold=None,
        self_esteem_score=None,
        resilience_score=0.8,
        humor_index=None,
        social_orientation=None,
        locus_of_control=None,
        mindset_orientation=None,
        peak_study_hour=None,
        help_seeking_style=None,
        career_aspiration_text=None,
        interest_tags=None,
    )
    assert compute_completeness(profile) == pytest.approx(3 / 15.0)


def test_promote_signals_to_profile_applies_signal_value_and_increments_version(monkeypatch):
    student_id = uuid4()
    tenant_id = uuid4()
    profile = SimpleNamespace(
        career_aspiration_text=None,
        resilience_score=None,
        profile_completeness_score=0.0,
        profile_version=1,
    )

    monkeypatch.setattr(
        "src.domains.mascot.services.profile_manager.get_or_create_profile",
        lambda _db, _student_id, _tenant_id: profile,
    )
    monkeypatch.setattr(
        "src.domains.mascot.services.profile_manager.compute_completeness",
        lambda _profile: 0.4,
    )

    aggregated_query = MagicMock()
    aggregated_query.filter.return_value = aggregated_query
    aggregated_query.group_by.return_value = aggregated_query
    aggregated_query.having.return_value = aggregated_query
    aggregated_query.all.return_value = [
        ("career_aspiration", "doctor", 2, 0.9),
        ("resilience", "detected", 2, 0.75),
    ]

    update_query_1 = MagicMock()
    update_query_1.filter.return_value = update_query_1
    update_query_2 = MagicMock()
    update_query_2.filter.return_value = update_query_2

    db = MagicMock()
    db.query.side_effect = [aggregated_query, update_query_1, update_query_2]

    promoted_count = promote_signals_to_profile(db, student_id, tenant_id)

    assert promoted_count == 2
    assert profile.career_aspiration_text == "doctor"
    assert profile.resilience_score == pytest.approx(0.55)
    assert profile.profile_completeness_score == 0.4
    assert profile.profile_version == 2
    assert update_query_1.update.called
    assert update_query_2.update.called
    db.commit.assert_called_once()
