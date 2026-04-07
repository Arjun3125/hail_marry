"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, Award, BookOpen, Sparkles } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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
            } catch (loadError) {
                setError(loadError instanceof Error ? loadError.message : "Failed to load results");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const summary = useMemo(() => {
        if (items.length === 0) return { subjects: 0, average: 0, strongest: null as ResultItem | null };
        const totalAverage = items.reduce((sum, item) => sum + item.avg, 0);
        const strongest = [...items].sort((left, right) => right.avg - left.avg)[0] ?? null;
        return {
            subjects: items.length,
            average: Math.round(totalAverage / items.length),
            strongest,
        };
    }, [items]);

    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Award className="h-3.5 w-3.5" />
                            Parent Results Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black text-[var(--text-primary)] md:text-5xl">
                                Results
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                A clear academic summary that highlights overall progress, strongest subjects, and the latest exam detail without overwhelming the parent view.
                            </p>
                        </div>
                    </div>
                    <PrismPanel className="p-5">
                        <h2 className="text-base font-semibold text-[var(--text-primary)]">Academic snapshot</h2>
                        <div className="mt-4 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                            <MetricCard label="Subjects" value={`${summary.subjects}`} tone="blue" />
                            <MetricCard label="Average" value={`${summary.average}%`} tone="emerald" />
                            <MetricCard label="Strongest" value={summary.strongest ? summary.strongest.name : "No data"} tone="amber" />
                        </div>
                    </PrismPanel>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="parent-results"
                        onRetry={() => window.location.reload()}
                    />
                ) : null}

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">Loading academic results...</p>
                    </PrismPanel>
                ) : (
                    <div className="grid gap-4 lg:grid-cols-[1.04fr_0.96fr]">
                        <PrismPanel className="p-5">
                            <div className="flex items-center gap-2">
                                <BookOpen className="h-4 w-4 text-status-blue" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Subject performance</h2>
                            </div>
                            {items.length > 0 ? (
                                <div className="mt-4 space-y-4">
                                    {items.map((item) => (
                                        <div key={item.name} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                            <div className="flex items-center justify-between gap-4">
                                                <div>
                                                    <h3 className="text-base font-semibold text-[var(--text-primary)]">{item.name}</h3>
                                                    <p className="mt-1 text-sm text-[var(--text-secondary)]">Average score: {item.avg}%</p>
                                                </div>
                                                <span className="rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--text-secondary)]">
                                                    {item.exams.length} exam{item.exams.length === 1 ? "" : "s"}
                                                </span>
                                            </div>
                                            <div className="mt-4 space-y-2">
                                                {item.exams.map((exam) => (
                                                    <div key={exam.name} className="flex items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.02)] px-4 py-3">
                                                        <p className="text-sm text-[var(--text-primary)]">{exam.name}</p>
                                                        <p className="text-sm font-medium text-[var(--text-secondary)]">{exam.marks} / {exam.max}</p>
                                                    </div>
                                                ))}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={BookOpen}
                                        title="No results found"
                                        description="Academic results will appear here once the next assessment data is recorded."
                                    />
                                </div>
                            )}
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <div className="flex items-center gap-2">
                                <Sparkles className="h-4 w-4 text-status-amber" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">What stands out</h2>
                            </div>
                            <div className="mt-4 space-y-4 text-sm leading-6 text-[var(--text-secondary)]">
                                <p>
                                    This view is designed to keep the story simple: where the student is strongest, whether scores are holding steady, and which subject may need encouragement next.
                                </p>
                                <p>
                                    {summary.strongest
                                        ? `${summary.strongest.name} is currently the strongest subject with an average of ${summary.strongest.avg}%.`
                                        : "There is not enough result data yet to identify the strongest subject."}
                                </p>
                                <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                    <div className="flex items-center gap-2">
                                        <Activity className="h-4 w-4 text-status-blue" />
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">Family-friendly reading</p>
                                    </div>
                                    <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                        Focus on the subject trend and the most recent exam result rather than comparing every raw number at once.
                                    </p>
                                </div>
                            </div>
                        </PrismPanel>
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    label,
    value,
    tone,
}: {
    label: string;
    value: string;
    tone: "blue" | "emerald" | "amber";
}) {
    const toneClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))]",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))]",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))]",
    } as const;

    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <div className={`mb-3 h-2 w-14 rounded-full ${toneClasses[tone]}`} />
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
