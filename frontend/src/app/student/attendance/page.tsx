"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Clock, XCircle } from "lucide-react";

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
import { api } from "@/lib/api";

type AttendanceItem = {
    date: string;
    day: string;
    status: "present" | "absent" | "late";
};

const statusIcon = {
    present: <CheckCircle2 className="h-4 w-4 text-[var(--success)]" />,
    absent: <XCircle className="h-4 w-4 text-[var(--error)]" />,
    late: <Clock className="h-4 w-4 text-[var(--warning)]" />,
};

const statusColor = {
    present: "bg-success-subtle text-[var(--success)]",
    absent: "bg-error-subtle text-[var(--error)]",
    late: "bg-warning-subtle text-[var(--warning)]",
};

export default function AttendancePage() {
    const [items, setItems] = useState<AttendanceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.student.attendance();
                setItems((payload || []) as AttendanceItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load attendance");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const stats = useMemo(() => {
        const total = items.length;
        const present = items.filter((item) => item.status === "present").length;
        const absent = items.filter((item) => item.status === "absent").length;
        const late = items.filter((item) => item.status === "late").length;
        const percentage = total > 0 ? Math.round((present / total) * 100) : 0;
        return { total, present, absent, late, percentage };
    }, [items]);

    return (
        <PrismPage variant="report" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Clock className="h-3.5 w-3.5" />Attendance Record</PrismHeroKicker>}
                    title="Track attendance as part of your study rhythm"
                    description="Use this view to see how regularly you are showing up, where you have missed time, and whether your attendance is staying above the expected threshold."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Overall attendance</span>
                        <strong className="prism-status-value">{stats.percentage}%</strong>
                        <span className="prism-status-detail">Current attendance rate across recorded days</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Present</span>
                        <strong className="prism-status-value">{stats.present}</strong>
                        <span className="prism-status-detail">Days marked present in the current record set</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Absent or late</span>
                        <strong className="prism-status-value">{stats.absent + stats.late}</strong>
                        <span className="prism-status-detail">Days that may need attention or follow-up</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-attendance" onRetry={() => window.location.reload()} /> : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismSectionHeader title="Attendance log" description="Review the recorded days below and use the overall percentage to check whether you are staying on track." />

                    <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                        <div className="mb-2 flex items-center justify-between">
                            <span className="text-sm font-medium text-[var(--text-primary)]">Overall attendance</span>
                            <span className={`text-sm font-semibold ${stats.percentage >= 75 ? "text-[var(--success)]" : "text-[var(--error)]"}`}>{stats.percentage}%</span>
                        </div>
                        <div className="h-3 rounded-full bg-[var(--bg-page)]">
                            <div className="h-3 rounded-full" style={{ width: `${stats.percentage}%`, backgroundColor: stats.percentage >= 75 ? "var(--success)" : "var(--error)" }} />
                        </div>
                        {stats.percentage < 75 ? <p className="mt-2 text-xs text-[var(--error)]">Below the usual 75% minimum requirement.</p> : null}
                    </div>

                    {loading ? (
                        <p className="text-sm text-[var(--text-secondary)]">Loading attendance...</p>
                    ) : items.length === 0 ? (
                        <EmptyState icon={Clock} title="No attendance records yet" description="Attendance entries will appear here once the current term starts recording classroom participation." eyebrow="No data yet" />
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full min-w-[480px]">
                                <thead>
                                    <tr className="border-b border-[var(--border)]">
                                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Date</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Day</th>
                                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {items.map((record, index) => (
                                        <tr key={`${record.date}-${index}`} className="border-b border-[var(--border-light)]">
                                            <td className="px-4 py-3 text-sm text-[var(--text-primary)]">{record.date}</td>
                                            <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{record.day}</td>
                                            <td className="px-4 py-3">
                                                <span className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-1 text-xs font-medium capitalize ${statusColor[record.status]}`}>
                                                    {statusIcon[record.status]}
                                                    {record.status}
                                                </span>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}
