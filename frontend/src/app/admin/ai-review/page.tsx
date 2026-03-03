"use client";

import { useEffect, useState } from "react";
import { Flag, CheckCircle2, Bot } from "lucide-react";

import { api } from "@/lib/api";

type ReviewItem = {
    id: string;
    user: string;
    query: string;
    response: string;
    mode: string;
    citations: number;
    response_time_ms: number;
    created_at: string;
};

export default function AIReviewPage() {
    const [items, setItems] = useState<ReviewItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.admin.aiReview();
                setItems((payload || []) as ReviewItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load AI review queue");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const formatDateTime = (value: string) => {
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Quality Review</h1>
                <p className="text-sm text-[var(--text-secondary)]">Review and audit AI responses for quality</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="space-y-3">
                {loading ? (
                    <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        Loading responses...
                    </div>
                ) : items.length === 0 ? (
                    <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        No responses available for review.
                    </div>
                ) : items.map((item) => (
                    <div key={item.id} className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                        <div className="flex items-center justify-between mb-3">
                            <div className="flex items-center gap-2">
                                <Bot className="w-4 h-4 text-[var(--primary)]" />
                                <span className="text-sm font-medium text-[var(--text-primary)]">{item.user}</span>
                                <span className="text-xs bg-[var(--primary-light)] text-[var(--primary)] px-2 py-0.5 rounded-full">{item.mode}</span>
                            </div>
                            <span className="text-xs text-[var(--text-muted)]">{formatDateTime(item.created_at)} | {item.response_time_ms}ms</span>
                        </div>
                        <p className="text-xs font-medium text-[var(--text-secondary)] mb-1">Q: {item.query}</p>
                        <p className="text-xs text-[var(--text-muted)] line-clamp-3 mb-3">{item.response}</p>
                        <div className="flex items-center justify-between">
                            <span className="text-xs text-[var(--text-muted)]">{item.citations} citations</span>
                            <div className="flex gap-2">
                                <button
                                    type="button"
                                    className="text-xs px-3 py-1.5 bg-green-50 text-[var(--success)] rounded-full font-medium flex items-center gap-1 opacity-60 cursor-not-allowed"
                                    disabled
                                >
                                    <CheckCircle2 className="w-3 h-3" /> Approve
                                </button>
                                <button
                                    type="button"
                                    className="text-xs px-3 py-1.5 bg-red-50 text-[var(--error)] rounded-full font-medium flex items-center gap-1 opacity-60 cursor-not-allowed"
                                    disabled
                                >
                                    <Flag className="w-3 h-3" /> Flag
                                </button>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
