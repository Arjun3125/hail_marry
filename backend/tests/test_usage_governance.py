import uuid

from src.domains.identity.models.user import User
from src.domains.identity.routes.auth import pwd_context
from src.domains.platform.services.usage_governance import (
    USER_QUOTAS,
    build_usage_snapshot,
    evaluate_governance,
    record_usage_event,
)


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
