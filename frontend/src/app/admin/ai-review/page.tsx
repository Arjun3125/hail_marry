"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { Bot, CheckCircle2, Flag, Loader2, Search, ShieldAlert } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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

    const summary = useMemo(() => ({
        pending: items.filter((item) => item.review_status === "pending").length,
        flagged: items.filter((item) => item.review_status === "flagged").length,
        approved: items.filter((item) => item.review_status === "approved").length,
    }), [items]);

    const formatDateTime = (value?: string | null) => {
        if (!value) return "—";
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
    };

    const formatReviewedDateTime = (value?: string | null) => {
        if (!value) return "Not reviewed";
        return formatDateTime(value);
    };

    const handleReviewAction = async (item: ReviewItem, action: "approve" | "flag") => {
        const note = window.prompt(
            action === "flag"
                ? "Add a note for why this response should be reviewed more closely."
                : "Optional note for the reviewer log.",
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
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ShieldAlert className="h-3.5 w-3.5" />
                            AI Quality Oversight
                        </PrismHeroKicker>
                    )}
                    title="Review grounded AI before it reaches trust issues"
                    description="Use this queue to inspect citations, trace quality, and reviewer notes so the student-facing experience stays safe, accurate, and academically grounded."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Pending review</span>
                        <strong className="prism-status-value">{summary.pending}</strong>
                        <span className="prism-status-detail">Responses waiting for staff judgment</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Flagged</span>
                        <strong className="prism-status-value">{summary.flagged}</strong>
                        <span className="prism-status-detail">Responses needing follow-up or prompt fixes</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Approved</span>
                        <strong className="prism-status-value">{summary.approved}</strong>
                        <span className="prism-status-detail">Reviewed answers that match the expected standard</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-ai-review"
                        onRetry={() => {
                            void loadItems(selectedId ?? undefined);
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(340px,0.92fr)]">
                    <PrismPanel className="space-y-4 p-5">
                        <PrismSectionHeader
                            title="Review queue"
                            description="Open the most recent responses first and check whether the answer, citations, and trace line up with student-safe expectations."
                        />

                        {loading ? (
                            <p className="text-sm text-[var(--text-secondary)]">Loading review queue...</p>
                        ) : items.length === 0 ? (
                            <EmptyState
                                icon={Bot}
                                title="No responses waiting for review"
                                description="The current queue is clear. New answers that require human review will appear here automatically."
                                eyebrow="Queue clear"
                                scopeNote="This surface only shows responses that have entered the AI quality review workflow."
                            />
                        ) : (
                            <div className="space-y-3">
                                {items.map((item) => (
                                    <div
                                        key={item.id}
                                        className={`rounded-3xl border p-4 transition-colors ${selectedId === item.id ? "border-[var(--primary)] bg-[rgba(96,165,250,0.08)]" : "border-[var(--border)] bg-[rgba(255,255,255,0.02)]"}`}
                                    >
                                        <div className="flex flex-wrap items-start justify-between gap-3">
                                            <div className="min-w-0 space-y-2">
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <span className="inline-flex items-center gap-2 text-sm font-semibold text-[var(--text-primary)]">
                                                        <Bot className="h-4 w-4 text-[var(--primary)]" />
                                                        {item.user}
                                                    </span>
                                                    <span className="rounded-full bg-[var(--primary-light)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--primary)]">
                                                        {item.mode}
                                                    </span>
                                                    <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${statusClasses[item.review_status]}`}>
                                                        {item.review_status}
                                                    </span>
                                                </div>
                                                <p className="text-sm font-medium text-[var(--text-primary)]">Q: {item.query}</p>
                                                <p className="text-sm leading-6 text-[var(--text-secondary)] line-clamp-3">{item.response}</p>
                                                {item.review_note ? (
                                                    <p className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-2 text-xs text-[var(--text-secondary)]">
                                                        Reviewer note: {item.review_note}
                                                    </p>
                                                ) : null}
                                            </div>
                                            <div className="text-right text-xs text-[var(--text-muted)]">
                                                <p>{formatDateTime(item.created_at)}</p>
                                                <p>{item.response_time_ms} ms</p>
                                            </div>
                                        </div>

                                        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                                            <div className="text-xs text-[var(--text-muted)]">
                                                {item.citations} citations
                                                {item.trace_id ? (
                                                    <>
                                                        {" • "}
                                                        <Link
                                                            href={`/admin/traces?trace=${encodeURIComponent(item.trace_id)}`}
                                                            className="text-[var(--primary)] hover:underline"
                                                        >
                                                            Open trace
                                                        </Link>
                                                    </>
                                                ) : null}
                                            </div>
                                            <div className="flex flex-wrap gap-2">
                                                <button
                                                    type="button"
                                                    onClick={() => void loadDetail(item.id)}
                                                    className="prism-action-secondary"
                                                >
                                                    <Search className="h-3.5 w-3.5" />
                                                    Details
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => void handleReviewAction(item, "approve")}
                                                    className="inline-flex items-center gap-2 rounded-full bg-success-subtle px-4 py-2 text-xs font-semibold text-status-green transition hover:opacity-90 disabled:opacity-60"
                                                    disabled={actioningId === item.id}
                                                >
                                                    {actioningId === item.id ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <CheckCircle2 className="h-3.5 w-3.5" />}
                                                    Approve
                                                </button>
                                                <button
                                                    type="button"
                                                    onClick={() => void handleReviewAction(item, "flag")}
                                                    className="inline-flex items-center gap-2 rounded-full bg-error-subtle px-4 py-2 text-xs font-semibold text-status-red transition hover:opacity-90 disabled:opacity-60"
                                                    disabled={actioningId === item.id}
                                                >
                                                    {actioningId === item.id ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Flag className="h-3.5 w-3.5" />}
                                                    Flag
                                                </button>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </PrismPanel>

                    <PrismPanel className="space-y-4 p-5 xl:sticky xl:top-6">
                        <PrismSectionHeader
                            title="Trace viewer"
                            description="Check the exact query, response, usage, and review history before marking the answer safe for student-facing use."
                        />

                        {detailLoading ? (
                            <p className="text-sm text-[var(--text-secondary)]">Loading trace details...</p>
                        ) : !detail ? (
                            <EmptyState
                                icon={ShieldAlert}
                                title="Select a response to inspect"
                                description="The right rail shows the exact answer, trace details, and reviewer history for the selected queue item."
                                eyebrow="Trace detail"
                            />
                        ) : (
                            <div className="space-y-4 text-sm">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Query</p>
                                    <p className="mt-2 text-[var(--text-primary)]">{detail.query}</p>
                                </div>
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Response</p>
                                    <p className="mt-2 whitespace-pre-wrap leading-6 text-[var(--text-secondary)]">{detail.response}</p>
                                </div>
                                <div className="grid grid-cols-2 gap-3">
                                    <InfoTile label="Trace ID" value={detail.trace_id || "Unavailable"} />
                                    <InfoTile label="Token usage" value={`${detail.token_usage ?? "Not captured"}`} />
                                    <InfoTile label="Status" value={detail.review_status} />
                                    <InfoTile label="Reviewed" value={formatReviewedDateTime(detail.reviewed_at)} />
                                </div>
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Review history</p>
                                    <div className="mt-3 space-y-2">
                                        {detail.review_history.length === 0 ? (
                                            <p className="text-sm text-[var(--text-secondary)]">No review actions recorded yet.</p>
                                        ) : detail.review_history.map((entry, index) => (
                                            <div key={`${entry.created_at}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{entry.action}</p>
                                                <p className="mt-1 text-xs text-[var(--text-muted)]">
                                                    {formatDateTime(entry.created_at)} by {entry.reviewed_by || "Unknown reviewer"}
                                                </p>
                                                {entry.note ? <p className="mt-2 text-sm text-[var(--text-secondary)]">{entry.note}</p> : null}
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}
                    </PrismPanel>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function InfoTile({ label, value }: { label: string; value: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-3">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-sm font-medium text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
