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

export default function AdminTracesPage() {
    const [traceId, setTraceId] = useState("");
    const [events, setEvents] = useState<TraceEvent[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

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
                        className="inline-flex items-center justify-center gap-2 rounded-xl bg-slate-900 px-4 py-2 text-sm font-medium text-white hover:bg-slate-800"
                    >
                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />} Load Trace
                    </button>
                </form>
                {error ? <p className="mt-3 text-sm text-[var(--error)]">{error}</p> : null}
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
                            <pre className="mt-3 overflow-x-auto rounded-xl bg-slate-950 p-3 text-xs text-slate-100">{JSON.stringify(event.metadata, null, 2)}</pre>
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
