"use client";

import { APIError } from "@/lib/api";

type Props = {
    error: APIError | null;
    queueEstimateText?: string;
    onRetry: () => void;
    onSimplifiedMode: () => void;
};

export function AIErrorState({ error, queueEstimateText, onRetry, onSimplifiedMode }: Props) {
    if (!error) return null;

    return (
        <div className="mb-4 rounded-xl border border-[var(--warning)]/30 bg-warning-subtle p-3">
            <p className="text-sm font-semibold text-[var(--text-primary)]">{error.message}</p>
            <p className="mt-1 text-xs text-[var(--text-muted)]">
                Suggested action: <span className="font-medium">{error.action}</span>
                {queueEstimateText ? ` · ${queueEstimateText}` : ""}
            </p>
            <div className="mt-3 flex flex-wrap gap-2">
                <button
                    onClick={onRetry}
                    className="rounded-lg bg-[var(--primary)] px-3 py-1.5 text-xs font-semibold text-white"
                >
                    Retry now
                </button>
                <button
                    onClick={onSimplifiedMode}
                    className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-xs font-semibold text-[var(--text-secondary)]"
                >
                    Try simplified mode
                </button>
                <span className="rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--text-muted)]">
                    Contact admin
                </span>
            </div>
        </div>
    );
}
