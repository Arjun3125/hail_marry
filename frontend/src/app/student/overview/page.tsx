"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import {
    AlertTriangle,
    Award,
    Bot,
    CalendarCheck,
    Clock,
    FileText,
    TrendingDown,
    TrendingUp,
    Upload,
    Zap,
} from "lucide-react";
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    BarChart,
    Bar,
    CartesianGrid,
} from "recharts";

import { api } from "@/lib/api";
import { SkeletonCard } from "@/components/Skeleton";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { AnimatedCounter, ProgressRing } from "@/components/ui/SharedUI";
import { RoleStartPanel } from "@/components/RoleStartPanel";

type DashboardStats = {
    attendance_pct: number;
    avg_marks: number;
    pending_assignments: number;
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

const emptyStats: DashboardStats = {
    attendance_pct: 0,
    avg_marks: 0,
    pending_assignments: 0,
    ai_queries_today: 0,
    ai_queries_limit: 50,
    upcoming_classes: [],
    my_uploads: 0,
    ai_insight: null,
};

// Mock sparkline data for the demo charts
const weeklyAttendance = [
    { day: "Mon", value: 92 }, { day: "Tue", value: 88 },
    { day: "Wed", value: 95 }, { day: "Thu", value: 90 },
    { day: "Fri", value: 85 }, { day: "Sat", value: 100 },
];

const weeklyMarks = [
    { day: "Week 1", value: 72 }, { day: "Week 2", value: 68 },
    { day: "Week 3", value: 78 }, { day: "Week 4", value: 82 },
    { day: "Week 5", value: 75 }, { day: "Week 6", value: 85 },
];

export default function StudentOverview() {
    const [stats, setStats] = useState<DashboardStats>(emptyStats);
    const [weakTopics, setWeakTopics] = useState<WeakTopic[]>([]);
    const [strongTopics, setStrongTopics] = useState<WeakTopic[]>([]);
    const [streak, setStreak] = useState<StreakInfo | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [chartsReady, setChartsReady] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [dashboardPayload, weakTopicPayload, streakPayload] = await Promise.all([
                api.student.dashboard(),
                api.student.weakTopics(),
                api.student.streaks(),
            ]);

            setStats((dashboardPayload || emptyStats) as DashboardStats);
            const topicPayload = (weakTopicPayload || { weak_topics: [], strong_topics: [] }) as WeakTopicPayload;
            setWeakTopics(topicPayload.weak_topics || []);
            setStrongTopics(topicPayload.strong_topics || []);
            setStreak((streakPayload || null) as StreakInfo | null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

    useEffect(() => {
        const id = requestAnimationFrame(() => setChartsReady(true));
        return () => cancelAnimationFrame(id);
    }, []);

    const onboardingChecklist = [
        { id: "ai-open", label: "Open AI study assistant" },
        { id: "assignment", label: "Complete one assignment task" },
        { id: "review", label: "Review weak topics and streak" },
    ];

    const taskFirstLinks = [
        { label: "Ask AI with citations", href: "/student/ai", priority: "high" as const },
        { label: "Open assignments", href: "/student/assignments", priority: "medium" as const },
        { label: "Review results trends", href: "/student/results", priority: "low" as const },
    ];

    const allTopics = useMemo(() => {
        return [...weakTopics, ...strongTopics].sort((a, b) => a.average_score - b.average_score);
    }, [weakTopics, strongTopics]);

    return (
        <div>
            {/* Header */}
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                    Dashboard
                </h1>
                <p className="text-sm text-[var(--text-secondary)]">Your live academic snapshot from attendance, marks, and AI usage.</p>
            </div>

            <RoleStartPanel role="student" />

            {!loading && streak ? (
                <div className="mb-6 bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 border border-[var(--border)]/60">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                        <div>
                            <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-2">Focus</p>
                            <div className="flex items-center gap-3">
                                <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white text-xl font-bold shadow-lg">
                                    {streak.current_streak}
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Current Streak</p>
                                    <p className="text-xs text-[var(--text-muted)]">Best: {streak.longest_streak} days</p>
                                </div>
                            </div>
                        </div>
                        <a
                            href="/student/ai"
                            className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold rounded-[var(--radius-sm)] bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)] shadow-sm"
                        >
                            <Zap className="w-4 h-4" /> Continue Studying
                        </a>
                    </div>
                    <div className="mt-4 flex flex-wrap items-center gap-2">
                        {(streak.badges || []).slice(0, 4).map((badge) => (
                            <span
                                key={badge.id}
                                className="inline-flex items-center gap-2 rounded-full bg-[var(--bg-page)] px-3 py-1 text-xs text-[var(--text-secondary)] border border-[var(--border-light)]"
                            >
                                <span>{badge.icon}</span>
                                {badge.name}
                            </span>
                        ))}
                        {(!streak.badges || streak.badges.length === 0) && (
                            <span className="text-xs text-[var(--text-muted)]">Log in daily to earn badges.</span>
                        )}
                    </div>
                </div>
            ) : null}

            {error ? <ErrorRemediation error={error} scope="student-overview" onRetry={() => void load()} simplifiedModeHref="/student/tools" /> : null}

            {/* ─── Glass KPI Cards ─── */}
            {loading ? (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                    {Array.from({ length: 5 }).map((_, i) => <SkeletonCard key={i} />)}
                </div>
            ) : (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4 mb-6">
                    {/* Attendance — with progress ring */}
                    <div className="glass-stat glass-stat-blue stagger-1">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">Attendance</span>
                            <CalendarCheck className="w-4 h-4" style={{ color: stats.attendance_pct >= 80 ? "var(--success)" : "var(--error)" }} />
                        </div>
                        <div className="flex items-center gap-3">
                            <ProgressRing
                                value={stats.attendance_pct}
                                size={52}
                                strokeWidth={5}
                                color={stats.attendance_pct >= 80 ? "var(--success)" : "var(--error)"}
                            >
                                <span className="text-[10px] font-bold text-[var(--text-primary)]">
                                    {stats.attendance_pct}%
                                </span>
                            </ProgressRing>
                            <div>
                                <div className="text-xl font-bold text-[var(--text-primary)]">
                                    <AnimatedCounter value={stats.attendance_pct} suffix="%" />
                                </div>
                                <div className="flex items-center gap-1 text-[10px]" style={{ color: stats.attendance_pct >= 80 ? "var(--success)" : "var(--error)" }}>
                                    {stats.attendance_pct >= 80 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                    {stats.attendance_pct >= 80 ? "Healthy" : "Low"}
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Average Marks */}
                    <div className="glass-stat glass-stat-green stagger-2">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">Marks</span>
                            <Award className="w-4 h-4" style={{ color: stats.avg_marks >= 70 ? "var(--success)" : "var(--warning)" }} />
                        </div>
                        <div className="text-2xl font-bold text-[var(--text-primary)]">
                            <AnimatedCounter value={stats.avg_marks} suffix="%" />
                        </div>
                        <div className="w-full bg-[var(--border)] h-2 rounded-full mt-2 overflow-hidden">
                            <div 
                                className="h-full rounded-full transition-all duration-1000 ease-out" 
                                style={{
                                    width: `${stats.avg_marks}%`, 
                                    backgroundColor: stats.avg_marks >= 70 ? "var(--success)" : "var(--warning)"
                                }} 
                            />
                        </div>
                        <div className="flex items-center gap-1 mt-3 text-[10px]" style={{ color: stats.avg_marks >= 70 ? "var(--success)" : "var(--warning)" }}>
                            {stats.avg_marks >= 70 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {stats.avg_marks >= 70 ? "On track" : "Below target"}
                        </div>
                        <p className="text-[10px] text-[var(--text-secondary)] mt-1 line-clamp-1">
                            {stats.ai_insight || "Consistent performance."}
                        </p>
                    </div>

                    {/* Pending Assignments */}
                    <div className="glass-stat glass-stat-amber stagger-3">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">Due</span>
                            <FileText className="w-4 h-4" style={{ color: stats.pending_assignments > 3 ? "var(--error)" : "var(--primary)" }} />
                        </div>
                        <div className="text-2xl font-bold text-[var(--text-primary)]">
                            <AnimatedCounter value={stats.pending_assignments} />
                        </div>
                        <p className="text-[10px] text-[var(--text-muted)] mt-1">Assignments pending</p>
                    </div>

                    {/* AI Queries */}
                    <div className="glass-stat glass-stat-purple stagger-4">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">AI</span>
                            <Bot className="w-4 h-4 text-[var(--accent-purple)]" />
                        </div>
                        <div className="text-2xl font-bold text-[var(--text-primary)]">
                            <AnimatedCounter value={stats.ai_queries_today} />
                            <span className="text-sm text-[var(--text-muted)]">/{stats.ai_queries_limit}</span>
                        </div>
                        <div className="h-1.5 bg-[var(--bg-page)] rounded-full mt-2 overflow-hidden">
                            <div
                                className="h-full rounded-full bg-[var(--accent-purple)] transition-all duration-1000"
                                style={{ width: `${Math.min(100, Math.round((stats.ai_queries_today / Math.max(1, stats.ai_queries_limit)) * 100))}%` }}
                            />
                        </div>
                    </div>

                    {/* Uploads */}
                    <div className="glass-stat glass-stat-pink stagger-5">
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-[10px] font-semibold text-[var(--text-muted)] uppercase tracking-widest">Notes</span>
                            <Upload className="w-4 h-4 text-pink-500" />
                        </div>
                        <div className="text-2xl font-bold text-[var(--text-primary)]">
                            <AnimatedCounter value={stats.my_uploads} />
                        </div>
                        <p className="text-[10px] text-[var(--text-muted)] mt-1">Uploaded files</p>
                    </div>
                </div>
            )}

            {/* ─── Weak Topics Alert ─── */}
            {weakTopics.length > 0 && (
                <div className="bg-red-50 dark:bg-red-900/10 border border-error-subtle dark:border-red-900/30 rounded-[var(--radius)] p-4 mb-6 stagger-6">
                    <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle className="w-4 h-4 text-[var(--error)]" />
                        <h2 className="text-sm font-semibold text-[var(--error)]">Weak Topics Detected</h2>
                    </div>
                    <div className="space-y-2">
                        {weakTopics.map((topic) => (
                            <div key={topic.subject} className="flex items-center gap-3">
                                <span className="w-24 text-xs text-[var(--text-secondary)]">{topic.subject}</span>
                                <div className="flex-1 h-5 bg-[var(--bg-card)] rounded-full overflow-hidden">
                                    <div
                                        className="h-full rounded-full bg-gradient-to-r from-red-500 to-red-400 transition-all duration-1000"
                                        style={{ width: `${topic.average_score}%` }}
                                    />
                                </div>
                                <span className="text-xs font-bold text-[var(--error)] w-10 text-right">{topic.average_score}%</span>
                            </div>
                        ))}
                    </div>
                    <a href="/student/tools" className="inline-flex items-center gap-1 mt-3 text-xs font-medium text-[var(--error)] hover:underline">
                        <Zap className="w-3 h-3" /> Get AI study plan
                    </a>
                </div>
            )}

            {/* ─── Charts Row ─── */}
            <div className="grid md:grid-cols-2 gap-6 mb-6">
                {/* Attendance Trend Chart */}
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] card-hover">
                    <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">📊 Weekly Attendance Trend</h2>
                    <div className="h-40">
                        {chartsReady ? (
                            <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={160}>
                            <AreaChart data={weeklyAttendance}>
                                <defs>
                                    <linearGradient id="attGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#2563eb" stopOpacity={0.3} />
                                        <stop offset="95%" stopColor="#2563eb" stopOpacity={0} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
                                <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                <YAxis domain={[70, 100]} tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                <Tooltip
                                    contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                                    labelStyle={{ color: "var(--text-primary)", fontWeight: 600 }}
                                />
                                <Area type="monotone" dataKey="value" stroke="#2563eb" strokeWidth={2.5} fill="url(#attGrad)" />
                            </AreaChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full rounded-[var(--radius-sm)] bg-[var(--bg-page)]" />
                        )}
                    </div>
                </div>

                {/* Marks Trend Chart */}
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] card-hover">
                    <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">📈 Marks Trend</h2>
                    <div className="h-40">
                        {chartsReady ? (
                            <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={160}>
                            <BarChart data={weeklyMarks}>
                                <defs>
                                    <linearGradient id="marksGrad" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                    </linearGradient>
                                </defs>
                                <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
                                <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                <YAxis domain={[50, 100]} tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                <Tooltip
                                    contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                                    labelStyle={{ color: "var(--text-primary)", fontWeight: 600 }}
                                />
                                <Bar dataKey="value" fill="url(#marksGrad)" radius={[4, 4, 0, 0]} />
                            </BarChart>
                            </ResponsiveContainer>
                        ) : (
                            <div className="h-full rounded-[var(--radius-sm)] bg-[var(--bg-page)]" />
                        )}
                    </div>
                </div>
            </div>

            {/* ─── Bottom Row ─── */}
            <div className="grid lg:grid-cols-3 gap-6">
                {/* Today's schedule */}
                <div className="lg:col-span-2 bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                    <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Today&apos;s Schedule</h2>
                    {loading ? (
                        <p className="text-sm text-[var(--text-muted)]">Loading schedule...</p>
                    ) : stats.upcoming_classes.length === 0 ? (
                        <div className="py-8 text-center">
                            <Clock className="w-10 h-10 mx-auto text-[var(--text-muted)] mb-2 opacity-40" />
                            <p className="text-sm text-[var(--text-muted)]">No classes scheduled today.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {stats.upcoming_classes.map((cls, i) => (
                                <div
                                    key={`${cls.subject}-${cls.time}-${i}`}
                                    className={`flex items-center gap-4 p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)] card-hover stagger-${Math.min(i + 1, 6)}`}
                                >
                                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500/20 to-blue-600/10 rounded-[var(--radius-sm)] flex items-center justify-center">
                                        <Clock className="w-4 h-4 text-[var(--primary)]" />
                                    </div>
                                    <div>
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{cls.subject}</p>
                                        <p className="text-xs text-[var(--text-muted)]">{cls.time}</p>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                {/* Right column */}
                <div className="space-y-4">
                    {/* AI Insight */}
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] gradient-border">
                        <div className="flex items-center gap-2 mb-3">
                            <Bot className="w-4 h-4 text-[var(--accent-purple)]" />
                            <h2 className="text-sm font-semibold text-[var(--text-primary)]">AI Insight</h2>
                        </div>
                        {stats.ai_insight ? (
                            <div className="p-3 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/10 dark:to-indigo-900/10 rounded-lg">
                                <p className="text-xs text-[var(--text-primary)] leading-relaxed">{stats.ai_insight}</p>
                                <a href="/student/ai" className="inline-flex items-center gap-1 mt-2 text-[10px] font-medium text-[var(--accent-purple)] hover:underline">
                                    Ask AI for help →
                                </a>
                            </div>
                        ) : (
                            <p className="text-xs text-[var(--text-muted)]">No AI insight available yet.</p>
                        )}
                    </div>

                    {/* Subject Performance */}
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Subject Performance</h2>
                        {loading ? (
                            <p className="text-sm text-[var(--text-muted)]">Loading...</p>
                        ) : allTopics.length === 0 ? (
                            <div className="py-4 text-center">
                                <Award className="w-8 h-8 mx-auto text-[var(--text-muted)] mb-2 opacity-40" />
                                <p className="text-xs text-[var(--text-muted)]">No subject data yet.</p>
                            </div>
                        ) : (
                            <div className="space-y-2.5">
                                {allTopics.map((topic) => (
                                    <div key={topic.subject} className="flex items-center gap-2">
                                        <span className="w-20 text-[10px] text-[var(--text-muted)] truncate">{topic.subject}</span>
                                        <div className="flex-1 h-3 bg-[var(--bg-page)] rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-1000 ${
                                                    topic.is_weak
                                                        ? "bg-gradient-to-r from-red-500 to-red-400"
                                                        : topic.average_score >= 80
                                                            ? "bg-gradient-to-r from-green-500 to-emerald-400"
                                                            : "bg-gradient-to-r from-blue-500 to-indigo-400"
                                                }`}
                                                style={{ width: `${topic.average_score}%` }}
                                            />
                                        </div>
                                        <span className={`text-[10px] font-bold w-8 text-right ${topic.is_weak ? "text-[var(--error)]" : "text-[var(--text-primary)]"}`}>
                                            {topic.average_score}%
                                        </span>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
