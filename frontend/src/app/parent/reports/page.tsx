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
    six_month_overview: {
        attendance_pct: number;
        average_marks: number;
        assignments_submitted: number;
        study_sessions: number;
        ai_requests: number;
        generated_tools: number;
    };
    monthly_snapshots: Array<{
        month: string;
        attendance_pct: number;
        average_marks: number;
        assignments_submitted: number;
    }>;
    recent_generated_tools: Array<{
        id: string;
        type: string;
        title: string;
        created_at: string;
    }>;
};

const EMPTY_PARENT_REPORT: ParentReport = {
    child: { id: "", name: "" },
    attendance_pct_30d: 0,
    weak_subjects: [],
    summary: "",
    six_month_overview: {
        attendance_pct: 0,
        average_marks: 0,
        assignments_submitted: 0,
        study_sessions: 0,
        ai_requests: 0,
        generated_tools: 0,
    },
    monthly_snapshots: [],
    recent_generated_tools: [],
};

function normalizeParentReport(payload: unknown): ParentReport {
    if (!payload || typeof payload !== "object") {
        return EMPTY_PARENT_REPORT;
    }
    const candidate = payload as Partial<ParentReport>;
    return {
        child: {
            id: candidate.child?.id ?? "",
            name: candidate.child?.name ?? "",
        },
        attendance_pct_30d: candidate.attendance_pct_30d ?? 0,
        weak_subjects: candidate.weak_subjects ?? [],
        summary: candidate.summary ?? "",
        six_month_overview: {
            attendance_pct: candidate.six_month_overview?.attendance_pct ?? 0,
            average_marks: candidate.six_month_overview?.average_marks ?? 0,
            assignments_submitted: candidate.six_month_overview?.assignments_submitted ?? 0,
            study_sessions: candidate.six_month_overview?.study_sessions ?? 0,
            ai_requests: candidate.six_month_overview?.ai_requests ?? 0,
            generated_tools: candidate.six_month_overview?.generated_tools ?? 0,
        },
        monthly_snapshots: candidate.monthly_snapshots ?? [],
        recent_generated_tools: candidate.recent_generated_tools ?? [],
    };
}

export default function ParentReportsPage() {
    const [report, setReport] = useState<ParentReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                setReport(normalizeParentReport(await api.parent.reports()));
            } catch (loadError) {
                setError(loadError instanceof Error ? loadError.message : "Failed to load report");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <PrismPage variant="report" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <FileText className="h-3.5 w-3.5" />
                            Family Progress Report
                        </PrismHeroKicker>
                    )}
                    title="See the month in plain academic language"
                    description="This report keeps the family view practical: attendance, focus subjects, and the overall learning story without admin jargon or technical noise."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Child</span>
                        <strong className="prism-status-value">{report?.child.name ?? "Loading"}</strong>
                        <span className="prism-status-detail">Student whose monthly report is shown here</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Attendance</span>
                        <strong className="prism-status-value">{report ? `${report.attendance_pct_30d}%` : "Loading"}</strong>
                        <span className="prism-status-detail">Attendance across the last 30 days</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Six-month AI support</span>
                        <strong className="prism-status-value">{report?.six_month_overview.ai_requests ?? 0}</strong>
                        <span className="prism-status-detail">Guided study requests captured in the demo history</span>
                    </div>
                </div>

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

                {report ? (
                    <div className="grid gap-4 lg:grid-cols-[0.98fr_1.02fr]">
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Six-month support picture"
                                description="Summarize the broader learning rhythm behind this monthly report."
                            />
                            <div className="mt-4 grid gap-3 sm:grid-cols-2">
                                <StatTile label="Attendance" value={`${report.six_month_overview.attendance_pct}%`} />
                                <StatTile label="Average marks" value={`${report.six_month_overview.average_marks}%`} />
                                <StatTile label="Assignments" value={`${report.six_month_overview.assignments_submitted}`} />
                                <StatTile label="Study sessions" value={`${report.six_month_overview.study_sessions}`} />
                                <StatTile label="AI requests" value={`${report.six_month_overview.ai_requests}`} />
                                <StatTile label="Generated tools" value={`${report.six_month_overview.generated_tools}`} />
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Monthly snapshots"
                                description="Show how attendance, marks, and assignment follow-through have moved over time."
                            />
                            <div className="mt-4 space-y-3">
                                {report.monthly_snapshots.map((snapshot, index) => (
                                    <div key={`${snapshot.month}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex items-center justify-between gap-4">
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{snapshot.month}</p>
                                            <p className="text-xs text-[var(--text-muted)]">{snapshot.assignments_submitted} assignment submission{snapshot.assignments_submitted === 1 ? "" : "s"}</p>
                                        </div>
                                        <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                            {snapshot.attendance_pct}% attendance and {snapshot.average_marks}% average marks.
                                        </p>
                                    </div>
                                ))}
                            </div>
                            <div className="mt-5 space-y-3">
                                {report.recent_generated_tools.map((item) => (
                                    <div key={item.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.02)] px-4 py-3">
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{item.title}</p>
                                        <p className="mt-1 text-xs text-[var(--text-muted)]">{item.type.replace(/_/g, " ")} generated on {item.created_at}</p>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    </div>
                ) : (
                    null
                )}
            </PrismSection>
        </PrismPage>
    );
}

function StatTile({ label, value }: { label: string; value: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
