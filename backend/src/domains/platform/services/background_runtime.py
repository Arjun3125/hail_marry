"""Local background runtime for deferred automation jobs.

This keeps teacher/parent automation off the request or tool-execution path
without depending on an external worker during local and demo deployments.
"""
from __future__ import annotations

import asyncio
import logging
import os
from collections.abc import Awaitable, Callable
from concurrent.futures import Future, ThreadPoolExecutor
from typing import Any

logger = logging.getLogger(__name__)

_MAX_AUTOMATION_WORKERS = max(1, int(os.getenv("VIDYA_AUTOMATION_WORKERS", "4")))
_AUTOMATION_EXECUTOR = ThreadPoolExecutor(
    max_workers=_MAX_AUTOMATION_WORKERS,
    thread_name_prefix="vidya-automation",
)


def submit_async_job(
    job_name: str,
    coroutine_fn: Callable[..., Awaitable[Any]],
    *args,
    **kwargs,
) -> Future[Any]:
    """Run an async automation job on the local bounded runtime."""

    def _runner() -> Any:
        return asyncio.run(coroutine_fn(*args, **kwargs))

    future = _AUTOMATION_EXECUTOR.submit(_runner)

    def _log_failure(done: Future[Any]) -> None:
        try:
            done.result()
        except Exception:
            logger.exception("Automation job %s failed", job_name)

    future.add_done_callback(_log_failure)
    return future
