"""Dedicated worker process for queued AI jobs."""
from __future__ import annotations

import asyncio
import contextlib
import logging
import os
import socket

from config import settings
from database import engine
from src.domains.platform.services.ai_queue import claim_next_job, process_job, recover_processing_jobs
from src.domains.platform.services.sentry_config import configure_sentry
from src.domains.platform.services.startup_checks import collect_dependency_status, enforce_startup_dependencies
from src.domains.platform.services.structured_logging import configure_structured_logging
from src.domains.platform.services.telemetry import configure_telemetry, instrument_sqlalchemy_engine
from src.domains.platform.services.worker_runtime import (
    mark_worker_failure,
    mark_worker_heartbeat,
    mark_worker_started,
    refresh_worker_heartbeat,
    mark_worker_success,
    update_dependency_status,
)
from src.shared.analytics import analytics

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


async def _run_periodic_aggregation() -> None:
    """Periodically aggregate tenant analytics. Resilient to missing tables."""
    from sqlalchemy.exc import ProgrammingError, OperationalError

    # Wait 30s on first run to give migrations time to complete
    await asyncio.sleep(30)

    while True:
        try:
            from src.domains.administrative.services.analytics_aggregator import run_analytics_aggregation
            await asyncio.to_thread(run_analytics_aggregation)
            await asyncio.sleep(900)  # 15 minutes
        except (ProgrammingError, OperationalError) as db_err:
            # Table doesn't exist yet (migrations haven't run) — wait and retry
            logger.warning("Analytics aggregation skipped (DB schema not ready): %s", type(db_err).__name__)
            await asyncio.sleep(120)  # Retry in 2 minutes
        except Exception as e:
            logger.error("Error in periodic aggregation task: %s", e)
            await asyncio.sleep(60)


async def _heartbeat_loop() -> None:
    interval = max(5, min(settings.worker_health.heartbeat_stale_seconds // 3, 20))
    while True:
        await asyncio.sleep(interval)
        try:
            refresh_worker_heartbeat()
        except Exception as exc:
            logger.warning("Heartbeat refresh failed: %s", exc)


def _raise_if_task_failed(task: asyncio.Task[None], name: str) -> None:
    if not task.done():
        return

    try:
        exc = task.exception()
    except asyncio.CancelledError as exc:
        raise RuntimeError(f"{name} task was cancelled unexpectedly") from exc

    if exc is not None:
        raise RuntimeError(f"{name} task crashed") from exc


async def worker_loop() -> None:
    # ── 1. DB bootstrap is handled by the worker entrypoint before this loop starts ──
    logger.info("Worker starting...")

    # ── 2. Startup dependency checks ──
    dependency_status = enforce_startup_dependencies("worker")
    update_dependency_status(dependency_status)
    mark_worker_started(WORKER_ID, dependency_status)

    # ── 3. Background tasks ──
    health_task = asyncio.create_task(_serve_worker_health())
    heartbeat_task = asyncio.create_task(_heartbeat_loop())
    aggregation_task = asyncio.create_task(_run_periodic_aggregation())

    # ── 4. Recover any stale jobs ──
    try:
        recovered = recover_processing_jobs()
        if recovered:
            logger.info("Recovered %s in-flight AI jobs back to the pending queue.", recovered)
    except Exception as e:
        logger.warning("Failed to recover jobs (queue may be disabled or unavailable): %s", e)

    logger.info("AI worker started.")

    # ── 5. Main job loop with exponential backoff ──
    consecutive_queue_failures = 0
    MAX_BACKOFF = 300  # 5 minutes max
    _queue_warned = False

    try:
        while True:
            _raise_if_task_failed(health_task, "worker health server")
            _raise_if_task_failed(heartbeat_task, "worker heartbeat")
            update_dependency_status(collect_dependency_status("worker"))
            mark_worker_heartbeat(status="idle")
            try:
                # Reset Redis availability cache periodically so we can reconnect
                if consecutive_queue_failures > 0 and consecutive_queue_failures % 10 == 0:
                    from src.domains.platform.services import ai_queue as _aq
                    _aq._redis_available = None

                job_id = await asyncio.to_thread(claim_next_job)
                consecutive_queue_failures = 0  # Reset on success
                if _queue_warned:
                    logger.info("Queue connection restored — processing jobs.")
                    _queue_warned = False
            except Exception as e:
                consecutive_queue_failures += 1
                backoff = min(15 * (2 ** (consecutive_queue_failures - 1)), MAX_BACKOFF)
                if not _queue_warned:
                    # Log once, then stay quiet
                    logger.info(
                        "Queue not available (%s). Worker will silently retry every %ds.",
                        e, MAX_BACKOFF,
                    )
                    _queue_warned = True
                await asyncio.sleep(backoff)
                continue

            if not job_id:
                continue

            logger.info("Processing AI job %s on worker %s", job_id, WORKER_ID)
            analytics.track_event(
                WORKER_ID, 
                "ai_worker_job_processed", 
                {"job_id": job_id, "worker_id": WORKER_ID}
            )
            mark_worker_heartbeat(status="running", job_id=job_id)
            try:
                result = await process_job(job_id, worker_id=WORKER_ID)
                if result and result.get("status") == "completed":
                    analytics.track_event(
                        WORKER_ID, 
                        "ai_worker_job_success", 
                        {"job_id": job_id, "worker_id": WORKER_ID}
                    )
                    mark_worker_success(job_id)
                else:
                    error_msg = result.get("error", "job did not complete") if result else "job missing"
                    analytics.track_event(
                        WORKER_ID, 
                        "ai_worker_job_failed", 
                        {"job_id": job_id, "worker_id": WORKER_ID, "error": error_msg}
                    )
                    mark_worker_failure(job_id, error_msg)
            except Exception as exc:
                analytics.track_event(
                    WORKER_ID, 
                    "ai_worker_job_exception", 
                    {"job_id": job_id, "worker_id": WORKER_ID, "error": str(exc)}
                )
                mark_worker_failure(job_id, str(exc))
                raise
    finally:
        health_task.cancel()
        heartbeat_task.cancel()
        aggregation_task.cancel()
        with contextlib.suppress(asyncio.CancelledError):
            await health_task
            await heartbeat_task
            await aggregation_task


if __name__ == "__main__":
    asyncio.run(worker_loop())
