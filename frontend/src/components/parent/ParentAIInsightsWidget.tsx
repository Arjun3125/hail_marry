"use client";

import { useEffect, useState } from "react";
import { Activity, Brain, Target, TrendingUp, Clock, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";

interface ParentAIInsights {
    total_sessions: number;
    total_study_time_hours: number;
    active_subjects: string[];
    average_engagement: number;
    recent_topics: string[];
    quiz_count: number;
    average_quiz_score?: number;
    topics_to_review: string[];
    period_days: number;
    message?: string;
}

function normalizeParentAIInsights(payload: unknown, days: number): ParentAIInsights | null {
    if (!payload || typeof payload !== "object") return null;
    const candidate = payload as Partial<ParentAIInsights>;

    return {
        total_sessions: Number(candidate.total_sessions ?? 0),
        total_study_time_hours: Number(candidate.total_study_time_hours ?? 0),
        active_subjects: Array.isArray(candidate.active_subjects) ? candidate.active_subjects : [],
        average_engagement: Number(candidate.average_engagement ?? 0),
        recent_topics: Array.isArray(candidate.recent_topics) ? candidate.recent_topics : [],
        quiz_count: Number(candidate.quiz_count ?? 0),
        average_quiz_score:
            typeof candidate.average_quiz_score === "number" ? candidate.average_quiz_score : undefined,
        topics_to_review: Array.isArray(candidate.topics_to_review) ? candidate.topics_to_review : [],
        period_days: Number(candidate.period_days ?? days),
        message: typeof candidate.message === "string" ? candidate.message : undefined,
    };
}

interface ParentAIInsightsWidgetProps {
    childId?: string;
    days?: number;
    loading?: boolean;
}

export function ParentAIInsightsWidget({
    childId,
    days = 7,
    loading: initialLoading = false,
}: ParentAIInsightsWidgetProps) {
    const [insights, setInsights] = useState<ParentAIInsights | null>(null);
    const [loading, setLoading] = useState(initialLoading);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const fetchInsights = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = normalizeParentAIInsights(await api.parent.aiInsights(childId, days), days);
                setInsights(data);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load AI insights");
                console.error("Error fetching parent AI insights:", err);
            } finally {
                setLoading(false);
            }
        };

        fetchInsights();
    }, [childId, days]);

    if (loading) {
        return (
            <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-6 animate-pulse">
                <div className="h-48 bg-slate-700/30 rounded-lg" />
            </div>
        );
    }

    if (error || !insights) {
        return null;
    }

    // Show empty state if no sessions
    if (insights.total_sessions === 0) {
        return (
            <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-6">
                <div className="flex items-center gap-3 text-[var(--text-secondary)]">
                    <Brain size={20} className="text-slate-500" />
                    <p className="text-sm">No AI learning sessions yet. Encourage your child to start with AI Studio!</p>
                </div>
            </div>
        );
    }

    const formatHours = (hours: number) => {
        if (hours < 1) {
            return `${Math.round(hours * 60)}m`;
        }
        return `${hours.toFixed(1)}h`;
    };

    const getEngagementStatus = (score: number) => {
        if (score >= 80) return { label: "Excellent", color: "text-emerald-400" };
        if (score >= 60) return { label: "Good", color: "text-amber-400" };
        if (score >= 40) return { label: "Fair", color: "text-orange-400" };
        return { label: "Needs Attention", color: "text-red-400" };
    };

    const engagementStatus = getEngagementStatus(insights.average_engagement);

    return (
        <div className="space-y-4">
            <div className="flex items-center gap-2">
                <Brain size={20} className="text-indigo-400" />
                <h3 className="text-sm font-semibold tracking-wide text-[var(--text-primary)]">
                    AI Learning Activity ({insights.period_days} days)
                </h3>
            </div>

            {/* Quick Stats Grid */}
            <div className="grid gap-3 md:grid-cols-2">
                {/* Sessions & Study Time */}
                <div className="rounded-lg border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                Study Sessions
                            </p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                                {insights.total_sessions}
                            </p>
                        </div>
                        <Activity size={24} className="text-indigo-400" />
                    </div>
                </div>

                {/* Study Time */}
                <div className="rounded-lg border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                Total Study Time
                            </p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                                {formatHours(insights.total_study_time_hours)}
                            </p>
                        </div>
                        <Clock size={24} className="text-amber-400" />
                    </div>
                </div>

                {/* Engagement */}
                <div className="rounded-lg border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                Engagement
                            </p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                                {insights.average_engagement.toFixed(0)}%
                            </p>
                            <p className={`text-xs mt-1 font-medium ${engagementStatus.color}`}>
                                {engagementStatus.label}
                            </p>
                        </div>
                        <TrendingUp size={24} className={engagementStatus.color} />
                    </div>
                </div>

                {/* Quiz Performance */}
                <div className="rounded-lg border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                    <div className="flex items-center justify-between">
                        <div>
                            <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                Quiz Attempts
                            </p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                                {insights.quiz_count}
                            </p>
                            {insights.average_quiz_score !== undefined && (
                                <p className="text-xs text-emerald-400 mt-1 font-medium">
                                    Avg: {insights.average_quiz_score.toFixed(0)}%
                                </p>
                            )}
                        </div>
                        <Target size={24} className="text-emerald-400" />
                    </div>
                </div>
            </div>

            {/* Active Subjects */}
            {insights.active_subjects.length > 0 && (
                <div className="rounded-lg border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                    <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)] mb-2">
                        Subjects Studied
                    </p>
                    <div className="flex flex-wrap gap-2">
                        {insights.active_subjects.map((subject) => (
                            <span
                                key={subject}
                                className="rounded-full bg-indigo-500/15 px-3 py-1 text-xs font-medium text-indigo-300"
                            >
                                {subject}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Topics to Review */}
            {insights.topics_to_review.length > 0 && (
                <div className="rounded-lg border border-amber-500/30 bg-amber-500/5 p-4">
                    <div className="flex gap-3">
                        <AlertCircle size={20} className="text-amber-400 flex-shrink-0 mt-0.5" />
                        <div>
                            <p className="text-[11px] uppercase tracking-[0.18em] text-amber-300 font-semibold mb-2">
                                Topics Needing Review
                            </p>
                            <div className="space-y-1">
                                {insights.topics_to_review.map((topic, idx) => (
                                    <p key={idx} className="text-sm text-[var(--text-secondary)]">
                                        • {topic}
                                    </p>
                                ))}
                            </div>
                            <p className="text-xs text-[var(--text-muted)] mt-2">
                                These topics showed misconceptions in recent sessions. Consider additional practice.
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Recent Topics */}
            {insights.recent_topics.length > 0 && (
                <div className="rounded-lg border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                    <p className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)] mb-2">
                        Recently Studied
                    </p>
                    <div className="space-y-1">
                        {insights.recent_topics.map((topic, idx) => (
                            <p key={idx} className="text-sm text-[var(--text-secondary)]">
                                • {topic}
                            </p>
                        ))}
                    </div>
                </div>
            )}
        </div>
    );
}
