"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import {
    ArrowRight,
    Bot,
    Clock3,
    FileText,
    Sparkles,
    Target,
    TrendingDown,
    TrendingUp,
    Zap,
} from "lucide-react";

import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSectionHeader } from "@/components/prism/PrismPage";
import { SkeletonCard } from "@/components/Skeleton";
import { RoleStartPanel } from "@/components/RoleStartPanel";
import { RoleMorningBriefing } from "@/components/RoleMorningBriefing";
import { MascotGreetingCard } from "@/components/mascot/MascotGreetingCard";
import { GamificationHero } from "@/components/student/GamificationHero";
import { AIActionCenter } from "@/components/student/AIActionCenter";
import { AcademicSnapshot } from "@/components/student/AcademicSnapshot";
import { AISessionInsights } from "@/components/student/AISessionInsights";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { APIError, api } from "@/lib/api";

type DashboardStats = {
    attendance_pct: number;
    avg_marks: number;
    pending_assignments: number;
    next_assignment?: {
        title: string;
        subject: string;
        due: string | null;
    } | null;
    ai_queries_today: number;
    ai_queries_limit: number;
    upcoming_classes: Array<{
        subject: string;
        time: string;
    }>;
    my_uploads: number;
    ai_insight: string | null;
};

type WeakTopic = {
    subject: string;
    average_score: number;
    exam_count: number;
    is_weak: boolean;
};

type WeakTopicPayload = {
    weak_topics: WeakTopic[];
    strong_topics: WeakTopic[];
};

type PersonalizedRecommendation = {
    id: string;
    label: string;
    description: string;
    prompt: string;
    target_tool?: string;
    reason?: string;
    priority?: string;
};

type StudyPathStep = {
    id: string;
    title: string;
    target_tool?: string;
    prompt?: string;
    status?: string;
};

type StudyPathPlan = {
    id: string;
    focus_topic: string;
    status: string;
    items: StudyPathStep[];
    next_action?: StudyPathStep | null;
};

type Badge = {
    id: string;
    name: string;
    icon: string;
};

type StreakInfo = {
    current_streak: number;
    longest_streak: number;
    total_sessions: number;
    last_login: string | null;
    badges: Badge[];
};

type WeeklyPoint = { day: string; value: number };

type StudentOverviewBootstrap = {
    dashboard?: DashboardStats | null;
    weak_topics?: WeakTopicPayload | null;
    streaks?: StreakInfo | null;
    recommendations?: { items?: PersonalizedRecommendation[] } | null;
    study_path?: { plan?: StudyPathPlan | null } | null;
    weekly_charts?: {
        weekly_attendance?: WeeklyPoint[];
        weekly_marks?: WeeklyPoint[];
    } | null;
};

const emptyStats: DashboardStats = {
    attendance_pct: 0,
    avg_marks: 0,
    pending_assignments: 0,
    next_assignment: null,
    ai_queries_today: 0,
    ai_queries_limit: 50,
    upcoming_classes: [],
    my_uploads: 0,
    ai_insight: null,
};


function normalizeBootstrap(payload: StudentOverviewBootstrap | null | undefined) {
    const dashboardPayload = payload?.dashboard || emptyStats;
    const topicPayload = payload?.weak_topics || { weak_topics: [], strong_topics: [] };
    const recommendationPayload = payload?.recommendations || { items: [] };
    const studyPathPayload = payload?.study_path || { plan: null };
    const chartsPayload = payload?.weekly_charts || {};

    return {
        stats: dashboardPayload as DashboardStats,
        weakTopics: topicPayload.weak_topics || [],
        strongTopics: topicPayload.strong_topics || [],
        streak: (payload?.streaks || null) as StreakInfo | null,
        recommendations: Array.isArray(recommendationPayload.items) ? recommendationPayload.items : [],
        studyPath: (studyPathPayload.plan || null) as StudyPathPlan | null,
        weeklyAttendance: (chartsPayload.weekly_attendance || []) as WeeklyPoint[],
        weeklyMarks: (chartsPayload.weekly_marks || []) as WeeklyPoint[],
    };
}

function formatDueLabel(value: string | null | undefined) {
    if (!value) return "No due date";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleDateString();
}

export function StudentOverviewClient({
    initialData = null,
}: {
    initialData?: StudentOverviewBootstrap | null;
}) {
    const initialState = normalizeBootstrap(initialData);
    const [stats, setStats] = useState<DashboardStats>(initialState.stats);
    const [weakTopics, setWeakTopics] = useState<WeakTopic[]>(initialState.weakTopics);
    const [strongTopics, setStrongTopics] = useState<WeakTopic[]>(initialState.strongTopics);
    const [recommendations, setRecommendations] = useState<PersonalizedRecommendation[]>(initialState.recommendations);
    const [studyPath, setStudyPath] = useState<StudyPathPlan | null>(initialState.studyPath);
    const [streak, setStreak] = useState<StreakInfo | null>(initialState.streak);
    const [weeklyAttendance, setWeeklyAttendance] = useState<WeeklyPoint[]>(initialState.weeklyAttendance);
    const [weeklyMarks, setWeeklyMarks] = useState<WeeklyPoint[]>(initialState.weeklyMarks);
    const [loading, setLoading] = useState(!initialData);
    const [error, setError] = useState<Error | null>(null);
    const [chartsReady, setChartsReady] = useState(false);
    const [showFullDashboard, setShowFullDashboard] = useState(false);

    const applyBootstrap = useCallback((payload: StudentOverviewBootstrap | null | undefined) => {
        const nextState = normalizeBootstrap(payload);
        setStats(nextState.stats);
        setWeakTopics(nextState.weakTopics);
        setStrongTopics(nextState.strongTopics);
        setStreak(nextState.streak);
        setRecommendations(nextState.recommendations);
        setStudyPath(nextState.studyPath);
        setWeeklyAttendance(nextState.weeklyAttendance);
        setWeeklyMarks(nextState.weeklyMarks);
    }, []);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            try {
                const payload = await api.student.overviewBootstrap();
                applyBootstrap((payload || null) as StudentOverviewBootstrap | null);
            } catch {
                const [dashboardPayload, weakTopicPayload, streakPayload, recommendationPayload, studyPathPayload] = await Promise.all([
                    api.student.dashboard(),
                    api.student.weakTopics(),
                    api.student.streaks(),
                    api.personalization.recommendations({ current_surface: "overview" }),
                    api.personalization.studyPath({ current_surface: "overview" }),
                ]);

                applyBootstrap({
                    dashboard: (dashboardPayload || emptyStats) as DashboardStats,
                    weak_topics: (weakTopicPayload || { weak_topics: [], strong_topics: [] }) as WeakTopicPayload,
                    streaks: (streakPayload || null) as StreakInfo | null,
                    recommendations: (recommendationPayload || { items: [] }) as { items?: PersonalizedRecommendation[] },
                    study_path: (studyPathPayload || { plan: null }) as { plan?: StudyPathPlan | null },
                });
            }
        } catch (err) {
            setError(err instanceof Error ? err : new APIError("Failed to load dashboard", 0, "unknown", "Retry now"));
        } finally {
            setLoading(false);
        }
    }, [applyBootstrap]);

    useEffect(() => {
        if (!initialData) {
            void load();
        }
    }, [initialData, load]);

    useEffect(() => {
        const id = requestAnimationFrame(() => setChartsReady(true));
        return () => cancelAnimationFrame(id);
    }, []);

    const allTopics = useMemo(() => {
        return [...weakTopics, ...strongTopics].sort((a, b) => a.average_score - b.average_score);
    }, [weakTopics, strongTopics]);

    const recordPersonalizationEvent = useCallback(
        (eventType: "recommendation_click" | "study_path_open", target: string, itemId?: string) => {
            void api.personalization.recordEvent({
                event_type: eventType,
                surface: "overview",
                target,
                item_id: itemId,
            }).catch(() => null);
        },
        [],
    );

    const focusTopic = useMemo(() => {
        return (
            studyPath?.focus_topic
            || stats.next_assignment?.subject
            || weakTopics[0]?.subject
            || stats.upcoming_classes[0]?.subject
            || "Science"
        );
    }, [stats.next_assignment?.subject, stats.upcoming_classes, studyPath?.focus_topic, weakTopics]);

    const leadRecommendation = recommendations[0] || null;
    const shortcutTool = leadRecommendation?.target_tool || studyPath?.next_action?.target_tool || "qa";
    const shortcutPrompt = leadRecommendation?.prompt || studyPath?.next_action?.prompt || `Help me understand ${focusTopic}`;
    const aiShortcutHref = `/student/ai-studio?mode=${encodeURIComponent(shortcutTool)}&prompt=${encodeURIComponent(shortcutPrompt)}`;

    const sinceYesterday = useMemo(() => {
        const lines = [
            stats.ai_queries_today > 0
                ? `You already used AI Studio ${stats.ai_queries_today} time${stats.ai_queries_today === 1 ? "" : "s"} today.`
                : "No AI sessions yet today, so the next focused question can reset momentum quickly.",
            stats.upcoming_classes[0]
                ? `Your next class is ${stats.upcoming_classes[0].subject} at ${stats.upcoming_classes[0].time}.`
                : "No more classes are scheduled today, so this is a good revision window.",
            weakTopics[0]
                ? `${weakTopics[0].subject} is still your weakest scored subject right now.`
                : "No weak subject warning is active right now.",
        ];
        return lines;
    }, [stats.ai_queries_today, stats.upcoming_classes, weakTopics]);
    const briefingFacts = useMemo(() => [
        `${stats.pending_assignments} pending assignment${stats.pending_assignments === 1 ? "" : "s"}`,
        `${stats.attendance_pct}% attendance`,
        `${stats.avg_marks}% average marks`,
        `Focus topic is ${focusTopic}`,
        stats.next_assignment ? `Next assignment is ${stats.next_assignment.title} for ${stats.next_assignment.subject}` : "",
    ], [focusTopic, stats.attendance_pct, stats.avg_marks, stats.next_assignment, stats.pending_assignments]);
    const briefingFallback = useMemo(() => [
        `${focusTopic} is the clearest study focus today.`,
        `${stats.pending_assignments} assignment${stats.pending_assignments === 1 ? "" : "s"} still need attention.`,
        `Attendance is ${stats.attendance_pct}%, so keep today consistent.`,
    ], [focusTopic, stats.attendance_pct, stats.pending_assignments]);

    const actionFeed = useMemo(() => {
        const items: Array<{ title: string; detail: string; href: string; label: string; icon: typeof Target }> = [];

        if (stats.next_assignment) {
            items.push({
                title: stats.next_assignment.title,
                detail: `${stats.next_assignment.subject} · due ${formatDueLabel(stats.next_assignment.due)}`,
                href: "/student/assignments",
                label: "Submit work",
                icon: FileText,
            });
        }

        if (studyPath?.next_action) {
            items.push({
                title: studyPath.next_action.title,
                detail: `Continue your learning path on ${studyPath.focus_topic}.`,
                href: aiShortcutHref,
                label: "Resume study",
                icon: Zap,
            });
        }

        if (stats.upcoming_classes[0]) {
            items.push({
                title: `${stats.upcoming_classes[0].subject} is coming up`,
                detail: `Class starts at ${stats.upcoming_classes[0].time}. Review the core idea before it begins.`,
                href: "/student/timetable",
                label: "Open timetable",
                icon: Clock3,
            });
        }

        if (weakTopics[0]) {
            items.push({
                title: `Strengthen ${weakTopics[0].subject}`,
                detail: `${weakTopics[0].average_score}% average across ${weakTopics[0].exam_count} assessment${weakTopics[0].exam_count === 1 ? "" : "s"}.`,
                href: aiShortcutHref,
                label: "Ask AI for help",
                icon: TrendingDown,
            });
        } else if (strongTopics[0]) {
            items.push({
                title: `${strongTopics[0].subject} is trending well`,
                detail: "Use that subject to build confidence before moving into a harder revision block.",
                href: "/student/results",
                label: "View progress",
                icon: TrendingUp,
            });
        }

        if (items.length === 0) {
            items.push({
                title: `Start a grounded ${focusTopic} session`,
                detail: "Open AI Studio with a single focused question and let the evidence rail guide the session.",
                href: aiShortcutHref,
                label: "Open AI Studio",
                icon: Bot,
            });
        }

        return items.slice(0, 4);
    }, [aiShortcutHref, focusTopic, stats.next_assignment, stats.upcoming_classes, strongTopics, studyPath, weakTopics]);

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <MascotGreetingCard role="student" />
            <PrismPageIntro
                kicker={<PrismHeroKicker>Student command center</PrismHeroKicker>}
                title="Open VidyaOS and know what to do next"
                description="The top of this page stays intentionally narrow: one study focus, one attendance signal, and one direct AI shortcut. Everything else can wait until you need it."
                aside={(
                    <div className="prism-briefing-panel">
                        <p className="prism-status-label">Today&apos;s focus</p>
                        <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                            {studyPath?.focus_topic || focusTopic}
                        </p>
                        <p className="mt-2 text-xs text-[var(--text-muted)]">
                            {streak ? `${streak.current_streak}-day streak active` : "Fresh day, fresh study block"}
                        </p>
                    </div>
                )}
            />

            {error ? <ErrorRemediation error={error} scope="student-overview" onRetry={() => void load()} simplifiedModeHref="/student/tools" /> : null}
            {!loading ? <RoleMorningBriefing role="student" facts={briefingFacts} fallback={briefingFallback} /> : null}

            {loading ? (
                <div className="grid gap-4 lg:grid-cols-3">
                    {Array.from({ length: 3 }).map((_, index) => <SkeletonCard key={index} />)}
                </div>
            ) : (
                <div className="grid gap-4 lg:grid-cols-[1.2fr_0.8fr_0.95fr]">
                    <div className="vidya-command-card">
                        <p className="prism-status-label">What to study today</p>
                        <h2 className="mt-3 text-2xl font-black text-[var(--text-primary)]">
                            {studyPath?.focus_topic || stats.next_assignment?.subject || focusTopic}
                        </h2>
                        <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
                            {stats.next_assignment
                                ? `${stats.next_assignment.title} is the clearest next action, so start there before the rest of the dashboard competes for attention.`
                                : leadRecommendation?.description || stats.ai_insight || "Start with a single focused question and let AI Studio build the next revision step."}
                        </p>
                        <div className="mt-5 flex flex-wrap gap-3">
                            <Link
                                href={aiShortcutHref}
                                onClick={() => recordPersonalizationEvent("recommendation_click", "ai_studio", leadRecommendation?.id)}
                                className="prism-action"
                            >
                                Start AI Studio <ArrowRight className="h-4 w-4" />
                            </Link>
                            <Link href="/student/assignments" className="prism-action-secondary">
                                View your work
                            </Link>
                        </div>
                    </div>

                    <div className="vidya-command-card">
                        <p className="prism-status-label">Attendance status</p>
                        <div className="mt-3 flex items-end gap-3">
                            <p className="text-4xl font-black text-[var(--text-primary)]">{stats.attendance_pct}%</p>
                            <span className={`mb-1 rounded-full px-2.5 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] ${
                                stats.attendance_pct >= 85
                                    ? "bg-success-subtle text-status-green"
                                    : stats.attendance_pct >= 75
                                        ? "bg-warning-subtle text-status-amber"
                                        : "bg-error-subtle text-status-red"
                            }`}>
                                {stats.attendance_pct >= 85 ? "On track" : stats.attendance_pct >= 75 ? "Watch" : "Urgent"}
                            </span>
                        </div>
                        <div className="mt-5 grid gap-3">
                            <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-4 py-3">
                                <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">Marks</p>
                                <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{stats.avg_marks}% average</p>
                            </div>
                            <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-4 py-3">
                                <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">Due this week</p>
                                <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{stats.pending_assignments}</p>
                            </div>
                        </div>
                    </div>

                    <div className="vidya-command-card">
                        <p className="prism-status-label">AI shortcut</p>
                        <div className="mt-3 flex items-center gap-3">
                            <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[rgba(79,142,247,0.16)] text-[var(--ai-primary)]">
                                <Sparkles className="h-5 w-5" />
                            </div>
                            <div>
                                <p className="text-lg font-semibold text-[var(--text-primary)]">Ask about {focusTopic}</p>
                                <p className="text-sm text-[var(--text-secondary)]">
                                    {(leadRecommendation?.target_tool || "qa").replaceAll("_", " ")}
                                </p>
                            </div>
                        </div>
                        <p className="mt-4 text-sm leading-6 text-[var(--text-secondary)]">
                            {leadRecommendation?.reason || "Use one targeted question instead of browsing the full toolset first."}
                        </p>
                        <Link
                            href={aiShortcutHref}
                            onClick={() => recordPersonalizationEvent("recommendation_click", "ai_shortcut", leadRecommendation?.id)}
                            className="mt-5 inline-flex items-center gap-2 text-sm font-semibold"
                            style={{ color: "var(--ai-primary)" }}
                        >
                            Open shortcut <ArrowRight className="h-4 w-4" />
                        </Link>
                    </div>
                </div>
            )}

            {!loading ? (
                <PrismPanel className="p-6">
                    <PrismSectionHeader title="Since yesterday" description="A short status layer that helps the app feel alive without turning it back into a crowded dashboard." />
                    <div className="mt-4 grid gap-4 md:grid-cols-3">
                        {sinceYesterday.map((item) => (
                            <div key={item} className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-5 py-5 text-sm leading-6 text-[var(--text-secondary)]">
                                {item}
                            </div>
                        ))}
                    </div>
                </PrismPanel>
            ) : null}

            <PrismPanel className="p-6">
                <PrismSectionHeader
                    title="Action feed"
                    description="Pending work, next classes, and weak-topic suggestions stay in one practical queue."
                    actions={(
                        <button
                            type="button"
                            onClick={() => setShowFullDashboard((prev) => !prev)}
                            className="prism-action-secondary"
                        >
                            {showFullDashboard ? "Compact view" : "Expanded view"}
                        </button>
                    )}
                />
                <div className="mt-4 space-y-4">
                    {loading ? (
                        <div className="grid gap-3 md:grid-cols-2">
                            {Array.from({ length: 4 }).map((_, index) => <SkeletonCard key={index} />)}
                        </div>
                    ) : (
                        actionFeed.map((item) => (
                            <div key={`${item.title}-${item.href}`} className="vidya-feed-row">
                                <div className="flex items-start gap-3">
                                    <div className="mt-1 flex h-10 w-10 items-center justify-center rounded-2xl bg-[rgba(79,142,247,0.12)] text-[var(--ai-primary)]">
                                        <item.icon className="h-4 w-4" />
                                    </div>
                                    <div>
                                        <p className="text-base font-semibold text-[var(--text-primary)]">{item.title}</p>
                                        <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{item.detail}</p>
                                    </div>
                                </div>
                                <Link href={item.href} className="prism-action-secondary">
                                    {item.label}
                                </Link>
                            </div>
                        ))
                    )}
                </div>
            </PrismPanel>

            {showFullDashboard ? (
                <div className="space-y-6">
                    <RoleStartPanel role="student" />

                    {streak ? (
                        <GamificationHero
                            streak={streak.current_streak}
                            attendance={stats.attendance_pct}
                            marks={stats.avg_marks}
                        />
                    ) : null}

                    <AIActionCenter
                        recommendations={recommendations.map((item) => item.label)}
                        weakTopics={weakTopics.map((item) => item.subject)}
                    />

                    {studyPath && studyPath.items.length > 0 ? (
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Continue learning path"
                                description={`Focus topic: ${studyPath.focus_topic}`}
                                actions={(
                                    <Link
                                        href="/student/assistant"
                                        onClick={() => recordPersonalizationEvent("study_path_open", "mascot", studyPath.id)}
                                        className="prism-action-secondary"
                                    >
                                        Open mascot
                                    </Link>
                                )}
                            />
                        <div className="mt-4 grid gap-4 md:grid-cols-3">
                                {studyPath.items.slice(0, 3).map((item, index) => (
                                    <div key={item.id} className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-5">
                                        <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">Step {index + 1}</p>
                                        <p className="mt-2 text-base font-semibold text-[var(--text-primary)]">{item.title}</p>
                                        <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                            {(item.target_tool || "assistant").replaceAll("_", " ")}
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    ) : null}

                    <AcademicSnapshot
                        weeklyAttendance={weeklyAttendance}
                        weeklyMarks={weeklyMarks}
                        upcomingClasses={stats.upcoming_classes}
                        allTopics={allTopics}
                        aiInsight={stats.ai_insight}
                        loading={loading}
                        chartsReady={chartsReady}
                    />

                    <PrismPanel className="p-5">
                        <AISessionInsights loading={loading} days={30} />
                    </PrismPanel>
                </div>
            ) : null}
        </PrismPage>
    );
}
