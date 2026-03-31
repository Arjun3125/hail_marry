"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Loader2, Search, Workflow } from "lucide-react";

import { api } from "@/lib/api";

type TraceEvent = {
    created_at: string;
    action: string;
    entity_type: string;
    metadata: Record<string, unknown>;
};

type TraceabilitySummary = {
    generated_at: string;
    period_days: number;
    total_errors: number;
    grouped_errors: Array<{
        error_code: string;
        title: string;
        subsystem: string;
        severity: string;
        count: number;
        latest_at: string;
    }>;
    subsystem_totals: Array<{
        subsystem: string;
        count: number;
    }>;
    recent_errors: Array<{
        created_at: string;
        error_code: string;
        subsystem: string;
        severity: string;
        detail: string;
        path: string;
        method: string;
        status_code: number;
        trace_id: string;
    }>;
};

export default function AdminTracesPage() {
    const [traceId, setTraceId] = useState("");
    const [events, setEvents] = useState<TraceEvent[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [summary, setSummary] = useState<TraceabilitySummary | null>(null);

    const loadTrace = async (value: string) => {
        if (!value.trim()) return;
        try {
            setLoading(true);
            setError(null);
            const payload = await api.admin.traceDetail(value.trim()) as { trace_id: string; events: TraceEvent[] };
            setTraceId(payload.trace_id);
            setEvents(payload.events || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load trace");
            setEvents([]);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void api.admin.traceabilitySummary(7)
            .then((payload) => setSummary(payload as TraceabilitySummary))
            .catch((err) => setError(err instanceof Error ? err.message : "Failed to load diagnostics summary"));

        const params = new URLSearchParams(window.location.search);
        const value = params.get("trace");
        if (value) {
            setTraceId(value);
            void loadTrace(value);
        }
    }, []);

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Trace Viewer</h1>
                <p className="text-sm text-[var(--text-secondary)]">Inspect persisted trace events across API, queue, worker, and AI service boundaries.</p>
            </div>

            <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                <form
                    className="flex flex-col gap-3 sm:flex-row"
                    onSubmit={(event) => {
                        event.preventDefault();
                        void loadTrace(traceId);
                    }}
                >
                    <input
                        value={traceId}
                        onChange={(event) => setTraceId(event.target.value)}
                        placeholder="Paste a trace id"
                        className="flex-1 rounded-xl border border-[var(--border)] px-4 py-2 text-sm text-[var(--text-primary)]"
                    />
                    <button
                        type="submit"
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-code-block px-4 py-2 text-sm font-medium text-white hover:bg-[var(--bg-hover)]"
                    >
                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Load Trace
                    </button>
                </form>
                {error ? <p className="mt-3 text-sm text-[var(--error)]">{error}</p> : null}
            </div>

            <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                <div className="mb-4 flex items-center gap-2">
                    <Workflow className="h-4 w-4 text-[var(--primary)]" />
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent Error Codes</h2>
                </div>
                {summary ? (
                    <div className="space-y-5">
                        <div className="grid gap-3 md:grid-cols-3">
                            <div className="rounded-xl border border-[var(--border)] px-4 py-3">
                                <p className="text-xs text-[var(--text-muted)]">Total errors</p>
                                <p className="text-lg font-semibold text-[var(--text-primary)]">{summary.total_errors}</p>
                            </div>
                            <div className="rounded-xl border border-[var(--border)] px-4 py-3">
                                <p className="text-xs text-[var(--text-muted)]">Tracked period</p>
                                <p className="text-lg font-semibold text-[var(--text-primary)]">{summary.period_days} days</p>
                            </div>
                            <div className="rounded-xl border border-[var(--border)] px-4 py-3">
                                <p className="text-xs text-[var(--text-muted)]">Generated at</p>
                                <p className="text-sm font-semibold text-[var(--text-primary)]">{new Date(summary.generated_at).toLocaleString()}</p>
                            </div>
                        </div>

                        <div className="grid gap-4 lg:grid-cols-2">
                            <div className="space-y-3">
                                <h3 className="text-sm font-semibold text-[var(--text-primary)]">Grouped by error code</h3>
                                {summary.grouped_errors.length === 0 ? (
                                    <p className="text-sm text-[var(--text-muted)]">No traceability failures recorded.</p>
                                ) : summary.grouped_errors.slice(0, 8).map((item) => (
                                    <div key={item.error_code} className="rounded-xl border border-[var(--border)] px-4 py-3">
                                        <div className="flex items-center justify-between gap-3">
                                            <div>
                                                <p className="font-mono text-sm text-[var(--text-primary)]">{item.error_code}</p>
                                                <p className="text-xs text-[var(--text-secondary)]">{item.title} • {item.subsystem}</p>
                                            </div>
                                            <span className="rounded-full bg-[var(--bg-page)] px-2 py-1 text-xs font-semibold text-[var(--text-primary)]">{item.count}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>

                            <div className="space-y-3">
                                <h3 className="text-sm font-semibold text-[var(--text-primary)]">Subsystem totals</h3>
                                {summary.subsystem_totals.length === 0 ? (
                                    <p className="text-sm text-[var(--text-muted)]">No subsystem failures recorded.</p>
                                ) : summary.subsystem_totals.map((item) => (
                                    <div key={item.subsystem} className="flex items-center justify-between rounded-xl border border-[var(--border)] px-4 py-3">
                                        <span className="text-sm text-[var(--text-primary)]">{item.subsystem}</span>
                                        <span className="font-semibold text-[var(--text-primary)]">{item.count}</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="space-y-3">
                            <h3 className="text-sm font-semibold text-[var(--text-primary)]">Recent failures</h3>
                            {summary.recent_errors.length === 0 ? (
                                <p className="text-sm text-[var(--text-muted)]">No recent failures recorded.</p>
                            ) : summary.recent_errors.slice(0, 10).map((item, index) => (
                                <div key={`${item.created_at}-${item.error_code}-${index}`} className="rounded-xl border border-[var(--border)] px-4 py-3">
                                    <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                        <div>
                                            <p className="font-mono text-sm text-[var(--text-primary)]">{item.error_code}</p>
                                            <p className="text-xs text-[var(--text-secondary)]">{item.subsystem} • {item.method} {item.path}</p>
                                        </div>
                                        <span className="text-xs text-[var(--text-muted)]">{new Date(item.created_at).toLocaleString()}</span>
                                    </div>
                                    <p className="mt-2 text-sm text-[var(--text-primary)]">{item.detail}</p>
                                    {item.trace_id ? (
                                        <p className="mt-2 text-xs text-[var(--text-muted)]">Trace: {item.trace_id}</p>
                                    ) : null}
                                </div>
                            ))}
                        </div>
                    </div>
                ) : (
                    <p className="text-sm text-[var(--text-muted)]">Loading diagnostics summary...</p>
                )}
            </div>

            <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-5 shadow-[var(--shadow-card)]">
                <div className="flex items-center gap-2 mb-4">
                    <Workflow className="h-4 w-4 text-[var(--primary)]" />
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Trace Timeline</h2>
                </div>
                <div className="space-y-3">
                    {events.length === 0 ? (
                        <p className="text-sm text-[var(--text-muted)]">No trace events loaded.</p>
                    ) : events.map((event, index) => (
                        <div key={`${event.created_at}-${event.action}-${index}`} className="rounded-xl border border-[var(--border)] px-4 py-3">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{event.action}</p>
                                    <p className="text-xs text-[var(--text-muted)]">{event.entity_type}</p>
                                </div>
                                <span className="text-xs text-[var(--text-muted)]">{new Date(event.created_at).toLocaleString()}</span>
                            </div>
                            <pre className="mt-3 overflow-x-auto rounded-xl bg-code-block p-3 text-xs text-code-block">{JSON.stringify(event.metadata, null, 2)}</pre>
                        </div>
                    ))}
                </div>
            </div>

            <div className="text-sm text-[var(--text-secondary)]">
                Jump from queue operations: <Link href="/admin/queue" className="text-[var(--primary)] hover:underline">AI Queue</Link>
            </div>
        </div>
    );
}
