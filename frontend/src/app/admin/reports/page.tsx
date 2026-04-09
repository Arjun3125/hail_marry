"use client";

import { useMemo, useState, type ComponentType } from "react";
import { BarChart3, Download, FileText, Sparkles } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { API_BASE, api } from "@/lib/api";

type ReportDef = {
    name: string;
    desc: string;
    type: "attendance" | "performance" | "ai-usage";
    icon: ComponentType<{ className?: string }>;
    run: () => Promise<unknown>;
    exportPath: string;
};

export default function AdminReportsPage() {
    const [loadingType, setLoadingType] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [lastReport, setLastReport] = useState<{ type: string; generated_at: string; rows: number } | null>(null);
    const [preview, setPreview] = useState<string>("No report generated yet.");

    const reports: ReportDef[] = [
        {
            name: "Attendance Report",
            desc: "Class-wise attendance summary",
            type: "attendance",
            icon: FileText,
            run: api.admin.reportsAttendance,
            exportPath: "/api/admin/export/attendance",
        },
        {
            name: "Performance Report",
            desc: "Subject-wise marks analysis",
            type: "performance",
            icon: BarChart3,
            run: api.admin.reportsPerformance,
            exportPath: "/api/admin/export/performance",
        },
        {
            name: "AI Usage Report",
            desc: "AI query logs and token usage",
            type: "ai-usage",
            icon: Sparkles,
            run: api.admin.reportsAIUsage,
            exportPath: "/api/admin/export/ai-usage",
        },
    ];

    const summary = useMemo(() => ({
        availableReports: reports.length,
        lastRows: lastReport?.rows ?? 0,
        lastType: lastReport?.type ?? "No report yet",
    }), [lastReport, reports.length]);

    const generateReport = async (report: ReportDef) => {
        try {
            setLoadingType(report.type);
            setError(null);
            const payload = await report.run();
            const rowsData = Array.isArray(payload) ? payload : [];
            const rows = rowsData.length;
            setLastReport({
                type: report.name,
                generated_at: new Date().toISOString(),
                rows,
            });
            setPreview(rows > 0 ? JSON.stringify(rowsData[0], null, 2) : "Report generated successfully (no rows).");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate report");
        } finally {
            setLoadingType(null);
        }
    };

    const downloadReport = (report: ReportDef) => {
        window.open(`${API_BASE}${report.exportPath}`, "_blank", "noopener,noreferrer");
    };

    const formatDateTime = (value: string) => {
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
    };

    return (
        <PrismPage variant="report" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <BarChart3 className="h-3.5 w-3.5" />
                            Institutional Reporting
                        </PrismHeroKicker>
                    )}
                    title="Generate school reports without leaving the academic workflow"
                    description="Use this surface to produce attendance, performance, and AI usage snapshots that support school leadership, not just platform monitoring."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Available reports</span>
                        <strong className="prism-status-value">{summary.availableReports}</strong>
                        <span className="prism-status-detail">Core report types ready to generate or export</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Last report rows</span>
                        <strong className="prism-status-value">{summary.lastRows}</strong>
                        <span className="prism-status-detail">Visible row count from the most recent run</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Last output</span>
                        <strong className="prism-status-value">{summary.lastType}</strong>
                        <span className="prism-status-detail">Most recent report generated on this surface</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-reports"
                        onRetry={() => {
                            if (loadingType) return;
                            setError(null);
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
                    <PrismPanel className="overflow-hidden p-0">
                        <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div>
                                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Report catalog</p>
                                    <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                        Generate the admin snapshot first, then export the same underlying dataset directly from this surface.
                                    </p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    {loadingType ? `Generating ${loadingType}` : "Ready"}
                                </div>
                            </div>
                        </div>

                        <div className="grid gap-4 p-5">
                            {reports.map((report) => (
                                <PrismPanel key={report.type} className="p-5">
                                    <div className="flex flex-col gap-4 xl:flex-row xl:items-start xl:justify-between">
                                        <div className="flex items-start gap-3">
                                            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[rgba(96,165,250,0.12)] text-[var(--text-primary)]">
                                                <report.icon className="h-5 w-5" />
                                            </div>
                                            <div>
                                                <h2 className="text-base font-semibold text-[var(--text-primary)]">{report.name}</h2>
                                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{report.desc}</p>
                                            </div>
                                        </div>

                                        <div className="grid gap-2 sm:grid-cols-2 xl:min-w-[240px]">
                                            <button
                                                className="prism-action"
                                                onClick={() => void generateReport(report)}
                                                disabled={loadingType !== null}
                                            >
                                                {loadingType === report.type ? "Generating..." : "Generate"}
                                            </button>
                                            <button
                                                className="prism-action-secondary"
                                                onClick={() => downloadReport(report)}
                                            >
                                                <Download className="h-4 w-4" />
                                                Export
                                            </button>
                                        </div>
                                    </div>
                                </PrismPanel>
                            ))}
                        </div>
                    </PrismPanel>

                    <div className="space-y-4">
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                kicker="Overview"
                                title="Recent output"
                                description="See the most recent generated report before exporting or regenerating."
                            />
                            {lastReport ? (
                                <div className="mt-4 space-y-4">
                                    <SummaryRow label="Type" value={lastReport.type} />
                                    <SummaryRow label="Generated" value={formatDateTime(lastReport.generated_at)} />
                                    <SummaryRow label="Rows" value={`${lastReport.rows}`} />
                                </div>
                            ) : (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={FileText}
                                        title="No reports generated yet"
                                        description="Use any report action on the left to create the first admin snapshot."
                                    />
                                </div>
                            )}
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                kicker="Preview"
                                title="Preview sample"
                                description="A quick sample row from the last generated payload."
                            />
                            <pre className="mt-4 overflow-auto rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4 text-xs leading-6 text-[var(--text-secondary)]">
                                {preview}
                            </pre>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                kicker="Notes"
                                title="Workflow notes"
                                description="Clarify what changed visually and what stayed operationally stable."
                            />
                            <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                <p>This route keeps reporting operationally simple: generate the snapshot, show the latest metadata, and let exports leave through the existing endpoints.</p>
                                <p>The underlying report contracts are unchanged, so this pass is strictly presentation and workflow framing.</p>
                            </div>
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-4 py-3">
            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</span>
            <span className="max-w-[58%] text-right text-sm font-medium text-[var(--text-primary)]">{value}</span>
        </div>
    );
}
