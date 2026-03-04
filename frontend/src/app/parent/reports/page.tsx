"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type ParentReport = {
    child: { id: string; name: string };
    attendance_pct_30d: number;
    weak_subjects: string[];
    summary: string;
};

export default function ParentReportsPage() {
    const [report, setReport] = useState<ParentReport | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.parent.reports();
                setReport(data as ParentReport);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load report");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div className="space-y-4">
            <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Progress Report</h1>
                <p className="text-sm text-[var(--text-secondary)]">Consolidated monthly snapshot.</p>
            </div>
            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}
            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading...</p>
            ) : report ? (
                <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] space-y-3">
                    <p className="text-sm text-[var(--text-secondary)]">Child: <span className="font-medium text-[var(--text-primary)]">{report.child.name}</span></p>
                    <p className="text-sm text-[var(--text-secondary)]">Attendance (30d): <span className="font-medium text-[var(--text-primary)]">{report.attendance_pct_30d}%</span></p>
                    <p className="text-sm text-[var(--text-secondary)]">Summary: <span className="font-medium text-[var(--text-primary)]">{report.summary}</span></p>
                    <div>
                        <p className="text-sm text-[var(--text-secondary)] mb-2">Weak Subjects</p>
                        <div className="flex flex-wrap gap-2">
                            {report.weak_subjects.length > 0 ? report.weak_subjects.map((s) => (
                                <span key={s} className="px-2 py-1 text-xs rounded-full bg-orange-50 text-orange-700">{s}</span>
                            )) : (
                                <span className="text-xs text-[var(--text-muted)]">No weak subjects identified.</span>
                            )}
                        </div>
                    </div>
                </div>
            ) : (
                <p className="text-sm text-[var(--text-muted)]">No report found.</p>
            )}
        </div>
    );
}
