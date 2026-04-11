"use client";

import { X } from "lucide-react";
import { useEffect, useState } from "react";
import { api } from "@/lib/api";

export interface SessionSummary {
    id: string;
    session_id: string;
    tool_mode: string;
    subject?: string;
    topic?: string;
    duration_seconds: number;
    engagement_score: number;
    mastery_level: string;
    quiz_score_percent?: number;
    started_at: string;
    ended_at?: string;
    key_insights: string[];
}

interface SessionSummaryModalProps {
    isOpen: boolean;
    onClose: () => void;
    sessionId?: string;
    days?: number;
    limit?: number;
}

export function SessionSummaryModal({
    isOpen,
    onClose,
    sessionId,
    days = 7,
    limit = 10,
}: SessionSummaryModalProps) {
    const [sessions, setSessions] = useState<SessionSummary[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [selectedSession, setSelectedSession] = useState<SessionSummary | null>(null);

    useEffect(() => {
        if (!isOpen) return;

        const fetchSessions = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.sessionTracking.getRecentSessions(days, limit);
                setSessions(data || []);
                
                // If sessionId is provided, select it by default
                if (sessionId && data) {
                    const session = data.find((s: SessionSummary) => s.session_id === sessionId);
                    if (session) {
                        setSelectedSession(session);
                    }
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to fetch sessions");
            } finally {
                setLoading(false);
            }
        };

        fetchSessions();
    }, [isOpen, days, limit, sessionId]);

    if (!isOpen) return null;

    const displaySession = selectedSession || sessions[0];
    const formatDuration = (seconds: number) => {
        const minutes = Math.floor(seconds / 60);
        const secs = seconds % 60;
        if (minutes === 0) return `${secs}s`;
        if (minutes > 60) {
            const hours = Math.floor(minutes / 60);
            const mins = minutes % 60;
            return `${hours}h ${mins}m`;
        }
        return `${minutes}m ${secs}s`;
    };

    const getMasteryColor = (level: string) => {
        switch (level) {
            case "advanced":
                return "text-emerald-400";
            case "intermediate":
                return "text-amber-400";
            case "beginner":
                return "text-slate-400";
            default:
                return "text-slate-400";
        }
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
            <div className="relative max-h-[90vh] w-full max-w-2xl overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.98),rgba(10,15,28,0.98))] shadow-2xl">
                {/* Header */}
                <div className="flex items-center justify-between border-b border-[var(--border)] p-6">
                    <div>
                        <h2 className="text-xl font-bold tracking-tight text-[var(--text-primary)]">
                            AI Session Summary
                        </h2>
                        <p className="text-sm text-[var(--text-secondary)] mt-1">
                            View your recent learning sessions
                        </p>
                    </div>
                    <button
                        onClick={onClose}
                        className="rounded-lg p-2 hover:bg-slate-700/30 transition-colors"
                    >
                        <X size={20} className="text-[var(--text-secondary)]" />
                    </button>
                </div>

                <div className="flex h-[calc(90vh-140px)] overflow-hidden">
                    {/* Sessions List */}
                    <div className="w-1/3 border-r border-[var(--border)] overflow-y-auto bg-slate-900/20">
                        {loading ? (
                            <div className="p-4 text-center text-[var(--text-secondary)]">
                                Loading sessions...
                            </div>
                        ) : error ? (
                            <div className="p-4 text-center text-red-400 text-sm">
                                {error}
                            </div>
                        ) : sessions.length === 0 ? (
                            <div className="p-4 text-center text-[var(--text-secondary)]">
                                No sessions found
                            </div>
                        ) : (
                            <div className="space-y-2 p-4">
                                {sessions.map((session) => (
                                    <button
                                        key={session.id}
                                        onClick={() => setSelectedSession(session)}
                                        className={`w-full text-left rounded-lg p-3 transition-colors border ${
                                            selectedSession?.id === session.id
                                                ? "border-indigo-500/50 bg-indigo-500/10"
                                                : "border-slate-700/30 hover:bg-slate-700/20"
                                        }`}
                                    >
                                        <div className="font-medium text-sm text-[var(--text-primary)]">
                                            {session.subject || "General"}
                                        </div>
                                        <div className="text-xs text-[var(--text-secondary)] mt-1">
                                            {session.tool_mode} • {formatDuration(session.duration_seconds)}
                                        </div>
                                        <div className="text-xs text-amber-400 mt-1">
                                            {new Date(session.started_at).toLocaleDateString()}
                                        </div>
                                    </button>
                                ))}
                            </div>
                        )}
                    </div>

                    {/* Session Details */}
                    <div className="w-2/3 overflow-y-auto p-6">
                        {displaySession ? (
                            <div className="space-y-6">
                                {/* Title Section */}
                                <div>
                                    <h3 className="text-lg font-semibold text-[var(--text-primary)]">
                                        {displaySession.subject || "General Session"}
                                    </h3>
                                    {displaySession.topic && (
                                        <p className="text-sm text-[var(--text-secondary)] mt-2">
                                            Topic: {displaySession.topic}
                                        </p>
                                    )}
                                </div>

                                {/* Key Metrics Grid */}
                                <div className="grid grid-cols-2 gap-4">
                                    <div className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-4">
                                        <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider">
                                            Tool
                                        </div>
                                        <div className="text-lg font-semibold text-[var(--text-primary)] mt-2 capitalize">
                                            {displaySession.tool_mode}
                                        </div>
                                    </div>

                                    <div className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-4">
                                        <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider">
                                            Duration
                                        </div>
                                        <div className="text-lg font-semibold text-[var(--text-primary)] mt-2">
                                            {formatDuration(displaySession.duration_seconds)}
                                        </div>
                                    </div>

                                    <div className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-4">
                                        <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider">
                                            Engagement
                                        </div>
                                        <div className="text-lg font-semibold text-[var(--text-primary)] mt-2">
                                            {displaySession.engagement_score.toFixed(1)}%
                                        </div>
                                    </div>

                                    <div className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-4">
                                        <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider">
                                            Mastery Level
                                        </div>
                                        <div className={`text-lg font-semibold mt-2 capitalize ${getMasteryColor(displaySession.mastery_level)}`}>
                                            {displaySession.mastery_level}
                                        </div>
                                    </div>
                                </div>

                                {/* Quiz Score */}
                                {displaySession.quiz_score_percent !== undefined && (
                                    <div className="rounded-lg border border-slate-700/30 bg-slate-800/30 p-4">
                                        <div className="text-xs text-[var(--text-secondary)] uppercase tracking-wider">
                                            Quiz Score
                                        </div>
                                        <div className="text-lg font-semibold text-emerald-400 mt-2">
                                            {displaySession.quiz_score_percent.toFixed(1)}%
                                        </div>
                                    </div>
                                )}

                                {/* Key Insights */}
                                {displaySession.key_insights && displaySession.key_insights.length > 0 && (
                                    <div>
                                        <h4 className="text-sm font-semibold text-[var(--text-primary)] uppercase tracking-wide mb-3">
                                            Key Insights
                                        </h4>
                                        <div className="space-y-2">
                                            {displaySession.key_insights.map((insight, idx) => (
                                                <div
                                                    key={idx}
                                                    className="rounded-lg border-l-2 border-indigo-500/50 bg-indigo-500/5 px-4 py-3"
                                                >
                                                    <p className="text-sm text-[var(--text-secondary)]">
                                                        {insight}
                                                    </p>
                                                </div>
                                            ))}
                                        </div>
                                    </div>
                                )}

                                {/* Timestamp */}
                                <div className="text-xs text-[var(--text-secondary)] pt-4 border-t border-slate-700/30">
                                    <div>Started: {new Date(displaySession.started_at).toLocaleString()}</div>
                                    {displaySession.ended_at && (
                                        <div>Ended: {new Date(displaySession.ended_at).toLocaleString()}</div>
                                    )}
                                </div>
                            </div>
                        ) : (
                            <div className="flex items-center justify-center h-full text-[var(--text-secondary)]">
                                Loading session details...
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer */}
                <div className="border-t border-[var(--border)] bg-slate-900/20 px-6 py-4 flex justify-end">
                    <button
                        onClick={onClose}
                        className="rounded-lg bg-indigo-600 px-6 py-2 font-medium text-white hover:bg-indigo-700 transition-colors"
                    >
                        Close
                    </button>
                </div>
            </div>
        </div>
    );
}
