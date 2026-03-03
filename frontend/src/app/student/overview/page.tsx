"use client";

import { useEffect, useMemo, useState } from "react";
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
} from "lucide-react";

import { api } from "@/lib/api";

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

export default function StudentOverview() {
    const [stats, setStats] = useState<DashboardStats>(emptyStats);
    const [weakTopics, setWeakTopics] = useState<WeakTopic[]>([]);
    const [strongTopics, setStrongTopics] = useState<WeakTopic[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);

                const [dashboardPayload, weakTopicPayload] = await Promise.all([
                    api.student.dashboard(),
                    api.student.weakTopics(),
                ]);

                setStats((dashboardPayload || emptyStats) as DashboardStats);
                const topicPayload = (weakTopicPayload || { weak_topics: [], strong_topics: [] }) as WeakTopicPayload;
                setWeakTopics(topicPayload.weak_topics || []);
                setStrongTopics(topicPayload.strong_topics || []);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const allTopics = useMemo(() => {
        return [...weakTopics, ...strongTopics].sort((a, b) => a.average_score - b.average_score);
    }, [weakTopics, strongTopics]);

    const kpiCards = useMemo(
        () => [
            {
                label: "Attendance",
                value: `${stats.attendance_pct}%`,
                icon: CalendarCheck,
                color: stats.attendance_pct >= 80 ? "var(--success)" : "var(--error)",
                trend: stats.attendance_pct >= 80 ? "Healthy" : "Needs attention",
                trendUp: stats.attendance_pct >= 80,
            },
            {
                label: "Average Marks",
                value: `${stats.avg_marks}%`,
                icon: Award,
                color: stats.avg_marks >= 70 ? "var(--success)" : "var(--warning)",
                trend: stats.avg_marks >= 70 ? "On track" : "Below target",
                trendUp: stats.avg_marks >= 70,
            },
            {
                label: "Due Assignments",
                value: stats.pending_assignments,
                icon: FileText,
                color: stats.pending_assignments > 3 ? "var(--error)" : "var(--primary)",
                trend: null,
                trendUp: false,
            },
            {
                label: "AI Queries Today",
                value: `${stats.ai_queries_today}/${stats.ai_queries_limit}`,
                icon: Bot,
                color: "var(--primary)",
                trend: null,
                trendUp: false,
            },
            {
                label: "Uploaded Notes",
                value: stats.my_uploads,
                icon: Upload,
                color: "var(--primary)",
                trend: null,
                trendUp: false,
            },
        ],
        [stats],
    );

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Dashboard</h1>
                <p className="text-sm text-[var(--text-secondary)]">Your live academic snapshot from attendance, marks, and AI usage.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
                {kpiCards.map((card) => (
                    <div
                        key={card.label}
                        className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]"
                    >
                        <div className="flex items-center justify-between mb-3">
                            <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                                {card.label}
                            </span>
                            <card.icon className="w-4 h-4" style={{ color: card.color }} />
                        </div>
                        <div className="text-2xl font-bold text-[var(--text-primary)]">
                            {loading ? "-" : card.value}
                        </div>
                        {card.trend ? (
                            <div
                                className="flex items-center gap-1 mt-1 text-xs"
                                style={{ color: card.trendUp ? "var(--success)" : "var(--warning)" }}
                            >
                                {card.trendUp ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                                {card.trend}
                            </div>
                        ) : null}
                    </div>
                ))}
            </div>

            {weakTopics.length > 0 ? (
                <div className="bg-red-50 border border-red-200 rounded-[var(--radius)] p-4 mb-6">
                    <div className="flex items-center gap-2 mb-3">
                        <AlertTriangle className="w-4 h-4 text-[var(--error)]" />
                        <h2 className="text-sm font-semibold text-[var(--error)]">Weak Topics Detected</h2>
                    </div>
                    <div className="space-y-2">
                        {weakTopics.map((topic) => (
                            <div key={topic.subject} className="flex items-center gap-3">
                                <span className="w-24 text-xs text-[var(--text-secondary)]">{topic.subject}</span>
                                <div className="flex-1 h-5 bg-white rounded-full overflow-hidden">
                                    <div
                                        className="h-full rounded-full bg-[var(--error)] transition-all"
                                        style={{ width: `${topic.average_score}%` }}
                                    />
                                </div>
                                <span className="text-xs font-bold text-[var(--error)] w-10 text-right">{topic.average_score}%</span>
                            </div>
                        ))}
                    </div>
                    <a href="/student/tools" className="inline-flex items-center gap-1 mt-3 text-xs font-medium text-[var(--error)] hover:underline">
                        <Bot className="w-3 h-3" /> Get AI study plan
                    </a>
                </div>
            ) : null}

            <div className="grid lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2 bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                    <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Today schedule</h2>
                    {loading ? (
                        <p className="text-sm text-[var(--text-muted)]">Loading schedule...</p>
                    ) : stats.upcoming_classes.length === 0 ? (
                        <p className="text-sm text-[var(--text-muted)]">No classes scheduled today.</p>
                    ) : (
                        <div className="space-y-3">
                            {stats.upcoming_classes.map((cls, i) => (
                                <div
                                    key={`${cls.subject}-${cls.time}-${i}`}
                                    className="flex items-center gap-4 p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]"
                                >
                                    <div className="w-10 h-10 bg-[var(--primary-light)] rounded-[var(--radius-sm)] flex items-center justify-center">
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

                <div className="space-y-4">
                    <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center gap-2 mb-4">
                            <Bot className="w-4 h-4 text-[var(--primary)]" />
                            <h2 className="text-base font-semibold text-[var(--text-primary)]">AI Insight</h2>
                        </div>
                        {stats.ai_insight ? (
                            <div className="p-4 bg-[var(--primary-light)] rounded-[var(--radius-sm)]">
                                <p className="text-sm text-[var(--text-primary)] leading-relaxed">{stats.ai_insight}</p>
                                <a href="/student/ai" className="inline-flex items-center gap-1 mt-3 text-xs font-medium text-[var(--primary)] hover:underline">
                                    Ask AI for help
                                </a>
                            </div>
                        ) : (
                            <p className="text-sm text-[var(--text-muted)]">No AI insight available yet.</p>
                        )}

                        <div className="mt-4">
                            <div className="flex items-center justify-between text-xs text-[var(--text-muted)] mb-1">
                                <span>AI usage</span>
                                <span>
                                    {stats.ai_queries_today}/{stats.ai_queries_limit}
                                </span>
                            </div>
                            <div className="h-2 bg-[var(--bg-page)] rounded-full">
                                <div
                                    className="h-2 bg-[var(--primary)] rounded-full transition-all"
                                    style={{
                                        width: `${Math.min(100, Math.round((stats.ai_queries_today / Math.max(1, stats.ai_queries_limit)) * 100))}%`,
                                    }}
                                />
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Subject performance</h2>
                        {loading ? (
                            <p className="text-sm text-[var(--text-muted)]">Loading performance...</p>
                        ) : allTopics.length === 0 ? (
                            <p className="text-sm text-[var(--text-muted)]">No subject performance data yet.</p>
                        ) : (
                            <div className="space-y-2">
                                {allTopics.map((topic) => (
                                    <div key={topic.subject} className="flex items-center gap-2">
                                        <span className="w-20 text-[10px] text-[var(--text-muted)]">{topic.subject}</span>
                                        <div className="flex-1 h-3 bg-[var(--bg-page)] rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${topic.is_weak ? "bg-[var(--error)]" : topic.average_score >= 80 ? "bg-[var(--success)]" : "bg-[var(--primary)]"}`}
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
