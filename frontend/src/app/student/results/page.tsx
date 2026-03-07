"use client";

import { useEffect, useMemo, useState } from "react";
import { Award, TrendingUp } from "lucide-react";

import { api } from "@/lib/api";

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
            <svg viewBox="0 0 160 34" className="w-full h-10">
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
        <svg viewBox="0 0 160 34" className="w-full h-10">
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

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Results</h1>
                <p className="text-sm text-[var(--text-secondary)]">Your marks, subject averages, and exam trend over time.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-6 shadow-[var(--shadow-card)] mb-6">
                <div className="flex items-center gap-3 mb-2">
                    <Award className="w-5 h-5 text-[var(--primary)]" />
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Overall Average</h2>
                </div>
                <div className="flex items-baseline gap-2">
                    <span className="text-4xl font-bold" style={{ color: getColor(overallAvg) }}>
                        {loading ? "-" : `${overallAvg}%`}
                    </span>
                    <span className="text-sm text-[var(--text-muted)]">across all subjects</span>
                </div>
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-6">
                <div className="flex items-center gap-2 mb-3">
                    <TrendingUp className="w-4 h-4 text-[var(--primary)]" />
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Performance Trend</h2>
                </div>
                {loading ? (
                    <p className="text-sm text-[var(--text-muted)]">Loading trend chart...</p>
                ) : trends.length === 0 ? (
                    <p className="text-sm text-[var(--text-muted)]">No trend data available yet.</p>
                ) : (
                    <div className="grid md:grid-cols-2 gap-4">
                        {trends.map((trend) => {
                            const percentages = trend.points.map((point) => point.percentage);
                            return (
                                <div key={trend.subject} className="rounded-[var(--radius-sm)] border border-[var(--border-light)] p-3">
                                    <div className="flex items-center justify-between mb-1">
                                        <span className="text-sm font-medium text-[var(--text-primary)]">{trend.subject}</span>
                                        <span className="text-xs font-semibold" style={{ color: getColor(trend.average) }}>
                                            Avg {trend.average}%
                                        </span>
                                    </div>
                                    <Sparkline points={percentages} />
                                    <div className="mt-2 flex flex-wrap gap-1.5">
                                        {trend.points.map((point, idx) => (
                                            <span key={`${trend.subject}-${idx}`} className="text-[10px] px-2 py-0.5 rounded-full bg-[var(--bg-page)] text-[var(--text-secondary)]">
                                                {point.exam}: {point.percentage}%
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                )}
            </div>

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                    Loading results...
                </div>
            ) : subjects.length === 0 ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                    No results published yet.
                </div>
            ) : (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {subjects.map((subject) => (
                        <div key={subject.name} className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center justify-between mb-4">
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
                                                <div className="flex items-center justify-between mb-1">
                                                    <span className="text-xs text-[var(--text-secondary)]">{exam.name}</span>
                                                    <span className="text-xs font-medium" style={{ color: getColor(pct) }}>
                                                        {exam.marks}/{exam.max}
                                                    </span>
                                                </div>
                                                <div className="h-2 bg-[var(--bg-page)] rounded-full">
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
        </div>
    );
}
