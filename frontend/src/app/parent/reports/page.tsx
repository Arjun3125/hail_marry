"use client";

import { useEffect, useState } from "react";
import { BookOpen, FileText, ShieldCheck, Sparkles } from "lucide-react";

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
import { api } from "@/lib/api";

type ParentReport = {
    child: { id: string; name: string };
    attendance_pct_30d: number;
    weak_subjects: string[];
    summary: string;
};

export default function ParentReportsPage() {
    const [report, setReport] = useState<ParentReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.parent.reports();
                setReport(data as ParentReport);
            } catch (loadError) {
                setError(loadError instanceof Error ? loadError.message : "Failed to load report");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]"
                    kicker={(
                        <PrismHeroKicker>
                            <FileText className="h-3.5 w-3.5" />
                            Parent Report Surface
                        </PrismHeroKicker>
                    )}
                    title="Progress Report"
                    description="A monthly family-facing summary that keeps attendance, focus subjects, and the overall academic story easy to understand."
                    aside={(
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Monthly snapshot"
                                description="A quick family-friendly overview before reading the narrative detail."
                            />
                            {report ? (
                                <div className="mt-4 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                                    <MetricCard label="Child" value={report.child.name} tone="blue" />
                                    <MetricCard label="Attendance" value={`${report.attendance_pct_30d}%`} tone="emerald" />
                                    <MetricCard label="Focus subjects" value={`${report.weak_subjects.length}`} tone="amber" />
                                </div>
                            ) : (
                                <p className="mt-4 text-sm text-[var(--text-secondary)]">Snapshot will appear once the report loads.</p>
                            )}
                        </PrismPanel>
                    )}
                />

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="parent-reports"
                        onRetry={() => window.location.reload()}
                    />
                ) : null}

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">Loading progress report...</p>
                    </PrismPanel>
                ) : report ? (
                    <div className="grid gap-4 lg:grid-cols-[1.02fr_0.98fr]">
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title={(
                                    <span className="inline-flex items-center gap-2">
                                        <Sparkles className="h-4 w-4 text-status-amber" />
                                        Monthly story
                                    </span>
                                )}
                                description="Translate the month into a simple narrative a parent can act on."
                            />
                            <div className="mt-4 space-y-4 text-sm leading-6 text-[var(--text-secondary)]">
                                <p>
                                    This monthly view is meant to answer three simple questions: how steady attendance has been, which subjects may need attention, and what overall message a parent should take from the month.
                                </p>
                                <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{report.summary}</p>
                                </div>
                                <p>
                                    Attendance across the last 30 days is currently <span className="font-semibold text-[var(--text-primary)]">{report.attendance_pct_30d}%</span>, which helps frame how consistently the month has gone.
                                </p>
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title={(
                                    <span className="inline-flex items-center gap-2">
                                        <BookOpen className="h-4 w-4 text-status-blue" />
                                        Focus subjects
                                    </span>
                                )}
                                description="Highlight the subjects that may need the most attention next."
                            />
                            {report.weak_subjects.length > 0 ? (
                                <div className="mt-4 space-y-3">
                                    {report.weak_subjects.map((subject) => (
                                        <div key={subject} className="flex items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{subject}</span>
                                            <span className="rounded-full border border-[rgba(245,158,11,0.24)] bg-[rgba(245,158,11,0.1)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-status-amber">
                                                Watch closely
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={ShieldCheck}
                                        title="No weak subjects identified"
                                        description="The current monthly report does not flag any subjects for extra concern."
                                    />
                                </div>
                            )}
                        </PrismPanel>
                    </div>
                ) : (
                    <PrismPanel className="p-6">
                        <EmptyState
                            icon={FileText}
                            title="No report found"
                            description="The monthly progress summary will appear here once it has been generated."
                        />
                    </PrismPanel>
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
