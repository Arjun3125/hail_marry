"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
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
    MessageSquareDashed,
    RefreshCw,
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
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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

type WhatsAppReleaseGateSnapshot = {
    generated_at: string;
    period_days: number;
    analytics: {
        total_messages: number;
        inbound: number;
        outbound: number;
        unique_users: number;
        avg_latency_ms: number | null;
    };
    release_gate_metrics: {
        duplicate_inbound_total: number;
        routing_failure_total: number;
        visible_failure_total: number;
        outbound_retryable_failure_total: number;
        upload_ingest_failure_total: number;
        link_ingest_failure_total: number;
    };
    derived_rates: {
        duplicate_inbound_pct: number;
        routing_failure_pct: number;
        visible_failure_pct: number;
        outbound_retryable_failure_pct: number;
    };
};

type MascotReleaseGateSnapshot = {
    generated_at: string;
    period_days: number;
    analytics: {
        total_actions: number;
        unique_users: number;
    };
    release_gate_metrics: {
        interpretation_success_total: number;
        interpretation_failure_total: number;
        execution_success_total: number;
        execution_failure_total: number;
        confirmation_success_total: number;
        confirmation_failure_total: number;
        confirmation_cancelled_total?: number;
        upload_success_total: number;
        upload_failure_total: number;
    };
    derived_rates: {
        interpretation_failure_pct: number;
        execution_failure_pct: number;
        upload_failure_pct: number;
        confirmation_failure_pct: number;
        overall_failure_pct: number;
    };
    active_alerts: Array<{
        code: string;
        severity: string;
        message: string;
    }>;
};

type MascotReleaseGateEvidence = {
    generated_at: string;
    filename: string;
    markdown: string;
    snapshot: MascotReleaseGateSnapshot;
};
type MascotStagingPacket = {
    generated_at: string;
    filename: string;
    markdown: string;
    whatsapp_snapshot: WhatsAppReleaseGateSnapshot;
    mascot_snapshot: MascotReleaseGateSnapshot;
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
    const [whatsappSnapshot, setWhatsappSnapshot] = useState<WhatsAppReleaseGateSnapshot | null>(null);
    const [mascotSnapshot, setMascotSnapshot] = useState<MascotReleaseGateSnapshot | null>(null);
    const [loading, setLoading] = useState(true);
    const [dispatchingAlerts, setDispatchingAlerts] = useState(false);
    const [refreshingWhatsApp, setRefreshingWhatsApp] = useState(false);
    const [copyingMascotEvidence, setCopyingMascotEvidence] = useState(false);
    const [copyingStagingPacket, setCopyingStagingPacket] = useState(false);
    const [mascotEvidenceStatus, setMascotEvidenceStatus] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [chartsReady, setChartsReady] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const [dashboardData, securityData, whatsappData, mascotData] = await Promise.all([
                api.admin.dashboard(),
                api.admin.security(),
                api.admin.whatsappReleaseGateSnapshot(7),
                api.admin.mascotReleaseGateSnapshot(7),
            ]);
            setDashboard(dashboardData as DashboardData);
            setActivity((securityData || []) as SecurityItem[]);
            setWhatsappSnapshot(whatsappData as WhatsAppReleaseGateSnapshot);
            setMascotSnapshot(mascotData as MascotReleaseGateSnapshot);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load admin dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    const refreshWhatsAppSnapshot = useCallback(async () => {
        try {
            setRefreshingWhatsApp(true);
            setError(null);
            const payload = await api.admin.whatsappReleaseGateSnapshot(7);
            setWhatsappSnapshot(payload as WhatsAppReleaseGateSnapshot);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to refresh WhatsApp release gate snapshot");
        } finally {
            setRefreshingWhatsApp(false);
        }
    }, []);

    const copyText = useCallback(async (text: string) => {
        if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text);
            return;
        }
        if (typeof document !== "undefined") {
            const textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.setAttribute("readonly", "true");
            textarea.style.position = "absolute";
            textarea.style.left = "-9999px";
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);
        }
    }, []);

    const copyMascotEvidenceDraft = useCallback(async () => {
        try {
            setCopyingMascotEvidence(true);
            setMascotEvidenceStatus(null);
            const payload = await api.admin.mascotReleaseGateEvidence(7) as MascotReleaseGateEvidence;
            await copyText(payload.markdown);
            setMascotEvidenceStatus(`Evidence draft copied from ${new Date(payload.generated_at).toLocaleString()}.`);
        } catch (err) {
            setMascotEvidenceStatus(err instanceof Error ? err.message : "Failed to copy mascot evidence draft");
        } finally {
            setCopyingMascotEvidence(false);
        }
    }, [copyText]);

    const copyCombinedStagingPacket = useCallback(async () => {
        try {
            setCopyingStagingPacket(true);
            setMascotEvidenceStatus(null);
            const payload = await api.admin.mascotStagingPacket(7) as MascotStagingPacket;
            await copyText(payload.markdown);
            setMascotEvidenceStatus(`Combined mascot + WhatsApp staging packet copied from ${new Date(payload.generated_at).toLocaleString()}.`);
        } catch (err) {
            setMascotEvidenceStatus(err instanceof Error ? err.message : "Failed to copy combined staging packet");
        } finally {
            setCopyingStagingPacket(false);
        }
    }, [copyText]);

    useEffect(() => {
        void load();
    }, [load]);

    useEffect(() => {
        setChartsReady(true);
    }, []);

    const kpis = [
        { label: "Total Students", value: dashboard?.total_students ?? 0, icon: Users, color: "var(--primary)", suffix: "" },
        { label: "Active Today", value: dashboard?.active_today ?? 0, icon: Activity, color: "var(--success)", suffix: "" },
        { label: "AI Queries Today", value: dashboard?.ai_queries_today ?? 0, icon: Bot, color: "var(--accent-purple)", suffix: "" },
        { label: "Avg Attendance", value: dashboard?.avg_attendance ?? 0, icon: CalendarCheck, color: "var(--success)", suffix: "%" },
        { label: "Avg Performance", value: dashboard?.avg_performance ?? 0, icon: Award, color: "var(--warning)", suffix: "%" },
        { label: "Open Complaints", value: dashboard?.open_complaints ?? 0, icon: MessageSquare, color: "var(--error)", suffix: "" },
    ];

    const onboardingChecklist = [
        { id: "setup", label: "Complete setup wizard" },
        { id: "users", label: "Verify classes and users" },
        { id: "health", label: "Review security and queue health" },
    ];

    const taskFirstLinks = [
        { label: "Continue setup wizard", href: "/admin/setup-wizard", priority: "high" as const },
        { label: "Manage users", href: "/admin/users", priority: "medium" as const },
        { label: "Check queue dashboard", href: "/admin/queue", priority: "low" as const },
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
                                {chartsReady ? (
                                    <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={160}>
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
                                ) : (
                                    <div className="h-full rounded-[var(--radius-sm)] bg-[var(--bg-page)]" />
                                )}
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
                                    {queueData.length > 0 && chartsReady ? (
                                        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={160}>
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

                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-6">
                        <div className="flex items-start justify-between gap-4 mb-4">
                            <div className="flex items-center gap-2">
                                <MessageSquareDashed className="w-4 h-4 text-[var(--success)]" />
                                <div>
                                    <h2 className="text-sm font-semibold text-[var(--text-primary)]">WhatsApp Release Gate</h2>
                                    <p className="text-xs text-[var(--text-muted)]">
                                        Staging evidence snapshot for the last 7 days. Live device validation is still required before final sign-off.
                                    </p>
                                </div>
                            </div>
                            <button
                                type="button"
                                onClick={() => void refreshWhatsAppSnapshot()}
                                className="inline-flex items-center gap-2 rounded-full bg-success-badge px-3 py-1 text-xs font-medium text-status-green hover:opacity-90 disabled:opacity-60"
                                disabled={refreshingWhatsApp}
                            >
                                <RefreshCw className={`w-3.5 h-3.5 ${refreshingWhatsApp ? "animate-spin" : ""}`} />
                                {refreshingWhatsApp ? "Refreshing..." : "Refresh Snapshot"}
                            </button>
                        </div>
                        {whatsappSnapshot ? (
                            <div className="grid gap-4 lg:grid-cols-2">
                                <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-4">
                                    <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-3">Derived Failure Rates</p>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Routing failure</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.derived_rates.routing_failure_pct}%</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Duplicate inbound</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.derived_rates.duplicate_inbound_pct}%</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Visible failure</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.derived_rates.visible_failure_pct}%</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Retryable outbound failure</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.derived_rates.outbound_retryable_failure_pct}%</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-4">
                                    <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-3">Current Snapshot</p>
                                    <div className="grid grid-cols-2 gap-3 text-sm">
                                        <div>
                                            <p className="text-[var(--text-muted)]">Messages</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.analytics.total_messages}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Unique users</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.analytics.unique_users}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Upload ingest failures</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.release_gate_metrics.upload_ingest_failure_total}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Link ingest failures</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.release_gate_metrics.link_ingest_failure_total}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Visible failures</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{whatsappSnapshot.release_gate_metrics.visible_failure_total}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Avg latency</p>
                                            <p className="font-semibold text-[var(--text-primary)]">
                                                {whatsappSnapshot.analytics.avg_latency_ms !== null ? `${whatsappSnapshot.analytics.avg_latency_ms} ms` : "N/A"}
                                            </p>
                                        </div>
                                    </div>
                                    <p className="mt-4 text-xs text-[var(--text-muted)]">
                                        Snapshot generated {new Date(whatsappSnapshot.generated_at).toLocaleString()}.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <p className="text-sm text-[var(--text-muted)]">WhatsApp release-gate snapshot unavailable.</p>
                        )}
                    </div>

                    {/* ─── Alerts + Security ─── */}
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-6">
                        <div className="flex items-start justify-between gap-4 mb-4">
                            <div className="flex items-center gap-2">
                                <Bot className="w-4 h-4 text-[var(--primary)]" />
                                <div>
                                    <h2 className="text-sm font-semibold text-[var(--text-primary)]">Mascot Release Gate</h2>
                                    <p className="text-xs text-[var(--text-muted)]">
                                        Snapshot for mascot interpretation, execution, upload reliability, and confirmation stability.
                                    </p>
                                </div>
                            </div>
                            <div className="flex flex-wrap items-center justify-end gap-2">
                                <button
                                    type="button"
                                    onClick={() => void copyMascotEvidenceDraft()}
                                    className="inline-flex items-center gap-2 rounded-full bg-primary-ghost px-3 py-1 text-xs font-medium text-[var(--primary)] hover:opacity-90 disabled:opacity-60"
                                    disabled={copyingMascotEvidence}
                                >
                                    <Bot className="w-3.5 h-3.5" />
                                    {copyingMascotEvidence ? "Copying..." : "Copy Evidence Draft"}
                                </button>
                                <button
                                    type="button"
                                    onClick={() => void copyCombinedStagingPacket()}
                                    className="inline-flex items-center gap-2 rounded-full bg-success-badge px-3 py-1 text-xs font-medium text-status-green hover:opacity-90 disabled:opacity-60"
                                    disabled={copyingStagingPacket}
                                >
                                    <MessageSquareDashed className="w-3.5 h-3.5" />
                                    {copyingStagingPacket ? "Copying..." : "Copy Staging Packet"}
                                </button>
                            </div>
                        </div>
                        {mascotSnapshot ? (
                            <div className="grid gap-4 lg:grid-cols-2">
                                <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-4">
                                    <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-3">Derived Failure Rates</p>
                                    <div className="space-y-2 text-sm">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Interpretation</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.derived_rates.interpretation_failure_pct}%</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Execution</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.derived_rates.execution_failure_pct}%</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Upload</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.derived_rates.upload_failure_pct}%</span>
                                        </div>
                                        <div className="flex items-center justify-between">
                                            <span className="text-[var(--text-secondary)]">Overall failure</span>
                                            <span className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.derived_rates.overall_failure_pct}%</span>
                                        </div>
                                    </div>
                                </div>
                                <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-4">
                                    <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-3">Current Snapshot</p>
                                    <div className="grid grid-cols-2 gap-3 text-sm">
                                        <div>
                                            <p className="text-[var(--text-muted)]">Actions</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.analytics.total_actions}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Unique users</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.analytics.unique_users}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Execution failures</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.release_gate_metrics.execution_failure_total}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Upload failures</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.release_gate_metrics.upload_failure_total}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Confirmation cancelled</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.release_gate_metrics.confirmation_cancelled_total ?? 0}</p>
                                        </div>
                                        <div>
                                            <p className="text-[var(--text-muted)]">Active alerts</p>
                                            <p className="font-semibold text-[var(--text-primary)]">{mascotSnapshot.active_alerts.length}</p>
                                        </div>
                                    </div>
                                    <p className="mt-4 text-xs text-[var(--text-muted)]">
                                        Snapshot generated {new Date(mascotSnapshot.generated_at).toLocaleString()}.
                                    </p>
                                </div>
                            </div>
                        ) : (
                            <p className="text-sm text-[var(--text-muted)]">Mascot release-gate snapshot unavailable.</p>
                        )}
                        {mascotEvidenceStatus ? (
                            <p className="mt-3 text-xs text-[var(--text-muted)]">{mascotEvidenceStatus}</p>
                        ) : null}
                    </div>

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
