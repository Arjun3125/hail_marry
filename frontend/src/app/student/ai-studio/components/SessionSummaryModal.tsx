"use client";

import { Clock, LogOut, RotateCcw } from "lucide-react";

export interface SessionSummaryData {
    duration: number;
    toolUsed: string;
    exchangeCount: number;
    topicsExplored: string[];
}

interface SessionSummaryModalProps {
    isOpen: boolean;
    sessionData: SessionSummaryData | null;
    onContinue: () => void;
    onEnd: () => void;
}

export function SessionSummaryModal({
    isOpen,
    sessionData,
    onContinue,
    onEnd,
}: SessionSummaryModalProps) {
    if (!isOpen || !sessionData) return null;
    const minutes = Math.floor(sessionData.duration / 60);
    const seconds = sessionData.duration % 60;
    const displayDuration = minutes > 0
        ? `${minutes} min ${seconds > 0 ? `${seconds} sec` : ""}`.trim()
        : `${seconds} sec`;

    return (
        <div className="fixed inset-0 z-50 flex items-end justify-center bg-black/40 md:items-center">
            <div className="w-full max-w-2xl rounded-t-3xl md:rounded-3xl bg-[var(--bg-panel)] shadow-[var(--shadow-level-3)] p-6 md:p-8 space-y-6 animate-in slide-in-from-bottom-4 md:slide-in-from-bottom-0">
                {/* Header */}
                <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">
                        Session Summary
                    </p>
                    <h2 className="mt-2 text-2xl font-black text-[var(--text-primary)]">
                        Time away detected
                    </h2>
                    <p className="mt-2 text-sm text-[var(--text-secondary)]">
                        You&apos;ve been inactive for 5 minutes. Would you like to continue your session or save your work and log out?
                    </p>
                </div>

                {/* Session Stats */}
                <div className="grid gap-4 md:grid-cols-3">
                    <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-5">
                        <div className="flex items-center gap-2 text-[var(--text-primary)]">
                            <Clock className="h-4 w-4" />
                            <p className="text-xs font-semibold uppercase tracking-[0.16em]">
                                Session duration
                            </p>
                        </div>
                        <p className="mt-3 text-2xl font-black text-[var(--text-primary)]">
                            {displayDuration}
                        </p>
                    </div>

                    <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-5">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                            Tool active
                        </p>
                        <p className="mt-3 text-2xl font-black text-status-blue capitalize">
                            {sessionData.toolUsed.replace(/_/g, " ")}
                        </p>
                    </div>

                    <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-5">
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                            Exchanges
                        </p>
                        <p className="mt-3 text-2xl font-black text-status-emerald">
                            {sessionData.exchangeCount}
                        </p>
                    </div>
                </div>

                {/* Topics if available */}
                {sessionData.topicsExplored.length > 0 && (
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                            Topics explored
                        </p>
                        <div className="mt-3 flex flex-wrap gap-2">
                            {sessionData.topicsExplored.slice(0, 5).map((topic) => (
                                <span
                                    key={topic}
                                    className="inline-flex items-center gap-2 rounded-full bg-[rgba(79,142,247,0.12)] px-3 py-1.5 text-xs font-medium text-[var(--text-primary)]"
                                >
                                    {topic}
                                </span>
                            ))}
                            {sessionData.topicsExplored.length > 5 && (
                                <span className="inline-flex items-center gap-2 rounded-full bg-[rgba(148,163,184,0.08)] px-3 py-1.5 text-xs font-medium text-[var(--text-secondary)]">
                                    +{sessionData.topicsExplored.length - 5} more
                                </span>
                            )}
                        </div>
                    </div>
                )}

                {/* Actions */}
                <div className="flex flex-col gap-3 md:flex-row md:justify-end">
                    <button
                        type="button"
                        onClick={onEnd}
                        className="order-2 md:order-1 inline-flex items-center justify-center gap-2 rounded-2xl px-5 py-3 text-sm font-semibold text-[var(--text-secondary)] hover:bg-[rgba(255,255,255,0.05)] transition-colors"
                    >
                        <LogOut className="h-4 w-4" />
                        End session
                    </button>
                    <button
                        type="button"
                        onClick={onContinue}
                        className="order-1 md:order-2 inline-flex items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(16,185,129,0.96),rgba(34,197,94,0.9))] px-5 py-3 text-sm font-bold text-[#06101e] hover:-translate-y-0.5 transition-transform shadow-[var(--shadow-level-2)]"
                    >
                        <RotateCcw className="h-4 w-4" />
                        Continue session
                    </button>
                </div>
            </div>
        </div>
    );
}
