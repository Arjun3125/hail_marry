"use client";

import { useEffect, useMemo, useState } from "react";
import { Award, BookOpen, Sparkles, TrendingUp } from "lucide-react";

import { api } from "@/lib/api";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";

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

function getColor(pct: number) {
    if (pct >= 80) return "var(--success)";
    if (pct >= 60) return "var(--warning)";
    return "var(--error)";
}

function Sparkline({ points }: { points: number[] }) {
    if (points.length === 0) {
        return null;
    }

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

    const overallAvg = useMemo(() => {
        if (subjects.length === 0) return 0;
        return Math.round(subjects.reduce((sum, item) => sum + item.avg, 0) / subjects.length);
    }, [subjects]);

    const strongestSubject = useMemo(() => {
        if (subjects.length === 0) return null;
        return [...subjects].sort((a, b) => b.avg - a.avg)[0];
    }, [subjects]);

    const subjectCount = subjects.length;

    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]"
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student Academic Outcomes
                        </PrismHeroKicker>
                    )}
                    title={<>Read performance as a <span className="premium-gradient">clear progression story</span>, not a scattered marks dump</>}
                    description="This view now separates overall standing, subject trends, and exam-level detail so students can see both where they are strong and where they need to recover."
                    aside={(
                        <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                            <PrismPanel className="p-4">
                                <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(129,140,248,0.08))]">
                                    <Award className="h-5 w-5 text-status-blue" />
                                </div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Overall average</p>
                                <p className="mt-2 text-2xl font-black" style={{ color: getColor(overallAvg) }}>
                                    {loading ? "--" : `${overallAvg}%`}
                                </p>
                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Normalized across all reported subjects.</p>
                            </PrismPanel>
                            <PrismPanel className="p-4">
                                <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(45,212,191,0.18),rgba(16,185,129,0.08))]">
                                    <BookOpen className="h-5 w-5 text-status-emerald" />
                                </div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Strongest subject</p>
                                <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{strongestSubject?.name || "--"}</p>
                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                                    {strongestSubject ? `${strongestSubject.avg}% current average.` : "Will appear after results are available."}
                                </p>
                            </PrismPanel>
                            <PrismPanel className="p-4">
                                <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.18),rgba(249,115,22,0.08))]">
                                    <TrendingUp className="h-5 w-5 text-status-amber" />
                                </div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Subjects tracked</p>
                                <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{loading ? "--" : subjectCount}</p>
                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Distinct subjects with exam-level marks in the current dataset.</p>
                            </PrismPanel>
                        </div>
                    )}
                />

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
                    <PrismPanel className="p-5">
                        <PrismSectionHeader
                            className="mb-4"
                            kicker="Insights"
                            title={(
                                <span className="inline-flex items-center gap-2">
                                    <TrendingUp className="h-4 w-4 text-[var(--primary)]" />
                                    Performance Trend
                                </span>
                            )}
                            description="Read subject-level momentum before dropping into exam-level detail."
                        />

                        {loading ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm text-[var(--text-muted)]">
                                Loading trend chart...
                            </div>
                        ) : trends.length === 0 ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm text-[var(--text-muted)]">
                                No trend data available yet.
                            </div>
                        ) : (
                            <div className="grid gap-4">
                                {trends.map((trend) => {
                                    const percentages = trend.points.map((point) => point.percentage);

                                    return (
                                        <div
                                            key={trend.subject}
                                            className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4"
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

                    <PrismPanel className="p-5">
                        <PrismSectionHeader
                            className="mb-4"
                            kicker="Detail"
                            title={(
                                <span className="inline-flex items-center gap-2">
                                    <Award className="h-4 w-4 text-[var(--primary)]" />
                                    Subject Breakdown
                                </span>
                            )}
                            description="Compare subject averages and exam-level performance in one scan."
                        />

                        {loading ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm text-[var(--text-muted)]">
                                Loading results...
                            </div>
                        ) : subjects.length === 0 ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm text-[var(--text-muted)]">
                                No results published yet.
                            </div>
                        ) : (
                            <div className="grid gap-4 md:grid-cols-2">
                                {subjects.map((subject) => (
                                    <div
                                        key={subject.name}
                                        className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4"
                                    >
                                        <div className="mb-4 flex items-center justify-between gap-3">
                                            <h3 className="text-base font-semibold text-[var(--text-primary)]">{subject.name}</h3>
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
