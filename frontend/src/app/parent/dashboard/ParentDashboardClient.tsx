"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { Activity, CalendarCheck, FileText, GraduationCap, Loader2, ShieldCheck, Volume2, VolumeX } from "lucide-react";

import { api } from "@/lib/api";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSectionHeader } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { SkeletonList } from "@/components/Skeleton";
import { RoleMorningBriefing } from "@/components/RoleMorningBriefing";
import { ParentAIInsightsWidget } from "@/components/parent/ParentAIInsightsWidget";

type ParentDashboard = {
    child: { id: string; name: string; email: string; class: string | null };
    attendance_pct: number;
    avg_marks: number;
    pending_assignments: number;
    next_assignment?: { title: string; subject: string; due: string | null } | null;
    latest_mark: { subject: string; exam: string; percentage: number; date: string | null } | null;
    summary: {
        assignments_submitted: number;
        study_sessions: number;
        ai_requests: number;
        generated_tools: number;
        latest_ai_session?: { topic: string; duration_minutes: number; last_studied_at: string | null } | null;
    };
};

const EMPTY_PARENT_DASHBOARD: ParentDashboard = {
    child: { id: "", name: "", email: "", class: null },
    attendance_pct: 0,
    avg_marks: 0,
    pending_assignments: 0,
    next_assignment: null,
    latest_mark: null,
    summary: { assignments_submitted: 0, study_sessions: 0, ai_requests: 0, generated_tools: 0, latest_ai_session: null },
};

function formatDate(value: string | null | undefined) {
    if (!value) return "No due date";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString();
}

function normalizeParentDashboard(payload: unknown): ParentDashboard {
    if (!payload || typeof payload !== "object") return EMPTY_PARENT_DASHBOARD;
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
        next_assignment: candidate.next_assignment ?? null,
        latest_mark: candidate.latest_mark ?? null,
        summary: {
            assignments_submitted: candidate.summary?.assignments_submitted ?? 0,
            study_sessions: candidate.summary?.study_sessions ?? 0,
            ai_requests: candidate.summary?.ai_requests ?? 0,
            generated_tools: candidate.summary?.generated_tools ?? 0,
            latest_ai_session: candidate.summary?.latest_ai_session ?? null,
        },
    };
}

export function ParentDashboardClient({ initialData = null }: { initialData?: unknown }) {
    const [data, setData] = useState<ParentDashboard | null>(initialData ? normalizeParentDashboard(initialData) : null);
    const [loading, setLoading] = useState(!initialData);
    const [error, setError] = useState<string | null>(null);
    const [speaking, setSpeaking] = useState(false);
    const [audioLoading, setAudioLoading] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            setData(normalizeParentDashboard(await api.parent.dashboard()));
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : "Failed to load dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!initialData) void load();
    }, [initialData, load]);

    useEffect(() => () => {
        if (typeof window !== "undefined") {
            window.speechSynthesis.cancel();
            setSpeaking(false);
        }
    }, []);
    const briefingFacts = useMemo(() => data ? [
        `${data.child.name} has ${data.attendance_pct}% attendance`,
        `Average marks are ${data.avg_marks}%`,
        data.next_assignment ? `Next assignment is ${data.next_assignment.title} due ${formatDate(data.next_assignment.due)}` : `${data.pending_assignments} pending assignments`,
        data.summary.latest_ai_session ? `Last AI Studio session was ${data.summary.latest_ai_session.topic} for ${data.summary.latest_ai_session.duration_minutes} minutes` : "",
    ] : [], [data]);
    const briefingFallback = useMemo(() => data ? [
        `${data.child.name || "Your child"} is at ${data.attendance_pct}% attendance.`,
        data.latest_mark ? `Latest score: ${data.latest_mark.percentage}% in ${data.latest_mark.subject}.` : "No recent marks are available yet.",
        data.next_assignment ? `${data.next_assignment.title} is the next assignment due.` : "No upcoming assignment due date is available.",
    ] : [], [data]);

    const playAudioReport = async () => {
        if (speaking) {
            window.speechSynthesis.cancel();
            setSpeaking(false);
            return;
        }
        try {
            setAudioLoading(true);
            setError(null);
            const lowDataEnabled = typeof window !== "undefined" && document.documentElement.classList.contains("low-data-mode");
            const connection = typeof navigator !== "undefined" ? (navigator as Navigator & { connection?: { type?: string; effectiveType?: string } }).connection : undefined;
            if (lowDataEnabled && connection?.type && connection.type !== "wifi") {
                setError("Low-data mode is on. Audio summaries download only on WiFi.");
                return;
            }
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
            <PrismPageIntro
                kicker={<PrismHeroKicker><ShieldCheck className="h-3.5 w-3.5" />Parent weekly summary</PrismHeroKicker>}
                title="Read your child&apos;s week in under a minute"
                description="The parent home is now intentionally simple: attendance, the latest score, the next assignment due, and one audio summary button."
            />

            {error ? <ErrorRemediation error={error} scope="parent-dashboard" onRetry={() => { void load(); }} /> : null}
            {!loading && data ? <RoleMorningBriefing role="parent" facts={briefingFacts} fallback={briefingFallback} /> : null}

            {loading ? (
                <PrismPanel className="min-h-[260px] p-6">
                    <p className="text-sm font-semibold text-[var(--text-primary)]">Preparing the parent weekly summary...</p>
                    <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">Checking attendance, marks, upcoming work, and the latest AI study activity.</p>
                    <div className="mt-5">
                        <SkeletonList items={4} />
                    </div>
                </PrismPanel>
            ) : data ? (
                <>
                    <PrismPanel className="p-6">
                        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                            <div>
                                <div className="inline-flex items-center gap-2 rounded-full border border-[rgba(249,115,22,0.22)] bg-[rgba(249,115,22,0.08)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-status-orange">
                                    <GraduationCap className="h-3.5 w-3.5" />
                                    {data.child.class ? `Class ${data.child.class}` : "Student profile"}
                                </div>
                                <h2 className="mt-4 text-3xl font-black text-[var(--text-primary)]">{data.child.name}</h2>
                                <p className="mt-2 text-sm text-[var(--text-secondary)]">{data.child.email}</p>
                            </div>
                            <button
                                type="button"
                                onClick={() => void playAudioReport()}
                                disabled={audioLoading}
                                className={`inline-flex items-center gap-3 rounded-2xl px-5 py-3 text-sm font-semibold text-white shadow-[var(--shadow-level-2)] ${speaking ? "bg-[linear-gradient(135deg,rgba(244,114,182,0.95),rgba(225,29,72,0.92))]" : "bg-[linear-gradient(135deg,rgba(245,158,11,0.95),rgba(249,115,22,0.92))]"}`}
                            >
                                {audioLoading ? <Loader2 className="h-5 w-5 animate-spin" /> : speaking ? <VolumeX className="h-5 w-5" /> : <Volume2 className="h-5 w-5" />}
                                {speaking ? "Stop audio summary" : "Play 2 min audio summary"}
                            </button>
                        </div>
                    </PrismPanel>

                    <div className="grid gap-4 md:grid-cols-3">
                        <MetricCard icon={CalendarCheck} title="Attendance %" value={`${data.attendance_pct}%`} summary={data.attendance_pct >= 75 ? "Healthy attendance range this week." : "Attendance needs attention this week."} />
                        <MetricCard icon={Activity} title="Last test score" value={data.latest_mark ? `${data.latest_mark.percentage}%` : "No marks"} summary={data.latest_mark ? `${data.latest_mark.subject} · ${data.latest_mark.exam}` : "No recent test has been recorded yet."} />
                        <MetricCard icon={FileText} title="Next assignment due" value={data.next_assignment ? formatDate(data.next_assignment.due) : `${data.pending_assignments} pending`} summary={data.next_assignment ? `${data.next_assignment.title} · ${data.next_assignment.subject}` : "No upcoming due date is available right now."} />
                    </div>

                    <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
                        <PrismPanel className="p-6">
                            <PrismSectionHeader title="Last week&apos;s highlights" description="A short vertical summary that feels more like a WhatsApp update than an admin report." />
                            <div className="mt-4 space-y-4">
                                <HighlightRow title="Attendance" detail={`${data.attendance_pct}% attendance recorded this week.`} />
                                <HighlightRow title="Latest result" detail={data.latest_mark ? `Scored ${data.latest_mark.percentage}% in ${data.latest_mark.subject}.` : "No recent marked assessment is available yet."} />
                                <HighlightRow title="Study activity" detail={`AI sessions: ${data.summary.ai_requests}. Study sessions: ${data.summary.study_sessions}.`} />
                                <HighlightRow
                                    title="Last AI Studio session"
                                    detail={data.summary.latest_ai_session
                                        ? `${data.summary.latest_ai_session.topic} • ${data.summary.latest_ai_session.duration_minutes} min${data.summary.latest_ai_session.last_studied_at ? ` • ${formatDate(data.summary.latest_ai_session.last_studied_at)}` : ""}`
                                        : "No AI Studio session is visible to parent view yet."}
                                />
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-6">
                            <PrismSectionHeader title="Quick links" description="If you want detail, it should still stay one tap away." />
                            <div className="mt-4 space-y-4">
                                <Link href="/parent/attendance" className="vidya-feed-row"><div><p className="text-sm font-semibold text-[var(--text-primary)]">Attendance log</p><p className="mt-1 text-sm text-[var(--text-secondary)]">Review daily attendance history.</p></div><span className="prism-action-secondary">Open</span></Link>
                                <Link href="/parent/results" className="vidya-feed-row"><div><p className="text-sm font-semibold text-[var(--text-primary)]">Exam results</p><p className="mt-1 text-sm text-[var(--text-secondary)]">See subject-wise marks and progress.</p></div><span className="prism-action-secondary">Open</span></Link>
                                <Link href="/parent/assistant?prompt=I%20want%20to%20report%20an%20issue%20about%20my%20child" className="vidya-feed-row"><div><p className="text-sm font-semibold text-[var(--text-primary)]">Report an issue</p><p className="mt-1 text-sm text-[var(--text-secondary)]">Start a parent support message without searching the admin system.</p></div><span className="prism-action-secondary">Open</span></Link>
                                <Link href="/parent/reports" className="vidya-feed-row"><div><p className="text-sm font-semibold text-[var(--text-primary)]">Progress reports</p><p className="mt-1 text-sm text-[var(--text-secondary)]">Open the full six-month overview only when needed.</p></div><span className="prism-action-secondary">Open</span></Link>
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-6">
                            <ParentAIInsightsWidget childId={data?.child.id} days={7} loading={loading} />
                        </PrismPanel>
                    </div>
                </>
            ) : null}
        </PrismPage>
    );
}

function MetricCard({ icon: Icon, title, value, summary }: { icon: typeof CalendarCheck; title: string; value: string; summary: string }) {
    return <PrismPanel className="p-6"><div className="mb-4 flex h-11 w-11 items-center justify-center rounded-2xl bg-[rgba(249,115,22,0.12)] text-status-orange"><Icon className="h-5 w-5" /></div><p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">{title}</p><p className="mt-2 text-3xl font-black text-[var(--text-primary)]">{value}</p><p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p></PrismPanel>;
}

function HighlightRow({ title, detail }: { title: string; detail: string }) {
    return <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-5 py-5"><p className="text-sm font-semibold text-[var(--text-primary)]">{title}</p><p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p></div>;
}
