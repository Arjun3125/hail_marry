"""Async AI Auto-Grading Queue — non-blocking batch grading for teachers.

When a teacher uploads a stack of answer sheets (common scenario: 40 papers
after a unit test), this module queues them for AI grading in the background
so the teacher doesn't wait for each paper to finish OCR + LLM evaluation.

Architecture:
- Teacher uploads → immediate ACK with job_id
- Background worker processes jobs from an in-memory queue
- Results are stored in DB and pushed to teacher via WebSocket notification
- Supports concurrent grading with configurable worker count
"""
from __future__ import annotations

import asyncio
import logging
import time
from dataclasses import dataclass, field
from typing import Any
from uuid import uuid4

from src.domains.platform.services.ai_grading import run_ai_grade
from src.domains.platform.services.notifications import add_notification

logger = logging.getLogger(__name__)

# ── Job queue ────────────────────────────────────────────────────────
MAX_CONCURRENT_WORKERS = 3
_job_queue: asyncio.Queue | None = None
_results: dict[str, dict[str, Any]] = {}
_teacher_index: dict[str, set[str]] = {}
_worker_started = False


@dataclass
class GradingJob:
    """A single AI grading job in the queue."""
    job_id: str = field(default_factory=lambda: uuid4().hex)
    teacher_id: str = ""
    tenant_id: str = ""
    file_path: str = ""
    file_name: str = ""
    answer_key: str = ""
    rubric: str = ""
    student_name: str = ""
    submitted_at: float = field(default_factory=time.time)
    status: str = "queued"  # queued, processing, completed, failed


def _get_queue() -> asyncio.Queue:
    global _job_queue
    if _job_queue is None:
        _job_queue = asyncio.Queue(maxsize=500)
    return _job_queue


async def enqueue_grading_job(
    *,
    teacher_id: str,
    tenant_id: str,
    file_path: str,
    file_name: str = "",
    answer_key: str = "",
    rubric: str = "",
    student_name: str = "",
) -> dict[str, Any]:
    """Enqueue a grading job and return immediately with a job_id.

    The teacher gets an instant response and can continue uploading.
    Results will be pushed via WebSocket notification when ready.
    """
    job = GradingJob(
        teacher_id=teacher_id,
        tenant_id=tenant_id,
        file_path=file_path,
        file_name=file_name or file_path.split("/")[-1].split("\\")[-1],
        answer_key=answer_key,
        rubric=rubric,
        student_name=student_name,
    )

    _results[job.job_id] = {
        "job_id": job.job_id,
        "teacher_id": teacher_id,
        "status": "queued",
        "file_name": job.file_name,
        "student_name": job.student_name,
        "submitted_at": job.submitted_at,
        "result": None,
    }
    _teacher_index.setdefault(teacher_id, set()).add(job.job_id)

    queue = _get_queue()
    await queue.put(job)

    # Auto-start workers if not already running
    _ensure_workers_started()

    logger.info(
        "Grading job %s queued for teacher %s (%d in queue)",
        job.job_id, teacher_id, queue.qsize(),
    )

    return {
        "job_id": job.job_id,
        "status": "queued",
        "queue_position": queue.qsize(),
        "estimated_wait_seconds": queue.qsize() * 15,  # ~15s per paper
    }


async def enqueue_batch_grading(
    *,
    teacher_id: str,
    tenant_id: str,
    files: list[dict[str, str]],
    answer_key: str = "",
    rubric: str = "",
) -> dict[str, Any]:
    """Enqueue multiple grading jobs at once (batch upload).

    Args:
        files: List of dicts with keys: file_path, file_name, student_name
    """
    job_ids = []
    for f in files:
        result = await enqueue_grading_job(
            teacher_id=teacher_id,
            tenant_id=tenant_id,
            file_path=f["file_path"],
            file_name=f.get("file_name", ""),
            answer_key=answer_key,
            rubric=rubric,
            student_name=f.get("student_name", ""),
        )
        job_ids.append(result["job_id"])

    return {
        "batch_size": len(files),
        "job_ids": job_ids,
        "estimated_total_seconds": len(files) * 15,
    }


def get_job_status(job_id: str) -> dict[str, Any] | None:
    """Check the status of a grading job."""
    return _results.get(job_id)


def get_teacher_jobs(teacher_id: str) -> list[dict[str, Any]]:
    """Get all grading jobs for a teacher, newest first."""
    jobs = [
        _results[job_id]
        for job_id in _teacher_index.get(teacher_id, set())
        if job_id in _results
    ]
    return sorted(jobs, key=lambda j: j.get("submitted_at", 0), reverse=True)


# ── Background workers ──────────────────────────────────────────────

def _ensure_workers_started():
    """Start background worker tasks if not already running."""
    global _worker_started
    if _worker_started:
        return
    _worker_started = True

    try:
        loop = asyncio.get_event_loop()
        for i in range(MAX_CONCURRENT_WORKERS):
            loop.create_task(_grading_worker(worker_id=i))
        logger.info("Started %d AI grading workers", MAX_CONCURRENT_WORKERS)
    except RuntimeError:
        logger.warning("Cannot start grading workers — no event loop")


async def _grading_worker(worker_id: int):
    """Background worker that processes grading jobs from the queue."""
    queue = _get_queue()

    while True:
        try:
            job: GradingJob = await queue.get()

            logger.info("Worker %d processing job %s (%s)", worker_id, job.job_id, job.file_name)

            # Update status
            if job.job_id in _results:
                _results[job.job_id]["status"] = "processing"
                _results[job.job_id]["teacher_id"] = job.teacher_id

            start_time = time.time()

            try:
                result = await run_ai_grade(
                    payload={
                        "file_path": job.file_path,
                        "file_name": job.file_name,
                        "answer_key": job.answer_key,
                        "rubric": job.rubric,
                    },
                    tenant_id=job.tenant_id,
                )

                elapsed = round(time.time() - start_time, 2)
                result["student_name"] = job.student_name
                result["grading_time_seconds"] = elapsed

                if job.job_id in _results:
                    _results[job.job_id]["status"] = "completed"
                    _results[job.job_id]["result"] = result

                # Notify teacher via WebSocket
                score_display = ""
                if result.get("ai_score") is not None:
                    score_display = f" — Score: {result['ai_score']}/{result.get('ai_max_score', '?')}"

                add_notification(
                    job.teacher_id,
                    title="✅ Grading Complete",
                    body=f"*{job.student_name or job.file_name}*{score_display}",
                    category="grading",
                    data={
                        "job_id": job.job_id,
                        "ai_score": result.get("ai_score"),
                        "ai_max_score": result.get("ai_max_score"),
                    },
                )

                logger.info(
                    "Job %s completed in %.2fs (score: %s/%s)",
                    job.job_id, elapsed,
                    result.get("ai_score"), result.get("ai_max_score"),
                )

            except Exception as exc:
                logger.exception("Job %s failed: %s", job.job_id, exc)
                if job.job_id in _results:
                    _results[job.job_id]["status"] = "failed"
                    _results[job.job_id]["result"] = {"error": str(exc)}

                add_notification(
                    job.teacher_id,
                    title="❌ Grading Failed",
                    body=f"Could not grade *{job.student_name or job.file_name}*. Please retry.",
                    category="grading",
                    data={"job_id": job.job_id, "error": str(exc)[:200]},
                )

            finally:
                queue.task_done()

        except asyncio.CancelledError:
            break
        except Exception:
            logger.exception("Grading worker %d encountered an error", worker_id)
            await asyncio.sleep(1)  # Brief backoff on unexpected errors
