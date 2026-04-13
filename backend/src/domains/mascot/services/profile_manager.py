"""Personality profile management service."""

from __future__ import annotations

from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models.personality_profile import StudentPersonalityProfile
from ..models.signals import ExtractedSignal, ProfileSignal


def get_or_create_profile(db: Session, student_id: UUID,
                          tenant_id: UUID) -> StudentPersonalityProfile:
    """
    Same pattern as memory_manager.get_or_create_memory.
    """
    profile = db.query(StudentPersonalityProfile).filter(
        StudentPersonalityProfile.student_id == student_id,
        StudentPersonalityProfile.tenant_id == tenant_id
    ).first()

    if not profile:
        profile = StudentPersonalityProfile(
            student_id=student_id,
            tenant_id=tenant_id,
            profile_completeness_score=0.0,
            profile_version=1
        )
        db.add(profile)
        db.commit()
        db.refresh(profile)

    return profile


def save_signal(db: Session, student_id: UUID, tenant_id: UUID,
               signal: ExtractedSignal, extraction_channel: str) -> ProfileSignal:
    """
    Create a new ProfileSignal record using signal.signal_type,
    signal.signal_value, signal.confidence_score, signal.extraction_method,
    and the passed extraction_channel. Add, commit, return.
    """
    profile_signal = ProfileSignal(
        student_id=student_id,
        tenant_id=tenant_id,
        signal_type=signal.signal_type,
        signal_value=signal.signal_value,
        confidence_score=signal.confidence_score,
        extraction_method=signal.extraction_method,
        extraction_channel=extraction_channel,
        promoted_to_profile=False
    )
    db.add(profile_signal)
    db.commit()
    db.refresh(profile_signal)
    return profile_signal


def promote_signals_to_profile(db: Session, student_id: UUID,
                               tenant_id: UUID) -> int:
    """
    This is the nightly promotion job for one student.

    Query profile_signals WHERE student_id=student_id
    AND promoted_to_profile=false
    GROUP BY signal_type, signal_value
    HAVING count(*) >= 2 OR max(confidence_score) >= 0.8

    For each qualifying signal_type, update the matching field in
    StudentPersonalityProfile using this mapping dict:

    SIGNAL_TO_FIELD = {
        "negative_self_talk": ("self_esteem_score", lambda current, signal: max(0.0, (current or 0.5) - 0.1)),
        "career_aspiration": ("career_aspiration_text", lambda current, signal: signal),
        "parental_pressure": ("parental_pressure_level", lambda current, signal: "high"),
        "learning_style_hint": ("learning_style_detected", lambda current, signal: signal),
        "competitive_motivation": ("social_orientation", lambda current, signal: "competitive"),
        "curiosity": ("primary_motivation_driver", lambda current, signal: "curiosity"),
        "resilience": ("resilience_score", lambda current, signal: min(1.0, (current or 0.5) + 0.05)),
    }

    Mark those signals as promoted_to_profile=true.
    Recalculate profile_completeness_score as count of non-null key fields / 15.
    Increment profile_version by 1.
    Commit. Return count of promoted signals.
    """
    SIGNAL_TO_FIELD = {
        "negative_self_talk": ("self_esteem_score", lambda current, signal: max(0.0, (current or 0.5) - 0.1)),
        "career_aspiration": ("career_aspiration_text", lambda current, signal: signal),
        "parental_pressure": ("parental_pressure_level", lambda current, signal: "high"),
        "learning_style_hint": ("learning_style_detected", lambda current, signal: signal),
        "competitive_motivation": ("social_orientation", lambda current, signal: "competitive"),
        "curiosity": ("primary_motivation_driver", lambda current, signal: "curiosity"),
        "resilience": ("resilience_score", lambda current, signal: min(1.0, (current or 0.5) + 0.05)),
    }

    # Get qualifying signals
    from sqlalchemy import and_, or_

    qualifying_signals = db.query(
        ProfileSignal.signal_type,
        ProfileSignal.signal_value,
        func.count(ProfileSignal.id).label('count'),
        func.max(ProfileSignal.confidence_score).label('max_confidence')
    ).filter(
        and_(
            ProfileSignal.student_id == student_id,
            ProfileSignal.tenant_id == tenant_id,
            ProfileSignal.promoted_to_profile.is_(False)
        )
    ).group_by(
        ProfileSignal.signal_type,
        ProfileSignal.signal_value
    ).having(
        or_(
            func.count(ProfileSignal.id) >= 2,
            func.max(ProfileSignal.confidence_score) >= 0.8
        )
    ).all()

    promoted_count = 0

    if qualifying_signals:
        # Get or create profile
        profile = get_or_create_profile(db, student_id, tenant_id)

        # Apply updates
        for signal_type, signal_value, count, max_confidence in qualifying_signals:
            if signal_type in SIGNAL_TO_FIELD:
                field_name, value_func = SIGNAL_TO_FIELD[signal_type]
                current_value = getattr(profile, field_name)
                new_value = value_func(current_value, signal_value)
                setattr(profile, field_name, new_value)

                # Mark signals as promoted
                db.query(ProfileSignal).filter(
                    ProfileSignal.student_id == student_id,
                    ProfileSignal.tenant_id == tenant_id,
                    ProfileSignal.signal_type == signal_type,
                    ProfileSignal.signal_value == signal_value,
                    ProfileSignal.promoted_to_profile.is_(False)
                ).update({"promoted_to_profile": True})

                promoted_count += 1

        # Recalculate completeness
        profile.profile_completeness_score = compute_completeness(profile)
        profile.profile_version += 1

        db.commit()

    return promoted_count


def compute_completeness(profile: StudentPersonalityProfile) -> float:
    """
    Count how many of these 15 fields are non-null:
    learning_style_detected, learning_style_stated, reasoning_type,
    primary_motivation_driver, stress_threshold, self_esteem_score,
    resilience_score, humor_index, social_orientation, locus_of_control,
    mindset_orientation, peak_study_hour, help_seeking_style,
    career_aspiration_text, interest_tags
    Return count / 15.0
    """
    fields_to_check = [
        'learning_style_detected', 'learning_style_stated', 'reasoning_type',
        'primary_motivation_driver', 'stress_threshold', 'self_esteem_score',
        'resilience_score', 'humor_index', 'social_orientation', 'locus_of_control',
        'mindset_orientation', 'peak_study_hour', 'help_seeking_style',
        'career_aspiration_text', 'interest_tags'
    ]

    non_null_count = sum(1 for field in fields_to_check if getattr(profile, field) is not None)
    return non_null_count / 15.0
