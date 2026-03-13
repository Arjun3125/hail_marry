"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type ResultItem = {
    name: string;
    avg: number;
    exams: Array<{ name: string; marks: number; max: number }>;
};

export default function ParentResultsPage() {
    const [items, setItems] = useState<ResultItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.parent.results();
                setItems((data || []) as ResultItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load results");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div className="space-y-4">
            <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Results</h1>
                <p className="text-sm text-[var(--text-secondary)]">Subject-wise academic performance.</p>
            </div>
            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}
            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading...</p>
            ) : (
                <div className="space-y-3">
                    {items.map((item) => (
                        <div key={item.name} className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center justify-between mb-3">
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">{item.name}</h2>
                                <span className="text-sm font-medium text-[var(--text-secondary)]">Avg: {item.avg}%</span>
                            </div>
                            <div className="space-y-2">
                                {item.exams.map((exam) => (
                                    <div key={exam.name} className="p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)] flex items-center justify-between">
                                        <p className="text-sm text-[var(--text-primary)]">{exam.name}</p>
                                        <p className="text-sm text-[var(--text-secondary)]">{exam.marks} / {exam.max}</p>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ))}
                    {items.length === 0 ? (
                        <p className="text-sm text-[var(--text-muted)]">No results found.</p>
                    ) : null}
                </div>
            )}
        </div>
    );
}
