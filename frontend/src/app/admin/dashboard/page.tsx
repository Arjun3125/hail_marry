"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import {
    Users,
    Bot,
    CalendarCheck,
    Award,
    MessageSquare,
    Activity,
    AlertTriangle,
    Workflow,
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
    queue_pending_depth: number;
    queue_processing_depth: number;
    queue_failure_rate_pct: number;
    queue_stuck_jobs: number;
    observability_alerts: Array<{
        code: string;
        severity: string;
        message: string;
    }>;
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
    const [dispatchingAlerts, setDispatchingAlerts] = useState(false);
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
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-base font-semibold text-[var(--text-primary)]">Queue Health</h2>
                            <Workflow className="w-4 h-4 text-[var(--primary)]" />
                        </div>
                        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                            <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-4">
                                <p className="text-xs text-[var(--text-muted)]">Pending Jobs</p>
                                <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{dashboard?.queue_pending_depth ?? 0}</p>
                            </div>
                            <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-4">
                                <p className="text-xs text-[var(--text-muted)]">Processing Jobs</p>
                                <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{dashboard?.queue_processing_depth ?? 0}</p>
                            </div>
                            <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-4">
                                <p className="text-xs text-[var(--text-muted)]">Failure Rate</p>
                                <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{dashboard?.queue_failure_rate_pct ?? 0}%</p>
                            </div>
                            <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-4">
                                <p className="text-xs text-[var(--text-muted)]">Stuck Jobs</p>
                                <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{dashboard?.queue_stuck_jobs ?? 0}</p>
                            </div>
                        </div>
                    </div>

                    <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-base font-semibold text-[var(--text-primary)]">Active Alerts</h2>
                            <div className="flex items-center gap-3">
                                <button
                                    type="button"
                                    onClick={async () => {
                                        try {
                                            setDispatchingAlerts(true);
                                            await api.admin.dispatchObservabilityAlerts();
                                        } catch (err) {
                                            setError(err instanceof Error ? err.message : "Failed to dispatch alerts");
                                        } finally {
                                            setDispatchingAlerts(false);
                                        }
                                    }}
                                    className="rounded-full bg-amber-100 px-3 py-1 text-xs font-medium text-amber-800 hover:bg-amber-200 disabled:opacity-60"
                                    disabled={dispatchingAlerts || (dashboard?.observability_alerts?.length ?? 0) === 0}
                                >
                                    {dispatchingAlerts ? "Dispatching..." : "Dispatch Alerts"}
                                </button>
                                <AlertTriangle className="w-4 h-4 text-[var(--warning)]" />
                            </div>
                        </div>
                        <div className="space-y-3">
                            {(dashboard?.observability_alerts || []).slice(0, 5).map((alert) => (
                                <div key={alert.code} className="rounded-[var(--radius-sm)] border border-amber-200 bg-amber-50 p-3">
                                    <div className="flex items-center justify-between gap-3">
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{alert.message}</p>
                                        <span className="text-[11px] uppercase tracking-wide text-amber-700">{alert.severity}</span>
                                    </div>
                                    <p className="mt-1 text-xs text-[var(--text-muted)]">{alert.code}</p>
                                </div>
                            ))}
                            {(dashboard?.observability_alerts?.length ?? 0) === 0 ? (
                                <p className="text-sm text-[var(--text-muted)]">No active observability alerts.</p>
                            ) : null}
                            <div className="pt-2 text-sm">
                                <Link href="/admin/traces" className="text-[var(--primary)] hover:underline">
                                    Open Trace Viewer
                                </Link>
                            </div>
                        </div>
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
