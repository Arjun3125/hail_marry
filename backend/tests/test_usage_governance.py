import uuid
from datetime import date

from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.platform.services.usage_governance import (
    USER_QUOTAS,
    build_usage_snapshot,
    evaluate_governance,
    record_usage_event,
)
from src.domains.platform.models.usage_counter import UsageCounter


def _create_user(db_session, tenant_id, *, role: str, email: str, full_name: str):
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        email=email,
        full_name=full_name,
        role=role,
        hashed_password=pwd_context.hash("pass123!"),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_usage_governance_blocks_daily_quota(db_session, active_tenant):
    student = _create_user(
        db_session,
        active_tenant.id,
        role="student",
        email="quota-student@testschool.edu",
        full_name="Quota Student",
    )

    record_usage_event(
        db_session,
        tenant_id=active_tenant.id,
        user_id=student.id,
        metric="qa_requests",
        count=USER_QUOTAS["qa_requests"]["day"],
        token_usage=800,
        model_used="llama3.2",
    )
    db_session.commit()

    decision = evaluate_governance(
        db_session,
        tenant_id=active_tenant.id,
        user_id=student.id,
        metric="qa_requests",
        mode="qa",
        estimated_prompt_tokens=120,
    )

    assert decision.allowed is False
    assert "today" in (decision.detail or "").lower()


def test_usage_snapshot_aggregates_tokens_cache_and_model_mix(db_session, active_tenant):
    student = _create_user(
        db_session,
        active_tenant.id,
        role="student",
        email="snapshot-student@testschool.edu",
        full_name="Snapshot Student",
    )
    teacher = _create_user(
        db_session,
        active_tenant.id,
        role="teacher",
        email="snapshot-teacher@testschool.edu",
        full_name="Snapshot Teacher",
    )

    record_usage_event(
        db_session,
        tenant_id=active_tenant.id,
        user_id=student.id,
        metric="qa_requests",
        token_usage=1200,
        cache_hit=False,
        model_used="llama3.2",
    )
    record_usage_event(
        db_session,
        tenant_id=active_tenant.id,
        user_id=teacher.id,
        metric="flashcard_generations",
        token_usage=400,
        cache_hit=True,
        model_used="llama3.2-mini",
        used_fallback_model=True,
    )
    db_session.commit()

    snapshot = build_usage_snapshot(db_session, tenant_id=active_tenant.id, days=7)

    assert snapshot["token_usage_today"] >= 1600
    assert snapshot["cache_hits_today"] >= 1
    assert any(item["metric"] == "qa_requests" for item in snapshot["tool_usage"])
    assert snapshot["model_mix"]["llama3.2"] >= 1
    assert snapshot["model_mix"]["llama3.2-mini"] >= 1


def _month_starts(reference: date, count: int = 6) -> list[date]:
    months: list[date] = []
    cursor = reference.replace(day=1)
    for _ in range(count):
        months.append(cursor)
        if cursor.month == 1:
            cursor = date(cursor.year - 1, 12, 1)
        else:
            cursor = date(cursor.year, cursor.month - 1, 1)
    months.reverse()
    return months


def test_usage_snapshot_includes_six_month_trend_and_role_history(db_session, active_tenant):
    student = _create_user(
        db_session,
        active_tenant.id,
        role="student",
        email="trend-student@testschool.edu",
        full_name="Trend Student",
    )
    teacher = _create_user(
        db_session,
        active_tenant.id,
        role="teacher",
        email="trend-teacher@testschool.edu",
        full_name="Trend Teacher",
    )
    parent = _create_user(
        db_session,
        active_tenant.id,
        role="parent",
        email="trend-parent@testschool.edu",
        full_name="Trend Parent",
    )
    admin = _create_user(
        db_session,
        active_tenant.id,
        role="admin",
        email="trend-admin@testschool.edu",
        full_name="Trend Admin",
    )

    today = date.today()
    for index, month_start in enumerate(_month_starts(today), start=1):
        request_count = 180 + (index * 45)
        token_total = 6500 + (index * 1800)
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=None,
                scope="tenant",
                metric="ai_requests",
                bucket_type="month",
                bucket_start=month_start,
                count=request_count,
                token_total=token_total,
                cache_hits=30 + (index * 4),
                estimated_cost_units=18.0 + index,
                last_model="llama3.2",
            )
        )
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=None,
                scope="tenant",
                metric="llm_tokens",
                bucket_type="month",
                bucket_start=month_start,
                count=0,
                token_total=token_total,
                cache_hits=30 + (index * 4),
                estimated_cost_units=18.0 + index,
                last_model="llama3.2",
            )
        )
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=None,
                scope="tenant",
                metric="qa_requests",
                bucket_type="month",
                bucket_start=month_start,
                count=120 + (index * 20),
                token_total=4200 + (index * 900),
                cache_hits=12 + index,
                estimated_cost_units=7.5 + index,
                last_model="llama3.2",
            )
        )
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=None,
                scope="tenant",
                metric="quiz_generations",
                bucket_type="month",
                bucket_start=month_start,
                count=45 + (index * 8),
                token_total=1800 + (index * 500),
                cache_hits=6 + index,
                estimated_cost_units=4.0 + index,
                last_model="llama3.2-mini",
            )
        )
        for user_id, role_count in [
            (student.id, 100 + (index * 20)),
            (teacher.id, 45 + (index * 8)),
            (parent.id, 12 + (index * 3)),
            (admin.id, 10 + (index * 2)),
        ]:
            db_session.add(
                UsageCounter(
                    tenant_id=active_tenant.id,
                    user_id=user_id,
                    scope="user",
                    metric="ai_requests",
                    bucket_type="month",
                    bucket_start=month_start,
                    count=role_count,
                    token_total=role_count * 180,
                    cache_hits=max(1, role_count // 8),
                    estimated_cost_units=role_count / 12,
                    last_model="llama3.2",
                )
            )

    for user_id, metric, count, tokens, model in [
        (student.id, "qa_requests", 9, 2400, "llama3.2"),
        (teacher.id, "quiz_generations", 4, 1100, "llama3.2-mini"),
        (parent.id, "qa_requests", 2, 380, "llama3.2"),
        (admin.id, "study_guide_generations", 1, 620, "llama3.2"),
    ]:
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=user_id,
                scope="user",
                metric=metric,
                bucket_type="day",
                bucket_start=today,
                count=count,
                token_total=tokens,
                cache_hits=1,
                estimated_cost_units=1.0,
                last_model=model,
            )
        )
    for user_id, requests, tokens in [
        (student.id, 9, 2400),
        (teacher.id, 4, 1100),
        (parent.id, 2, 380),
        (admin.id, 1, 620),
    ]:
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=user_id,
                scope="user",
                metric="ai_requests",
                bucket_type="day",
                bucket_start=today,
                count=requests,
                token_total=tokens,
                cache_hits=1,
                estimated_cost_units=1.0,
                last_model="llama3.2",
            )
        )
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=user_id,
                scope="user",
                metric="llm_tokens",
                bucket_type="day",
                bucket_start=today,
                count=0,
                token_total=tokens,
                cache_hits=1,
                estimated_cost_units=1.0,
                last_model="llama3.2",
            )
        )

    for metric, count, tokens, model in [
        ("ai_requests", 16, 4500, "llama3.2"),
        ("llm_tokens", 0, 4500, "llama3.2"),
        ("qa_requests", 11, 2780, "llama3.2"),
        ("quiz_generations", 4, 1100, "llama3.2-mini"),
        ("study_guide_generations", 1, 620, "llama3.2"),
    ]:
        db_session.add(
            UsageCounter(
                tenant_id=active_tenant.id,
                user_id=None,
                scope="tenant",
                metric=metric,
                bucket_type="day",
                bucket_start=today,
                count=count,
                token_total=tokens,
                cache_hits=3,
                estimated_cost_units=2.4,
                last_model=model,
            )
        )

    db_session.commit()

    snapshot = build_usage_snapshot(db_session, tenant_id=active_tenant.id, days=7)

    assert len(snapshot["monthly_trend"]) == 6
    assert snapshot["monthly_trend"][-1]["requests"] > snapshot["monthly_trend"][0]["requests"]
    assert snapshot["six_month_totals"]["requests"] >= 2000
    assert snapshot["top_workflows_6m"][0]["metric"] == "qa_requests"
    assert snapshot["role_monthly"][-1]["parents"] > 0
    assert snapshot["by_role"]["parents"] > 0
    assert snapshot["peak_day"] is not None
