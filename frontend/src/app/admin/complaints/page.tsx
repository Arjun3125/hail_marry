"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, Clock, MessageSquareWarning } from "lucide-react";

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

type ComplaintStatus = "open" | "in_review" | "resolved";

type ComplaintItem = {
    id: string;
    student: string;
    category: string;
    description: string;
    status: ComplaintStatus;
    resolution_note: string;
    date: string;
};

type ComplaintPayload = {
    items: ComplaintItem[];
    summary: {
        total: number;
        open: number;
        in_review: number;
        resolved: number;
        resolved_last_30d: number;
        resolution_rate_pct: number;
    };
    monthly_activity: Array<{
        month: string;
        total: number;
        resolved: number;
    }>;
    categories: Array<{
        category: string;
        count: number;
    }>;
};

const statusConfig = {
    open: { icon: Clock, color: "text-[var(--warning)]", bg: "bg-warning-subtle" },
    in_review: { icon: AlertCircle, color: "text-[var(--primary)]", bg: "bg-info-subtle" },
    resolved: { icon: CheckCircle2, color: "text-[var(--success)]", bg: "bg-success-subtle" },
};

export default function AdminComplaintsPage() {
    const [items, setItems] = useState<ComplaintItem[]>([]);
    const [meta, setMeta] = useState<ComplaintPayload | null>(null);
    const [filter, setFilter] = useState<"all" | ComplaintStatus>("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [busyId, setBusyId] = useState<string | null>(null);

    const loadComplaints = async () => {
        const payload = (await api.admin.complaints()) as ComplaintPayload;
        setMeta(payload);
        setItems(payload?.items || []);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadComplaints();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load complaints");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const filtered = useMemo(() => {
        if (filter === "all") return items;
        return items.filter((item) => item.status === filter);
    }, [items, filter]);

    const summary = useMemo(() => ({
        open: meta?.summary.open ?? items.filter((item) => item.status === "open").length,
        inReview: meta?.summary.in_review ?? items.filter((item) => item.status === "in_review").length,
        resolved: meta?.summary.resolved ?? items.filter((item) => item.status === "resolved").length,
    }), [items, meta]);

    const updateStatus = async (id: string, status: ComplaintStatus) => {
        try {
            setBusyId(id);
            setError(null);
            await api.admin.updateComplaint(id, status, status === "resolved" ? "Resolved by admin review" : "");
            await loadComplaints();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update complaint");
        } finally {
            setBusyId(null);
        }
    };

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <MessageSquareWarning className="h-3.5 w-3.5" />
                            Student Concern Oversight
                        </PrismHeroKicker>
                    )}
                    title="Handle student complaints with clear follow-through"
                    description="This queue helps the institution respond to concerns quickly, document what changed, and keep trust visible for students and families."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Open</span>
                        <strong className="prism-status-value">{summary.open}</strong>
                        <span className="prism-status-detail">Complaints still waiting for first action</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">In review</span>
                        <strong className="prism-status-value">{summary.inReview}</strong>
                        <span className="prism-status-detail">Cases already under active school review</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Resolution rate</span>
                        <strong className="prism-status-value">{meta?.summary.resolution_rate_pct ?? 0}%</strong>
                        <span className="prism-status-detail">Share of complaint history that already has a recorded outcome</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation error={error} scope="admin-complaints" onRetry={() => window.location.reload()} />
                ) : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismSectionHeader
                        title="Complaint queue"
                        description="Use the filters to focus on unresolved issues and update the status once the school has responded."
                        actions={(
                            <div className="flex flex-wrap gap-2">
                                {(["all", "open", "in_review", "resolved"] as const).map((value) => (
                                    <button
                                        key={value}
                                        className={filter === value ? "prism-action" : "prism-action-secondary"}
                                        onClick={() => setFilter(value)}
                                        type="button"
                                    >
                                        {value.replace("_", " ")}
                                    </button>
                                ))}
                            </div>
                        )}
                    />

                    {loading ? (
                        <p className="text-sm text-[var(--text-secondary)]">Loading complaints...</p>
                    ) : filtered.length === 0 ? (
                        <EmptyState
                            icon={MessageSquareWarning}
                            title="No complaints in this view"
                            description="When students or parents raise issues, the filtered list will appear here with status and follow-up notes."
                            eyebrow="Queue empty"
                            scopeNote="Use the filters above to switch between open, in-review, and resolved complaint states."
                        />
                    ) : (
                        <div className="space-y-3">
                            {filtered.map((item) => {
                                const cfg = statusConfig[item.status];
                                const Icon = cfg.icon;
                                return (
                                    <div key={item.id} className="rounded-3xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                        <div className="flex flex-wrap items-start justify-between gap-3">
                                            <div>
                                                <div className="flex flex-wrap items-center gap-2">
                                                    <span className="text-sm font-semibold text-[var(--text-primary)]">{item.student}</span>
                                                    <span className="rounded-full bg-[var(--bg-page)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                                                        {item.category}
                                                    </span>
                                                </div>
                                                <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">{item.description}</p>
                                                {item.resolution_note ? (
                                                    <p className="mt-3 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.02)] px-3 py-2 text-xs text-[var(--text-secondary)]">
                                                        Resolution note: {item.resolution_note}
                                                    </p>
                                                ) : null}
                                            </div>
                                            <span className={`inline-flex items-center gap-1 rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${cfg.bg} ${cfg.color}`}>
                                                <Icon className="h-3.5 w-3.5" />
                                                {item.status.replace("_", " ")}
                                            </span>
                                        </div>

                                        <div className="mt-4 flex flex-wrap items-center justify-between gap-3">
                                            <span className="text-xs text-[var(--text-muted)]">{item.date}</span>
                                            {item.status !== "resolved" ? (
                                                <div className="flex flex-wrap gap-2">
                                                    <button
                                                        className="prism-action"
                                                        onClick={() => void updateStatus(item.id, "resolved")}
                                                        disabled={busyId === item.id}
                                                        type="button"
                                                    >
                                                        Mark resolved
                                                    </button>
                                                    <button
                                                        className="prism-action-secondary"
                                                        onClick={() => void updateStatus(item.id, "in_review")}
                                                        disabled={busyId === item.id}
                                                        type="button"
                                                    >
                                                        Move to review
                                                    </button>
                                                </div>
                                            ) : null}
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </PrismPanel>

                {meta ? (
                    <div className="grid gap-4 lg:grid-cols-[0.98fr_1.02fr]">
                        <PrismPanel className="space-y-4 p-5">
                            <PrismSectionHeader
                                title="Six-month complaint rhythm"
                                description="Show how the support queue has behaved over time in the demo school."
                            />
                            <div className="grid gap-3">
                                {meta.monthly_activity.map((item, index) => (
                                    <div key={`${item.month}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex items-center justify-between gap-4">
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{item.month}</p>
                                            <p className="text-xs text-[var(--text-muted)]">{item.total} opened</p>
                                        </div>
                                        <p className="mt-1 text-sm text-[var(--text-secondary)]">{item.resolved} resolved during the same monthly window.</p>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="space-y-4 p-5">
                            <PrismSectionHeader
                                title="Category mix"
                                description="Keep common complaint themes visible so the demo reflects real institutional follow-through."
                            />
                            <div className="space-y-3">
                                {meta.categories.map((item) => (
                                    <div key={item.category} className="flex items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{item.category}</p>
                                        <p className="text-sm text-[var(--text-secondary)]">{item.count}</p>
                                    </div>
                                ))}
                            </div>
                            <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Resolved in 30 days</p>
                                <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{meta.summary.resolved_last_30d}</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">Recent follow-through already visible in the seeded complaint history.</p>
                            </div>
                        </PrismPanel>
                    </div>
                ) : null}
            </PrismSection>
        </PrismPage>
    );
}
