"use client";

import { useEffect, useMemo, useState } from "react";
import { Activity, Award, BookOpen, Sparkles } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type ResultItem = {
    name: string;
    avg: number;
    exams: Array<{ name: string; marks: number; max: number }>;
};

type ResultPayload = {
    items: ResultItem[];
    summary: {
        subjects: number;
        average: number;
        strongest: string | null;
        exams_recorded: number;
    };
    monthly_trend: Array<{
        month: string;
        average_pct: number;
        exams_recorded: number;
    }>;
    recent_exams: Array<{
        subject: string;
        exam: string;
        percentage: number;
        date: string | null;
    }>;
};

function isResultExam(value: unknown): value is ResultItem["exams"][number] {
    return Boolean(
        value
        && typeof value === "object"
        && typeof (value as ResultItem["exams"][number]).name === "string"
        && typeof (value as ResultItem["exams"][number]).marks === "number"
        && typeof (value as ResultItem["exams"][number]).max === "number"
    );
}

function isResultItem(value: unknown): value is ResultItem {
    return Boolean(
        value
        && typeof value === "object"
        && typeof (value as ResultItem).name === "string"
        && typeof (value as ResultItem).avg === "number"
        && Array.isArray((value as ResultItem).exams)
        && (value as ResultItem).exams.every(isResultExam)
    );
}

function normalizeResultPayload(payload: unknown): ResultPayload {
    if (Array.isArray(payload)) {
        const items = payload.filter(isResultItem);
        return {
            items,
            summary: {
                subjects: items.length,
                average: 0,
                strongest: null,
                exams_recorded: 0,
            },
            monthly_trend: [],
            recent_exams: [],
        };
    }
    if (!payload || typeof payload !== "object") {
        return {
            items: [],
            summary: {
                subjects: 0,
                average: 0,
                strongest: null,
                exams_recorded: 0,
            },
            monthly_trend: [],
            recent_exams: [],
        };
    }
    const candidate = payload as Partial<ResultPayload>;
    const items = Array.isArray(candidate.items) ? candidate.items.filter(isResultItem) : [];
    return {
        items,
        summary: {
            subjects: candidate.summary?.subjects ?? items.length,
            average: candidate.summary?.average ?? 0,
            strongest: candidate.summary?.strongest ?? null,
            exams_recorded: candidate.summary?.exams_recorded ?? 0,
        },
        monthly_trend: candidate.monthly_trend ?? [],
        recent_exams: candidate.recent_exams ?? [],
    };
}

export default function ParentResultsPage() {
    const [items, setItems] = useState<ResultItem[]>([]);
    const [monthlyTrend, setMonthlyTrend] = useState<ResultPayload["monthly_trend"]>([]);
    const [recentExams, setRecentExams] = useState<ResultPayload["recent_exams"]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = normalizeResultPayload(await api.parent.results());
                setItems(data.items);
                setMonthlyTrend(data.monthly_trend);
                setRecentExams(data.recent_exams);
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
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Award className="h-3.5 w-3.5" />
                            Parent Results Surface
                        </PrismHeroKicker>
                    )}
                    title="Read academic progress clearly before looking at raw marks"
                    description="See the overall story first: how many subjects are visible, where performance is strongest, and which result details may need family attention."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">How to use this</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with the subject average and strongest area, then use the exam details only for follow-up questions or encouragement.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Subjects</span>
                        <span className="prism-status-value">{summary.subjects}</span>
                        <span className="prism-status-detail">Subjects currently represented in the results dataset.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Average</span>
                        <span className="prism-status-value">{summary.average}%</span>
                        <span className="prism-status-detail">Mean performance across the loaded subjects.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Strongest</span>
                        <span className="prism-status-value">{summary.strongest ? summary.strongest.name : "No data"}</span>
                        <span className="prism-status-detail">Highest current subject average in the available results.</span>
                    </div>
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
                    <>
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
                                            eyebrow="No results yet"
                                            scopeNote="Once assessment data is published, this page keeps the reading parent-friendly by summarizing subjects, averages, and the most recent marks together."
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

                        <div className="grid gap-4 lg:grid-cols-[0.94fr_1.06fr]">
                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Activity className="h-4 w-4 text-status-blue" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Six-month result trend</h2>
                                </div>
                                <div className="mt-4 grid gap-3">
                                    {monthlyTrend.length > 0 ? (
                                        monthlyTrend.map((item, index) => (
                                            <div key={`${item.month}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                <div className="flex items-center justify-between gap-4">
                                                    <p className="text-sm font-medium text-[var(--text-primary)]">{item.month}</p>
                                                    <p className="text-sm text-[var(--text-secondary)]">{item.average_pct}% average</p>
                                                </div>
                                                <p className="mt-1 text-xs text-[var(--text-muted)]">{item.exams_recorded} recorded exam{item.exams_recorded === 1 ? "" : "s"}.</p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-sm text-[var(--text-secondary)]">Six-month result trend will appear here once assessments span multiple months.</p>
                                    )}
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Award className="h-4 w-4 text-status-amber" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent exam trail</h2>
                                </div>
                                <div className="mt-4 space-y-3">
                                    {recentExams.length > 0 ? (
                                        recentExams.map((item) => (
                                            <div key={`${item.subject}-${item.exam}-${item.date}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                <div className="flex items-center justify-between gap-4">
                                                    <div>
                                                        <p className="text-sm font-medium text-[var(--text-primary)]">{item.subject}</p>
                                                        <p className="mt-1 text-xs text-[var(--text-muted)]">{item.exam}</p>
                                                    </div>
                                                    <div className="text-right">
                                                        <p className="text-sm font-semibold text-[var(--text-primary)]">{item.percentage}%</p>
                                                        <p className="mt-1 text-xs text-[var(--text-muted)]">{item.date ?? "No date"}</p>
                                                    </div>
                                                </div>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-sm text-[var(--text-secondary)]">Recent exams will appear here once marks are published.</p>
                                    )}
                                </div>
                            </PrismPanel>
                        </div>
                    </>
                )}
            </PrismSection>
        </PrismPage>
    );
}
