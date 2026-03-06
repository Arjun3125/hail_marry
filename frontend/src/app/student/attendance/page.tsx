"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, XCircle, Clock } from "lucide-react";

import { api } from "@/lib/api";

type AttendanceItem = {
    date: string;
    day: string;
    status: "present" | "absent" | "late";
};

const statusIcon = {
    present: <CheckCircle2 className="w-4 h-4 text-[var(--success)]" />,
    absent: <XCircle className="w-4 h-4 text-[var(--error)]" />,
    late: <Clock className="w-4 h-4 text-[var(--warning)]" />,
};

const statusColor = {
    present: "bg-green-50 text-[var(--success)]",
    absent: "bg-red-50 text-[var(--error)]",
    late: "bg-yellow-50 text-[var(--warning)]",
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
        const present = items.filter((d) => d.status === "present").length;
        const absent = items.filter((d) => d.status === "absent").length;
        const late = items.filter((d) => d.status === "late").length;
        const percentage = total > 0 ? Math.round((present / total) * 100) : 0;
        return { total, present, absent, late, percentage };
    }, [items]);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Attendance</h1>
                <p className="text-sm text-[var(--text-secondary)]">Your attendance records for the current term</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
                {[
                    { label: "Total Days", value: stats.total, color: "var(--primary)" },
                    { label: "Present", value: stats.present, color: "var(--success)" },
                    { label: "Absent", value: stats.absent, color: "var(--error)" },
                    { label: "Late", value: stats.late, color: "var(--warning)" },
                ].map((s) => (
                    <div key={s.label} className="bg-white rounded-[var(--radius)] p-4 shadow-[var(--shadow-card)]">
                        <p className="text-xs text-[var(--text-muted)] mb-1">{s.label}</p>
                        <p className="text-2xl font-bold" style={{ color: s.color }}>{s.value}</p>
                    </div>
                ))}
            </div>

            <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-6">
                <div className="flex items-center justify-between mb-2">
                    <span className="text-sm font-medium text-[var(--text-primary)]">Overall Attendance</span>
                    <span className="text-sm font-bold" style={{ color: stats.percentage >= 75 ? "var(--success)" : "var(--error)" }}>
                        {stats.percentage}%
                    </span>
                </div>
                <div className="h-3 bg-[var(--bg-page)] rounded-full">
                    <div
                        className="h-3 rounded-full transition-all"
                        style={{
                            width: `${stats.percentage}%`,
                            backgroundColor: stats.percentage >= 75 ? "var(--success)" : "var(--error)",
                        }}
                    />
                </div>
                {stats.percentage < 75 ? (
                    <p className="text-xs text-[var(--error)] mt-2">Below 75% minimum attendance requirement</p>
                ) : null}
            </div>

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[480px]">
                        <thead>
                            <tr className="border-b border-[var(--border)]">
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Date</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Day</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={3} className="px-5 py-4 text-sm text-[var(--text-muted)]">Loading attendance...</td>
                                </tr>
                            ) : items.length === 0 ? (
                                <tr>
                                    <td colSpan={3} className="px-5 py-4 text-sm text-[var(--text-muted)]">No attendance records found.</td>
                                </tr>
                            ) : items.map((record, idx) => (
                                <tr key={`${record.date}-${idx}`} className="border-b border-[var(--border-light)] hover:bg-[var(--bg-page)] transition-colors">
                                    <td className="px-5 py-3 text-sm text-[var(--text-primary)]">{record.date}</td>
                                    <td className="px-5 py-3 text-sm text-[var(--text-secondary)]">{record.day}</td>
                                    <td className="px-5 py-3">
                                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium capitalize ${statusColor[record.status]}`}>
                                            {statusIcon[record.status]}
                                            {record.status}
                                        </span>
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
