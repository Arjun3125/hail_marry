"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type ParentDashboard = {
    child: {
        id: string;
        name: string;
        email: string;
        class: string | null;
    };
    attendance_pct: number;
    avg_marks: number;
    pending_assignments: number;
};

export default function ParentDashboardPage() {
    const [data, setData] = useState<ParentDashboard | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.parent.dashboard();
                setData(payload as ParentDashboard);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div className="space-y-6">
            <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Parent Dashboard</h1>
                <p className="text-sm text-[var(--text-secondary)]">Track your child&apos;s progress in one place.</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading...</p>
            ) : data ? (
                <>
                    <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-2">Child Profile</h2>
                        <p className="text-sm text-[var(--text-secondary)]">{data.child.name} ({data.child.email})</p>
                        <p className="text-sm text-[var(--text-secondary)]">Class: {data.child.class || "N/A"}</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <p className="text-xs text-[var(--text-muted)] mb-1">Attendance</p>
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data.attendance_pct}%</p>
                        </div>
                        <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <p className="text-xs text-[var(--text-muted)] mb-1">Average Marks</p>
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data.avg_marks}%</p>
                        </div>
                        <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <p className="text-xs text-[var(--text-muted)] mb-1">Pending Assignments</p>
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data.pending_assignments}</p>
                        </div>
                    </div>
                </>
            ) : (
                <p className="text-sm text-[var(--text-muted)]">No data available.</p>
            )}
        </div>
    );
}
