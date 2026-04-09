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
        <div className="prism-error-shell prism-remediation-card mb-6">
            <div className="flex items-start gap-4">
                <div className="prism-error-icon">
                    <AlertTriangle className="h-4 w-4 text-[var(--error)]" />
                </div>
                <div className="flex-1">
                    <p className="prism-error-eyebrow">Needs attention</p>
                    <p className="mt-1 text-sm font-semibold text-[var(--text-primary)]">{meta.title}</p>
                    <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{message}</p>
                    <p className="mt-3 text-xs leading-5 text-[var(--text-muted)]">{meta.helpText}</p>

                    <div className="mt-4 flex flex-wrap gap-2 text-[11px] text-[var(--text-secondary)]">
                        {errorCode ? <span className="prism-chip font-mono">Error Code: {errorCode}</span> : null}
                        {traceId ? <span className="prism-chip font-mono">Trace ID: {traceId}</span> : null}
                        <span className="prism-chip font-mono">Ref ID: {ids.refId}</span>
                    </div>

                    <div className="prism-empty-actions mt-4">
                        {onRetry ? (
                            <button
                                onClick={onRetry}
                                className="prism-action inline-flex items-center gap-1.5 !bg-[linear-gradient(135deg,rgba(226,232,240,0.96),rgba(186,200,222,0.94))] !text-[#0b1527] !shadow-[0_16px_30px_rgba(15,23,42,0.18)]"
                            >
                                <RefreshCw className="h-3.5 w-3.5" /> {meta.actionLabel}
                            </button>
                        ) : null}
                        <button
                            onClick={() => void contactAdmin()}
                            className="prism-action-secondary text-xs"
                        >
                            Contact admin
                        </button>
                        {simplifiedModeHref ? (
                            <a
                                href={simplifiedModeHref}
                                className="prism-action-secondary text-xs"
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
