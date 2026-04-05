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

import { APIError, api } from "@/lib/api";
import { SkeletonCard } from "@/components/Skeleton";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { AnimatedCounter } from "@/components/ui/SharedUI";
import { RoleStartPanel } from "@/components/RoleStartPanel";
import { GamificationHero } from "@/components/student/GamificationHero";
import { AIActionCenter } from "@/components/student/AIActionCenter";
import { AcademicSnapshot } from "@/components/student/AcademicSnapshot";

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
    const [recommendations, setRecommendations] = useState<PersonalizedRecommendation[]>([]);
    const [studyPath, setStudyPath] = useState<StudyPathPlan | null>(null);
    const [streak, setStreak] = useState<StreakInfo | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<Error | null>(null);
    const [chartsReady, setChartsReady] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);

            const [dashboardPayload, weakTopicPayload, streakPayload, recommendationPayload, studyPathPayload] = await Promise.all([
                api.student.dashboard(),
                api.student.weakTopics(),
                api.student.streaks(),
                api.personalization.recommendations({ current_surface: "overview" }),
                api.personalization.studyPath({ current_surface: "overview" }),
            ]);

            setStats((dashboardPayload || emptyStats) as DashboardStats);
            const topicPayload = (weakTopicPayload || { weak_topics: [], strong_topics: [] }) as WeakTopicPayload;
            setWeakTopics(topicPayload.weak_topics || []);
            setStrongTopics(topicPayload.strong_topics || []);
            setStreak((streakPayload || null) as StreakInfo | null);
            setRecommendations(
                Array.isArray((recommendationPayload as { items?: PersonalizedRecommendation[] } | null)?.items)
                    ? ((recommendationPayload as { items: PersonalizedRecommendation[] }).items || [])
                    : [],
            );
            setStudyPath(
                ((studyPathPayload as { plan?: StudyPathPlan | null } | null)?.plan || null) as StudyPathPlan | null,
            );
        } catch (err) {
            setError(err instanceof Error ? err : new APIError("Failed to load dashboard", 0, "unknown", "Retry now"));
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
                <div className="mb-6">
                    <GamificationHero 
                        streak={streak.current_streak} 
                        attendance={stats.attendance_pct} 
                        marks={stats.avg_marks} 
                    />
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
                    {/* Reduced KPI Row -> Stats now natively display in the Hero container above. We only render the action cards remaining here. */}
                    
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

            {/* ─── AI Action Center ─── */}
            <div className="mb-6 stagger-6">
                <AIActionCenter 
                    recommendations={recommendations.map(r => r.label)} 
                    weakTopics={weakTopics.map(w => w.subject)} 
                />
            </div>

            {studyPath && studyPath.items.length > 0 && (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 border border-[var(--border)]/60 mb-6">
                    <div className="flex items-center justify-between gap-3 mb-4">
                        <div className="flex items-center gap-2">
                            <Zap className="w-4 h-4 text-[var(--primary)]" />
                            <div>
                                <h2 className="text-sm font-semibold text-[var(--text-primary)]">Continue learning path</h2>
                                <p className="text-xs text-[var(--text-secondary)]">Focus topic: {studyPath.focus_topic}</p>
                            </div>
                        </div>
                        <a
                            href="/student/assistant"
                            onClick={() => recordPersonalizationEvent("study_path_open", "mascot", studyPath.id)}
                            className="inline-flex items-center gap-2 rounded-[var(--radius-sm)] bg-[var(--primary)] px-3 py-2 text-xs font-semibold text-white hover:bg-[var(--primary-hover)]"
                        >
                            <Bot className="w-3.5 h-3.5" /> Open mascot
                        </a>
                    </div>
                    {studyPath.next_action ? (
                        <div className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-page)] p-4 mb-4">
                            <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-2">Next action</p>
                            <p className="text-sm font-semibold text-[var(--text-primary)]">{studyPath.next_action.title}</p>
                            <p className="text-xs text-[var(--text-secondary)] mt-1">
                                Tool: {(studyPath.next_action.target_tool || "assistant").replace("_", " ")}
                            </p>
                        </div>
                    ) : null}
                    <div className="grid gap-3 md:grid-cols-3">
                        {studyPath.items.slice(0, 3).map((item, index) => (
                            <div key={item.id} className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-page)] p-4">
                                <div className="flex items-center justify-between gap-2 mb-2">
                                    <span className="text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Step {index + 1}</span>
                                    <span className="text-[10px] rounded-full bg-[var(--bg-card)] px-2 py-1 text-[var(--text-secondary)] border border-[var(--border)]">
                                        {item.status || "pending"}
                                    </span>
                                </div>
                                <p className="text-sm font-semibold text-[var(--text-primary)] mb-2">{item.title}</p>
                                <p className="text-xs text-[var(--text-secondary)]">
                                    {(item.target_tool || "assistant").replace("_", " ")}
                                </p>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* --- Academic Snapshot --- */}
            <div className="mb-6 stagger-7">
                <AcademicSnapshot
                    weeklyAttendance={weeklyAttendance}
                    weeklyMarks={weeklyMarks}
                    upcomingClasses={stats.upcoming_classes}
                    allTopics={allTopics}
                    aiInsight={stats.ai_insight}
                    loading={loading}
                    chartsReady={chartsReady}
                />
            </div>
        </div>
    );
}
