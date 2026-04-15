"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertCircle, ArrowRight, CalendarCheck, ClipboardCheck, Sparkles, TrendingDown } from "lucide-react";

import { api } from "@/lib/api";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSectionHeader } from "@/components/prism/PrismPage";
import { RoleMorningBriefing } from "@/components/RoleMorningBriefing";
import ErrorRemediation from "@/components/ui/ErrorRemediation";

type TeacherClass = { id: string; name: string; students: number; avg_attendance: number; avg_marks: number };
type TodayClass = { class_id: string; class_name: string; subject: string; start_time: string; end_time: string };
type TeacherDashboardData = { classes?: TeacherClass[]; today_classes?: TodayClass[]; pending_reviews?: number; open_assignments?: number };

function formatStartTime(value: string | null | undefined) {
    if (!value) return "TBD";
    if (!value.includes(":")) return value;
    const [hours = "", minutes = ""] = value.split(":");
    return minutes ? `${hours}:${minutes}` : hours || value;
}

function normalizeDashboardData(payload: TeacherDashboardData | null | undefined) {
    return {
        classes: (payload?.classes || []) as TeacherClass[],
        todayClasses: (payload?.today_classes || []) as TodayClass[],
        pendingReviews: Number(payload?.pending_reviews || 0),
        openAssignments: Number(payload?.open_assignments || 0),
    };
}

function formatActivationLeadTime(value: string | null | undefined) {
    if (!value || !value.includes(":")) return "today";
    const [hoursRaw = "0", minutesRaw = "0"] = value.split(":");
    const start = new Date();
    start.setHours(Number(hoursRaw), Number(minutesRaw), 0, 0);
    const diffMinutes = Math.round((start.getTime() - Date.now()) / 60_000);
    if (diffMinutes <= 0) return "now";
    if (diffMinutes < 60) return `in ${diffMinutes} minutes`;
    const hours = Math.floor(diffMinutes / 60);
    const minutes = diffMinutes % 60;
    return minutes ? `in ${hours} hr ${minutes} min` : `in ${hours} hr`;
}

export function TeacherDashboardClient({ initialData = null }: { initialData?: TeacherDashboardData | null }) {
    const normalizedInitial = normalizeDashboardData(initialData);
    const [classes, setClasses] = useState<TeacherClass[]>(normalizedInitial.classes);
    const [todayClasses, setTodayClasses] = useState<TodayClass[]>(normalizedInitial.todayClasses);
    const [pendingReviews, setPendingReviews] = useState(normalizedInitial.pendingReviews);
    const [openAssignments, setOpenAssignments] = useState(normalizedInitial.openAssignments);
    const [loading, setLoading] = useState(!initialData);
    const [error, setError] = useState<string | null>(null);

    const applyDashboard = useCallback((payload: TeacherDashboardData | null | undefined) => {
        const normalized = normalizeDashboardData(payload);
        setClasses(normalized.classes);
        setTodayClasses(normalized.todayClasses);
        setPendingReviews(normalized.pendingReviews);
        setOpenAssignments(normalized.openAssignments);
    }, []);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            applyDashboard((await api.teacher.dashboard()) as TeacherDashboardData | null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load dashboard");
        } finally {
            setLoading(false);
        }
    }, [applyDashboard]);

    useEffect(() => {
        if (!initialData) void load();
    }, [initialData, load]);

    const weakestClass = useMemo(() => classes.length ? [...classes].sort((a, b) => a.avg_marks - b.avg_marks)[0] : null, [classes]);
    const nextClass = todayClasses[0] || null;
    const briefingFacts = useMemo(() => [
        `${todayClasses.length} class session${todayClasses.length === 1 ? "" : "s"} scheduled today`,
        `${pendingReviews} assignment review${pendingReviews === 1 ? "" : "s"} pending`,
        `${openAssignments} open assignment${openAssignments === 1 ? "" : "s"}`,
        weakestClass ? `${weakestClass.name} has the lowest average marks at ${weakestClass.avg_marks}%` : "",
    ], [openAssignments, pendingReviews, todayClasses.length, weakestClass]);
    const briefingFallback = useMemo(() => [
        `You have ${todayClasses.length} class session${todayClasses.length === 1 ? "" : "s"} today.`,
        `${pendingReviews} submission${pendingReviews === 1 ? "" : "s"} still need review.`,
        weakestClass ? `${weakestClass.name} needs revision focus.` : "No weak-class signal is active right now.",
    ], [pendingReviews, todayClasses.length, weakestClass]);

    return (
        <PrismPage variant="dashboard" className="max-w-6xl space-y-6">
            <PrismPageIntro
                kicker={<PrismHeroKicker>Teacher daily workflow</PrismHeroKicker>}
                title="Guide the day, not the dashboard"
                description="The teacher home now strips back to the daily workflow: classes, attendance, grading, and weak-topic follow-up."
            />

            {error ? <ErrorRemediation error={error} scope="teacher-dashboard" onRetry={() => void load()} /> : null}
            {!loading ? <RoleMorningBriefing role="teacher" facts={briefingFacts} fallback={briefingFallback} /> : null}

            {loading ? (
                <PrismPanel className="p-8 text-sm text-[var(--text-secondary)]">Loading today&apos;s teaching workflow...</PrismPanel>
            ) : (
                <div className="grid gap-6 xl:grid-cols-[1.12fr_0.88fr]">
                    {nextClass ? (
                        <PrismPanel className="p-6 xl:col-span-2">
                            <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Teacher activation</p>
                                    <h2 className="mt-2 text-2xl font-black text-[var(--text-primary)]">Take attendance for your next class.</h2>
                                    <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                        {nextClass.class_name} {nextClass.subject} starts {formatActivationLeadTime(nextClass.start_time)}.
                                    </p>
                                </div>
                                <Link
                                    href={`/teacher/attendance?classId=${nextClass.class_id}`}
                                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(16,185,129,0.96),rgba(34,197,94,0.9))] px-5 py-3 text-sm font-bold text-[#06101e] transition hover:-translate-y-0.5"
                                >
                                    Open attendance sheet
                                    <ArrowRight className="h-4 w-4" />
                                </Link>
                            </div>
                        </PrismPanel>
                    ) : null}

                    <PrismPanel className="p-6">
                        <PrismSectionHeader title="Today&apos;s classes" description="Attendance should be one click away from every active session." />
                        <div className="mt-4 space-y-4">
                            {todayClasses.length > 0 ? todayClasses.map((slot) => (
                                <div key={`${slot.class_id}-${slot.start_time}`} className="vidya-feed-row">
                                    <div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">{slot.class_name} · {slot.subject}</p>
                                        <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{formatStartTime(slot.start_time)} to {formatStartTime(slot.end_time)}</p>
                                    </div>
                                    <Link href={`/teacher/attendance?classId=${slot.class_id}`} className="prism-action-secondary">
                                        Take attendance
                                    </Link>
                                </div>
                            )) : <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-5 py-5 text-sm text-[var(--text-secondary)]">No classes are scheduled right now.</div>}
                        </div>
                    </PrismPanel>

                    <PrismPanel className="p-6">
                        <PrismSectionHeader title="Needs your attention" description="Daily work should resolve from here without hunting through the nav." />
                        <div className="mt-4 space-y-4">
                            <AttentionRow title="Pending reviews" detail="Student submissions waiting for grading or review." href="/teacher/assignments" value={`${pendingReviews}`} />
                            <AttentionRow title="Open assignments" detail="Active coursework still running across your classes." href="/teacher/assignments" value={`${openAssignments}`} />
                            <AttentionRow title="Weak-topic follow-up" detail={weakestClass ? `${weakestClass.name} is the weakest class right now at ${weakestClass.avg_marks}%.` : "No class-level weakness signal is active yet."} href="/teacher/doubt-heatmap" value={weakestClass ? weakestClass.name : "Open"} />
                            <AttentionRow title="Prepare next assessment" detail="Create and send the next assessment while today&apos;s class context is fresh." href="/teacher/generate-assessment" value="Open" />
                        </div>
                    </PrismPanel>

                    <PrismPanel className="p-6 xl:col-span-2">
                        <PrismSectionHeader title="Since yesterday" description="A light context layer helps VidyaOS feel continuous across your teaching day." />
                        <div className="mt-4 grid gap-4 sm:grid-cols-2 md:grid-cols-3">
                            <SummaryTile icon={ClipboardCheck} title="Grading queue" detail={`${pendingReviews} review item${pendingReviews === 1 ? "" : "s"} still waiting.`} />
                            <SummaryTile icon={CalendarCheck} title="Teaching load" detail={`${todayClasses.length} class session${todayClasses.length === 1 ? "" : "s"} scheduled today.`} />
                            <SummaryTile icon={weakestClass ? TrendingDown : Sparkles} title="Coaching signal" detail={weakestClass ? `${weakestClass.name} needs revision focus.` : "No weak class signal is active right now."} />
                        </div>
                    </PrismPanel>
                </div>
            )}
        </PrismPage>
    );
}

function AttentionRow({ title, detail, href, value }: { title: string; detail: string; href: string; value: string }) {
    return <div className="vidya-feed-row"><div><p className="text-sm font-semibold text-[var(--text-primary)]">{title}</p><p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p></div><Link href={href} className="prism-action-secondary">{value}</Link></div>;
}

function SummaryTile({ icon: Icon, title, detail }: { icon: typeof AlertCircle; title: string; detail: string }) {
    return <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-5"><div className="flex items-center gap-2 text-[var(--text-primary)]"><Icon className="h-4 w-4" /><p className="text-sm font-semibold">{title}</p></div><p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p></div>;
}

