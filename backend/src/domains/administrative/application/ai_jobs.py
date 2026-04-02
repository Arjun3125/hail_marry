"""Application helpers for admin AI job workflows."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session


def build_ai_job_list_response(
    *,
    db: Session,
    tenant_id,
    limit: int,
    status: str | None,
    job_type: str | None,
    list_admin_jobs_fn,
    resolve_user_names_fn,
) -> list[dict]:
    jobs = list_admin_jobs_fn(
        tenant_id=str(tenant_id),
        limit=limit,
        status=status,
        job_type=job_type,
    )
    user_map = resolve_user_names_fn(db, [job.get("user_id") for job in jobs])
    for job in jobs:
        job["user_name"] = user_map.get(job.get("user_id"), "Unknown") if job.get("user_id") else None
    return jobs


def build_ai_job_detail_response(
    *,
    db: Session,
    tenant_id,
    job_id: str,
    get_admin_job_detail_fn,
    resolve_user_names_fn,
    ai_job_audit_history_fn,
) -> dict:
    job = get_admin_job_detail_fn(job_id, str(tenant_id))
    if not job:
        raise HTTPException(status_code=404, detail="AI job not found")

    user_map = resolve_user_names_fn(db, [job.get("user_id")])
    job["user_name"] = user_map.get(job.get("user_id"), "Unknown") if job.get("user_id") else None
    job["audit_history"] = ai_job_audit_history_fn(
        db,
        tenant_id=tenant_id,
        job_id=job_id,
        limit=100,
    )
    return job
