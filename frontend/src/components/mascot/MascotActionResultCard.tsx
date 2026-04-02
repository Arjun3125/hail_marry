"use client";

import { ArrowRight, CheckCircle2, Compass, FileText, Layers3, Route, Sparkles } from "lucide-react";

import { MascotResponse } from "./types";

function prettifyActionKind(kind: string) {
    return kind.replace(/_/g, " ");
}

function summarizeArtifact(artifact: Record<string, unknown>) {
    if (typeof artifact.file_name === "string") {
        const chunks = typeof artifact.chunks === "number" ? `${artifact.chunks} chunks` : null;
        const ocr = artifact.ocr_processed ? "OCR processed" : null;
        return {
            title: `Indexed ${artifact.file_name}`,
            detail: [chunks, ocr].filter(Boolean).join(" • "),
            citations: null,
            icon: FileText,
        };
    }
    if (typeof artifact.tool === "string") {
        const tool = String(artifact.tool).toUpperCase();
        const answer = typeof artifact.answer === "string" ? artifact.answer : null;
        const citations = Array.isArray(artifact.citations) ? artifact.citations.map(String) : null;
        return {
            title: `${tool} output ready`,
            detail: answer ? answer : "Grounded output prepared for this request.",
            citations: citations?.length ? citations : null,
            icon: Layers3,
        };
    }
    return {
        title: "Workflow artifact ready",
        detail: "The mascot produced structured output for this step.",
        citations: null,
        icon: Sparkles,
    };
}

export function MascotActionResultCard({
    response,
    onNavigate,
    onSelectSuggestion,
}: {
    response: MascotResponse;
    onNavigate?: (href: string, notebookId?: string | null) => void;
    onSelectSuggestion?: (value: string) => void;
}) {
    const summaries = response.actions
        .map((action) => action.result_summary)
        .filter((value): value is string => Boolean(value));
    const artifacts = response.artifacts.slice(0, 2);

    if (!summaries.length && !response.navigation && !artifacts.length && !response.follow_up_suggestions.length) return null;

    return (
        <div className="mt-3 space-y-3 rounded-[24px] border border-[var(--border)] bg-[var(--bg-page)] p-3">
            {response.actions.length ? (
                <div className="flex flex-wrap gap-2">
                    {response.actions.map((action, index) => (
                        <span
                            key={`${action.kind}-${index}`}
                            className="inline-flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1 text-[11px] font-medium text-[var(--text-secondary)]"
                        >
                            <CheckCircle2 className="h-3.5 w-3.5 text-[var(--success)]" />
                            {prettifyActionKind(action.kind)}
                        </span>
                    ))}
                </div>
            ) : null}

            {summaries.length ? (
                <div className="space-y-2">
                    {summaries.map((summary) => (
                        <div key={summary} className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] px-3 py-2 text-xs leading-5 text-[var(--text-secondary)]">
                            {summary}
                        </div>
                    ))}
                </div>
            ) : null}

            {artifacts.length ? (
                <div className="grid gap-2">
                    {artifacts.map((artifact, index) => {
                        const summary = summarizeArtifact(artifact);
                        const Icon = summary.icon;
                        return (
                            <div key={`artifact-${index}`} className="flex flex-col gap-2 rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] px-3 py-3">
                                <div className="flex items-start gap-3">
                                    <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-2xl bg-[var(--bg-page)] text-[var(--primary)] shrink-0">
                                        <Icon className="h-4 w-4" />
                                    </div>
                                    <div className="min-w-0 flex-1">
                                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">Artifact</p>
                                        <p className="mt-1 text-sm font-medium text-[var(--text-primary)]">{summary.title}</p>
                                        <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{summary.detail}</p>
                                    </div>
                                </div>
                                {summary.citations && (
                                    <div className="mt-1 flex flex-wrap gap-1 border-t border-[var(--border)] pt-2">
                                        {summary.citations.map((cite, i) => (
                                            <span key={i} className="rounded border border-[var(--border)] bg-[var(--bg-page)] px-2 py-0.5 text-[10px] uppercase tracking-wide text-[var(--text-secondary)]">
                                                {cite}
                                            </span>
                                        ))}
                                    </div>
                                )}
                            </div>
                        );
                    })}
                </div>
            ) : null}

            {response.navigation?.href ? (
                <button
                    type="button"
                    onClick={() => onNavigate?.(response.navigation?.href || "", response.navigation?.notebook_id || null)}
                    className="inline-flex items-center gap-2 rounded-2xl bg-[var(--primary)] px-4 py-2 text-xs font-semibold text-white"
                >
                    <Compass className="h-4 w-4" />
                    Open {String(response.navigation.target || "page").replace(/_/g, " ")}
                </button>
            ) : null}

            {response.follow_up_suggestions.length ? (
                <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[var(--bg-card)] px-3 py-3">
                    <div className="mb-2 flex items-center gap-2 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                        <Route className="h-3.5 w-3.5" />
                        Next steps
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {response.follow_up_suggestions.slice(0, 3).map((item) => (
                            <button
                                key={item}
                                type="button"
                                onClick={() => onSelectSuggestion?.(item)}
                                className="inline-flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1.5 text-xs text-[var(--text-secondary)] transition-colors hover:border-[var(--primary)] hover:text-[var(--text-primary)]"
                            >
                                {item}
                                <ArrowRight className="h-3.5 w-3.5" />
                            </button>
                        ))}
                    </div>
                </div>
            ) : null}
        </div>
    );
}
