"""Application helpers for student spaced-repetition review workflows.

Optimized for high-concurrency Indian EdTech deployments:
- The SM-2 core update (interval + ease_factor) commits immediately so
  students see instant feedback.
- Expensive mastery-snapshot computations and outcome recording are
  deferred to a background thread, reducing DB lock hold times during
  peak revision hours (5-8 PM IST, thousands of concurrent flashcard
  reviews).
"""

from __future__ import annotations

import logging
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from typing import Any
from collections.abc import Callable

from sqlalchemy.orm import Session

from src.domains.platform.models.spaced_repetition import ReviewSchedule

logger = logging.getLogger(__name__)
_DEFERRED_REVIEW_EXECUTOR = ThreadPoolExecutor(max_workers=4, thread_name_prefix="student-review")


def list_student_reviews(
    *,
    db: Session,
    tenant_id,
    student_id,
) -> dict[str, Any]:
    reviews = (
        db.query(ReviewSchedule)
        .filter(
            ReviewSchedule.tenant_id == tenant_id,
            ReviewSchedule.student_id == student_id,
        )
        .order_by(ReviewSchedule.next_review_at)
        .all()
    )

    now = datetime.now(timezone.utc)
    due: list[dict[str, Any]] = []
    upcoming: list[dict[str, Any]] = []
    for review in reviews:
        review_at = review.next_review_at
        if review_at and review_at.tzinfo is None:
            review_at = review_at.replace(tzinfo=timezone.utc)
        is_due = review_at <= now if review_at else False
        entry = {
            "id": str(review.id),
            "topic": review.topic,
            "subject_id": str(review.subject_id) if review.subject_id else None,
            "next_review_at": str(review.next_review_at),
            "interval_days": review.interval_days,
            "ease_factor": round(review.ease_factor, 2),
            "review_count": review.review_count,
            "is_due": is_due,
        }
        if is_due:
            due.append(entry)
        else:
            upcoming.append(entry)

    return {"due": due, "upcoming": upcoming, "total": len(reviews)}


def _sm2_update(interval: int, ease_factor: float, rating: int) -> tuple[int, float]:
    """SM-2 spaced repetition update returning next interval and ease factor."""
    if rating < 3:
        return 1, max(1.3, ease_factor - 0.2)

    new_ef = ease_factor + (0.1 - (5 - rating) * (0.08 + (5 - rating) * 0.02))
    new_ef = max(1.3, new_ef)
    if interval == 0:
        new_interval = 1
    elif interval == 1:
        new_interval = 6
    else:
        new_interval = round(interval * new_ef)
    return new_interval, new_ef


def create_student_review(
    *,
    db: Session,
    tenant_id,
    student_id,
    topic: str,
    subject_id: str | None,
    parse_uuid_fn: Callable[[str, str], Any],
    ensure_topic_mastery_seed_fn: Callable[..., Any],
) -> dict[str, Any]:
    normalized_topic = topic.strip()
    if not normalized_topic:
        raise ValueError("topic is required")

    subject_uuid = None
    if subject_id:
        subject_uuid = parse_uuid_fn(subject_id, "subject_id")

    now = datetime.now(timezone.utc)
    review = ReviewSchedule(
        tenant_id=tenant_id,
        student_id=student_id,
        subject_id=subject_uuid,
        topic=normalized_topic,
        next_review_at=now + timedelta(days=1),
        interval_days=1,
        ease_factor=2.5,
        review_count=0,
    )
    db.add(review)
    ensure_topic_mastery_seed_fn(
        db,
        tenant_id=tenant_id,
        user_id=student_id,
        topic=normalized_topic,
        subject_id=subject_uuid,
        evidence_type="review_created",
    )
    db.commit()
    db.refresh(review)

    return {
        "success": True,
        "review_id": str(review.id),
        "topic": review.topic,
        "next_review_at": str(review.next_review_at),
    }


def complete_student_review(
    *,
    db: Session,
    tenant_id,
    student_id,
    review_id: str,
    rating: int,
    parse_uuid_fn: Callable[[str, str], Any],
    get_topic_mastery_snapshot_fn: Callable[..., dict[str, Any]],
    record_review_completion_fn: Callable[..., Any],
    record_mastery_outcome_fn: Callable[..., Any],
    db_session_factory: Callable[..., Session] | None = None,
) -> dict[str, Any]:
    """Complete a spaced-repetition review.

    Optimized for high-concurrency:
    - The SM-2 core update (interval, ease_factor, review_count) commits
      immediately so the student sees instant feedback.
    - Expensive mastery-snapshot computations and outcome recording are
      deferred to a background thread using a separate DB session, reducing
      row-level lock contention during peak revision hours.
    """
    if rating < 1 or rating > 5:
        raise ValueError("rating must be between 1 and 5")

    review_uuid = parse_uuid_fn(review_id, "review_id")
    review = (
        db.query(ReviewSchedule)
        .filter(
            ReviewSchedule.id == review_uuid,
            ReviewSchedule.tenant_id == tenant_id,
            ReviewSchedule.student_id == student_id,
        )
        .first()
    )
    if not review:
        raise LookupError("Review not found")

    # ── Fast path: SM-2 core update (commits immediately) ────────────
    new_interval, new_ef = _sm2_update(review.interval_days, review.ease_factor, rating)
    review.interval_days = new_interval
    review.ease_factor = new_ef
    review.review_count += 1
    next_review_at = datetime.now(timezone.utc) + timedelta(days=new_interval)
    review.next_review_at = next_review_at
    review.updated_at = datetime.now(timezone.utc)

    # Capture values needed by the background thread before committing
    review_topic = review.topic
    review_subject_id = review.subject_id
    review_count = review.review_count

    # Commit the core SM-2 fields immediately — student gets instant feedback
    db.commit()

    # ── Deferred path: mastery analytics (background thread) ─────────
    # These operations involve multiple DB reads + writes for mastery
    # snapshots and are NOT on the student's critical rendering path.
    def _deferred_mastery_work():
        """Run mastery snapshot + outcome recording off the request path."""
        try:
            if not db_session_factory:
                logger.info(
                    "Skipping deferred mastery work because no db_session_factory was provided",
                    extra={"student_id": str(student_id), "review_id": str(review_uuid)},
                )
                return

            bg_db = db_session_factory()

            try:
                before_snapshot = get_topic_mastery_snapshot_fn(
                    bg_db,
                    tenant_id=tenant_id,
                    user_id=student_id,
                    topic=review_topic,
                    subject_id=review_subject_id,
                )
                record_review_completion_fn(
                    bg_db,
                    tenant_id=tenant_id,
                    user_id=student_id,
                    topic=review_topic,
                    rating=rating,
                    next_review_at=next_review_at,
                    subject_id=review_subject_id,
                )
                bg_db.commit()

                after_snapshot = get_topic_mastery_snapshot_fn(
                    bg_db,
                    tenant_id=tenant_id,
                    user_id=student_id,
                    topic=review_topic,
                    subject_id=review_subject_id,
                )
                record_mastery_outcome_fn(
                    topic=review_topic,
                    before_snapshot=before_snapshot,
                    after_snapshot=after_snapshot,
                )
            finally:
                bg_db.close()
        except Exception:
            logger.warning(
                "Deferred mastery work failed for review topic=%s student=%s",
                review_topic,
                student_id,
                exc_info=True,
            )

    # Fire-and-forget on a daemon thread — does not block the HTTP response
    _DEFERRED_REVIEW_EXECUTOR.submit(_deferred_mastery_work)

    return {
        "success": True,
        "review_id": str(review_uuid),
        "new_interval_days": new_interval,
        "new_ease_factor": round(new_ef, 2),
        "next_review_at": str(next_review_at),
        "review_count": review_count,
    }
