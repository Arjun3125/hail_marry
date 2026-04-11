"use client";

import { useEffect, useState } from "react";
import { BarChart, Bar, CartesianGrid, Tooltip, XAxis, YAxis, ResponsiveContainer } from "recharts";
import { Activity, Brain, Clock, TrendingUp, Zap } from "lucide-react";
import { api } from "@/lib/api";
import { SessionSummaryModal } from "./SessionSummaryModal";

interface AISessionInsightsProps {
    loading?: boolean;
    days?: number;
}

interface SessionStats {
    total_sessions: number;
    total_study_time_hours: number;
    average_engagement: number;
    active_subjects: string[];
    quiz_attempts: number;
    average_quiz_score?: number;
    mastery_progress: Record<string, string>;
    recommended_topics: string[];
}

type ChartDataPoint = {
    name: string;
    value: number;
    [key: string]: string | number;
};

export function AISessionInsights({ loading: initialLoading = false, days = 30 }: AISessionInsightsProps) {
    const [stats, setStats] = useState<SessionStats | null>(null);
    const [loading, setLoading] = useState(initialLoading);
    const [error, setError] = useState<string | null>(null);
    const [isModalOpen, setIsModalOpen] = useState(false);
    const [chartData, setChartData] = useState<ChartDataPoint[]>([]);

    useEffect(() => {
        const fetchInsights = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.sessionTracking.getParentInsights(undefined, days);
                setStats(data);

                // Prepare chart data from mastery progress
                if (data.mastery_progress) {
                    const masteryLevels: Record<string, number> = {
                        beginner: 1,
                        intermediate: 2,
                        advanced: 3,
                    };
                    const chartPoints: ChartDataPoint[] = Object.entries(data.mastery_progress).map(
                        ([subject, level]: [string, unknown]) => ({
                            name: subject,
                            value: masteryLevels[level as string] || 1,
                            level: level as string,
                        })
                    );
                    setChartData(chartPoints);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to fetch insights");
                console.error("Error fetching AI session insights:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchInsights();
    }, [days]);

    if (loading) {
        return (
            <div className="space-y-4">
                <div className="h-32 rounded-2xl border border-[var(--border)] bg-slate-800/20 animate-pulse" />
                <div className="h-64 rounded-2xl border border-[var(--border)] bg-slate-800/20 animate-pulse" />
            </div>
        );
    }

    if (error || !stats) {
        return null;
    }

    const formatHours = (hours: number) => {
        if (hours < 1) {
            return `${Math.round(hours * 60)}m`;
        }
        return `${hours.toFixed(1)}h`;
    };

    return (
        <>
            <div className="space-y-6">
                {/* Header with title and action */}
                <div className="flex items-center justify-between">
                    <div>
                        <h2 className="text-xl font-bold tracking-tight text-[var(--text-primary)] flex items-center gap-2">
                            <Brain size={24} className="text-indigo-400" />
                            AI Learning Analytics
                        </h2>
                        <p className="text-sm text-[var(--text-secondary)] mt-1">
                            Your AI Studio sessions and learning insights for the past {days} days
                        </p>
                    </div>
                    <button
                        onClick={() => setIsModalOpen(true)}
                        className="rounded-lg bg-indigo-600 px-4 py-2 text-sm font-medium text-white hover:bg-indigo-700 transition-colors"
                    >
                        View Details
                    </button>
                </div>

                {/* Key Metrics Grid */}
                <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">
                    {/* Sessions Count */}
                    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-5">
                        <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-indigo-500/10 blur-2xl" />
                        <div className="relative z-10">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                                        Sessions
                                    </div>
                                    <div className="text-3xl font-bold text-[var(--text-primary)] mt-2">
                                        {stats.total_sessions}
                                    </div>
                                </div>
                                <div className="rounded-full bg-indigo-500/20 p-3">
                                    <Activity size={20} className="text-indigo-400" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Study Time */}
                    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-5">
                        <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-amber-500/10 blur-2xl" />
                        <div className="relative z-10">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                                        Study Time
                                    </div>
                                    <div className="text-3xl font-bold text-[var(--text-primary)] mt-2">
                                        {formatHours(stats.total_study_time_hours)}
                                    </div>
                                </div>
                                <div className="rounded-full bg-amber-500/20 p-3">
                                    <Clock size={20} className="text-amber-400" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Engagement Score */}
                    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-5">
                        <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-emerald-500/10 blur-2xl" />
                        <div className="relative z-10">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                                        Avg. Engagement
                                    </div>
                                    <div className="text-3xl font-bold text-[var(--text-primary)] mt-2">
                                        {stats.average_engagement.toFixed(0)}%
                                    </div>
                                </div>
                                <div className="rounded-full bg-emerald-500/20 p-3">
                                    <Zap size={20} className="text-emerald-400" />
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Quiz Score */}
                    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-5">
                        <div className="pointer-events-none absolute -right-8 -top-8 h-24 w-24 rounded-full bg-violet-500/10 blur-2xl" />
                        <div className="relative z-10">
                            <div className="flex items-center justify-between">
                                <div>
                                    <div className="text-xs font-semibold uppercase tracking-wider text-[var(--text-secondary)]">
                                        Avg. Quiz Score
                                    </div>
                                    <div className="text-3xl font-bold text-[var(--text-primary)] mt-2">
                                        {stats.average_quiz_score ? `${stats.average_quiz_score.toFixed(0)}%` : "—"}
                                    </div>
                                </div>
                                <div className="rounded-full bg-violet-500/20 p-3">
                                    <TrendingUp size={20} className="text-violet-400" />
                                </div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Mastery Progress Chart */}
                {chartData.length > 0 && (
                    <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-6">
                        <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_90%_0%,rgba(99,102,241,0.08),transparent_55%)]" />
                        <div className="relative z-10">
                            <h3 className="text-sm font-semibold tracking-wide text-[var(--text-primary)] mb-4">
                                Subject Mastery Progress
                            </h3>
                            <div className="h-64 w-full">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={chartData} margin={{ top: 10, right: 20, left: -20, bottom: 40 }}>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.2)" />
                                        <XAxis
                                            dataKey="name"
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 11, fill: "#94a3b8" }}
                                            angle={-45}
                                            textAnchor="end"
                                            height={80}
                                        />
                                        <YAxis
                                            domain={[0, 3]}
                                            axisLine={false}
                                            tickLine={false}
                                            tick={{ fontSize: 11, fill: "#94a3b8" }}
                                            ticks={[0, 1, 2, 3]}
                                            tickFormatter={(value) => {
                                                const levels = ["None", "Beginner", "Intermediate", "Advanced"];
                                                return levels[value] || String(value);
                                            }}
                                        />
                                        <Tooltip
                                            contentStyle={{
                                                backgroundColor: "rgba(9, 15, 28, 0.94)",
                                                border: "1px solid rgba(148, 163, 184, 0.2)",
                                                borderRadius: "12px",
                                                color: "#e2e8f0",
                                            }}
                                            formatter={(value) => {
                                                const levels = ["None", "Beginner", "Intermediate", "Advanced"];
                                                return [levels[value as number], "Mastery Level"];
                                            }}
                                        />
                                        <Bar dataKey="value" fill="#818cf8" radius={[8, 8, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>
                    </div>
                )}

                {/* Active Subjects and Recommended Topics */}
                <div className="grid gap-6 md:grid-cols-2">
                    {/* Active Subjects */}
                    {stats.active_subjects.length > 0 && (
                        <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-6">
                            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_90%_0%,rgba(168,85,247,0.08),transparent_55%)]" />
                            <div className="relative z-10">
                                <h3 className="text-sm font-semibold tracking-wide text-[var(--text-primary)] mb-4">
                                    Active Subjects
                                </h3>
                                <div className="space-y-2">
                                    {stats.active_subjects.map((subject) => (
                                        <div key={subject} className="rounded-lg bg-slate-800/50 px-4 py-3 border border-slate-700/30">
                                            <p className="text-sm text-[var(--text-primary)]">{subject}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Recommended Topics for Review */}
                    {stats.recommended_topics.length > 0 && (
                        <div className="relative overflow-hidden rounded-2xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.8),rgba(10,15,28,0.9))] p-6">
                            <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_90%_0%,rgba(239,68,68,0.08),transparent_55%)]" />
                            <div className="relative z-10">
                                <h3 className="text-sm font-semibold tracking-wide text-[var(--text-primary)] mb-4">
                                    Topics to Revisit
                                </h3>
                                <div className="space-y-2 max-h-48 overflow-y-auto">
                                    {stats.recommended_topics.slice(0, 5).map((topic, idx) => (
                                        <div key={idx} className="rounded-lg border-l-2 border-red-500/50 bg-red-500/5 px-4 py-3">
                                            <p className="text-sm text-[var(--text-secondary)]">{topic}</p>
                                        </div>
                                    ))}
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Session Summary Modal */}
            <SessionSummaryModal isOpen={isModalOpen} onClose={() => setIsModalOpen(false)} days={days} />
        </>
    );
}
