"use client";

import { useEffect, useMemo, useState } from "react";
import {
    BarChart3,
    BrainCircuit,
    Sparkles,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
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
        <PrismPage variant="dashboard" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <BrainCircuit className="h-3.5 w-3.5" />
                            Teacher Insight Surface
                        </PrismHeroKicker>
                    )}
                    title="Class Insights Dashboard"
                    description="Scan weak subjects, compare class-level performance, and review the next recommended teaching move without leaving the operational teacher flow."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with weak signals, then use the recommendation panel to decide whether the next move is revision, reteaching, or assessment follow-up.
                            </p>
                        </div>
                    )}
                />

                {!loading && !error ? (
                    <div className="prism-status-strip">
                        <div className="prism-status-item">
                            <span className="prism-status-label">Classes analyzed</span>
                            <span className="prism-status-value">{summary.totalClasses}</span>
                            <span className="prism-status-detail">Insight coverage across current classroom cohorts.</span>
                        </div>
                        <div className="prism-status-item">
                            <span className="prism-status-label">Weak signals</span>
                            <span className="prism-status-value">{summary.weakSignals}</span>
                            <span className="prism-status-detail">Subjects currently flagged for intervention.</span>
                        </div>
                        <div className="prism-status-item">
                            <span className="prism-status-label">Average level</span>
                            <span className="prism-status-value">{summary.totalClasses ? `${summary.avgPerformance}%` : "-"}</span>
                            <span className="prism-status-detail">Mean subject performance across the loaded dataset.</span>
                        </div>
                    </div>
                ) : null}

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
                        eyebrow="Awaiting teaching signals"
                        scopeNote="As results and assessments accumulate, this page becomes the fastest way to identify where reteaching or intervention is needed."
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
                                                Performance distribution, weak-topic detection, and one recommended teaching move for this class.
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
                                            <button type="button" disabled title="Coming soon" className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60">
                                                <Sparkles className="h-4 w-4" />
                                                Deploy action plan
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
