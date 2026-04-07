"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import {
    Activity,
    AlertTriangle,
    Clock3,
    Loader2,
    Search,
    ShieldAlert,
    Workflow,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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

function formatDateTime(value?: string | null) {
    if (!value) return "-";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function AdminTracesPage() {
    const [traceId, setTraceId] = useState("");
    const [events, setEvents] = useState<TraceEvent[]>([]);
    const [loading, setLoading] = useState(false);
    const [summaryLoading, setSummaryLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [summary, setSummary] = useState<TraceabilitySummary | null>(null);
    const [loadedTraceId, setLoadedTraceId] = useState<string | null>(null);

    const loadTrace = async (value: string) => {
        const trimmed = value.trim();
        if (!trimmed) return;
        try {
            setLoading(true);
            setError(null);
            const payload = await api.admin.traceDetail(trimmed) as { trace_id: string; events: TraceEvent[] };
            setTraceId(payload.trace_id);
            setLoadedTraceId(payload.trace_id);
            setEvents(payload.events || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load trace");
            setLoadedTraceId(null);
            setEvents([]);
        } finally {
            setLoading(false);
        }
    };

    const loadSummary = async () => {
        try {
            setSummaryLoading(true);
            setError(null);
            const payload = await api.admin.traceabilitySummary(7);
            setSummary(payload as TraceabilitySummary);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load diagnostics summary");
            setSummary(null);
        } finally {
            setSummaryLoading(false);
        }
    };

    useEffect(() => {
        void loadSummary();

        const params = new URLSearchParams(window.location.search);
        const value = params.get("trace");
        if (value) {
            setTraceId(value);
            void loadTrace(value);
        }
    }, []);

    const heroMetrics = useMemo(() => {
        const highestGroup = summary?.grouped_errors?.[0];
        const busiestSubsystem = summary?.subsystem_totals?.[0];
        return {
            totalErrors: summary ? `${summary.total_errors}` : "-",
            highestGroup: highestGroup ? `${highestGroup.error_code} · ${highestGroup.count}` : "No grouped errors",
            busiestSubsystem: busiestSubsystem ? `${busiestSubsystem.subsystem} · ${busiestSubsystem.count}` : "No subsystem pressure",
        };
    }, [summary]);

    return (
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Workflow className="h-3.5 w-3.5" />
                            Admin Traceability Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Trace Viewer
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                Inspect persisted trace events across API, queue, worker, and AI service boundaries with one diagnostics-first admin surface.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <MetricCard
                            icon={AlertTriangle}
                            title="Total errors"
                            value={heroMetrics.totalErrors}
                            summary={summary ? `Last ${summary.period_days} days of traceability diagnostics` : "Traceability window summary"}
                            accent="amber"
                        />
                        <MetricCard
                            icon={ShieldAlert}
                            title="Highest pressure code"
                            value={heroMetrics.highestGroup}
                            summary="Most frequent grouped error across the active reporting window"
                            accent="blue"
                        />
                        <MetricCard
                            icon={Activity}
                            title="Busiest subsystem"
                            value={heroMetrics.busiestSubsystem}
                            summary="Subsystem with the highest recent traceability failure count"
                            accent="emerald"
                        />
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-traces"
                        onRetry={() => {
                            void loadSummary();
                            if (traceId.trim()) {
                                void loadTrace(traceId);
                            }
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(360px,0.92fr)]">
                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                                <div>
                                    <h2 className="text-lg font-semibold text-[var(--text-primary)]">Trace Diagnostics</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Review aggregate error pressure before drilling into a single trace.
                                    </p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    {summary ? `Generated ${formatDateTime(summary.generated_at)}` : "Awaiting diagnostics"}
                                </div>
                            </div>

                            {summaryLoading ? (
                                <div className="mt-4 flex items-center gap-2 text-sm text-[var(--text-muted)]">
                                    <Loader2 className="h-4 w-4 animate-spin" /> Loading diagnostics summary...
                                </div>
                            ) : summary ? (
                                <div className="mt-4 grid gap-4 sm:grid-cols-3">
                                    <CompactMetric title="Tracked period" value={`${summary.period_days} days`} />
                                    <CompactMetric title="Grouped codes" value={`${summary.grouped_errors.length}`} />
                                    <CompactMetric title="Recent failures" value={`${summary.recent_errors.length}`} />
                                </div>
                            ) : (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={Workflow}
                                        title="Diagnostics are not available"
                                        description="The traceability summary could not be loaded for this environment."
                                    />
                                </div>
                            )}
                        </PrismPanel>

                        <div className="grid gap-6 lg:grid-cols-[0.98fr_1.02fr]">
                            <PrismPanel className="p-5">
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Grouped Error Codes</h2>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Prioritize the failure families creating the most operational drag.
                                </p>
                                <div className="mt-4 space-y-3">
                                    {!summary || summary.grouped_errors.length === 0 ? (
                                        <p className="text-sm text-[var(--text-muted)]">No grouped traceability failures recorded.</p>
                                    ) : summary.grouped_errors.slice(0, 8).map((item) => (
                                        <div key={item.error_code} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                            <div className="flex items-start justify-between gap-3">
                                                <div>
                                                    <p className="font-mono text-sm font-semibold text-[var(--text-primary)]">{item.error_code}</p>
                                                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                        {item.title} · {item.subsystem}
                                                    </p>
                                                </div>
                                                <span className="rounded-full bg-[var(--bg-page)] px-2.5 py-1 text-xs font-semibold text-[var(--text-primary)]">
                                                    {item.count}
                                                </span>
                                            </div>
                                            <div className="mt-3 flex flex-wrap items-center gap-2 text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                                <span>{item.severity}</span>
                                                <span>Latest {formatDateTime(item.latest_at)}</span>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Subsystem Totals</h2>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Compare where traceability pressure is accumulating across the stack.
                                </p>
                                <div className="mt-4 space-y-3">
                                    {!summary || summary.subsystem_totals.length === 0 ? (
                                        <p className="text-sm text-[var(--text-muted)]">No subsystem failures recorded.</p>
                                    ) : summary.subsystem_totals.map((item) => (
                                        <div key={item.subsystem} className="flex items-center justify-between rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{item.subsystem}</span>
                                            <span className="text-sm font-semibold text-[var(--text-primary)]">{item.count}</span>
                                        </div>
                                    ))}
                                </div>
                            </PrismPanel>
                        </div>

                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent Failures</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Use recent path, method, and trace references to decide which incident to open first.
                                    </p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    {summary?.recent_errors.length ?? 0} records
                                </div>
                            </div>

                            <div className="mt-4 space-y-3">
                                {!summary || summary.recent_errors.length === 0 ? (
                                    <p className="text-sm text-[var(--text-muted)]">No recent failures recorded.</p>
                                ) : summary.recent_errors.slice(0, 10).map((item, index) => (
                                    <div key={`${item.created_at}-${item.error_code}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                            <div>
                                                <p className="font-mono text-sm font-semibold text-[var(--text-primary)]">{item.error_code}</p>
                                                <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                    {item.subsystem} · {item.method} {item.path}
                                                </p>
                                            </div>
                                            <div className="text-right text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                                <div>{item.severity}</div>
                                                <div className="mt-1">{formatDateTime(item.created_at)}</div>
                                            </div>
                                        </div>
                                        <p className="mt-3 text-sm leading-6 text-[var(--text-primary)]">{item.detail}</p>
                                        {item.trace_id ? (
                                            <div className="mt-3 text-xs text-[var(--text-muted)]">
                                                Trace:{" "}
                                                <button
                                                    type="button"
                                                    className="font-medium text-[var(--primary)] hover:underline"
                                                    onClick={() => {
                                                        setTraceId(item.trace_id);
                                                        void loadTrace(item.trace_id);
                                                    }}
                                                >
                                                    {item.trace_id}
                                                </button>
                                            </div>
                                        ) : null}
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    </div>

                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5 xl:sticky xl:top-6">
                            <div className="flex items-center gap-2">
                                <Search className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Trace Lookup</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Paste a trace ID from queue, error summaries, or incident notes to inspect the full event chain.
                            </p>

                            <form
                                className="mt-4 flex flex-col gap-3"
                                onSubmit={(event) => {
                                    event.preventDefault();
                                    void loadTrace(traceId);
                                }}
                            >
                                <input
                                    value={traceId}
                                    onChange={(event) => setTraceId(event.target.value)}
                                    placeholder="Paste a trace id"
                                    className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                />
                                <button
                                    type="submit"
                                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-3 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5"
                                >
                                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                                    Load Trace
                                </button>
                            </form>

                            <div className="mt-4 grid gap-3 sm:grid-cols-2">
                                <CompactMetric title="Loaded trace" value={loadedTraceId ?? "None"} />
                                <CompactMetric title="Events loaded" value={`${events.length}`} />
                            </div>

                            <div className="mt-4 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Linked workflow</p>
                                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                    Move from trace analysis back to queue control when the incident requires cancel, retry, or dead-letter intervention.
                                </p>
                                <div className="mt-3 text-sm">
                                    <Link href="/admin/queue" className="font-medium text-[var(--primary)] hover:underline">
                                        Jump to AI Queue
                                    </Link>
                                </div>
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <div className="flex items-center gap-2">
                                <Clock3 className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Trace Timeline</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Event-by-event view of the selected trace, including raw metadata snapshots for debugging.
                            </p>

                            <div className="mt-4 space-y-3">
                                {loading ? (
                                    <div className="flex items-center gap-2 text-sm text-[var(--text-muted)]">
                                        <Loader2 className="h-4 w-4 animate-spin" /> Loading trace detail...
                                    </div>
                                ) : events.length === 0 ? (
                                    <EmptyState
                                        icon={Workflow}
                                        title="No trace events loaded"
                                        description="Load a trace ID from the summary or queue to inspect the event chain."
                                    />
                                ) : events.map((event, index) => (
                                    <div key={`${event.created_at}-${event.action}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                                            <div>
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{event.action}</p>
                                                <p className="mt-1 text-xs text-[var(--text-secondary)]">{event.entity_type}</p>
                                            </div>
                                            <span className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                                {formatDateTime(event.created_at)}
                                            </span>
                                        </div>
                                        <pre className="mt-3 overflow-x-auto rounded-2xl bg-code-block p-3 text-xs text-code-block">
                                            {JSON.stringify(event.metadata, null, 2)}
                                        </pre>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    icon: Icon,
    title,
    value,
    summary,
    accent,
}: {
    icon: typeof Activity;
    title: string;
    value: string;
    summary: string;
    accent: "blue" | "emerald" | "amber";
}) {
    const accentClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))] text-status-blue",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))] text-status-emerald",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))] text-status-amber",
    } as const;

    return (
        <PrismPanel className="p-4">
            <div className={`mb-3 flex h-11 w-11 items-center justify-center rounded-2xl ${accentClasses[accent]}`}>
                <Icon className="h-5 w-5" />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </PrismPanel>
    );
}

function CompactMetric({ title, value }: { title: string; value: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 break-all text-sm font-semibold text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
