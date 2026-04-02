"""Messaging adapters used by admin interfaces."""

from __future__ import annotations

from src.domains.platform.services.ai_queue import (
    cancel_job,
    drain_queue,
    get_job_detail_for_tenant,
    get_queue_metrics,
    list_jobs_for_tenant,
    move_to_dead_letter,
    pause_queue,
    resume_queue,
    retry_job,
)


def load_queue_metrics(tenant_id: str) -> dict:
    return get_queue_metrics(tenant_id)


def pause_admin_queue() -> None:
    pause_queue()


def resume_admin_queue() -> None:
    resume_queue()


def drain_admin_queue(tenant_id: str) -> int:
    return drain_queue(tenant_id)


def list_admin_jobs(*, tenant_id: str, limit: int = 50, status: str | None = None, job_type: str | None = None) -> list[dict]:
    return list_jobs_for_tenant(
        tenant_id=tenant_id,
        limit=limit,
        status=status,
        job_type=job_type,
    )


def get_admin_job_detail(job_id: str, tenant_id: str) -> dict | None:
    return get_job_detail_for_tenant(job_id, tenant_id)


def cancel_admin_job(job_id: str, tenant_id: str, *, actor_user_id: str | None = None) -> dict:
    return cancel_job(job_id, tenant_id, actor_user_id=actor_user_id)


def retry_admin_job(job_id: str, tenant_id: str, *, actor_user_id: str | None = None) -> dict:
    return retry_job(job_id, tenant_id, actor_user_id=actor_user_id)


def dead_letter_admin_job(job_id: str, tenant_id: str, *, actor_user_id: str | None = None) -> dict:
    return move_to_dead_letter(job_id, tenant_id, actor_user_id=actor_user_id)
