"""Centralized usage governance for quotas, token ceilings, routing, and reporting."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from typing import Any
from uuid import UUID

from sqlalchemy import inspect
from sqlalchemy.orm import Session

from src.domains.identity.models.user import User
from src.domains.platform.models.audit import AuditLog
from src.domains.platform.models.usage_counter import UsageCounter


DEFAULT_TENANT_REQUESTS_PER_MINUTE = 100
DEFAULT_TENANT_COST_GUARDRAIL_UNITS = 500.0

USER_QUOTAS: dict[str, dict[str, int]] = {
    "ai_requests": {"day": 80, "month": 2000},
    "qa_requests": {"day": 50, "month": 1500},
    "study_guide_generations": {"day": 6, "month": 180},
    "quiz_generations": {"day": 10, "month": 300},
    "flashcard_generations": {"day": 10, "month": 300},
    "mindmap_generations": {"day": 5, "month": 150},
    "flowchart_generations": {"day": 3, "month": 90},
    "concept_map_generations": {"day": 3, "month": 90},
    "socratic_sessions": {"day": 25, "month": 750},
    "debate_sessions": {"day": 8, "month": 180},
    "essay_reviews": {"day": 8, "month": 180},
    "weak_topic_plans": {"day": 8, "month": 180},
    "audio_overviews": {"day": 4, "month": 120},
    "video_overviews": {"day": 3, "month": 90},
    "documents_uploaded": {"day": 3, "month": 50},
    "youtube_ingestions": {"day": 3, "month": 30},
    "ocr_operations": {"day": 10, "month": 300},
    "batch_jobs_queued": {"day": 25, "month": 600},
    "llm_tokens": {"day": 30000, "month": 750000},
}

TOKEN_CEILINGS: dict[str, tuple[int, int]] = {
    "qa": (2000, 800),
    "study_guide": (2200, 1000),
    "quiz": (1500, 700),
    "flashcards": (1000, 500),
    "mindmap": (1200, 600),
    "flowchart": (1200, 600),
    "concept_map": (1200, 600),
    "weak_topic": (1500, 700),
    "socratic": (1800, 700),
    "debate": (2000, 900),
    "essay_review": (2200, 900),
    "audio_overview": (2200, 900),
    "video_overview": (2200, 900),
}

MODE_TO_METRIC = {
    "qa": "qa_requests",
    "study_guide": "study_guide_generations",
    "quiz": "quiz_generations",
    "flashcards": "flashcard_generations",
    "mindmap": "mindmap_generations",
    "flowchart": "flowchart_generations",
    "concept_map": "concept_map_generations",
    "socratic": "socratic_sessions",
    "debate": "debate_sessions",
    "essay_review": "essay_reviews",
    "weak_topic": "weak_topic_plans",
    "audio_overview": "audio_overviews",
    "video_overview": "video_overviews",
}

MODEL_COST_WEIGHTS = {
    "primary": 1.0,
    "fallback": 0.45,
}

BATCHABLE_METRICS = {
    "quiz_generations",
    "flashcard_generations",
    "mindmap_generations",
    "flowchart_generations",
    "concept_map_generations",
    "study_guide_generations",
}


@dataclass(slots=True)
class GovernanceDecision:
    allowed: bool
    metric: str
    detail: str | None = None
    daily_count: int = 0
    monthly_count: int = 0
    daily_limit: int | None = None
    monthly_limit: int | None = None
    model_override: str | None = None
    max_prompt_tokens: int | None = None
    max_completion_tokens: int | None = None
    queue_recommended: bool = False
    guardrail_active: bool = False


def approximate_token_count(text: str | None) -> int:
    normalized = (text or "").strip()
    if not normalized:
        return 0
    return max(1, len(normalized) // 4)


def resolve_metric_for_mode(mode: str) -> str:
    return MODE_TO_METRIC.get(mode, "ai_requests")


def resolve_upload_metrics(file_ext: str) -> list[str]:
    lowered = (file_ext or "").strip().lower()
    if lowered in {"jpg", "jpeg", "png"}:
        return ["ocr_operations"]
    return ["documents_uploaded"]


def resolve_token_ceiling(mode: str) -> tuple[int | None, int | None]:
    prompt, completion = TOKEN_CEILINGS.get(mode, (2000, 800))
    return prompt, completion


def get_tenant_requests_per_minute() -> int:
    return DEFAULT_TENANT_REQUESTS_PER_MINUTE


def _bucket_start(bucket_type: str, *, today: date | None = None) -> date:
    current = today or date.today()
    if bucket_type == "month":
        return current.replace(day=1)
    return current


def _month_starts_ending_on(reference: date, *, count: int) -> list[date]:
    cursor = reference.replace(day=1)
    months: list[date] = []
    for _ in range(count):
        months.append(cursor)
        if cursor.month == 1:
            cursor = date(cursor.year - 1, 12, 1)
        else:
            cursor = date(cursor.year, cursor.month - 1, 1)
    months.reverse()
    return months


def _supports_usage_counter_storage(db: Session) -> bool:
    return all(hasattr(db, attr) for attr in ("get_bind", "query", "add"))


def _ensure_usage_counter_table(db: Session) -> None:
    if not _supports_usage_counter_storage(db):
        return
    bind = db.get_bind()
    inspector = inspect(bind)
    if "usage_counters" not in inspector.get_table_names():
        UsageCounter.__table__.create(bind=bind, checkfirst=True)


def _table_exists(db: Session, table_name: str) -> bool:
    if not _supports_usage_counter_storage(db):
        return False
    return table_name in inspect(db.get_bind()).get_table_names()


def _get_counter(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID | None,
    scope: str,
    metric: str,
    bucket_type: str,
    bucket_start: date,
) -> UsageCounter | None:
    if not _supports_usage_counter_storage(db):
        return None
    _ensure_usage_counter_table(db)
    return (
        db.query(UsageCounter)
        .filter(
            UsageCounter.tenant_id == tenant_id,
            UsageCounter.user_id == user_id,
            UsageCounter.scope == scope,
            UsageCounter.metric == metric,
            UsageCounter.bucket_type == bucket_type,
            UsageCounter.bucket_start == bucket_start,
        )
        .first()
    )


def _get_counter_count(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID | None,
    scope: str,
    metric: str,
    bucket_type: str,
) -> int:
    row = _get_counter(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        scope=scope,
        metric=metric,
        bucket_type=bucket_type,
        bucket_start=_bucket_start(bucket_type),
    )
    return int(row.count if row else 0)


def _get_counter_tokens(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID | None,
    scope: str,
    metric: str,
    bucket_type: str,
) -> int:
    row = _get_counter(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        scope=scope,
        metric=metric,
        bucket_type=bucket_type,
        bucket_start=_bucket_start(bucket_type),
    )
    return int(row.token_total if row else 0)


def _upsert_counter(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID | None,
    scope: str,
    metric: str,
    count_inc: int = 0,
    token_inc: int = 0,
    cache_hit_inc: int = 0,
    cost_inc: float = 0.0,
    last_model: str | None = None,
    bucket_type: str,
) -> UsageCounter:
    start = _bucket_start(bucket_type)
    if not _supports_usage_counter_storage(db):
        counter = UsageCounter(
            tenant_id=tenant_id,
            user_id=user_id,
            scope=scope,
            metric=metric,
            bucket_type=bucket_type,
            bucket_start=start,
        )
        counter.count = int(counter.count or 0) + count_inc
        counter.token_total = int(counter.token_total or 0) + token_inc
        counter.cache_hits = int(counter.cache_hits or 0) + cache_hit_inc
        counter.estimated_cost_units = float(counter.estimated_cost_units or 0.0) + float(cost_inc)
        if last_model:
            counter.last_model = last_model
        counter.updated_at = datetime.now(UTC)
        return counter
    counter = _get_counter(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        scope=scope,
        metric=metric,
        bucket_type=bucket_type,
        bucket_start=start,
    )
    if counter is None:
        counter = UsageCounter(
            tenant_id=tenant_id,
            user_id=user_id,
            scope=scope,
            metric=metric,
            bucket_type=bucket_type,
            bucket_start=start,
        )
        db.add(counter)
    counter.count = int(counter.count or 0) + count_inc
    counter.token_total = int(counter.token_total or 0) + token_inc
    counter.cache_hits = int(counter.cache_hits or 0) + cache_hit_inc
    counter.estimated_cost_units = float(counter.estimated_cost_units or 0.0) + float(cost_inc)
    if last_model:
        counter.last_model = last_model
    counter.updated_at = datetime.now(UTC)
    return counter


def _estimate_cost_units(token_usage: int, *, used_fallback: bool) -> float:
    if token_usage <= 0:
        return 0.0
    weight = MODEL_COST_WEIGHTS["fallback" if used_fallback else "primary"]
    return round((token_usage / 1000.0) * weight, 4)


def _should_use_fallback(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    metric: str,
    daily_count: int,
    daily_limit: int | None,
) -> tuple[bool, bool]:
    user_daily_tokens = _get_counter_tokens(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        scope="user",
        metric="llm_tokens",
        bucket_type="day",
    )
    tenant_daily_tokens = _get_counter_tokens(
        db,
        tenant_id=tenant_id,
        user_id=None,
        scope="tenant",
        metric="llm_tokens",
        bucket_type="day",
    )
    fallback = False
    guardrail_active = False
    token_limit = USER_QUOTAS["llm_tokens"]["day"]
    if user_daily_tokens >= int(token_limit * 0.8) or tenant_daily_tokens >= int(token_limit * 5):
        fallback = True
    if daily_limit and daily_count >= int(daily_limit * 0.85):
        fallback = True
    if metric in BATCHABLE_METRICS and tenant_daily_tokens >= int(token_limit * 6):
        guardrail_active = True
    return fallback, guardrail_active


def evaluate_governance(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID,
    metric: str,
    mode: str | None = None,
    estimated_prompt_tokens: int = 0,
) -> GovernanceDecision:
    quotas = USER_QUOTAS.get(metric) or {}
    daily_limit = quotas.get("day")
    monthly_limit = quotas.get("month")
    daily_count = _get_counter_count(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        scope="user",
        metric=metric,
        bucket_type="day",
    )
    monthly_count = _get_counter_count(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        scope="user",
        metric=metric,
        bucket_type="month",
    )
    if daily_limit is not None and daily_count >= daily_limit:
        return GovernanceDecision(
            allowed=False,
            metric=metric,
            detail=f"You have reached today's {metric.replace('_', ' ')} limit. Try again tomorrow.",
            daily_count=daily_count,
            monthly_count=monthly_count,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
        )
    if monthly_limit is not None and monthly_count >= monthly_limit:
        return GovernanceDecision(
            allowed=False,
            metric=metric,
            detail=f"You have reached this month's {metric.replace('_', ' ')} limit.",
            daily_count=daily_count,
            monthly_count=monthly_count,
            daily_limit=daily_limit,
            monthly_limit=monthly_limit,
        )

    if estimated_prompt_tokens > 0:
        day_tokens = _get_counter_tokens(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            scope="user",
            metric="llm_tokens",
            bucket_type="day",
        )
        month_tokens = _get_counter_tokens(
            db,
            tenant_id=tenant_id,
            user_id=user_id,
            scope="user",
            metric="llm_tokens",
            bucket_type="month",
        )
        if day_tokens >= USER_QUOTAS["llm_tokens"]["day"]:
            return GovernanceDecision(
                allowed=False,
                metric="llm_tokens",
                detail="You have reached today's AI token budget. Try again tomorrow.",
                daily_count=day_tokens,
                monthly_count=month_tokens,
                daily_limit=USER_QUOTAS["llm_tokens"]["day"],
                monthly_limit=USER_QUOTAS["llm_tokens"]["month"],
            )
        if month_tokens >= USER_QUOTAS["llm_tokens"]["month"]:
            return GovernanceDecision(
                allowed=False,
                metric="llm_tokens",
                detail="You have reached this month's AI token budget.",
                daily_count=day_tokens,
                monthly_count=month_tokens,
                daily_limit=USER_QUOTAS["llm_tokens"]["day"],
                monthly_limit=USER_QUOTAS["llm_tokens"]["month"],
            )

    fallback, guardrail_active = _should_use_fallback(
        db,
        tenant_id=tenant_id,
        user_id=user_id,
        metric=metric,
        daily_count=daily_count,
        daily_limit=daily_limit,
    )
    max_prompt_tokens, max_completion_tokens = resolve_token_ceiling(mode or metric)
    return GovernanceDecision(
        allowed=True,
        metric=metric,
        daily_count=daily_count,
        monthly_count=monthly_count,
        daily_limit=daily_limit,
        monthly_limit=monthly_limit,
        model_override=None if not fallback else "fallback",
        max_prompt_tokens=max_prompt_tokens,
        max_completion_tokens=max_completion_tokens,
        queue_recommended=guardrail_active and metric in BATCHABLE_METRICS,
        guardrail_active=guardrail_active,
    )


def apply_model_override(default_model: str, fallback_model: str, override: str | None) -> str:
    if override == "fallback":
        return fallback_model or default_model
    return default_model


def record_usage_event(
    db: Session,
    *,
    tenant_id: UUID,
    user_id: UUID | None,
    metric: str,
    count: int = 1,
    token_usage: int = 0,
    cache_hit: bool = False,
    model_used: str | None = None,
    used_fallback_model: bool = False,
    metadata: dict[str, Any] | None = None,
) -> None:
    counters_to_increment = {metric}
    if metric in MODE_TO_METRIC.values():
        counters_to_increment.add("ai_requests")
    if token_usage > 0:
        counters_to_increment.add("llm_tokens")
    cost_inc = _estimate_cost_units(token_usage, used_fallback=used_fallback_model)

    for bucket_type in ("day", "month"):
        for counter_metric in counters_to_increment:
            count_inc = count if counter_metric != "llm_tokens" else 0
            token_inc = token_usage if counter_metric == "llm_tokens" else token_usage
            if user_id:
                _upsert_counter(
                    db,
                    tenant_id=tenant_id,
                    user_id=user_id,
                    scope="user",
                    metric=counter_metric,
                    count_inc=count_inc,
                    token_inc=token_inc,
                    cache_hit_inc=1 if cache_hit else 0,
                    cost_inc=cost_inc,
                    last_model=model_used,
                    bucket_type=bucket_type,
                )
            _upsert_counter(
                db,
                tenant_id=tenant_id,
                user_id=None,
                scope="tenant",
                metric=counter_metric,
                count_inc=count_inc,
                token_inc=token_inc,
                cache_hit_inc=1 if cache_hit else 0,
                cost_inc=cost_inc,
                last_model=model_used,
                bucket_type=bucket_type,
            )

    if _table_exists(db, "audit_logs"):
        db.add(
            AuditLog(
                tenant_id=tenant_id,
                user_id=user_id,
                action="usage.governance.recorded",
                entity_type="usage_counter",
                metadata_={
                    "metric": metric,
                    "count": count,
                    "token_usage": token_usage,
                    "cache_hit": cache_hit,
                    "model_used": model_used,
                    "used_fallback_model": used_fallback_model,
                    **(metadata or {}),
                },
            )
        )


def _aggregate_tenant_counter(
    db: Session,
    *,
    tenant_id: UUID,
    bucket_type: str,
) -> list[UsageCounter]:
    _ensure_usage_counter_table(db)
    return (
        db.query(UsageCounter)
        .filter(
            UsageCounter.tenant_id == tenant_id,
            UsageCounter.user_id.is_(None),
            UsageCounter.scope == "tenant",
            UsageCounter.bucket_type == bucket_type,
            UsageCounter.bucket_start == _bucket_start(bucket_type),
        )
        .all()
    )


def build_usage_snapshot(db: Session, *, tenant_id: UUID, days: int = 7) -> dict[str, Any]:
    today = _bucket_start("day")
    week_start = today - timedelta(days=max(days - 1, 0))
    six_month_day_start = today - timedelta(days=179)
    month_starts = _month_starts_ending_on(today, count=6)
    aggregate_metrics = {"ai_requests", "llm_tokens"}
    rows = _aggregate_tenant_counter(db, tenant_id=tenant_id, bucket_type="day")
    by_metric: dict[str, dict[str, Any]] = {}
    for row in rows:
        entry = by_metric.setdefault(
            row.metric,
            {"count": 0, "token_total": 0, "cache_hits": 0, "estimated_cost_units": 0.0},
        )
        entry["count"] += int(row.count or 0)
        entry["token_total"] += int(row.token_total or 0)
        entry["cache_hits"] += int(row.cache_hits or 0)
        entry["estimated_cost_units"] += float(row.estimated_cost_units or 0.0)
    week_rows = (
        db.query(UsageCounter)
        .filter(
            UsageCounter.tenant_id == tenant_id,
            UsageCounter.user_id.is_(None),
            UsageCounter.scope == "tenant",
            UsageCounter.bucket_type == "day",
            UsageCounter.bucket_start >= week_start,
            UsageCounter.bucket_start <= today,
        )
        .all()
    )
    role_totals = {"students": 0, "teachers": 0, "admin": 0, "parents": 0}

    user_rows = (
        db.query(User, UsageCounter)
        .outerjoin(
            UsageCounter,
            (UsageCounter.user_id == User.id)
            & (UsageCounter.tenant_id == User.tenant_id)
            & (UsageCounter.scope == "user")
            & (UsageCounter.bucket_type == "day")
            & (UsageCounter.bucket_start == today),
        )
        .filter(User.tenant_id == tenant_id)
        .all()
    )

    user_summaries: dict[UUID, dict[str, Any]] = {}
    for user, counter in user_rows:
        summary = user_summaries.setdefault(
            user.id,
            {
                "name": user.full_name,
                "role": user.role,
                "requests_primary": 0,
                "requests_fallback": 0,
                "tokens_primary": 0,
                "tokens_fallback": 0,
                "tokens_llm": 0,
            },
        )
        if counter is None:
            continue
        if counter.metric == "ai_requests":
            summary["requests_primary"] += int(counter.count or 0)
            summary["tokens_primary"] += int(counter.token_total or 0)
        elif counter.metric == "llm_tokens":
            summary["tokens_llm"] += int(counter.token_total or 0)
        else:
            summary["requests_fallback"] += int(counter.count or 0)
            summary["tokens_fallback"] += int(counter.token_total or 0)

    heavy_users: list[dict[str, Any]] = []
    for summary in user_summaries.values():
        total = summary["requests_primary"] or summary["requests_fallback"]
        tokens_today = summary["tokens_llm"] or summary["tokens_primary"] or summary["tokens_fallback"]
        role_key = {
            "student": "students",
            "teacher": "teachers",
            "admin": "admin",
            "parent": "parents",
        }.get(summary["role"])
        if role_key in role_totals:
            role_totals[role_key] += total
        heavy_users.append(
            {
                "name": summary["name"],
                "role": summary["role"],
                "queries": total,
                "tokens_today": tokens_today,
            }
        )
    heavy_users.sort(key=lambda item: item["queries"], reverse=True)

    total_role_usage = max(sum(role_totals.values()), 1)
    model_mix: dict[str, int] = {}
    for row in rows:
        if row.metric not in aggregate_metrics and row.last_model:
            model_mix[row.last_model] = model_mix.get(row.last_model, 0) + int(row.count or 0)

    recent_day_rows = (
        db.query(UsageCounter)
        .filter(
            UsageCounter.tenant_id == tenant_id,
            UsageCounter.user_id.is_(None),
            UsageCounter.scope == "tenant",
            UsageCounter.bucket_type == "day",
            UsageCounter.bucket_start >= six_month_day_start,
            UsageCounter.bucket_start <= today,
        )
        .all()
    )
    month_rows = (
        db.query(UsageCounter)
        .filter(
            UsageCounter.tenant_id == tenant_id,
            UsageCounter.user_id.is_(None),
            UsageCounter.scope == "tenant",
            UsageCounter.bucket_type == "month",
            UsageCounter.bucket_start >= month_starts[0],
            UsageCounter.bucket_start <= month_starts[-1],
        )
        .all()
    )
    month_lookup = {(row.metric, row.bucket_start): row for row in month_rows}
    monthly_trend = []
    for month_start in month_starts:
        ai_row = month_lookup.get(("ai_requests", month_start))
        token_row = month_lookup.get(("llm_tokens", month_start))
        requests = int(ai_row.count or 0) if ai_row else 0
        tokens = int(token_row.token_total or 0) if token_row else int(ai_row.token_total or 0) if ai_row else 0
        cache_hits = int(token_row.cache_hits or 0) if token_row else int(ai_row.cache_hits or 0) if ai_row else 0
        estimated_cost = float(token_row.estimated_cost_units or 0.0) if token_row else float(ai_row.estimated_cost_units or 0.0) if ai_row else 0.0
        monthly_trend.append(
            {
                "month": month_start.isoformat(),
                "label": month_start.strftime("%b"),
                "requests": requests,
                "tokens": tokens,
                "cache_hits": cache_hits,
                "estimated_cost_units": round(estimated_cost, 3),
            }
        )

    workflow_rollups: dict[str, dict[str, Any]] = {}
    for row in month_rows:
        if row.metric in aggregate_metrics:
            continue
        entry = workflow_rollups.setdefault(
            row.metric,
            {"count": 0, "token_total": 0, "cache_hits": 0, "estimated_cost_units": 0.0},
        )
        entry["count"] += int(row.count or 0)
        entry["token_total"] += int(row.token_total or 0)
        entry["cache_hits"] += int(row.cache_hits or 0)
        entry["estimated_cost_units"] += float(row.estimated_cost_units or 0.0)

    ai_day_rows = [row for row in recent_day_rows if row.metric == "ai_requests"]
    llm_day_lookup = {
        row.bucket_start: row for row in recent_day_rows if row.metric == "llm_tokens"
    }
    peak_ai_row = max(ai_day_rows, key=lambda row: int(row.count or 0), default=None)
    peak_day = None
    if peak_ai_row is not None:
        peak_llm_row = llm_day_lookup.get(peak_ai_row.bucket_start)
        peak_day = {
            "date": peak_ai_row.bucket_start.isoformat(),
            "requests": int(peak_ai_row.count or 0),
            "tokens": int(peak_llm_row.token_total or 0) if peak_llm_row else int(peak_ai_row.token_total or 0),
            "cache_hits": int(peak_llm_row.cache_hits or 0) if peak_llm_row else int(peak_ai_row.cache_hits or 0),
        }

    role_month_rows = (
        db.query(User.role, UsageCounter.metric, UsageCounter.bucket_start, UsageCounter.count)
        .join(
            User,
            (UsageCounter.user_id == User.id)
            & (UsageCounter.tenant_id == User.tenant_id),
        )
        .filter(
            UsageCounter.tenant_id == tenant_id,
            UsageCounter.scope == "user",
            UsageCounter.bucket_type == "month",
            UsageCounter.bucket_start >= month_starts[0],
            UsageCounter.bucket_start <= month_starts[-1],
        )
        .all()
    )
    role_month_totals: dict[tuple[date, str], dict[str, int]] = {}
    for role, metric, bucket_start, count in role_month_rows:
        if role is None or bucket_start is None or metric is None:
            continue
        bucket = role_month_totals.setdefault((bucket_start, role), {"primary": 0, "fallback": 0})
        if metric == "ai_requests":
            bucket["primary"] += int(count or 0)
        elif metric != "llm_tokens":
            bucket["fallback"] += int(count or 0)

    role_monthly = []
    for month_start in month_starts:
        month_counts = {
            "students": role_month_totals.get((month_start, "student"), {}).get("primary", 0)
            or role_month_totals.get((month_start, "student"), {}).get("fallback", 0),
            "teachers": role_month_totals.get((month_start, "teacher"), {}).get("primary", 0)
            or role_month_totals.get((month_start, "teacher"), {}).get("fallback", 0),
            "admin": role_month_totals.get((month_start, "admin"), {}).get("primary", 0)
            or role_month_totals.get((month_start, "admin"), {}).get("fallback", 0),
            "parents": role_month_totals.get((month_start, "parent"), {}).get("primary", 0)
            or role_month_totals.get((month_start, "parent"), {}).get("fallback", 0),
        }
        month_counts["month"] = month_start.isoformat()
        month_counts["label"] = month_start.strftime("%b")
        role_monthly.append(month_counts)

    quota_saturation: list[dict[str, Any]] = []
    for metric, limits in USER_QUOTAS.items():
        current = int(by_metric.get(metric, {}).get("count", 0))
        if metric == "llm_tokens":
            current = int(by_metric.get(metric, {}).get("token_total", 0))
        daily_limit = limits.get("day", 0)
        saturation = round((current / daily_limit) * 100, 1) if daily_limit else 0.0
        quota_saturation.append(
            {
                "metric": metric,
                "current": current,
                "daily_limit": daily_limit,
                "saturation_pct": saturation,
            }
        )
    quota_saturation.sort(key=lambda item: item["saturation_pct"], reverse=True)

    token_usage_today = int(by_metric.get("llm_tokens", {}).get("token_total", 0))
    if token_usage_today == 0:
        token_usage_today = int(by_metric.get("ai_requests", {}).get("token_total", 0))
    estimated_cost_units_today = round(float(by_metric.get("llm_tokens", {}).get("estimated_cost_units", 0.0)), 3)
    if estimated_cost_units_today == 0.0:
        estimated_cost_units_today = round(float(by_metric.get("ai_requests", {}).get("estimated_cost_units", 0.0)), 3)
    cache_hits_today = int(by_metric.get("llm_tokens", {}).get("cache_hits", 0))
    if cache_hits_today == 0:
        cache_hits_today = int(by_metric.get("ai_requests", {}).get("cache_hits", 0))

    six_month_totals = {
        "requests": int(sum(item["requests"] for item in monthly_trend)),
        "tokens": int(sum(item["tokens"] for item in monthly_trend)),
        "cache_hits": int(sum(item["cache_hits"] for item in monthly_trend)),
        "estimated_cost_units": round(sum(item["estimated_cost_units"] for item in monthly_trend), 3),
    }

    return {
        "total_week": int(sum((row.count or 0) for row in week_rows if row.metric == "ai_requests")),
        "by_role": {
            "students": round(role_totals["students"] / total_role_usage * 100),
            "teachers": round(role_totals["teachers"] / total_role_usage * 100),
            "admin": round(role_totals["admin"] / total_role_usage * 100),
            "parents": round(role_totals["parents"] / total_role_usage * 100),
        },
        "heavy_users": heavy_users[:5],
        "tool_usage": [
            {
                "metric": metric,
                "count": int(values["count"]),
                "token_total": int(values["token_total"]),
                "cache_hits": int(values["cache_hits"]),
            }
            for metric, values in sorted(by_metric.items(), key=lambda item: (-item[1]["count"], item[0]))
            if metric not in aggregate_metrics
        ],
        "token_usage_today": token_usage_today,
        "estimated_cost_units_today": estimated_cost_units_today,
        "cache_hits_today": cache_hits_today,
        "guardrails": {
            "tenant_requests_per_minute": get_tenant_requests_per_minute(),
            "tenant_daily_cost_units_threshold": DEFAULT_TENANT_COST_GUARDRAIL_UNITS,
            "queued_batch_metrics": sorted(BATCHABLE_METRICS),
            "days_window": days,
        },
        "quota_saturation": quota_saturation[:8],
        "model_mix": model_mix,
        "monthly_trend": monthly_trend,
        "role_monthly": role_monthly,
        "six_month_totals": six_month_totals,
        "top_workflows_6m": [
            {
                "metric": metric,
                "count": int(values["count"]),
                "token_total": int(values["token_total"]),
                "cache_hits": int(values["cache_hits"]),
                "estimated_cost_units": round(float(values["estimated_cost_units"]), 3),
            }
            for metric, values in sorted(workflow_rollups.items(), key=lambda item: (-item[1]["count"], item[0]))[:8]
        ],
        "peak_day": peak_day,
    }
