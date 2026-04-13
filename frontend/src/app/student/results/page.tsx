"use client";

import { useEffect, useMemo, useState } from "react";
import { Award, Sparkles, TrendingUp } from "lucide-react";

import { api } from "@/lib/api";
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
import { useVidyaContext } from "@/providers/VidyaContextProvider";

type ExamResult = {
    name: string;
    marks: number;
    max: number;
};

type SubjectResult = {
    name: string;
    exams: ExamResult[];
    avg: number;
};

type TrendPoint = {
    exam: string;
    date: string | null;
    marks: number;
    max: number;
    percentage: number;
};

type SubjectTrend = {
    subject: string;
    average: number;
    points: TrendPoint[];
};

function getColor(pct: number | null | undefined) {
    if (pct == null) return "var(--text-primary)";
    if (pct >= 80) return "var(--success)";
    if (pct >= 60) return "var(--warning)";
    return "var(--error)";
}

function Sparkline({ points }: { points: number[] }) {
    if (points.length === 0) return null;

    if (points.length === 1) {
        const y = 30 - (points[0] / 100) * 28;
        return (
            <svg viewBox="0 0 160 34" className="h-10 w-full">
                <line x1="0" y1="30" x2="160" y2="30" stroke="var(--border)" strokeWidth="1" />
                <circle cx="80" cy={y} r="3" fill={getColor(points[0])} />
            </svg>
        );
    }

    const step = 150 / (points.length - 1);
    const coords = points.map((value, idx) => {
        const x = 5 + idx * step;
        const y = 30 - (value / 100) * 28;
        return `${x},${y}`;
    });

    return (
        <svg viewBox="0 0 160 34" className="h-10 w-full">
            <line x1="0" y1="30" x2="160" y2="30" stroke="var(--border)" strokeWidth="1" />
            <polyline fill="none" stroke="var(--primary)" strokeWidth="2" points={coords.join(" ")} />
            {points.map((value, idx) => {
                const x = 5 + idx * step;
                const y = 30 - (value / 100) * 28;
                return <circle key={`${idx}-${value}`} cx={x} cy={y} r="2.4" fill={getColor(value)} />;
            })}
        </svg>
    );
}

export default function ResultsPage() {
    const [subjects, setSubjects] = useState<SubjectResult[]>([]);
    const [trends, setTrends] = useState<SubjectTrend[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const { activeSubject, mergeContext } = useVidyaContext();

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const [resultPayload, trendPayload] = await Promise.all([
                    api.student.results(),
                    api.student.resultsTrends(),
                ]);
                setSubjects((resultPayload || []) as SubjectResult[]);
                setTrends((trendPayload || []) as SubjectTrend[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load results");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const filteredSubjects = useMemo(() => {
        if (!activeSubject) return subjects;
        return subjects.filter(subject => subject.name === activeSubject);
    }, [subjects, activeSubject]);

    const filteredTrends = useMemo(() => {
        if (!activeSubject) return trends;
        return trends.filter(trend => trend.subject === activeSubject);
    }, [trends, activeSubject]);

    const availableSubjects = useMemo(() => {
        const subjectNames = subjects.map(subject => subject.name);
        return subjectNames.sort();
    }, [subjects]);

    const filteredSubjectCount = filteredSubjects.length;

    const overallAvg = useMemo(() => {
        if (filteredSubjects.length === 0) return null;
        return Math.round(filteredSubjects.reduce((sum, item) => sum + item.avg, 0) / filteredSubjects.length);
    }, [filteredSubjects]);

    const strongestSubject = useMemo(() => {
        if (filteredSubjects.length === 0) return null;
        return [...filteredSubjects].sort((a, b) => b.avg - a.avg)[0];
    }, [filteredSubjects]);

    return (
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student Academic Outcomes
                        </PrismHeroKicker>
                    )}
                    title="Read marks as a progression story, not an exam dump"
                    description="Use this view to identify where you are stable, where momentum is improving, and which subject needs the next focused study block."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">How to use it</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with the trend view, compare the strongest and weakest subjects, then turn weak areas into a review plan or quiz session.
                            </p>
                        </div>
                    )}
                />

                {/* Subject Filter */}
                {availableSubjects.length > 1 && (
                    <PrismPanel className="mb-6">
                        <div className="flex items-center gap-4">
                            <Award className="w-4 h-4 text-secondary" />
                            <span className="font-semibold">Filter by Subject</span>
                            <select
                                value={activeSubject || ""}
                                onChange={(e) => mergeContext({ activeSubject: e.target.value || null })}
                                className="px-3 py-1 border border-subtle rounded-lg text-sm"
                            >
                                <option value="">All Subjects</option>
                                {availableSubjects.map(subject => (
                                    <option key={subject} value={subject}>{subject}</option>
                                ))}
                            </select>
                            {activeSubject && (
                                <button
                                    onClick={() => mergeContext({ activeSubject: null })}
                                    className="text-sm text-primary hover:underline"
                                >
                                    Clear filter
                                </button>
                            )}
                        </div>
                    </PrismPanel>
                )}

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Overall average</span>
                        <span className="prism-status-value" style={{ color: getColor(overallAvg) }}>
                            {loading || overallAvg == null ? "--" : `${overallAvg}%`}
                        </span>
                        <span className="prism-status-detail">Normalized across all published subjects in the current dataset.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Strongest subject</span>
                        <span className="prism-status-value">{strongestSubject?.name || "--"}</span>
                        <span className="prism-status-detail">
                            {strongestSubject ? `${strongestSubject.avg}% current average.` : "Will appear after results are available."}
                        </span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Subjects tracked</span>
                        <span className="prism-status-value">{loading ? "--" : filteredSubjectCount}</span>
                        <span className="prism-status-detail">Distinct subjects with exam-level marks in the active dataset.</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="student-results"
                        onRetry={() => {
                            void (async () => {
                                try {
                                    setLoading(true);
                                    setError(null);
                                    const [resultPayload, trendPayload] = await Promise.all([
                                        api.student.results(),
                                        api.student.resultsTrends(),
                                    ]);
                                    setSubjects((resultPayload || []) as SubjectResult[]);
                                    setTrends((trendPayload || []) as SubjectTrend[]);
                                } catch (err) {
                                    setError(err instanceof Error ? err.message : "Failed to load results");
                                } finally {
                                    setLoading(false);
                                }
                            })();
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
                    <PrismPanel className="p-6">
                        <PrismSectionHeader
                            className="mb-4"
                            kicker="Momentum"
                            title={(
                                <span className="inline-flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4 text-[var(--primary)]" />
                                    Subject trend
                                </span>
                            )}
                            description="Read subject-level movement before dropping into exam-level detail."
                        />

                        {loading ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm text-[var(--text-muted)]">
                                Loading trend chart...
                            </div>
                        ) : filteredTrends.length === 0 ? (
                            <EmptyState
                                title="No trend data available yet"
                                description={activeSubject ? `No trend data available for ${activeSubject} yet.` : "Trend lines will appear once multiple results are published for the same subject."}
                                eyebrow="Awaiting history"
                                scopeNote="When enough exams exist, this section helps you spot whether performance is improving, stable, or slipping."
                            />
                        ) : (
                            <div className="grid gap-5">
                                {filteredTrends.map((trend) => {
                                    const percentages = trend.points.map((point) => point.percentage);

                                    return (
                                        <div
                                            key={trend.subject}
                                            className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-5"
                                        >
                                            <div className="mb-2 flex items-center justify-between gap-3">
                                                <span className="text-sm font-semibold text-[var(--text-primary)]">{trend.subject}</span>
                                                <span className="text-xs font-semibold" style={{ color: getColor(trend.average) }}>
                                                    Avg {trend.average}%
                                                </span>
                                            </div>
                                            <Sparkline points={percentages} />
                                            <div className="mt-3 flex flex-wrap gap-1.5">
                                                {trend.points.map((point, idx) => (
                                                    <span
                                                        key={`${trend.subject}-${idx}`}
                                                        className="rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-2 py-0.5 text-[10px] text-[var(--text-secondary)]"
                                                    >
                                                        {point.exam}: {point.percentage}%
                                                    </span>
                                                ))}
                                            </div>
                                        </div>
                                    );
                                })}
                            </div>
                        )}
                    </PrismPanel>

                    <PrismPanel className="p-6">
                        <PrismSectionHeader
                            className="mb-4"
                            kicker="Breakdown"
                            title={(
                                <span className="inline-flex items-center gap-2">
                                    <Award className="h-4 w-4 text-[var(--primary)]" />
                                    Subject detail
                                </span>
                            )}
                            description="Compare subject averages and exam-level performance in one scan."
                        />

                        {loading ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm text-[var(--text-muted)]">
                                Loading results...
                            </div>
                        ) : filteredSubjects.length === 0 ? (
                            <EmptyState
                                title="No results published yet"
                                description={activeSubject ? `No results available for ${activeSubject} yet.` : "Results will appear here once exams are graded and released."}
                                eyebrow="Awaiting publication"
                                scopeNote="Use assignments and reviews to keep studying while this section waits for published marks."
                                action={{ label: "Open Reviews", href: "/student/reviews" }}
                            />
                        ) : (
                            <div className="grid gap-5 md:grid-cols-2">
                                {filteredSubjects.map((subject) => (
                                    <div
                                        key={subject.name}
                                        className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-5"
                                    >
                                        <div className="mb-4 flex items-center justify-between gap-3">
                                            <div>
                                                <h3 className="text-base font-semibold text-[var(--text-primary)]">{subject.name}</h3>
                                                <p className="mt-1 text-[11px] text-[var(--text-muted)]">Use this subject view to decide your next revision block.</p>
                                            </div>
                                            <span className="text-sm font-bold" style={{ color: getColor(subject.avg) }}>
                                                {subject.avg}%
                                            </span>
                                        </div>

                                        <div className="space-y-3">
                                            {subject.exams.length === 0 ? (
                                                <p className="text-xs text-[var(--text-muted)]">No exams for this subject.</p>
                                            ) : (
                                                subject.exams.map((exam) => {
                                                    const pct = exam.max > 0 ? Math.round((exam.marks / exam.max) * 100) : 0;

                                                    return (
                                                        <div key={exam.name}>
                                                            <div className="mb-1 flex items-center justify-between gap-3">
                                                                <span className="text-xs text-[var(--text-secondary)]">{exam.name}</span>
                                                                <span className="text-xs font-medium" style={{ color: getColor(pct) }}>
                                                                    {exam.marks}/{exam.max}
                                                                </span>
                                                            </div>
                                                            <div className="h-2 rounded-full bg-[rgba(255,255,255,0.05)]">
                                                                <div
                                                                    className="h-2 rounded-full transition-all"
                                                                    style={{ width: `${pct}%`, backgroundColor: getColor(pct) }}
                                                                />
                                                            </div>
                                                        </div>
                                                    );
                                                })
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </PrismPanel>
                </div>
            </PrismSection>
        </PrismPage>
    );
}
