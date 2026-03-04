"use client";

import { useEffect, useState } from "react";
import {
    Users,
    Bot,
    CalendarCheck,
    Award,
    MessageSquare,
    Activity,
} from "lucide-react";

import { api } from "@/lib/api";

type DashboardData = {
    total_students: number;
    total_teachers: number;
    active_today: number;
    ai_queries_today: number;
    avg_attendance: number;
    avg_performance: number;
    open_complaints: number;
};

type SecurityItem = {
    id: string;
    user: string;
    action: string;
    date: string;
};

export default function AdminDashboard() {
    const [dashboard, setDashboard] = useState<DashboardData | null>(null);
    const [activity, setActivity] = useState<SecurityItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const [dashboardData, securityData] = await Promise.all([
                    api.admin.dashboard(),
                    api.admin.security(),
                ]);
                setDashboard(dashboardData as DashboardData);
                setActivity((securityData || []) as SecurityItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load admin dashboard");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const kpis = [
        { label: "Total Students", value: dashboard?.total_students ?? 0, icon: Users, color: "var(--primary)" },
        { label: "Active Today", value: dashboard?.active_today ?? 0, icon: Activity, color: "var(--success)" },
        { label: "AI Queries Today", value: dashboard?.ai_queries_today ?? 0, icon: Bot, color: "var(--primary)" },
        { label: "Avg Attendance", value: `${dashboard?.avg_attendance ?? 0}%`, icon: CalendarCheck, color: "var(--success)" },
        { label: "Avg Performance", value: `${dashboard?.avg_performance ?? 0}%`, icon: Award, color: "var(--warning)" },
        { label: "Open Complaints", value: dashboard?.open_complaints ?? 0, icon: MessageSquare, color: "var(--error)" },
    ];

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Admin Dashboard</h1>
                <p className="text-sm text-[var(--text-secondary)]">Institutional overview</p>
            </div>

            {error ? (
                <div className="mb-6 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="text-sm text-[var(--text-muted)]">Loading dashboard...</div>
            ) : (
                <>
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                        {kpis.map((kpi) => (
                            <div key={kpi.label} className="bg-white rounded-[var(--radius)] p-4 shadow-[var(--shadow-card)]">
                                <div className="flex items-center justify-between mb-2">
                                    <kpi.icon className="w-4 h-4" style={{ color: kpi.color }} />
                                </div>
                                <p className="text-2xl font-bold text-[var(--text-primary)]">{kpi.value}</p>
                                <p className="text-xs text-[var(--text-muted)] mt-1">{kpi.label}</p>
                            </div>
                        ))}
                    </div>

                    <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Recent Security Activity</h2>
                        <div className="space-y-3">
                            {activity.slice(0, 8).map((item) => (
                                <div key={item.id} className="flex items-center justify-between p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]">
                                    <div>
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{item.action}</p>
                                        <p className="text-xs text-[var(--text-muted)]">by {item.user}</p>
                                    </div>
                                    <span className="text-xs text-[var(--text-muted)]">
                                        {new Date(item.date).toLocaleString()}
                                    </span>
                                </div>
                            ))}
                            {activity.length === 0 ? (
                                <p className="text-sm text-[var(--text-muted)]">No security activity found.</p>
                            ) : null}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
