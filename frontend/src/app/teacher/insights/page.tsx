"use client";

import { useEffect, useState } from "react";
import { BarChart3, AlertTriangle, TrendingUp } from "lucide-react";

import { api } from "@/lib/api";

type InsightSubject = {
    subject: string;
    avg_pct: number;
    is_weak: boolean;
};

type ClassInsight = {
    class: string;
    subjects: InsightSubject[];
    weak_topics: string[];
    recommendation: string;
};

export default function TeacherInsightsPage() {
    const [insights, setInsights] = useState<ClassInsight[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.insights();
                setInsights(((payload as { insights?: ClassInsight[] })?.insights || []) as ClassInsight[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load insights");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Class Insights</h1>
                <p className="text-sm text-[var(--text-secondary)]">Performance analytics and weak topic detection</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                    Loading insights...
                </div>
            ) : insights.length === 0 ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                    No class insights available yet.
                </div>
            ) : insights.map((cls) => (
                <div key={cls.class} className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 mb-4">
                    <div className="flex items-center justify-between mb-4">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">{cls.class}</h2>
                        <span className="flex items-center gap-1.5 text-xs text-[var(--primary)] font-medium">
                            <BarChart3 className="w-3.5 h-3.5" /> AI Analysis
                        </span>
                    </div>

                    <div className="space-y-3 mb-4">
                        {cls.subjects.map((subject) => (
                            <div key={subject.subject} className="flex items-center gap-3">
                                <span className="w-24 text-xs text-[var(--text-secondary)]">{subject.subject}</span>
                                <div className="flex-1 h-6 bg-[var(--bg-page)] rounded-full overflow-hidden">
                                    <div
                                        className={`h-full rounded-full transition-all ${subject.is_weak ? "bg-[var(--error)]" : subject.avg_pct >= 80 ? "bg-[var(--success)]" : "bg-[var(--primary)]"}`}
                                        style={{ width: `${subject.avg_pct}%` }}
                                    />
                                </div>
                                <span className={`text-xs font-bold w-10 text-right ${subject.is_weak ? "text-[var(--error)]" : "text-[var(--text-primary)]"}`}>
                                    {subject.avg_pct}%
                                </span>
                                {subject.is_weak ? <AlertTriangle className="w-3.5 h-3.5 text-[var(--error)]" /> : null}
                            </div>
                        ))}
                    </div>

                    {cls.weak_topics.length > 0 ? (
                        <div className="p-3 bg-error-subtle rounded-[var(--radius-sm)] mb-3">
                            <p className="text-xs font-medium text-[var(--error)] mb-1">Weak Topics Detected</p>
                            <div className="flex flex-wrap gap-1.5">
                                {cls.weak_topics.map((topic) => (
                                    <span key={topic} className="text-[10px] bg-[var(--bg-card)] text-[var(--error)] px-2 py-0.5 rounded-full">{topic}</span>
                                ))}
                            </div>
                        </div>
                    ) : null}

                    <div className="p-3 bg-[var(--primary-light)] rounded-[var(--radius-sm)]">
                        <p className="text-xs text-[var(--primary)] font-medium flex items-center gap-1.5">
                            <TrendingUp className="w-3.5 h-3.5" /> {cls.recommendation}
                        </p>
                    </div>
                </div>
            ))}
        </div>
    );
}
