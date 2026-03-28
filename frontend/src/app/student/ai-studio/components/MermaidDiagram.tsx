"use client";

import mermaid from "mermaid";
import { Copy, GitBranch } from "lucide-react";
import { useEffect, useMemo, useState } from "react";

let mermaidInitialized = false;

export function MermaidDiagram({ chart }: { chart: string }) {
    const [svg, setSvg] = useState<string>("");
    const [error, setError] = useState<string | null>(null);
    const chartId = useMemo(() => `mermaid-${Math.random().toString(36).slice(2)}`, []);

    useEffect(() => {
        if (!mermaidInitialized) {
            mermaid.initialize({
                startOnLoad: false,
                securityLevel: "loose",
                theme: "dark",
            });
            mermaidInitialized = true;
        }
    }, []);

    useEffect(() => {
        let cancelled = false;
        const render = async () => {
            try {
                const { svg: rendered } = await mermaid.render(chartId, chart);
                if (!cancelled) {
                    setSvg(rendered);
                    setError(null);
                }
            } catch {
                if (!cancelled) {
                    setSvg("");
                    setError("Could not render Mermaid diagram.");
                }
            }
        };
        void render();
        return () => {
            cancelled = true;
        };
    }, [chart, chartId]);

    const copyChart = async () => {
        await navigator.clipboard.writeText(chart);
    };

    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-page)]">
            <div className="flex items-center justify-between border-b border-[var(--border)] px-4 py-3">
                <div className="flex items-center gap-2">
                    <div className="rounded-lg bg-sky-500/15 p-2 text-sky-400">
                        <GitBranch className="h-4 w-4" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-[var(--text-primary)]">Flowchart preview</p>
                        <p className="text-xs text-[var(--text-muted)]">Mermaid-backed diagram and export-friendly source</p>
                    </div>
                </div>
                <button
                    type="button"
                    onClick={() => void copyChart()}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]"
                >
                    <Copy className="h-3.5 w-3.5" />
                    Copy code
                </button>
            </div>

            {error ? (
                <div className="px-4 py-6 text-sm text-[var(--text-secondary)]">{error}</div>
            ) : (
                <div
                    className="overflow-x-auto p-4 mermaid-diagram"
                    dangerouslySetInnerHTML={{ __html: svg }}
                />
            )}
        </div>
    );
}
