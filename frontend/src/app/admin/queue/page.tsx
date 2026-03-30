"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
    Activity,
    AlertTriangle,
    Ban,
    Clock3,
    Loader2,
    RefreshCcw,
    RotateCcw,
    ServerCrash,
    ShieldAlert,
    Trash2,
    Workflow,
} from "lucide-react";

import { api } from "@/lib/api";

type QueueMetrics = {
    pending_depth: number;
    processing_depth: number;
    tracked_jobs: number;
    completed_last_window: number;
    failed_last_window: number;
    failure_rate_pct: number;
    retry_count: number;
    stuck_jobs: number;
    stuck_job_ids: string[];
    dead_letter_count: number;
    metrics_window_seconds: number;
    stuck_after_seconds: number;
    max_pending_jobs: number;
    max_pending_jobs_per_tenant: number;
    by_status: Record<string, number>;
    by_type: Record<string, number>;
};

type OCRMetricRow = {
    outcome: string;
    engine: string;
    count: number;
};

type QueueStatus = "queued" | "running" | "completed" | "failed" | "cancelled" | "dead_letter";

type QueueJob = {
    job_id: string;
    job_type: string;
    trace_id?: string | null;
    status: QueueStatus;
    created_at?: string | null;
    updated_at?: string | null;
    started_at?: string | null;
    completed_at?: string | null;
    attempts: number;
    max_retries: number;
    error?: string | null;
    priority?: number | null;
    worker_id?: string | null;
    duration_ms?: number | null;
    user_id?: string | null;
    user_name?: string | null;
    last_event?: {
        stage: string;
        source: string;
        timestamp: string;
        detail?: string | null;
    } | null;
};

type AuditHistoryEntry = {
    action: string;
    actor?: string | null;
    created_at: string;
    metadata?: Record<string, unknown> | null;
    job_id?: string | null;
};

type QueueJobDetail = QueueJob & {
    tenant_id?: string;
    request?: Record<string, unknown> | null;
    result?: unknown;
    events: Array<{
        stage: string;
        source: string;
        timestamp: string;
        detail?: string | null;
    }>;
    audit_history?: AuditHistoryEntry[];
};

const STATUS_OPTIONS = ["all", "queued", "running", "completed", "failed", "cancelled", "dead_letter"];
const JOB_TYPE_OPTIONS = [
    "all",
    "text_query",
    "audio_overview",
    "video_overview",
    "study_tool",
    "teacher_assessment",
    "url_ingest",
    "teacher_document_ingest",
    "teacher_youtube_ingest",
];

const statusClasses: Record<QueueStatus, string> = {
    queued: "bg-warning-subtle text-status-amber",
    running: "bg-info-subtle text-status-blue",
    completed: "bg-success-subtle text-status-green",
    failed: "bg-error-subtle text-status-red",
    cancelled: "bg-[var(--bg-hover)] text-[var(--text-secondary)]",
    dead_letter: "bg-violet-badge text-status-violet",
};

function formatDateTime(value?: string | null) {
    if (!value) return "-";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function formatDuration(value?: number | null) {
    if (value == null) return "-";
    if (value < 1000) return `${value}ms`;
    return `${(value / 1000).toFixed(1)}s`;
}

function formatWindow(seconds: number) {
    if (seconds % 3600 === 0) return `${seconds / 3600}h`;
    if (seconds % 60 === 0) return `${seconds / 60}m`;
    return `${seconds}s`;
}

export default function AdminQueuePage() {
    const [metrics, setMetrics] = useState<QueueMetrics | null>(null);
    const [jobs, setJobs] = useState<QueueJob[]>([]);
    const [ocrMetrics, setOcrMetrics] = useState<OCRMetricRow[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [detail, setDetail] = useState<QueueJobDetail | null>(null);
    const [history, setHistory] = useState<AuditHistoryEntry[]>([]);
    const [loading, setLoading] = useState(true);
    const [detailLoading, setDetailLoading] = useState(false);
    const [actionLoading, setActionLoading] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [statusFilter, setStatusFilter] = useState("all");
    const [jobTypeFilter, setJobTypeFilter] = useState("all");

    const queryParams = useMemo(() => ({
        limit: 100,
        status: statusFilter !== "all" ? statusFilter : undefined,
        job_type: jobTypeFilter !== "all" ? jobTypeFilter : undefined,
    }), [jobTypeFilter, statusFilter]);

    const loadDetail = async (jobId: string) => {
        try {
            setSelectedId(jobId);
            setDetailLoading(true);
            const payload = await api.admin.aiJobDetail(jobId);
            setDetail(payload as QueueJobDetail);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load AI job details");
        } finally {
            setDetailLoading(false);
        }
    };

    const loadData = async (preserveSelected = true) => {
        try {
            setLoading(true);
            setError(null);
            const [metricsPayload, jobsPayload, historyPayload] = await Promise.all([
                api.admin.aiJobsMetrics(),
                api.admin.aiJobs(queryParams),
                api.admin.aiJobsHistory(25),
            ]);
            const nextMetrics = metricsPayload as QueueMetrics;
            const nextJobs = (jobsPayload || []) as QueueJob[];
            setMetrics(nextMetrics);
            setJobs(nextJobs);
            setHistory((historyPayload || []) as AuditHistoryEntry[]);
            try {
                const ocrPayload = (await api.admin.ocrMetrics()) as { metrics?: OCRMetricRow[] };
                setOcrMetrics((ocrPayload?.metrics || []) as OCRMetricRow[]);
            } catch {
                setOcrMetrics([]);
            }

            const nextSelected = preserveSelected && selectedId
                ? nextJobs.find((job) => job.job_id === selectedId)?.job_id || nextJobs[0]?.job_id || null
                : nextJobs[0]?.job_id || null;
            if (nextSelected) {
                void loadDetail(nextSelected);
            } else {
                setSelectedId(null);
                setDetail(null);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load AI queue observability");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void loadData(false);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [queryParams]);

    useEffect(() => {
        const intervalId = window.setInterval(() => {
            void loadData(true);
        }, 10000);
        return () => window.clearInterval(intervalId);
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, [queryParams, selectedId]);

    const runAction = async (jobId: string, action: "cancel" | "retry" | "deadLetter") => {
        try {
            setActionLoading(`${action}:${jobId}`);
            if (action === "cancel") {
                await api.admin.cancelAIJob(jobId);
            } else if (action === "retry") {
                await api.admin.retryAIJob(jobId);
            } else {
                await api.admin.deadLetterAIJob(jobId);
            }
            await loadData(true);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Queue action failed");
        } finally {
            setActionLoading(null);
        }
    };

    return (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.15fr)_minmax(360px,0.85fr)]">
            <div className="space-y-6 min-w-0">
                <div className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Queue Operations</h1>
                        <p className="text-sm text-[var(--text-secondary)]">
                            Monitor queue health, control stuck or failed jobs, and review persistent audit history.
                        </p>
                    </div>
                    <button
                        type="button"
                        onClick={() => void loadData(true)}
                        className="inline-flex items-center gap-2 rounded-xl bg-code-block px-4 py-2 text-sm font-medium text-white hover:bg-[var(--bg-hover)]"
                    >
                        <RefreshCcw className="h-4 w-4" /> Refresh
                    </button>
                </div>

                {error ? (
                    <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                        {error}
                    </div>
                ) : null}

                <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
                    <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">Queue Depth</span>
                            <Activity className="h-4 w-4 text-[var(--primary)]" />
                        </div>
                        <p className="mt-3 text-2xl font-bold text-[var(--text-primary)]">{metrics ? metrics.pending_depth : "-"}</p>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">
                            Tenant cap {metrics ? metrics.max_pending_jobs_per_tenant : "-"} / global cap {metrics ? metrics.max_pending_jobs : "-"}.
                        </p>
                    </div>
                    <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">Worker Throughput</span>
                            <Workflow className="h-4 w-4 text-[var(--primary)]" />
                        </div>
                        <p className="mt-3 text-2xl font-bold text-[var(--text-primary)]">
                            {metrics ? metrics.completed_last_window : "-"}
                        </p>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">
                            Completed in the last {metrics ? formatWindow(metrics.metrics_window_seconds) : "window"}.
                        </p>
                    </div>
                    <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">Failure / Dead Letter</span>
                            <ServerCrash className="h-4 w-4 text-[var(--error)]" />
                        </div>
                        <p className="mt-3 text-2xl font-bold text-[var(--text-primary)]">
                            {metrics ? `${metrics.failure_rate_pct}% / ${metrics.dead_letter_count}` : "-"}
                        </p>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">
                            Recent failures and current dead-letter bucket size.
                        </p>
                    </div>
                    <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-[var(--text-secondary)]">Retries / Stuck</span>
                            <RotateCcw className="h-4 w-4 text-[var(--primary)]" />
                        </div>
                        <p className="mt-3 text-2xl font-bold text-[var(--text-primary)]">
                            {metrics ? `${metrics.retry_count} / ${metrics.stuck_jobs}` : "-"}
                        </p>
                        <p className="mt-1 text-xs text-[var(--text-muted)]">
                            Stuck means running longer than {metrics ? formatWindow(metrics.stuck_after_seconds) : "-"}.
                        </p>
                    </div>
                </div>

                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                    <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                        <div>
                            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Queued Jobs</h2>
                            <p className="text-sm text-[var(--text-secondary)]">
                                Tenant-fair, priority-ordered queue with admin controls for cancellation, retry, and dead-lettering.
                            </p>
                        </div>
                        <div className="flex flex-col gap-2 sm:flex-row">
                            <select
                                value={statusFilter}
                                onChange={(event) => setStatusFilter(event.target.value)}
                                className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm text-[var(--text-secondary)]"
                            >
                                {STATUS_OPTIONS.map((option) => (
                                    <option key={option} value={option}>{option}</option>
                                ))}
                            </select>
                            <select
                                value={jobTypeFilter}
                                onChange={(event) => setJobTypeFilter(event.target.value)}
                                className="rounded-xl border border-[var(--border)] px-3 py-2 text-sm text-[var(--text-secondary)]"
                            >
                                {JOB_TYPE_OPTIONS.map((option) => (
                                    <option key={option} value={option}>{option}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {loading ? (
                        <div className="mt-4 flex items-center gap-2 text-sm text-[var(--text-muted)]">
                            <Loader2 className="h-4 w-4 animate-spin" /> Loading queue state...
                        </div>
                    ) : jobs.length === 0 ? (
                        <p className="mt-4 text-sm text-[var(--text-muted)]">No jobs found for the current filters.</p>
                    ) : (
                        <div className="mt-4 overflow-x-auto">
                            <table className="min-w-full divide-y divide-[var(--border)] text-sm">
                                <thead>
                                    <tr className="text-left text-xs uppercase tracking-wide text-[var(--text-muted)]">
                                        <th className="py-3 pr-4">Job</th>
                                        <th className="py-3 pr-4">Requester</th>
                                        <th className="py-3 pr-4">Trace</th>
                                        <th className="py-3 pr-4">Attempts</th>
                                        <th className="py-3 pr-4">Priority</th>
                                        <th className="py-3 pr-4">Worker</th>
                                        <th className="py-3 pr-4">Duration</th>
                                        <th className="py-3 pr-4">State</th>
                                        <th className="py-3">Actions</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-slate-100">
                                    {jobs.map((job) => {
                                        const actionKeyBase = `${job.job_id}`;
                                        return (
                                            <tr
                                                key={job.job_id}
                                                onClick={() => void loadDetail(job.job_id)}
                                                className={`transition-colors hover:bg-[var(--bg-page)] ${selectedId === job.job_id ? "bg-info-subtle/60" : ""}`}
                                            >
                                                <td className="py-3 pr-4 align-top cursor-pointer">
                                                    <div className="font-medium text-[var(--text-primary)]">{job.job_type}</div>
                                                    <div className="text-xs text-[var(--text-muted)] break-all">{job.job_id}</div>
                                                    <div className="text-xs text-[var(--text-muted)]">{formatDateTime(job.created_at)}</div>
                                                </td>
                                                <td className="py-3 pr-4 align-top cursor-pointer text-[var(--text-secondary)]">{job.user_name || "Unknown"}</td>
                                                <td className="py-3 pr-4 align-top text-xs text-[var(--text-secondary)]">
                                                    {job.trace_id ? (
                                                        <Link
                                                            href={`/admin/traces?trace=${encodeURIComponent(job.trace_id)}`}
                                                            className="hover:text-[var(--primary)] hover:underline"
                                                            onClick={(event) => event.stopPropagation()}
                                                        >
                                                            {job.trace_id}
                                                        </Link>
                                                    ) : "-"}
                                                </td>
                                                <td className="py-3 pr-4 align-top cursor-pointer text-[var(--text-secondary)]">{job.attempts} / {job.max_retries + 1}</td>
                                                <td className="py-3 pr-4 align-top cursor-pointer text-[var(--text-secondary)]">{job.priority ?? "-"}</td>
                                                <td className="py-3 pr-4 align-top cursor-pointer text-xs text-[var(--text-secondary)]">{job.worker_id || "-"}</td>
                                                <td className="py-3 pr-4 align-top cursor-pointer text-[var(--text-secondary)]">{formatDuration(job.duration_ms)}</td>
                                                <td className="py-3 pr-4 align-top cursor-pointer">
                                                    <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-medium ${statusClasses[job.status]}`}>
                                                        {job.status}
                                                    </span>
                                                </td>
                                                <td className="py-3 align-top">
                                                    <div className="flex flex-wrap gap-2">
                                                        {job.status === "queued" ? (
                                                            <button
                                                                type="button"
                                                                onClick={(event) => {
                                                                    event.stopPropagation();
                                                                    void runAction(job.job_id, "cancel");
                                                                }}
                                                                className="inline-flex items-center gap-1 rounded-full bg-[var(--bg-hover)] px-3 py-1 text-xs font-medium text-[var(--text-secondary)] hover:bg-[var(--border)] disabled:opacity-60"
                                                                disabled={actionLoading === `cancel:${actionKeyBase}`}
                                                            >
                                                                {actionLoading === `cancel:${actionKeyBase}` ? <Loader2 className="h-3 w-3 animate-spin" /> : <Ban className="h-3 w-3" />} Cancel
                                                            </button>
                                                        ) : null}
                                                        {job.status === "failed" || job.status === "dead_letter" ? (
                                                            <button
                                                                type="button"
                                                                onClick={(event) => {
                                                                    event.stopPropagation();
                                                                    void runAction(job.job_id, "retry");
                                                                }}
                                                                className="inline-flex items-center gap-1 rounded-full bg-info-subtle px-3 py-1 text-xs font-medium text-status-blue hover:bg-info-badge disabled:opacity-60"
                                                                disabled={actionLoading === `retry:${actionKeyBase}`}
                                                            >
                                                                {actionLoading === `retry:${actionKeyBase}` ? <Loader2 className="h-3 w-3 animate-spin" /> : <RotateCcw className="h-3 w-3" />} Retry
                                                            </button>
                                                        ) : null}
                                                        {job.status === "failed" ? (
                                                            <button
                                                                type="button"
                                                                onClick={(event) => {
                                                                    event.stopPropagation();
                                                                    void runAction(job.job_id, "deadLetter");
                                                                }}
                                                                className="inline-flex items-center gap-1 rounded-full bg-violet-badge px-3 py-1 text-xs font-medium text-status-violet hover:bg-violet-badge disabled:opacity-60"
                                                                disabled={actionLoading === `deadLetter:${actionKeyBase}`}
                                                            >
                                                                {actionLoading === `deadLetter:${actionKeyBase}` ? <Loader2 className="h-3 w-3 animate-spin" /> : <Trash2 className="h-3 w-3" />} Dead Letter
                                                            </button>
                                                        ) : null}
                                                    </div>
                                                </td>
                                            </tr>
                                        );
                                    })}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>

                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                    <div className="flex items-center gap-2 mb-4">
                        <ShieldAlert className="h-4 w-4 text-[var(--primary)]" />
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Persistent Audit History</h2>
                    </div>
                    <div className="space-y-2">
                        {history.length === 0 ? (
                            <p className="text-sm text-[var(--text-muted)]">No historical queue audit events yet.</p>
                        ) : history.map((entry, index) => (
                            <div key={`${entry.job_id}-${entry.created_at}-${index}`} className="rounded-xl border border-[var(--border)] px-3 py-2">
                                <div className="flex items-center justify-between gap-3">
                                    <p className="text-xs font-medium text-[var(--text-primary)]">{entry.action}</p>
                                    <span className="text-[11px] text-[var(--text-muted)]">{formatDateTime(entry.created_at)}</span>
                                </div>
                                <p className="text-xs text-[var(--text-muted)] break-all">Job {entry.job_id || "-"}</p>
                                <p className="text-xs text-[var(--text-secondary)]">Actor: {entry.actor || "System"}</p>
                                {entry.metadata?.detail ? <p className="mt-1 text-xs text-[var(--text-secondary)]">{String(entry.metadata.detail)}</p> : null}
                            </div>
                        ))}
                    </div>
                </div>

                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                    <div className="flex items-center gap-2 mb-4">
                        <Workflow className="h-4 w-4 text-[var(--primary)]" />
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">OCR Observability</h2>
                    </div>
                    {ocrMetrics.length === 0 ? (
                        <p className="text-sm text-[var(--text-muted)]">No OCR metrics captured yet.</p>
                    ) : (
                        <div className="space-y-2">
                            {ocrMetrics.map((row) => (
                                <div
                                    key={`${row.outcome}-${row.engine}`}
                                    className="flex items-center justify-between rounded-xl border border-[var(--border)] px-3 py-2"
                                >
                                    <div>
                                        <p className="text-xs font-medium text-[var(--text-primary)] capitalize">{row.outcome.replace("_", " ")}</p>
                                        <p className="text-[11px] text-[var(--text-muted)]">{row.engine}</p>
                                    </div>
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{row.count}</p>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>

            <div className="h-fit rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)] xl:sticky xl:top-6">
                <div className="flex items-center gap-2 mb-4">
                    <Clock3 className="h-4 w-4 text-[var(--primary)]" />
                    <h2 className="text-sm font-semibold text-[var(--text-primary)]">Job Detail</h2>
                </div>

                {detailLoading ? (
                    <p className="text-sm text-[var(--text-muted)]">Loading job detail...</p>
                ) : !detail ? (
                    <p className="text-sm text-[var(--text-muted)]">Select a job to inspect queue timeline, audit history, and result payload.</p>
                ) : (
                    <div className="space-y-4 text-sm min-w-0">
                        <div className="grid gap-3 sm:grid-cols-2">
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-xs text-[var(--text-muted)]">Job Type</p>
                                <p className="font-medium text-[var(--text-primary)] break-words">{detail.job_type}</p>
                            </div>
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-xs text-[var(--text-muted)]">Trace ID</p>
                                <p className="font-medium text-[var(--text-primary)] break-all">{detail.trace_id || "-"}</p>
                            </div>
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-xs text-[var(--text-muted)]">Requester</p>
                                <p className="font-medium text-[var(--text-primary)]">{detail.user_name || "Unknown"}</p>
                            </div>
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-xs text-[var(--text-muted)]">Worker</p>
                                <p className="font-medium text-[var(--text-primary)] break-all">{detail.worker_id || "-"}</p>
                            </div>
                        </div>

                        {detail.error ? (
                            <div className="rounded-xl border border-error-subtle bg-error-subtle px-3 py-2 text-sm text-[var(--error)]">
                                <div className="flex items-start gap-2">
                                    <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0" />
                                    <span>{detail.error}</span>
                                </div>
                            </div>
                        ) : null}

                        <div>
                            <p className="mb-2 text-xs uppercase tracking-wide text-[var(--text-muted)]">Event Timeline</p>
                            <div className="space-y-2">
                                {detail.events.length === 0 ? (
                                    <p className="text-xs text-[var(--text-muted)]">No trace events recorded.</p>
                                ) : detail.events.map((event, index) => (
                                    <div key={`${event.timestamp}-${index}`} className="rounded-xl border border-[var(--border)] px-3 py-2">
                                        <div className="flex items-center justify-between gap-3">
                                            <p className="text-xs font-medium text-[var(--text-primary)]">{event.stage}</p>
                                            <span className="text-[11px] text-[var(--text-muted)]">{event.source}</span>
                                        </div>
                                        <p className="text-xs text-[var(--text-muted)]">{formatDateTime(event.timestamp)}</p>
                                        {event.detail ? <p className="mt-1 text-xs text-[var(--text-secondary)]">{event.detail}</p> : null}
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div>
                            <p className="mb-2 text-xs uppercase tracking-wide text-[var(--text-muted)]">Audit History</p>
                            <div className="space-y-2">
                                {detail.audit_history && detail.audit_history.length > 0 ? detail.audit_history.map((entry, index) => (
                                    <div key={`${entry.action}-${entry.created_at}-${index}`} className="rounded-xl border border-[var(--border)] px-3 py-2">
                                        <p className="text-xs font-medium text-[var(--text-primary)]">{entry.action}</p>
                                        <p className="text-xs text-[var(--text-muted)]">{formatDateTime(entry.created_at)} by {entry.actor || "System"}</p>
                                        {entry.metadata?.detail ? <p className="mt-1 text-xs text-[var(--text-secondary)]">{String(entry.metadata.detail)}</p> : null}
                                    </div>
                                )) : <p className="text-xs text-[var(--text-muted)]">No audit history recorded.</p>}
                            </div>
                        </div>

                        <div>
                            <p className="mb-2 text-xs uppercase tracking-wide text-[var(--text-muted)]">Request Snapshot</p>
                            <pre className="overflow-x-auto rounded-xl bg-code-block p-3 text-xs text-code-block">{JSON.stringify(detail.request ?? {}, null, 2)}</pre>
                        </div>

                        <div>
                            <p className="mb-2 text-xs uppercase tracking-wide text-[var(--text-muted)]">Result Snapshot</p>
                            <pre className="overflow-x-auto rounded-xl bg-code-block p-3 text-xs text-code-block">{JSON.stringify(detail.result ?? {}, null, 2)}</pre>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
