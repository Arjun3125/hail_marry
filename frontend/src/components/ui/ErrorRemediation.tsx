"use client";

import { AlertTriangle, RefreshCw } from "lucide-react";

import { APIError } from "@/lib/api";
import { classifyError, supportIds } from "@/lib/errorRemediation";

function extractErrorCode(error: string): string | null {
    const match = error.match(/Error Code:\s*([A-Z]+-[A-Z]+-\d{3})/i);
    return match ? match[1].toUpperCase() : null;
}

export default function ErrorRemediation({
    error,
    scope,
    onRetry,
    simplifiedModeHref,
}: {
    error: string | Error;
    scope: string;
    onRetry?: () => void;
    simplifiedModeHref?: string;
}) {
    const message = error instanceof Error ? error.message : error;
    const apiError = error instanceof APIError ? error : null;
    const meta = classifyError(message, apiError?.status);
    const ids = supportIds(scope, message);
    const errorCode = apiError?.errorCode || extractErrorCode(message);
    const traceId = apiError?.traceId || null;

    const contactAdmin = async () => {
        const supportMessage = `Support needed for ${scope}. Error Code: ${errorCode || "N/A"}, Trace ID: ${traceId || "N/A"}, Ref ID: ${ids.refId}. Error: ${message}`;
        try {
            await navigator.clipboard.writeText(supportMessage);
            alert("Support details copied. Share this with your admin.");
        } catch {
            alert(supportMessage);
        }
    };

    return (
        <div className="mb-6 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle p-4">
            <div className="flex items-start gap-3">
                <AlertTriangle className="mt-0.5 h-4 w-4 text-[var(--error)]" />
                <div className="flex-1">
                    <p className="text-sm font-semibold text-[var(--error)]">{meta.title}</p>
                    <p className="mt-1 text-sm text-[var(--error)]/90">{message}</p>
                    <p className="mt-2 text-xs text-[var(--text-secondary)]">{meta.helpText}</p>

                    <div className="mt-3 text-[11px] text-[var(--text-secondary)]">
                        {errorCode ? <span className="font-mono">Error Code: {errorCode}</span> : null}
                        {errorCode ? <span className="mx-2">&bull;</span> : null}
                        {traceId ? <span className="font-mono">Trace ID: {traceId}</span> : null}
                        {traceId ? <span className="mx-2">&bull;</span> : null}
                        <span className="font-mono">Ref ID: {ids.refId}</span>
                    </div>

                    <div className="mt-3 flex flex-wrap gap-2">
                        {onRetry ? (
                            <button
                                onClick={onRetry}
                                className="inline-flex items-center gap-1.5 rounded-[var(--radius-sm)] bg-[var(--error)] px-3 py-1.5 text-xs font-semibold text-white hover:opacity-90"
                            >
                                <RefreshCw className="h-3.5 w-3.5" /> {meta.actionLabel}
                            </button>
                        ) : null}
                        <button
                            onClick={() => void contactAdmin()}
                            className="rounded-[var(--radius-sm)] border border-[var(--border-light)] bg-[var(--bg-card)] px-3 py-1.5 text-xs font-semibold text-[var(--text-primary)]"
                        >
                            Contact admin
                        </button>
                        {simplifiedModeHref ? (
                            <a
                                href={simplifiedModeHref}
                                className="rounded-[var(--radius-sm)] border border-[var(--border-light)] bg-[var(--bg-page)] px-3 py-1.5 text-xs font-semibold text-[var(--text-primary)]"
                            >
                                Try simplified mode
                            </a>
                        ) : null}
                    </div>
                </div>
            </div>
        </div>
    );
}
