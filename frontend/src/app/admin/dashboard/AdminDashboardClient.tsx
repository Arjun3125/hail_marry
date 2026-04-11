"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { AlertTriangle, Bot, CalendarCheck, MessageSquare, MessageSquareDashed, RefreshCw, Shield, Users, Workflow } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { RoleMorningBriefing } from "@/components/RoleMorningBriefing";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection, PrismSectionHeader } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type DashboardData = {
    total_students: number;
    total_teachers: number;
    total_parents: number;
    active_today: number;
    ai_queries_today: number;
    avg_attendance: number;
    avg_performance: number;
    open_complaints: number;
    queue_pending_depth: number;
    queue_processing_depth: number;
    queue_failure_rate_pct: number;
    queue_stuck_jobs: number;
    observability_alerts: Array<{ code: string; severity: string; message: string }>;
    student_risk_summary: { high_risk_students: number; medium_risk_students: number; academic_high_risk: number; fee_high_risk: number };
    student_risk_alerts: Array<{ student_id: string; student_name: string; class_name: string; dropout_risk: string; academic_risk: string; fee_risk: string; attendance_pct: number; overall_score_pct: number | null }>;
    monthly_trends: Array<{ month: string; active_users: number; ai_queries: number; complaints_resolved: number; attendance_pct: number; average_marks: number }>;
    complaint_health: { resolution_rate_pct: number };
    latest_milestones: { last_ai_query_at: string | null; last_complaint_at: string | null; last_resolved_complaint_at: string | null; last_attendance_marked_at: string | null };
};
type SecurityItem = { id: string; user: string; action: string; date: string };
type WhatsAppReleaseGateSnapshot = { analytics: { total_messages: number; unique_users: number }; derived_rates: { visible_failure_pct: number; routing_failure_pct: number; duplicate_inbound_pct: number; outbound_retryable_failure_pct: number } };
type MascotReleaseGateSnapshot = { analytics: { total_actions: number; unique_users: number }; derived_rates: { interpretation_failure_pct: number; execution_failure_pct: number; upload_failure_pct: number; overall_failure_pct: number } };
type MascotReleaseGateEvidence = { generated_at: string; markdown: string };
type MascotStagingPacket = { generated_at: string; markdown: string };
type AdminDashboardBootstrap = { dashboard?: unknown; security?: unknown; whatsapp_snapshot?: unknown; mascot_snapshot?: unknown };

const EMPTY: DashboardData = {
    total_students: 0, total_teachers: 0, total_parents: 0, active_today: 0, ai_queries_today: 0, avg_attendance: 0, avg_performance: 0, open_complaints: 0,
    queue_pending_depth: 0, queue_processing_depth: 0, queue_failure_rate_pct: 0, queue_stuck_jobs: 0, observability_alerts: [],
    student_risk_summary: { high_risk_students: 0, medium_risk_students: 0, academic_high_risk: 0, fee_high_risk: 0 }, student_risk_alerts: [],
    monthly_trends: [], complaint_health: { resolution_rate_pct: 0 }, latest_milestones: { last_ai_query_at: null, last_complaint_at: null, last_resolved_complaint_at: null, last_attendance_marked_at: null },
};

function normalizeDashboardData(payload: unknown): DashboardData {
    if (!payload || typeof payload !== "object") return EMPTY;
    const candidate = payload as Partial<DashboardData>;
    return {
        total_students: candidate.total_students ?? 0,
        total_teachers: candidate.total_teachers ?? 0,
        total_parents: candidate.total_parents ?? 0,
        active_today: candidate.active_today ?? 0,
        ai_queries_today: candidate.ai_queries_today ?? 0,
        avg_attendance: candidate.avg_attendance ?? 0,
        avg_performance: candidate.avg_performance ?? 0,
        open_complaints: candidate.open_complaints ?? 0,
        queue_pending_depth: candidate.queue_pending_depth ?? 0,
        queue_processing_depth: candidate.queue_processing_depth ?? 0,
        queue_failure_rate_pct: candidate.queue_failure_rate_pct ?? 0,
        queue_stuck_jobs: candidate.queue_stuck_jobs ?? 0,
        observability_alerts: candidate.observability_alerts ?? [],
        student_risk_summary: {
            high_risk_students: candidate.student_risk_summary?.high_risk_students ?? 0,
            medium_risk_students: candidate.student_risk_summary?.medium_risk_students ?? 0,
            academic_high_risk: candidate.student_risk_summary?.academic_high_risk ?? 0,
            fee_high_risk: candidate.student_risk_summary?.fee_high_risk ?? 0,
        },
        student_risk_alerts: candidate.student_risk_alerts ?? [],
        monthly_trends: candidate.monthly_trends ?? [],
        complaint_health: { resolution_rate_pct: candidate.complaint_health?.resolution_rate_pct ?? 0 },
        latest_milestones: {
            last_ai_query_at: candidate.latest_milestones?.last_ai_query_at ?? null,
            last_complaint_at: candidate.latest_milestones?.last_complaint_at ?? null,
            last_resolved_complaint_at: candidate.latest_milestones?.last_resolved_complaint_at ?? null,
            last_attendance_marked_at: candidate.latest_milestones?.last_attendance_marked_at ?? null,
        },
    };
}

function formatDateTime(value: string | null) {
    if (!value) return "No data";
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function getRiskPillPresentation(value: string | null | undefined) {
    switch ((value ?? "").toLowerCase()) {
        case "high": return "bg-error-subtle text-status-red";
        case "medium": return "bg-warning-subtle text-status-amber";
        case "low": return "bg-success-subtle text-status-green";
        default: return "border border-[var(--border)] bg-[var(--bg-page)] text-[var(--text-muted)]";
    }
}

export function AdminDashboardClient({ initialData = null }: { initialData?: AdminDashboardBootstrap | null }) {
    const [dashboard, setDashboard] = useState<DashboardData | null>(normalizeDashboardData(initialData?.dashboard));
    const [activity, setActivity] = useState<SecurityItem[]>(Array.isArray(initialData?.security) ? (initialData?.security as SecurityItem[]) : []);
    const [whatsappSnapshot, setWhatsappSnapshot] = useState<WhatsAppReleaseGateSnapshot | null>((initialData?.whatsapp_snapshot || null) as WhatsAppReleaseGateSnapshot | null);
    const [mascotSnapshot, setMascotSnapshot] = useState<MascotReleaseGateSnapshot | null>((initialData?.mascot_snapshot || null) as MascotReleaseGateSnapshot | null);
    const [loading, setLoading] = useState(!initialData);
    const [error, setError] = useState<string | null>(null);
    const [refreshingWhatsApp, setRefreshingWhatsApp] = useState(false);
    const [dispatchingAlerts, setDispatchingAlerts] = useState(false);
    const [copyingMascotEvidence, setCopyingMascotEvidence] = useState(false);
    const [copyingStagingPacket, setCopyingStagingPacket] = useState(false);
    const [mascotEvidenceStatus, setMascotEvidenceStatus] = useState<string | null>(null);
    const [lastLiveRefreshAt, setLastLiveRefreshAt] = useState<string | null>(null);

    const load = useCallback(async (options?: { silent?: boolean }) => {
        try {
            if (!options?.silent) setLoading(true);
            setError(null);
            const payload = await api.admin.dashboardBootstrap();
            setDashboard(normalizeDashboardData(payload?.dashboard));
            setActivity(Array.isArray(payload?.security) ? (payload.security as SecurityItem[]) : []);
            setWhatsappSnapshot((payload?.whatsapp_snapshot || null) as WhatsAppReleaseGateSnapshot | null);
            setMascotSnapshot((payload?.mascot_snapshot || null) as MascotReleaseGateSnapshot | null);
            setLastLiveRefreshAt(new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }));
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load admin dashboard");
        } finally {
            if (!options?.silent) setLoading(false);
        }
    }, []);

    useEffect(() => {
        if (!initialData) void load();
    }, [initialData, load]);

    useEffect(() => {
        const id = window.setInterval(() => {
            void load({ silent: true });
        }, 60_000);
        return () => window.clearInterval(id);
    }, [load]);

    const copyText = useCallback(async (text: string) => {
        if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) await navigator.clipboard.writeText(text);
    }, []);

    const refreshWhatsAppSnapshot = useCallback(async () => {
        try {
            setRefreshingWhatsApp(true);
            setWhatsappSnapshot(await api.admin.whatsappReleaseGateSnapshot(7) as WhatsAppReleaseGateSnapshot);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to refresh WhatsApp release gate snapshot");
        } finally {
            setRefreshingWhatsApp(false);
        }
    }, []);

    const dispatchAlerts = useCallback(async () => {
        try {
            setDispatchingAlerts(true);
            await api.admin.dispatchObservabilityAlerts();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to dispatch alerts");
        } finally {
            setDispatchingAlerts(false);
        }
    }, []);

    const copyMascotEvidenceDraft = useCallback(async () => {
        try {
            setCopyingMascotEvidence(true);
            const payload = await api.admin.mascotReleaseGateEvidence(7) as MascotReleaseGateEvidence;
            await copyText(payload.markdown);
            setMascotEvidenceStatus(`Mascot evidence copied from ${new Date(payload.generated_at).toLocaleString()}.`);
        } catch (err) {
            setMascotEvidenceStatus(err instanceof Error ? err.message : "Failed to copy mascot evidence draft");
        } finally {
            setCopyingMascotEvidence(false);
        }
    }, [copyText]);

    const copyCombinedStagingPacket = useCallback(async () => {
        try {
            setCopyingStagingPacket(true);
            const payload = await api.admin.mascotStagingPacket(7) as MascotStagingPacket;
            await copyText(payload.markdown);
            setMascotEvidenceStatus(`Combined staging packet copied from ${new Date(payload.generated_at).toLocaleString()}.`);
        } catch (err) {
            setMascotEvidenceStatus(err instanceof Error ? err.message : "Failed to copy combined staging packet");
        } finally {
            setCopyingStagingPacket(false);
        }
    }, [copyText]);

    const health = useMemo(() => {
        const activeRatio = dashboard?.total_students ? Math.round(((dashboard.active_today ?? 0) / dashboard.total_students) * 100) : 0;
        const queueReliability = Math.max(0, Math.min(100, Math.round(100 - (dashboard?.queue_failure_rate_pct ?? 0) * 4 - (dashboard?.queue_stuck_jobs ?? 0) * 6)));
        const score = Math.round(((dashboard?.avg_attendance ?? 0) * 0.35) + ((dashboard?.avg_performance ?? 0) * 0.25) + ((dashboard?.complaint_health?.resolution_rate_pct ?? 0) * 0.15) + (activeRatio * 0.15) + (queueReliability * 0.1));
        const label = score >= 80 ? "Good" : score >= 65 ? "Watch" : "Urgent";
        return { score, label, activeRatio, queueReliability };
    }, [dashboard]);

    const recentTrend = useMemo(() => [...(dashboard?.monthly_trends || [])].slice(-4).reverse(), [dashboard?.monthly_trends]);
    const briefingFacts = useMemo(() => [
        `${dashboard?.avg_attendance ?? 0}% average attendance`,
        `${dashboard?.open_complaints ?? 0} open complaint${dashboard?.open_complaints === 1 ? "" : "s"}`,
        `${dashboard?.ai_queries_today ?? 0} AI quer${dashboard?.ai_queries_today === 1 ? "y" : "ies"} today`,
        `${dashboard?.student_risk_summary?.high_risk_students ?? 0} high-risk learner${dashboard?.student_risk_summary?.high_risk_students === 1 ? "" : "s"}`,
        `${dashboard?.observability_alerts?.length ?? 0} active alert${dashboard?.observability_alerts?.length === 1 ? "" : "s"}`,
    ], [dashboard]);
    const briefingFallback = useMemo(() => [
        `${dashboard?.avg_attendance ?? 0}% attendance so far today.`,
        `${dashboard?.open_complaints ?? 0} complaint${dashboard?.open_complaints === 1 ? "" : "s"} pending review.`,
        `${dashboard?.student_risk_summary?.high_risk_students ?? 0} learner${dashboard?.student_risk_summary?.high_risk_students === 1 ? "" : "s"} need high-priority intervention.`,
    ], [dashboard]);

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro kicker={<PrismHeroKicker><Shield className="h-3.5 w-3.5" />Admin command center</PrismHeroKicker>} title="See school health in one screen before you drill down" description="The admin home now leads with control: one health score, today&apos;s attendance, complaint load, and AI usage, then the supporting operational evidence underneath." />
                {error ? <ErrorRemediation error={error} scope="admin-dashboard" onRetry={() => void load()} /> : null}
                {!loading && dashboard ? <RoleMorningBriefing role="admin" facts={briefingFacts} fallback={briefingFallback} /> : null}
                {loading ? <PrismPanel className="p-8 text-sm text-[var(--text-secondary)]">Loading institutional overview...</PrismPanel> : (
                    <>
                        <div className="grid gap-4 xl:grid-cols-[1.18fr_0.82fr]">
                            <PrismPanel className="p-6">
                                <p className="prism-status-label">School health</p>
                                <div className="mt-4 flex items-end gap-4">
                                    <p className="text-6xl font-black text-[var(--text-primary)]">{health.score}</p>
                                    <span className={`mb-2 rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${health.label === "Good" ? "bg-success-subtle text-status-green" : health.label === "Watch" ? "bg-warning-subtle text-status-amber" : "bg-error-subtle text-status-red"}`}>{health.label}</span>
                                </div>
                                <p className="mt-4 max-w-2xl text-sm leading-7 text-[var(--text-secondary)]">This score blends attendance, academic performance, complaint resolution, daily activity, and queue reliability so an owner can judge institutional stability immediately.</p>
                                <div className="mt-6 grid gap-3 md:grid-cols-2 xl:grid-cols-4">
                                    <HeroMetric icon={CalendarCheck} label="Attendance today" value={`${dashboard?.avg_attendance ?? 0}%`} detail="Across marked classes" />
                                    <HeroMetric icon={MessageSquare} label="Pending complaints" value={`${dashboard?.open_complaints ?? 0}`} detail="Still open right now" />
                                    <HeroMetric icon={Bot} label="AI usage today" value={`${dashboard?.ai_queries_today ?? 0}`} detail="Institution-wide queries" />
                                    <HeroMetric icon={Users} label="Students active" value={`${dashboard?.active_today ?? 0}`} detail={`${health.activeRatio}% of learners`} />
                                </div>
                            </PrismPanel>
                            <PrismPanel className="p-6">
                                <PrismSectionHeader title="Since yesterday" description="A small live layer makes the platform feel like an operating system, not a static report." />
                                <div className="mt-4 space-y-3">
                                    <InfoLine label="Last attendance update" value={formatDateTime(dashboard?.latest_milestones?.last_attendance_marked_at ?? null)} />
                                    <InfoLine label="Last AI query" value={formatDateTime(dashboard?.latest_milestones?.last_ai_query_at ?? null)} />
                                    <InfoLine label="Last complaint change" value={formatDateTime(dashboard?.latest_milestones?.last_resolved_complaint_at || dashboard?.latest_milestones?.last_complaint_at || null)} />
                                </div>
                            </PrismPanel>
                        </div>

                        <div className="prism-status-strip">
                            <StatusTile label="Classes in session" value={`${dashboard?.latest_milestones?.last_attendance_marked_at ? 1 : 0}`} detail="Inferred from attendance activity in the live operations window." />
                            <StatusTile label="Teachers online" value={`${dashboard?.total_teachers ?? 0}`} detail="Provisioned staff scope until presence telemetry is connected." />
                            <StatusTile label="Students active" value={`${dashboard?.active_today ?? 0}`} detail={lastLiveRefreshAt ? `Live strip refreshed at ${lastLiveRefreshAt}.` : "Auto-refreshes every 60 seconds."} />
                            <StatusTile label="Reliability" value={`${health.queueReliability}%`} detail="Queue reliability after failures and stuck jobs are weighted in." />
                            <StatusTile label="Live alerts" value={`${dashboard?.observability_alerts?.length ?? 0}`} detail="Operational issues visible to admin right now." />
                        </div>

                        <div className="grid gap-6 xl:grid-cols-3">
                            <PrismPanel className="p-5">
                                <PrismSectionHeader title="Pending actions" description="What still needs owner attention." />
                                <div className="mt-4 space-y-3">
                                    <FeedRow title="Complaints waiting" detail="Open concerns still visible to students or parents." href="/admin/complaints" value={`${dashboard?.open_complaints ?? 0}`} />
                                    <FeedRow title="Alerts to review" detail="Operational issues most likely to erode trust." href="/admin/security" value={`${dashboard?.observability_alerts?.length ?? 0}`} />
                                    <FeedRow title="High-risk learners" detail="Students who need intervention before the next slip compounds." href="/admin/reports" value={`${dashboard?.student_risk_summary?.high_risk_students ?? 0}`} />
                                    <FeedRow title="Queue backlog" detail="Deferred work waiting before the product fully catches up." href="/admin/queue" value={`${dashboard?.queue_pending_depth ?? 0}`} />
                                </div>
                            </PrismPanel>
                            <PrismPanel className="p-5">
                                <PrismSectionHeader title="Performance trend" description="Recent months without turning the home screen into an analytics wall." />
                                <div className="mt-4 space-y-3">
                                    {recentTrend.length > 0 ? recentTrend.map((item) => (
                                        <div key={item.month} className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4">
                                            <div className="flex items-center justify-between gap-3">
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{item.month}</p>
                                                <span className="text-xs text-[var(--text-muted)]">{item.active_users} active users</span>
                                            </div>
                                            <div className="mt-3 grid gap-2 sm:grid-cols-2">
                                                <MiniStat label="Attendance" value={`${item.attendance_pct}%`} />
                                                <MiniStat label="Average marks" value={`${item.average_marks}%`} />
                                                <MiniStat label="AI queries" value={`${item.ai_queries}`} />
                                                <MiniStat label="Complaints resolved" value={`${item.complaints_resolved}`} />
                                            </div>
                                        </div>
                                    )) : <EmptyState icon={Workflow} title="Trend data unavailable" description="Monthly institution trend data has not been recorded yet." eyebrow="No trend" />}
                                </div>
                            </PrismPanel>
                            <PrismPanel className="p-5">
                                <PrismSectionHeader title="Recent activity" description="Keep operational movement visible." actions={<button type="button" onClick={() => void dispatchAlerts()} className="prism-action-secondary" disabled={dispatchingAlerts || (dashboard?.observability_alerts?.length ?? 0) === 0}>{dispatchingAlerts ? "Dispatching..." : "Dispatch alerts"}</button>} />
                                <div className="mt-4 space-y-3">
                                    {activity.length > 0 ? activity.slice(0, 5).map((item) => (
                                        <div key={item.id} className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-4 py-3">
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{item.action}</p>
                                            <p className="mt-1 text-xs text-[var(--text-muted)]">by {item.user} · {new Date(item.date).toLocaleString()}</p>
                                        </div>
                                    )) : <EmptyState icon={Shield} title="No recent security events" description="Security activity will appear here when access or policy events are recorded." eyebrow="Quiet" />}
                                </div>
                            </PrismPanel>
                        </div>

                        <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Student risk radar" description="Who is drifting, why, and what the school should do next." actions={<Link href="/admin/reports" className="prism-action-secondary">Open reports</Link>} />
                                <div className="grid gap-3 sm:grid-cols-4">
                                    <MiniStat label="High risk" value={`${dashboard?.student_risk_summary?.high_risk_students ?? 0}`} />
                                    <MiniStat label="Medium risk" value={`${dashboard?.student_risk_summary?.medium_risk_students ?? 0}`} />
                                    <MiniStat label="Academic high risk" value={`${dashboard?.student_risk_summary?.academic_high_risk ?? 0}`} />
                                    <MiniStat label="Fee high risk" value={`${dashboard?.student_risk_summary?.fee_high_risk ?? 0}`} />
                                </div>
                                {dashboard?.student_risk_alerts?.length ? (
                                    <div className="space-y-3">
                                        {dashboard.student_risk_alerts.map((alert) => (
                                            <div key={alert.student_id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                                <div className="flex flex-wrap items-start justify-between gap-3">
                                                    <div>
                                                        <p className="text-sm font-semibold text-[var(--text-primary)]">{alert.student_name}</p>
                                                        <p className="text-xs text-[var(--text-muted)]">{alert.class_name}</p>
                                                    </div>
                                                    <div className="flex flex-wrap gap-2">
                                                        {([{ label: "Dropout", value: alert.dropout_risk }, { label: "Academic", value: alert.academic_risk }, { label: "Fee", value: alert.fee_risk }] as const).map((pill) => (
                                                            <span key={`${alert.student_id}-${pill.label}`} className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${getRiskPillPresentation(pill.value)}`}>{pill.label} {pill.value}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                                                    <MiniStat label="Attendance" value={`${alert.attendance_pct}%`} />
                                                    <MiniStat label="Performance" value={alert.overall_score_pct !== null ? `${alert.overall_score_pct}%` : "Not enough data"} />
                                                    <MiniStat label="Suggested focus" value={alert.fee_risk === "high" ? "Fee recovery" : alert.academic_risk === "high" ? "Academic intervention" : "Attendance follow-up"} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : <EmptyState icon={AlertTriangle} title="No active student risk alerts" description="No high-priority academic, attendance, or fee risk cases are currently flagged." eyebrow="Stable" />}
                            </PrismPanel>
                            <PrismPanel className="space-y-4 p-5">
                                <PrismSectionHeader title="Current alerts" description="Operational issues most likely to affect reliability or school trust." />
                                {(dashboard?.observability_alerts?.length ?? 0) > 0 ? (dashboard?.observability_alerts || []).slice(0, 5).map((alert, index) => (
                                    <div key={`${alert.code}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <p className="text-sm text-[var(--text-primary)]">{alert.message}</p>
                                            <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${alert.severity === "critical" ? "bg-error-subtle text-status-red" : "bg-warning-subtle text-status-amber"}`}>{alert.severity}</span>
                                        </div>
                                    </div>
                                )) : <EmptyState icon={AlertTriangle} title="No active alerts" description="The platform does not currently show any active observability alerts." eyebrow="Stable" />}
                            </PrismPanel>
                        </div>

                        <div className="grid gap-6 xl:grid-cols-2">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="WhatsApp release gate" description="Operational evidence stays below the hero layer but remains one click away." actions={<button type="button" onClick={() => void refreshWhatsAppSnapshot()} className="prism-action-secondary" disabled={refreshingWhatsApp}><RefreshCw className={`h-4 w-4 ${refreshingWhatsApp ? "animate-spin" : ""}`} />{refreshingWhatsApp ? "Refreshing..." : "Refresh snapshot"}</button>} />
                                {whatsappSnapshot ? <div className="grid gap-3 md:grid-cols-2"><MiniStat label="Total messages" value={`${whatsappSnapshot.analytics.total_messages}`} /><MiniStat label="Unique users" value={`${whatsappSnapshot.analytics.unique_users}`} /><MiniStat label="Visible failure" value={`${whatsappSnapshot.derived_rates.visible_failure_pct}%`} /><MiniStat label="Routing failure" value={`${whatsappSnapshot.derived_rates.routing_failure_pct}%`} /><MiniStat label="Duplicate inbound" value={`${whatsappSnapshot.derived_rates.duplicate_inbound_pct}%`} /><MiniStat label="Retryable outbound" value={`${whatsappSnapshot.derived_rates.outbound_retryable_failure_pct}%`} /></div> : <EmptyState icon={MessageSquareDashed} title="WhatsApp snapshot unavailable" description="The staging evidence snapshot could not be loaded for this window." eyebrow="Evidence unavailable" />}
                            </PrismPanel>
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Mascot release gate" description="Keep assistant reliability evidence close to the operations layer." actions={<div className="flex flex-wrap gap-2"><button type="button" onClick={() => void copyMascotEvidenceDraft()} className="prism-action-secondary" disabled={copyingMascotEvidence}>{copyingMascotEvidence ? "Copying..." : "Copy evidence"}</button><button type="button" onClick={() => void copyCombinedStagingPacket()} className="prism-action" disabled={copyingStagingPacket}>{copyingStagingPacket ? "Copying..." : "Copy staging packet"}</button></div>} />
                                {mascotSnapshot ? <div className="grid gap-3 md:grid-cols-2"><MiniStat label="Total actions" value={`${mascotSnapshot.analytics.total_actions}`} /><MiniStat label="Unique users" value={`${mascotSnapshot.analytics.unique_users}`} /><MiniStat label="Interpretation failure" value={`${mascotSnapshot.derived_rates.interpretation_failure_pct}%`} /><MiniStat label="Execution failure" value={`${mascotSnapshot.derived_rates.execution_failure_pct}%`} /><MiniStat label="Upload failure" value={`${mascotSnapshot.derived_rates.upload_failure_pct}%`} /><MiniStat label="Overall failure" value={`${mascotSnapshot.derived_rates.overall_failure_pct}%`} /></div> : <EmptyState icon={Bot} title="Mascot snapshot unavailable" description="The mascot reliability snapshot could not be loaded for this window." eyebrow="Evidence unavailable" />}
                                {mascotEvidenceStatus ? <p className="text-xs text-[var(--text-secondary)]">{mascotEvidenceStatus}</p> : null}
                            </PrismPanel>
                        </div>
                    </>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function HeroMetric({ icon: Icon, label, value, detail }: { icon: typeof Users; label: string; value: string; detail: string }) {
    return <div data-testid="stat-card" className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-4"><div className="flex items-center gap-2 text-[var(--text-secondary)]"><Icon className="h-4 w-4" /><p className="text-[11px] font-semibold uppercase tracking-[0.18em]">{label}</p></div><p className="mt-3 text-2xl font-black text-[var(--text-primary)]">{value}</p><p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p></div>;
}
function StatusTile({ label, value, detail }: { label: string; value: string; detail: string }) {
    return <div data-testid="stat-card" className="prism-status-item"><span className="prism-status-label">{label}</span><strong className="prism-status-value">{value}</strong><span className="prism-status-detail">{detail}</span></div>;
}
function MiniStat({ label, value }: { label: string; value: string }) {
    return <div data-testid="stat-card" className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-4 py-3"><p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p><p className="mt-2 text-base font-medium text-[var(--text-primary)]">{value}</p></div>;
}
function InfoLine({ label, value }: { label: string; value: string }) {
    return <div className="rounded-2xl border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] px-4 py-3"><p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p><p className="mt-2 text-sm font-medium text-[var(--text-primary)]">{value}</p></div>;
}
function FeedRow({ title, detail, href, value }: { title: string; detail: string; href: string; value: string }) {
    return <div className="vidya-feed-row"><div><p className="text-sm font-semibold text-[var(--text-primary)]">{title}</p><p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p></div><Link href={href} className="prism-action-secondary">{value}</Link></div>;
}
