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
    Shield,
} from "lucide-react";
import {
    ResponsiveContainer,
    PieChart,
    Pie,
    Cell,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
} from "recharts";

import { api } from "@/lib/api";
import { SkeletonCard } from "@/components/Skeleton";
import { AnimatedCounter, ProgressRing } from "@/components/ui/SharedUI";
import { RoleStartPanel } from "@/components/RoleStartPanel";

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

const glassColors = ["glass-stat-blue", "glass-stat-green", "glass-stat-purple", "glass-stat-amber", "glass-stat-pink", "glass-stat-blue"];

// Mock data for charts
const weeklyActivity = [
    { day: "Mon", students: 120, ai: 45 },
    { day: "Tue", students: 135, ai: 62 },
    { day: "Wed", students: 145, ai: 58 },
    { day: "Thu", students: 130, ai: 72 },
    { day: "Fri", students: 110, ai: 50 },
    { day: "Sat", students: 40, ai: 15 },
];

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
        { label: "Total Students", value: dashboard?.total_students ?? 0, icon: Users, color: "var(--primary)", suffix: "" },
        { label: "Active Today", value: dashboard?.active_today ?? 0, icon: Activity, color: "var(--success)", suffix: "" },
        { label: "AI Queries Today", value: dashboard?.ai_queries_today ?? 0, icon: Bot, color: "var(--accent-purple)", suffix: "" },
        { label: "Avg Attendance", value: dashboard?.avg_attendance ?? 0, icon: CalendarCheck, color: "var(--success)", suffix: "%" },
        { label: "Avg Performance", value: dashboard?.avg_performance ?? 0, icon: Award, color: "var(--warning)", suffix: "%" },
        { label: "Open Complaints", value: dashboard?.open_complaints ?? 0, icon: MessageSquare, color: "var(--error)", suffix: "" },
    ];

    // Queue health pie chart
    const queueData = [
        { name: "Pending", value: dashboard?.queue_pending_depth ?? 0, color: "#f59e0b" },
        { name: "Processing", value: dashboard?.queue_processing_depth ?? 0, color: "#3b82f6" },
        { name: "Stuck", value: dashboard?.queue_stuck_jobs ?? 0, color: "#ef4444" },
    ].filter(d => d.value > 0);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Admin Dashboard</h1>
                <p className="text-sm text-[var(--text-secondary)]">Institutional overview</p>
            </div>

            <RoleStartPanel role="admin" />

            {error && (
                <div className="mb-6 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                    {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
                </div>
            ) : (
                <>
                    {/* ─── Glass KPI Cards ─── */}
                    <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4 mb-6">
                        {kpis.map((kpi, i) => (
                            <div key={kpi.label} className={`glass-stat ${glassColors[i]} stagger-${i + 1}`}>
                                <div className="flex items-center justify-between mb-2">
                                    <kpi.icon className="w-4 h-4" style={{ color: kpi.color }} />
                                </div>
                                <p className="text-2xl font-bold text-[var(--text-primary)]">
                                    <AnimatedCounter value={kpi.value} suffix={kpi.suffix} />
                                </p>
                                <p className="text-[10px] text-[var(--text-muted)] mt-1 uppercase tracking-wider">{kpi.label}</p>
                            </div>
                        ))}
                    </div>

                    {/* ─── Charts Row ─── */}
                    <div className="grid md:grid-cols-2 gap-6 mb-6">
                        {/* Weekly Activity Bar Chart */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] card-hover">
                            <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">📊 Weekly Activity</h2>
                            <div className="h-44">
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={weeklyActivity}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
                                        <XAxis dataKey="day" tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                        <YAxis tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                        <Tooltip
                                            contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                                            labelStyle={{ color: "var(--text-primary)", fontWeight: 600 }}
                                        />
                                        <Bar dataKey="students" name="Students" fill="#3b82f6" radius={[3, 3, 0, 0]} />
                                        <Bar dataKey="ai" name="AI Queries" fill="#8b5cf6" radius={[3, 3, 0, 0]} />
                                    </BarChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Queue Health */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] card-hover">
                            <div className="flex items-center gap-2 mb-4">
                                <Workflow className="w-4 h-4 text-[var(--primary)]" />
                                <h2 className="text-sm font-semibold text-[var(--text-primary)]">Queue Health</h2>
                            </div>
                            <div className="flex items-center gap-6">
                                <div className="w-28 h-28">
                                    {queueData.length > 0 ? (
                                        <ResponsiveContainer width="100%" height="100%">
                                            <PieChart>
                                                <Pie data={queueData} cx="50%" cy="50%" innerRadius={30} outerRadius={50} dataKey="value" paddingAngle={3}>
                                                    {queueData.map((d, i) => (
                                                        <Cell key={i} fill={d.color} />
                                                    ))}
                                                </Pie>
                                                <Tooltip contentStyle={{ fontSize: 11 }} />
                                            </PieChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <ProgressRing value={100} color="var(--success)" size={112} strokeWidth={8}>
                                            <span className="text-xs font-bold text-[var(--success)]">✓</span>
                                        </ProgressRing>
                                    )}
                                </div>
                                <div className="space-y-2 flex-1">
                                    <div className="flex justify-between text-xs">
                                        <span className="text-[var(--text-muted)]">Pending</span>
                                        <span className="font-bold text-amber-500">{dashboard?.queue_pending_depth ?? 0}</span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                        <span className="text-[var(--text-muted)]">Processing</span>
                                        <span className="font-bold text-blue-500">{dashboard?.queue_processing_depth ?? 0}</span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                        <span className="text-[var(--text-muted)]">Failure Rate</span>
                                        <span className="font-bold text-[var(--error)]">{dashboard?.queue_failure_rate_pct ?? 0}%</span>
                                    </div>
                                    <div className="flex justify-between text-xs">
                                        <span className="text-[var(--text-muted)]">Stuck Jobs</span>
                                        <span className="font-bold text-[var(--error)]">{dashboard?.queue_stuck_jobs ?? 0}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* ─── Alerts + Security ─── */}
                    <div className="grid lg:grid-cols-2 gap-6">
                        {/* Active Alerts */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center justify-between mb-4">
                                <div className="flex items-center gap-2">
                                    <AlertTriangle className="w-4 h-4 text-[var(--warning)]" />
                                    <h2 className="text-sm font-semibold text-[var(--text-primary)]">Active Alerts</h2>
                                </div>
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
                                    className="rounded-full bg-warning-badge dark:bg-amber-900/20 px-3 py-1 text-xs font-medium text-status-amber dark:text-amber-400 hover-error-subtle dark:hover:bg-amber-900/40 disabled:opacity-60 transition-colors"
                                    disabled={dispatchingAlerts || (dashboard?.observability_alerts?.length ?? 0) === 0}
                                >
                                    {dispatchingAlerts ? "Dispatching..." : "Dispatch Alerts"}
                                </button>
                            </div>
                            <div className="space-y-2">
                                {(dashboard?.observability_alerts || []).slice(0, 5).map((alert) => (
                                    <div key={alert.code} className="rounded-lg border border-amber-200 dark:border-amber-900/30 bg-warning-subtle dark:bg-amber-900/10 p-3">
                                        <div className="flex items-center justify-between gap-3">
                                            <p className="text-xs font-medium text-[var(--text-primary)]">{alert.message}</p>
                                            <span className={`text-[10px] uppercase tracking-wide font-semibold px-2 py-0.5 rounded-full ${
                                                alert.severity === "critical"
                                                    ? "bg-error-badge text-status-red dark:bg-red-900/20 dark:text-red-400"
                                                    : "bg-warning-badge text-status-amber dark:bg-amber-900/20 dark:text-amber-400"
                                            }`}>
                                                {alert.severity}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                                {(dashboard?.observability_alerts?.length ?? 0) === 0 && (
                                    <div className="py-6 text-center">
                                        <AlertTriangle className="w-8 h-8 mx-auto text-[var(--text-muted)] mb-2 opacity-30" />
                                        <p className="text-xs text-[var(--text-muted)]">No active alerts — all systems healthy.</p>
                                    </div>
                                )}
                                <div className="pt-1">
                                    <Link href="/admin/traces" className="text-xs text-[var(--primary)] hover:underline">
                                        Open Trace Viewer →
                                    </Link>
                                </div>
                            </div>
                        </div>

                        {/* Recent Security Activity */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center gap-2 mb-4">
                                <Shield className="w-4 h-4 text-[var(--primary)]" />
                                <h2 className="text-sm font-semibold text-[var(--text-primary)]">Security Activity</h2>
                            </div>
                            <div className="space-y-2">
                                {activity.slice(0, 6).map((item) => (
                                    <div key={item.id} className="flex items-center justify-between p-2.5 rounded-lg bg-[var(--bg-page)] card-hover">
                                        <div>
                                            <p className="text-xs font-medium text-[var(--text-primary)]">{item.action}</p>
                                            <p className="text-[10px] text-[var(--text-muted)]">by {item.user}</p>
                                        </div>
                                        <span className="text-[10px] text-[var(--text-muted)]">
                                            {new Date(item.date).toLocaleString()}
                                        </span>
                                    </div>
                                ))}
                                {activity.length === 0 && (
                                    <div className="py-6 text-center">
                                        <Shield className="w-8 h-8 mx-auto text-[var(--text-muted)] mb-2 opacity-30" />
                                        <p className="text-xs text-[var(--text-muted)]">No security events recorded.</p>
                                    </div>
                                )}
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
