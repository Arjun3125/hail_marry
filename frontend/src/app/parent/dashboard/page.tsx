"use client";

import { useCallback, useEffect, useState } from "react";
import {
    Activity,
    CalendarCheck,
    Clock,
    FileText,
    GraduationCap,
    Loader2,
    ShieldCheck,
    Sparkles,
    Volume2,
    VolumeX,
} from "lucide-react";

import { api } from "@/lib/api";
import { RoleStartPanel } from "@/components/RoleStartPanel";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";

type ParentDashboard = {
    child: {
        id: string;
        name: string;
        email: string;
        class: string | null;
    };
    attendance_pct: number;
    avg_marks: number;
    pending_assignments: number;
    latest_mark: {
        subject: string;
        exam: string;
        percentage: number;
        date: string | null;
    } | null;
    next_class: {
        day: number;
        start_time: string;
        end_time: string;
        subject: string;
    } | null;
    summary: {
        assignments_submitted: number;
        study_sessions: number;
        ai_requests: number;
        generated_tools: number;
        latest_milestones: {
            last_assignment_submitted_at: string | null;
            last_study_session_at: string | null;
            last_ai_request_at: string | null;
            last_generated_tool_at: string | null;
        };
        recent_generated_tools: Array<{
            id: string;
            type: string;
            title: string;
            created_at: string;
        }>;
    };
    monthly_attendance: Array<{
        month: string;
        present: number;
        absent: number;
        late: number;
        attendance_pct: number;
        marked_days: number;
    }>;
    monthly_performance: Array<{
        month: string;
        average_pct: number;
        exams_recorded: number;
    }>;
    monthly_assignments: Array<{
        month: string;
        assignments_submitted: number;
    }>;
};

const EMPTY_PARENT_DASHBOARD: ParentDashboard = {
    child: {
        id: "",
        name: "",
        email: "",
        class: null,
    },
    attendance_pct: 0,
    avg_marks: 0,
    pending_assignments: 0,
    latest_mark: null,
    next_class: null,
    summary: {
        assignments_submitted: 0,
        study_sessions: 0,
        ai_requests: 0,
        generated_tools: 0,
        latest_milestones: {
            last_assignment_submitted_at: null,
            last_study_session_at: null,
            last_ai_request_at: null,
            last_generated_tool_at: null,
        },
        recent_generated_tools: [],
    },
    monthly_attendance: [],
    monthly_performance: [],
    monthly_assignments: [],
};

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

function formatDate(value: string | null) {
    if (!value) return "No recent date";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString();
}

function normalizeParentDashboard(payload: unknown): ParentDashboard {
    if (!payload || typeof payload !== "object") {
        return EMPTY_PARENT_DASHBOARD;
    }
    const candidate = payload as Partial<ParentDashboard>;
    return {
        child: {
            id: candidate.child?.id ?? "",
            name: candidate.child?.name ?? "",
            email: candidate.child?.email ?? "",
            class: candidate.child?.class ?? null,
        },
        attendance_pct: candidate.attendance_pct ?? 0,
        avg_marks: candidate.avg_marks ?? 0,
        pending_assignments: candidate.pending_assignments ?? 0,
        latest_mark: candidate.latest_mark ?? null,
        next_class: candidate.next_class ?? null,
        summary: {
            assignments_submitted: candidate.summary?.assignments_submitted ?? 0,
            study_sessions: candidate.summary?.study_sessions ?? 0,
            ai_requests: candidate.summary?.ai_requests ?? 0,
            generated_tools: candidate.summary?.generated_tools ?? 0,
            latest_milestones: {
                last_assignment_submitted_at: candidate.summary?.latest_milestones?.last_assignment_submitted_at ?? null,
                last_study_session_at: candidate.summary?.latest_milestones?.last_study_session_at ?? null,
                last_ai_request_at: candidate.summary?.latest_milestones?.last_ai_request_at ?? null,
                last_generated_tool_at: candidate.summary?.latest_milestones?.last_generated_tool_at ?? null,
            },
            recent_generated_tools: candidate.summary?.recent_generated_tools ?? [],
        },
        monthly_attendance: candidate.monthly_attendance ?? [],
        monthly_performance: candidate.monthly_performance ?? [],
        monthly_assignments: candidate.monthly_assignments ?? [],
    };
}

export default function ParentDashboardPage() {
    const [data, setData] = useState<ParentDashboard | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [speaking, setSpeaking] = useState(false);
    const [audioLoading, setAudioLoading] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const payload = await api.parent.dashboard();
            setData(normalizeParentDashboard(payload));
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : "Failed to load dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

    const playAudioReport = async () => {
        if (speaking) {
            window.speechSynthesis.cancel();
            setSpeaking(false);
            return;
        }
        try {
            setAudioLoading(true);
            setError(null);
            const report = (await api.parent.audioReport()) as { text: string };
            const utterance = new SpeechSynthesisUtterance(report.text);
            utterance.rate = 0.9;
            utterance.onend = () => setSpeaking(false);
            utterance.onerror = () => setSpeaking(false);
            window.speechSynthesis.speak(utterance);
            setSpeaking(true);
        } catch {
            setError("Failed to load audio report");
        } finally {
            setAudioLoading(false);
        }
    };

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ShieldCheck className="h-3.5 w-3.5" />
                            Parent Support Surface
                        </PrismHeroKicker>
                    )}
                    title="See your child's week in one clear family summary"
                    description="Track attendance, marks, upcoming classes, and the next action that matters without needing to decode an admin dashboard."
                    aside={(
                        <PrismPanel className="p-5">
                        <div className="flex items-start gap-4">
                            <button
                                type="button"
                                onClick={() => void playAudioReport()}
                                disabled={audioLoading}
                                className={`inline-flex h-14 w-14 shrink-0 items-center justify-center rounded-full text-white shadow-[0_16px_30px_rgba(15,23,42,0.16)] transition-all ${
                                    speaking
                                        ? "bg-[linear-gradient(135deg,rgba(244,114,182,0.95),rgba(225,29,72,0.92))]"
                                        : "bg-[linear-gradient(135deg,rgba(245,158,11,0.95),rgba(249,115,22,0.92))] hover:-translate-y-0.5"
                                } disabled:opacity-60`}
                                aria-label={speaking ? "Stop audio update" : "Play audio update"}
                            >
                                {audioLoading ? <Loader2 className="h-6 w-6 animate-spin" /> : speaking ? <VolumeX className="h-6 w-6" /> : <Volume2 className="h-6 w-6" />}
                            </button>
                            <div>
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Listen to update</h2>
                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                                    {speaking ? "Playing an AI-generated progress summary now." : "Hear a short AI summary of recent attendance, marks, and upcoming schedule changes."}
                                </p>
                            </div>
                        </div>
                        </PrismPanel>
                    )}
                />

                <RoleStartPanel role="parent" />

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="parent-dashboard"
                        onRetry={() => {
                            void load();
                        }}
                    />
                ) : null}

                {loading ? (
                    <PrismPanel className="flex min-h-[260px] flex-col items-center justify-center gap-3 p-10 text-[var(--text-secondary)]">
                        <Loader2 className="h-8 w-8 animate-spin" />
                        <p className="text-sm">Syncing child progress...</p>
                    </PrismPanel>
                ) : data ? (
                    <>
                        <div className="grid gap-4 lg:grid-cols-[1.08fr_0.92fr]">
                            <PrismPanel className="p-6">
                                <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                                    <div>
                                        <div className="inline-flex items-center gap-2 rounded-full border border-[rgba(245,158,11,0.22)] bg-[rgba(245,158,11,0.08)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-status-amber">
                                            <GraduationCap className="h-3.5 w-3.5" />
                                            {data.child.class ? `Class ${data.child.class}` : "Student profile"}
                                        </div>
                                        <h2 className="mt-4 text-3xl font-black text-[var(--text-primary)]">
                                            {data.child.name}
                                        </h2>
                                        <p className="mt-2 text-sm text-[var(--text-secondary)]">{data.child.email}</p>
                                    </div>
                                    <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-secondary)]">
                                        Weekly snapshot focused on reassurance, not admin density.
                                    </div>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-6">
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Next class</h2>
                                {data.next_class ? (
                                    <div className="mt-4 flex items-center gap-4">
                                        <div className="flex h-20 w-20 shrink-0 flex-col items-center justify-center rounded-[24px] border border-[rgba(96,165,250,0.16)] bg-[rgba(96,165,250,0.08)]">
                                            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-status-blue">{DAYS[data.next_class.day] || "Day"}</span>
                                            <span className="mt-1 text-xl font-black text-[var(--text-primary)]">{data.next_class.start_time.split(":")[0]}</span>
                                        </div>
                                        <div>
                                            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Up next</p>
                                            <h3 className="mt-2 text-xl font-bold text-[var(--text-primary)]">{data.next_class.subject}</h3>
                                            <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                                {data.next_class.start_time} - {data.next_class.end_time}
                                            </p>
                                        </div>
                                    </div>
                                ) : (
                                    <p className="mt-4 text-sm text-[var(--text-secondary)]">No upcoming classes are scheduled right now.</p>
                                )}
                            </PrismPanel>
                        </div>

                        <div className="grid gap-4 md:grid-cols-3">
                            <MetricCard
                                icon={CalendarCheck}
                                title="Attendance"
                                value={`${data.attendance_pct}%`}
                                summary={data.attendance_pct >= 75 ? "Attendance is in a healthy range." : "Attendance needs attention this week."}
                                tone={data.attendance_pct >= 75 ? "emerald" : "amber"}
                            />
                            <MetricCard
                                icon={Activity}
                                title="Latest score"
                                value={data.latest_mark ? `${data.latest_mark.percentage}%` : "No marks"}
                                summary={data.latest_mark ? `${data.latest_mark.subject} - ${data.latest_mark.exam}` : "No recent marks have been recorded."}
                                tone="blue"
                            />
                            <MetricCard
                                icon={FileText}
                                title="Pending work"
                                value={`${data.pending_assignments}`}
                                summary={data.pending_assignments > 0 ? "Assignments still need attention this week." : "No assignments are currently pending."}
                                tone={data.pending_assignments > 0 ? "amber" : "emerald"}
                            />
                        </div>

                        <div className="grid gap-4 lg:grid-cols-[1.04fr_0.96fr]">
                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Sparkles className="h-4 w-4 text-status-amber" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Progress story</h2>
                                </div>
                                <div className="mt-4 space-y-4 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>
                                        Attendance is currently <span className="font-semibold text-[var(--text-primary)]">{data.attendance_pct}%</span>, and the latest academic result is{" "}
                                        <span className="font-semibold text-[var(--text-primary)]">{data.latest_mark ? `${data.latest_mark.percentage}% in ${data.latest_mark.subject}` : "not yet available"}</span>.
                                    </p>
                                    <p>
                                        {data.pending_assignments > 0
                                            ? `${data.pending_assignments} assignment${data.pending_assignments === 1 ? "" : "s"} still need attention, so this week should stay focused on completion and follow-through.`
                                            : "There are no pending assignments right now, which creates room to focus on consistency and revision."}
                                    </p>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Clock className="h-4 w-4 text-status-blue" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent academic detail</h2>
                                </div>
                                {data.latest_mark ? (
                                    <div className="mt-4 space-y-3">
                                        <DetailRow label="Subject" value={data.latest_mark.subject} />
                                        <DetailRow label="Assessment" value={data.latest_mark.exam} />
                                        <DetailRow label="Recorded" value={formatDate(data.latest_mark.date)} />
                                        <DetailRow label="Average marks" value={`${data.avg_marks}%`} />
                                    </div>
                                ) : (
                                    <p className="mt-4 text-sm text-[var(--text-secondary)]">Recent mark details will appear here once the next graded result is available.</p>
                                )}
                            </PrismPanel>
                        </div>

                        <div className="grid gap-4 lg:grid-cols-[1.06fr_0.94fr]">
                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Activity className="h-4 w-4 text-status-blue" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Six-month learning rhythm</h2>
                                </div>
                                <div className="mt-4 grid gap-3 md:grid-cols-3">
                                    {data.monthly_attendance.map((month, index) => (
                                        <div key={`${month.month}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{month.month}</p>
                                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{month.attendance_pct}% attendance</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                {month.marked_days} marked day{month.marked_days === 1 ? "" : "s"} and {data.monthly_assignments[index]?.assignments_submitted ?? 0} assignment submission{(data.monthly_assignments[index]?.assignments_submitted ?? 0) === 1 ? "" : "s"}.
                                            </p>
                                            <p className="mt-2 text-xs text-[var(--text-muted)]">
                                                Result average: {data.monthly_performance[index]?.average_pct ?? 0}% from {data.monthly_performance[index]?.exams_recorded ?? 0} exam{(data.monthly_performance[index]?.exams_recorded ?? 0) === 1 ? "" : "s"}.
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <FileText className="h-4 w-4 text-status-amber" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Study activity trail</h2>
                                </div>
                                <div className="mt-4 grid gap-3 sm:grid-cols-2">
                                    <DetailCard label="Assignments done" value={`${data.summary.assignments_submitted}`} detail="Submitted across the last six months" />
                                    <DetailCard label="Study sessions" value={`${data.summary.study_sessions}`} detail="Focused learning sessions captured in demo history" />
                                    <DetailCard label="AI requests" value={`${data.summary.ai_requests}`} detail="Child questions and guided support moments" />
                                    <DetailCard label="Generated tools" value={`${data.summary.generated_tools}`} detail="Audio, video, mind maps, and revision artifacts" />
                                </div>
                                <div className="mt-5 space-y-3">
                                    {data.summary.recent_generated_tools.length > 0 ? (
                                        data.summary.recent_generated_tools.map((item) => (
                                            <div key={item.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                <p className="text-sm font-medium text-[var(--text-primary)]">{item.title}</p>
                                                <p className="mt-1 text-xs text-[var(--text-muted)]">
                                                    {item.type.replace(/_/g, " ")} • {formatDate(item.created_at)}
                                                </p>
                                            </div>
                                        ))
                                    ) : (
                                        <p className="text-sm text-[var(--text-secondary)]">Saved study tools will appear here once the learner generates them.</p>
                                    )}
                                </div>
                            </PrismPanel>
                        </div>
                    </>
                ) : null}
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    icon: Icon,
    title,
    value,
    summary,
    tone,
}: {
    icon: typeof CalendarCheck;
    title: string;
    value: string;
    summary: string;
    tone: "blue" | "emerald" | "amber";
}) {
    const toneClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))] text-status-blue",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))] text-status-emerald",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))] text-status-amber",
    } as const;

    return (
        <PrismPanel className="p-5">
            <div className={`mb-4 flex h-11 w-11 items-center justify-center rounded-2xl ${toneClasses[tone]}`}>
                <Icon className="h-5 w-5" />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 text-3xl font-black text-[var(--text-primary)]">{value}</p>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </PrismPanel>
    );
}

function DetailRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</span>
            <span className="text-sm font-medium text-[var(--text-primary)]">{value}</span>
        </div>
    );
}

function DetailCard({ label, value, detail }: { label: string; value: string; detail: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{detail}</p>
        </div>
    );
}
