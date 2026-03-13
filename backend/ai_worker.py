"""Dedicated worker process for queued AI jobs."""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import socket

from config import settings
from database import engine
from services.ai_queue import claim_next_job, process_job, recover_processing_jobs
from services.sentry_config import configure_sentry
from services.startup_checks import collect_dependency_status, enforce_startup_dependencies
from services.structured_logging import configure_structured_logging
from services.telemetry import configure_telemetry, instrument_sqlalchemy_engine
from services.worker_runtime import (
    mark_worker_failure,
    mark_worker_heartbeat,
    mark_worker_started,
    mark_worker_success,
    update_dependency_status,
)

configure_structured_logging(service_name="vidyaos-ai-worker")
configure_sentry(service_name="vidyaos-ai-worker")
configure_telemetry(service_name="vidyaos-ai-worker")
instrument_sqlalchemy_engine(engine)
logger = logging.getLogger("ai-worker")
WORKER_ID = f"{socket.gethostname()}:{os.getpid()}"


async def _serve_worker_health() -> None:
    if not settings.worker_health.enabled:
        return

    import uvicorn
    from worker_health_app import app as worker_health_app

    config = uvicorn.Config(
        worker_health_app,
        host=settings.worker_health.host,
        port=settings.worker_health.port,
        log_level="warning",
    )
    server = uvicorn.Server(config)
    await server.serve()


async def worker_loop() -> None:
    dependency_status = enforce_startup_dependencies("worker")
    update_dependency_status(dependency_status)
    mark_worker_started(WORKER_ID, dependency_status)
    health_task = asyncio.create_task(_serve_worker_health())

    recovered = recover_processing_jobs()
    if recovered:
        logger.info("Recovered %s in-flight AI jobs back to the pending queue.", recovered)

    logger.info("AI worker started.")
    try:
        while True:
            update_dependency_status(collect_dependency_status("worker"))
            mark_worker_heartbeat(status="idle")
            job_id = await asyncio.to_thread(claim_next_job)
            if not job_id:
                continue

            logger.info("Processing AI job %s on worker %s", job_id, WORKER_ID)
            mark_worker_heartbeat(status="running", job_id=job_id)
            try:
                result = await process_job(job_id, worker_id=WORKER_ID)
                if result and result.get("status") == "completed":
                    mark_worker_success(job_id)
                else:
                    mark_worker_failure(job_id, result.get("error", "job did not complete") if result else "job missing")
            except Exception as exc:
                mark_worker_failure(job_id, str(exc))
                raise
    finally:
        health_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await health_task


if __name__ == "__main__":
    asyncio.run(worker_loop())
