"use client";

import { useEffect, useMemo, useState } from "react";
import {
    AlertTriangle,
    BarChart3,
    BrainCircuit,
    Sparkles,
    TrendingUp,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { SkeletonCard } from "@/components/Skeleton";
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

    const summary = useMemo(() => {
        const totalClasses = insights.length;
        const weakSubjects = insights.flatMap((classInsight) =>
            classInsight.subjects.filter((subject) => subject.is_weak),
        );
        const allSubjects = insights.flatMap((classInsight) => classInsight.subjects);
        const avgPerformance = allSubjects.length
            ? Math.round(allSubjects.reduce((sum, subject) => sum + Number(subject.avg_pct || 0), 0) / allSubjects.length)
            : 0;

        return {
            totalClasses,
            weakSignals: weakSubjects.length,
            avgPerformance,
        };
    }, [insights]);

    return (
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <BrainCircuit className="h-3.5 w-3.5" />
                            Teacher Insight Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                AI Class Insights
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                Scan weak signals, compare subject performance, and review the next intervention recommendation without losing the practical teacher workflow.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <MetricCard
                            icon={BarChart3}
                            title="Classes analyzed"
                            value={`${summary.totalClasses}`}
                            accent="blue"
                            summary="Insight coverage across current classroom cohorts"
                        />
                        <MetricCard
                            icon={AlertTriangle}
                            title="Weak signals"
                            value={`${summary.weakSignals}`}
                            accent="amber"
                            summary="Subjects currently flagged for intervention"
                        />
                        <MetricCard
                            icon={TrendingUp}
                            title="Average level"
                            value={summary.totalClasses ? `${summary.avgPerformance}%` : "-"}
                            accent="emerald"
                            summary="Mean subject performance across the loaded dataset"
                        />
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="teacher-insights"
                        onRetry={() => {
                            window.location.reload();
                        }}
                    />
                ) : null}

                {loading ? (
                    <div className="grid gap-6 md:grid-cols-2">
                        {Array.from({ length: 4 }).map((_, index) => (
                            <SkeletonCard key={index} />
                        ))}
                    </div>
                ) : insights.length === 0 ? (
                    <EmptyState
                        icon={BrainCircuit}
                        title="No insight telemetry yet"
                        description="This surface will populate once class performance data is available for analysis."
                    />
                ) : (
                    <div className="grid gap-6">
                        {insights.map((classInsight) => (
                            <PrismPanel key={classInsight.class} className="overflow-hidden p-0">
                                <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                    <div className="flex flex-wrap items-center justify-between gap-3">
                                        <div>
                                            <h2 className="text-2xl font-black text-[var(--text-primary)]">{classInsight.class}</h2>
                                            <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                                Performance distribution, weak-topic detection, and an intervention recommendation for this class.
                                            </p>
                                        </div>
                                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                            <BarChart3 className="h-3.5 w-3.5" />
                                            {classInsight.subjects.length} tracked subjects
                                        </div>
                                    </div>
                                </div>

                                <div className="grid gap-6 p-5 xl:grid-cols-[1.2fr_0.8fr]">
                                    <div className="space-y-4">
                                        <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Subject performance</p>
                                        <div className="space-y-4">
                                            {classInsight.subjects.map((subject) => {
                                                const tone = subject.is_weak
                                                    ? "from-red-500 to-rose-400"
                                                    : subject.avg_pct >= 80
                                                        ? "from-emerald-500 to-teal-400"
                                                        : "from-blue-500 to-indigo-400";

                                                return (
                                                    <div key={subject.subject} className="space-y-2">
                                                        <div className="flex items-center justify-between gap-3">
                                                            <div className="flex items-center gap-2">
                                                                <span className="text-sm font-semibold text-[var(--text-primary)]">{subject.subject}</span>
                                                                {subject.is_weak ? (
                                                                    <span className="rounded-full bg-error-subtle px-2 py-0.5 text-[10px] font-semibold text-[var(--error)]">
                                                                        weak
                                                                    </span>
                                                                ) : null}
                                                            </div>
                                                            <span className={`text-sm font-semibold ${subject.is_weak ? "text-[var(--error)]" : "text-[var(--text-primary)]"}`}>
                                                                {subject.avg_pct}%
                                                            </span>
                                                        </div>
                                                        <div className="h-3 overflow-hidden rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.08)]">
                                                            <div
                                                                className={`h-full rounded-full bg-gradient-to-r ${tone}`}
                                                                style={{ width: `${subject.avg_pct}%` }}
                                                            />
                                                        </div>
                                                    </div>
                                                );
                                            })}
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        <PrismPanel className="p-5">
                                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Targeted interventions</p>
                                            <div className="mt-4 flex flex-wrap gap-2">
                                                {classInsight.weak_topics.length > 0 ? (
                                                    classInsight.weak_topics.map((topic) => (
                                                        <span
                                                            key={topic}
                                                            className="rounded-full border border-[var(--error)]/20 bg-error-subtle px-3 py-1.5 text-xs font-semibold text-[var(--error)]"
                                                        >
                                                            {topic}
                                                        </span>
                                                    ))
                                                ) : (
                                                    <p className="text-sm text-[var(--text-muted)]">No major weak topics identified.</p>
                                                )}
                                            </div>
                                        </PrismPanel>

                                        <PrismPanel className="p-5">
                                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Copilot recommendation</p>
                                            <p className="mt-4 text-sm leading-7 text-[var(--text-primary)]">{classInsight.recommendation}</p>
                                            <button className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5">
                                                <Sparkles className="h-4 w-4" />
                                                Deploy Action Plan
                                            </button>
                                        </PrismPanel>
                                    </div>
                                </div>
                            </PrismPanel>
                        ))}
                    </div>
                )}
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
    icon: typeof BarChart3;
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
