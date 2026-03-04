"use client";

import { useState, type ComponentType } from "react";
import { Download, FileText, BarChart3 } from "lucide-react";

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
    const [lastReport, setLastReport] = useState<{
        type: string;
        generated_at: string;
        rows: number;
    } | null>(null);
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
            icon: FileText,
            run: api.admin.reportsAIUsage,
            exportPath: "/api/admin/export/ai-usage",
        },
    ];

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
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Reports</h1>
                <p className="text-sm text-[var(--text-secondary)]">Generate and export institutional reports</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid md:grid-cols-3 gap-4 mb-8">
                {reports.map((report) => (
                    <div key={report.type} className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                        <report.icon className="w-8 h-8 text-[var(--primary)] mb-3" />
                        <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-1">{report.name}</h3>
                        <p className="text-xs text-[var(--text-muted)] mb-4">{report.desc}</p>
                        <div className="grid grid-cols-2 gap-2">
                            <button
                                className="px-3 py-2 bg-[var(--primary)] text-white text-xs font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-60"
                                onClick={() => void generateReport(report)}
                                disabled={loadingType !== null}
                            >
                                {loadingType === report.type ? "Generating..." : "Generate"}
                            </button>
                            <button
                                className="px-3 py-2 bg-[var(--bg-page)] text-[var(--text-secondary)] text-xs font-medium rounded-[var(--radius-sm)] hover:bg-[var(--border-light)] flex items-center justify-center gap-1"
                                onClick={() => downloadReport(report)}
                            >
                                <Download className="w-3.5 h-3.5" /> Export
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Recent Reports</h2>
                {lastReport ? (
                    <div className="space-y-3">
                        <div className="text-sm text-[var(--text-secondary)]">
                            <p><span className="font-medium text-[var(--text-primary)]">Type:</span> {lastReport.type}</p>
                            <p><span className="font-medium text-[var(--text-primary)]">Generated:</span> {formatDateTime(lastReport.generated_at)}</p>
                            <p><span className="font-medium text-[var(--text-primary)]">Rows:</span> {lastReport.rows}</p>
                        </div>
                        <pre className="text-xs bg-[var(--bg-page)] p-3 rounded-[var(--radius-sm)] overflow-auto">{preview}</pre>
                    </div>
                ) : (
                    <div className="text-sm text-[var(--text-muted)] text-center py-8">No reports generated yet. Click Generate above to create one.</div>
                )}
            </div>
        </div>
    );
}
