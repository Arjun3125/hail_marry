"""Local background runtime for deferred automation jobs.

This keeps teacher/parent automation off the request or tool-execution path
without depending on an external worker during local and demo deployments.

Uses a single event loop running in a dedicated thread to avoid:
- Multiple asyncio.run() calls causing thread safety issues
- Event loop conflicts in concurrent scenarios
- Resource leaks from creating/destroying loops per job
"""
from __future__ import annotations

import asyncio
import logging
import os
import threading
from collections.abc import Awaitable, Callable
from concurrent.futures import Future
from typing import Any

logger = logging.getLogger(__name__)

_MAX_AUTOMATION_WORKERS = max(1, int(os.getenv("VIDYA_AUTOMATION_WORKERS", "4")))

# Single event loop thread - prevents multiple asyncio.run() calls
_event_loop: asyncio.AbstractEventLoop | None = None
_loop_thread: threading.Thread | None = None
_loop_lock = threading.Lock()


def _get_or_create_event_loop() -> asyncio.AbstractEventLoop:
    """Get or create the background automation event loop."""
    global _event_loop, _loop_thread
    
    with _loop_lock:
        if _event_loop is None or not _loop_thread.is_alive():
            _event_loop = asyncio.new_event_loop()
            
            def _run_loop():
                asyncio.set_event_loop(_event_loop)
                _event_loop.run_forever()
            
            _loop_thread = threading.Thread(
                target=_run_loop,
                name="vidya-automation-eventloop",
                daemon=True
            )
            _loop_thread.start()
            logger.info("Started automation background event loop")
        
        return _event_loop


def submit_async_job(
    job_name: str,
    coroutine_fn: Callable[..., Awaitable[Any]],
    *args,
    **kwargs,
) -> Future[Any]:
    """Run an async automation job on the shared background event loop.
    
    Jobs are submitted to a single event loop running in a dedicated thread,
    preventing thread safety issues from multiple asyncio.run() calls.
    """
    loop = _get_or_create_event_loop()
    
    # Create coroutine
    coro = coroutine_fn(*args, **kwargs)
    
    # Submit to the shared event loop (thread-safe)
    future = asyncio.run_coroutine_threadsafe(coro, loop)
    
    def _log_completion(done: Future[Any]) -> None:
        try:
            done.result(timeout=1)
            logger.debug("Automation job %s completed successfully", job_name)
        except asyncio.TimeoutError:
            logger.error("Automation job %s timed out", job_name)
        except Exception:
            logger.exception("Automation job %s failed", job_name)
    
    # Add callback to log results
    future.add_done_callback(_log_completion)
    return future

    def _log_failure(done: Future[Any]) -> None:
        try:
            done.result()
        except Exception:
            logger.exception("Automation job %s failed", job_name)

    future.add_done_callback(_log_failure)
    return future
