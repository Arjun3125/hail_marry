"use client";

import { useEffect, useMemo, useState } from "react";
import { Clock, CheckCircle2, AlertCircle } from "lucide-react";

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

const statusConfig = {
    open: { icon: Clock, color: "text-[var(--warning)]", bg: "bg-yellow-50" },
    in_review: { icon: AlertCircle, color: "text-[var(--primary)]", bg: "bg-blue-50" },
    resolved: { icon: CheckCircle2, color: "text-[var(--success)]", bg: "bg-green-50" },
};

export default function AdminComplaintsPage() {
    const [items, setItems] = useState<ComplaintItem[]>([]);
    const [filter, setFilter] = useState<"all" | ComplaintStatus>("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [busyId, setBusyId] = useState<string | null>(null);

    const loadComplaints = async () => {
        const payload = await api.admin.complaints();
        setItems((payload || []) as ComplaintItem[]);
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
        return items.filter((i) => i.status === filter);
    }, [items, filter]);

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
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Complaint Oversight</h1>
                <p className="text-sm text-[var(--text-secondary)]">Review and manage student complaints</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="flex gap-3 mb-4">
                {(["all", "open", "in_review", "resolved"] as const).map((value) => (
                    <button
                        key={value}
                        className={`text-xs px-3 py-1.5 rounded-full border capitalize ${filter === value
                            ? "bg-[var(--primary)] border-[var(--primary)] text-white"
                            : "bg-[var(--bg-card)] border-[var(--border)] text-[var(--text-secondary)] hover:bg-[var(--primary-light)] hover:text-[var(--primary)]"
                            }`}
                        onClick={() => setFilter(value)}
                    >
                        {value.replace("_", " ")}
                    </button>
                ))}
            </div>

            <div className="space-y-3">
                {loading ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        Loading complaints...
                    </div>
                ) : filtered.length === 0 ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        No complaints found.
                    </div>
                ) : filtered.map((item) => {
                    const cfg = statusConfig[item.status];
                    const Icon = cfg.icon;
                    return (
                        <div key={item.id} className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                            <div className="flex items-center justify-between mb-2">
                                <div className="flex items-center gap-2">
                                    <span className="text-sm font-medium text-[var(--text-primary)]">{item.student}</span>
                                    <span className="text-xs bg-[var(--bg-page)] text-[var(--text-muted)] px-2 py-0.5 rounded-full">{item.category}</span>
                                </div>
                                <span className={`flex items-center gap-1 text-xs font-medium px-2.5 py-1 rounded-full ${cfg.bg} ${cfg.color} capitalize`}>
                                    <Icon className="w-3 h-3" /> {item.status.replace("_", " ")}
                                </span>
                            </div>
                            <p className="text-sm text-[var(--text-secondary)] mb-2">{item.description}</p>
                            {item.resolution_note ? (
                                <p className="text-xs text-[var(--text-muted)] mb-2">Resolution: {item.resolution_note}</p>
                            ) : null}
                            <div className="flex items-center justify-between">
                                <span className="text-xs text-[var(--text-muted)]">{item.date}</span>
                                {item.status !== "resolved" ? (
                                    <div className="flex gap-2">
                                        <button
                                            className="text-xs px-3 py-1.5 bg-[var(--primary)] text-white rounded-[var(--radius-sm)] font-medium disabled:opacity-60"
                                            onClick={() => void updateStatus(item.id, "resolved")}
                                            disabled={busyId === item.id}
                                        >
                                            Mark Resolved
                                        </button>
                                        <button
                                            className="text-xs px-3 py-1.5 bg-yellow-50 text-[var(--warning)] rounded-[var(--radius-sm)] font-medium disabled:opacity-60"
                                            onClick={() => void updateStatus(item.id, "in_review")}
                                            disabled={busyId === item.id}
                                        >
                                            In Review
                                        </button>
                                    </div>
                                ) : null}
                            </div>
                        </div>
                    );
                })}
            </div>
        </div>
    );
}
