"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { Flag, CheckCircle2, Bot, Loader2, Search, ShieldAlert } from "lucide-react";

import { api } from "@/lib/api";

type ReviewItem = {
    id: string;
    user: string;
    query: string;
    response: string;
    mode: string;
    citations: number;
    response_time_ms: number;
    trace_id: string | null;
    created_at: string;
    review_status: "pending" | "approved" | "flagged";
    review_note?: string | null;
    reviewed_at?: string | null;
    reviewed_by?: string | null;
};

type ReviewDetail = ReviewItem & {
    token_usage?: number | null;
    review_history: Array<{
        action: string;
        note?: string | null;
        reviewed_by?: string | null;
        created_at: string;
    }>;
};

const statusClasses: Record<ReviewItem["review_status"], string> = {
    pending: "bg-warning-subtle text-status-amber",
    approved: "bg-success-subtle text-status-green",
    flagged: "bg-error-subtle text-status-red",
};

export default function AIReviewPage() {
    const [items, setItems] = useState<ReviewItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [detail, setDetail] = useState<ReviewDetail | null>(null);
    const [detailLoading, setDetailLoading] = useState(false);
    const [actioningId, setActioningId] = useState<string | null>(null);

    const loadItems = async (focusId?: string) => {
        try {
            setLoading(true);
            setError(null);
            const payload = await api.admin.aiReview();
            const nextItems = (payload || []) as ReviewItem[];
            setItems(nextItems);
            if (!focusId && nextItems.length > 0 && !selectedId) {
                focusId = nextItems[0].id;
            }
            if (focusId) {
                void loadDetail(focusId);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load AI review queue");
        } finally {
            setLoading(false);
        }
    };

    const loadDetail = async (id: string) => {
        try {
            setSelectedId(id);
            setDetailLoading(true);
            const payload = await api.admin.aiReviewDetail(id);
            setDetail(payload as ReviewDetail);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load AI trace details");
        } finally {
            setDetailLoading(false);
        }
    };

    useEffect(() => {
        void loadItems();
        // eslint-disable-next-line react-hooks/exhaustive-deps
    }, []);

    const formatDateTime = (value?: string | null) => {
        if (!value) return "—";
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
    };

    const handleReviewAction = async (item: ReviewItem, action: "approve" | "flag") => {
        const note = window.prompt(
            action === "flag"
                ? "Add a note for why this response is flagged"
                : "Optional approval note",
            item.review_note || ""
        );
        if (note === null) return;

        try {
            setActioningId(item.id);
            await api.admin.updateAIReview(item.id, { action, note });
            await loadItems(item.id);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update review");
        } finally {
            setActioningId(null);
        }
    };

    return (
        <div className="grid gap-6 xl:grid-cols-[minmax(0,1.2fr)_minmax(340px,0.8fr)]">
            <div>
                <div className="mb-6">
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Quality Review</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Approve, flag, and inspect grounded AI responses.</p>
                </div>

                {error ? (
                    <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                        {error}
                    </div>
                ) : null}

                <div className="space-y-3">
                    {loading ? (
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                            Loading responses...
                        </div>
                    ) : items.length === 0 ? (
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                            No responses available for review.
                        </div>
                    ) : items.map((item) => (
                        <div
                            key={item.id}
                            className={`bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 border transition-colors ${selectedId === item.id ? "border-[var(--primary)]" : "border-transparent"}`}
                        >
                            <div className="flex items-center justify-between mb-3 gap-3">
                                <div className="flex items-center gap-2 min-w-0">
                                    <Bot className="w-4 h-4 text-[var(--primary)]" />
                                    <span className="text-sm font-medium text-[var(--text-primary)] truncate">{item.user}</span>
                                    <span className="text-xs bg-[var(--primary-light)] text-[var(--primary)] px-2 py-0.5 rounded-full">{item.mode}</span>
                                    <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${statusClasses[item.review_status]}`}>
                                        {item.review_status}
                                    </span>
                                </div>
                                <span className="text-xs text-[var(--text-muted)] shrink-0">{formatDateTime(item.created_at)} | {item.response_time_ms}ms</span>
                            </div>
                            <p className="text-xs font-medium text-[var(--text-secondary)] mb-1">Q: {item.query}</p>
                            <p className="text-xs text-[var(--text-muted)] line-clamp-3 mb-3">{item.response}</p>
                            {item.review_note ? (
                                <p className="mb-3 rounded-xl bg-[var(--bg-page)] px-3 py-2 text-xs text-[var(--text-secondary)]">
                                    Review note: {item.review_note}
                                </p>
                            ) : null}
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div className="text-xs text-[var(--text-muted)]">
                                    {item.citations} citations
                                    {item.trace_id ? (
                                        <>
                                            {" • "}
                                            <Link
                                                href={`/admin/traces?trace=${encodeURIComponent(item.trace_id)}`}
                                                className="text-[var(--primary)] hover:underline"
                                            >
                                                Trace {item.trace_id}
                                            </Link>
                                        </>
                                    ) : null}
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    <button
                                        type="button"
                                        onClick={() => void loadDetail(item.id)}
                                        className="text-xs px-3 py-1.5 bg-[var(--bg-hover)] text-[var(--text-secondary)] rounded-full font-medium flex items-center gap-1 hover:bg-[var(--border)] transition-colors"
                                    >
                                        <Search className="w-3 h-3" /> Details
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => void handleReviewAction(item, "approve")}
                                        className="text-xs px-3 py-1.5 bg-success-subtle text-[var(--success)] rounded-full font-medium flex items-center gap-1 hover:bg-success-badge transition-colors disabled:opacity-60"
                                        disabled={actioningId === item.id}
                                    >
                                        {actioningId === item.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <CheckCircle2 className="w-3 h-3" />} Approve
                                    </button>
                                    <button
                                        type="button"
                                        onClick={() => void handleReviewAction(item, "flag")}
                                        className="text-xs px-3 py-1.5 bg-error-subtle text-[var(--error)] rounded-full font-medium flex items-center gap-1 hover:bg-error-badge transition-colors disabled:opacity-60"
                                        disabled={actioningId === item.id}
                                    >
                                        {actioningId === item.id ? <Loader2 className="w-3 h-3 animate-spin" /> : <Flag className="w-3 h-3" />} Flag
                                    </button>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 h-fit xl:sticky xl:top-6">
                <div className="flex items-center gap-2 mb-4">
                    <ShieldAlert className="w-4 h-4 text-[var(--primary)]" />
                    <h2 className="text-sm font-semibold text-[var(--text-primary)]">Trace Viewer</h2>
                </div>

                {detailLoading ? (
                    <p className="text-sm text-[var(--text-muted)]">Loading trace details...</p>
                ) : !detail ? (
                    <p className="text-sm text-[var(--text-muted)]">Select a response to inspect query, trace, and review history.</p>
                ) : (
                    <div className="space-y-4 text-sm">
                        <div>
                            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)] mb-1">Query</p>
                            <p className="text-[var(--text-primary)]">{detail.query}</p>
                        </div>
                        <div>
                            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)] mb-1">Response</p>
                            <p className="text-[var(--text-secondary)] whitespace-pre-wrap">{detail.response}</p>
                        </div>
                        <div className="grid grid-cols-2 gap-3 text-xs">
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-[var(--text-muted)] mb-1">Trace ID</p>
                                <p className="font-medium text-[var(--text-primary)]">{detail.trace_id || "—"}</p>
                            </div>
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-[var(--text-muted)] mb-1">Token Usage</p>
                                <p className="font-medium text-[var(--text-primary)]">{detail.token_usage ?? "—"}</p>
                            </div>
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-[var(--text-muted)] mb-1">Status</p>
                                <p className="font-medium text-[var(--text-primary)]">{detail.review_status}</p>
                            </div>
                            <div className="rounded-xl bg-[var(--bg-page)] p-3">
                                <p className="text-[var(--text-muted)] mb-1">Reviewed At</p>
                                <p className="font-medium text-[var(--text-primary)]">{formatDateTime(detail.reviewed_at)}</p>
                            </div>
                        </div>
                        <div>
                            <p className="text-xs uppercase tracking-wide text-[var(--text-muted)] mb-2">Review History</p>
                            <div className="space-y-2">
                                {detail.review_history.length === 0 ? (
                                    <p className="text-xs text-[var(--text-muted)]">No review actions yet.</p>
                                ) : detail.review_history.map((entry, index) => (
                                    <div key={`${entry.created_at}-${index}`} className="rounded-xl border border-[var(--border)] px-3 py-2">
                                        <p className="text-xs font-medium text-[var(--text-primary)]">{entry.action}</p>
                                        <p className="text-xs text-[var(--text-muted)]">{formatDateTime(entry.created_at)} by {entry.reviewed_by || "Unknown reviewer"}</p>
                                        {entry.note ? <p className="text-xs text-[var(--text-secondary)] mt-1">{entry.note}</p> : null}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
