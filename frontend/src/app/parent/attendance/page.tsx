"use client";

import { useEffect, useState } from "react";

import { api } from "@/lib/api";

type AttendanceItem = {
    date: string;
    day: string;
    status: string;
};

export default function ParentAttendancePage() {
    const [items, setItems] = useState<AttendanceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.parent.attendance();
                setItems((data || []) as AttendanceItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load attendance");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div className="space-y-4">
            <div>
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Attendance</h1>
                <p className="text-sm text-[var(--text-secondary)]">Latest attendance records.</p>
            </div>
            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}
            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading...</p>
            ) : (
                <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                    <div className="space-y-2">
                        {items.map((item) => (
                            <div key={`${item.date}-${item.status}`} className="p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)] flex items-center justify-between">
                                <div>
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{item.date}</p>
                                    <p className="text-xs text-[var(--text-muted)]">{item.day}</p>
                                </div>
                                <span className="text-xs font-medium uppercase text-[var(--text-secondary)]">{item.status}</span>
                            </div>
                        ))}
                        {items.length === 0 ? (
                            <p className="text-sm text-[var(--text-muted)]">No attendance records found.</p>
                        ) : null}
                    </div>
                </div>
            )}
        </div>
    );
}
