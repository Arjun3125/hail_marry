"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import {
    AlertTriangle,
    Bot,
    CalendarCheck,
    MessageSquare,
    MessageSquareDashed,
    RefreshCw,
    Shield,
    Users,
    Workflow,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { RoleStartPanel } from "@/components/RoleStartPanel";
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
    student_risk_summary: {
        high_risk_students: number;
        medium_risk_students: number;
        academic_high_risk: number;
        fee_high_risk: number;
    };
    student_risk_alerts: Array<{
        student_id: string;
        student_name: string;
        class_name: string;
        dropout_risk: string;
        academic_risk: string;
        fee_risk: string;
        attendance_pct: number;
        overall_score_pct: number | null;
    }>;
    role_totals: {
        students: number;
        teachers: number;
        parents: number;
        admins: number;
    };
    monthly_trends: Array<{
        month: string;
        active_users: number;
        ai_queries: number;
        complaints_opened: number;
        complaints_resolved: number;
        attendance_pct: number;
        average_marks: number;
    }>;
    complaint_health: {
        opened_last_30d: number;
        resolved_last_30d: number;
        resolution_rate_pct: number;
    };
    latest_milestones: {
        last_ai_query_at: string | null;
        last_complaint_at: string | null;
        last_resolved_complaint_at: string | null;
        last_attendance_marked_at: string | null;
        last_exam_date: string | null;
    };
};

type SecurityItem = { id: string; user: string; action: string; date: string };

type WhatsAppReleaseGateSnapshot = {
    generated_at: string;
    analytics: { total_messages: number; unique_users: number };
    derived_rates: {
        duplicate_inbound_pct: number;
        routing_failure_pct: number;
        visible_failure_pct: number;
        outbound_retryable_failure_pct: number;
    };
};

type MascotReleaseGateSnapshot = {
    generated_at: string;
    analytics: { total_actions: number; unique_users: number };
    derived_rates: {
        interpretation_failure_pct: number;
        execution_failure_pct: number;
        upload_failure_pct: number;
        overall_failure_pct: number;
    };
};

type MascotReleaseGateEvidence = { generated_at: string; markdown: string };
type MascotStagingPacket = { generated_at: string; markdown: string };

const EMPTY_ADMIN_DASHBOARD: DashboardData = {
    total_students: 0,
    total_teachers: 0,
    total_parents: 0,
    active_today: 0,
    ai_queries_today: 0,
    avg_attendance: 0,
    avg_performance: 0,
    open_complaints: 0,
    queue_pending_depth: 0,
    queue_processing_depth: 0,
    queue_failure_rate_pct: 0,
    queue_stuck_jobs: 0,
    observability_alerts: [],
    student_risk_summary: {
        high_risk_students: 0,
        medium_risk_students: 0,
        academic_high_risk: 0,
        fee_high_risk: 0,
    },
    student_risk_alerts: [],
    role_totals: {
        students: 0,
        teachers: 0,
        parents: 0,
        admins: 0,
    },
    monthly_trends: [],
    complaint_health: {
        opened_last_30d: 0,
        resolved_last_30d: 0,
        resolution_rate_pct: 0,
    },
    latest_milestones: {
        last_ai_query_at: null,
        last_complaint_at: null,
        last_resolved_complaint_at: null,
        last_attendance_marked_at: null,
        last_exam_date: null,
    },
};

function normalizeDashboardData(payload: unknown): DashboardData {
    if (!payload || typeof payload !== "object") {
        return EMPTY_ADMIN_DASHBOARD;
    }
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
        role_totals: {
            students: candidate.role_totals?.students ?? 0,
            teachers: candidate.role_totals?.teachers ?? 0,
            parents: candidate.role_totals?.parents ?? 0,
            admins: candidate.role_totals?.admins ?? 0,
        },
        monthly_trends: candidate.monthly_trends ?? [],
        complaint_health: {
            opened_last_30d: candidate.complaint_health?.opened_last_30d ?? 0,
            resolved_last_30d: candidate.complaint_health?.resolved_last_30d ?? 0,
            resolution_rate_pct: candidate.complaint_health?.resolution_rate_pct ?? 0,
        },
        latest_milestones: {
            last_ai_query_at: candidate.latest_milestones?.last_ai_query_at ?? null,
            last_complaint_at: candidate.latest_milestones?.last_complaint_at ?? null,
            last_resolved_complaint_at: candidate.latest_milestones?.last_resolved_complaint_at ?? null,
            last_attendance_marked_at: candidate.latest_milestones?.last_attendance_marked_at ?? null,
            last_exam_date: candidate.latest_milestones?.last_exam_date ?? null,
        },
    };
}

export default function AdminDashboard() {
    const [dashboard, setDashboard] = useState<DashboardData | null>(null);
    const [activity, setActivity] = useState<SecurityItem[]>([]);
    const [whatsappSnapshot, setWhatsappSnapshot] = useState<WhatsAppReleaseGateSnapshot | null>(null);
    const [mascotSnapshot, setMascotSnapshot] = useState<MascotReleaseGateSnapshot | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [refreshingWhatsApp, setRefreshingWhatsApp] = useState(false);
    const [dispatchingAlerts, setDispatchingAlerts] = useState(false);
    const [copyingMascotEvidence, setCopyingMascotEvidence] = useState(false);
    const [copyingStagingPacket, setCopyingStagingPacket] = useState(false);
    const [mascotEvidenceStatus, setMascotEvidenceStatus] = useState<string | null>(null);

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
            setDashboard(normalizeDashboardData(dashboardData));
            setActivity((securityData || []) as SecurityItem[]);
            setWhatsappSnapshot(whatsappData as WhatsAppReleaseGateSnapshot);
            setMascotSnapshot(mascotData as MascotReleaseGateSnapshot);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load admin dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

    const copyText = useCallback(async (text: string) => {
        if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
            await navigator.clipboard.writeText(text);
            return;
        }
        if (typeof document !== "undefined") {
            const textarea = document.createElement("textarea");
            textarea.value = text;
            textarea.style.position = "absolute";
            textarea.style.left = "-9999px";
            document.body.appendChild(textarea);
            textarea.select();
            document.execCommand("copy");
            document.body.removeChild(textarea);
        }
    }, []);

    const refreshWhatsAppSnapshot = useCallback(async () => {
        try {
            setRefreshingWhatsApp(true);
            const payload = await api.admin.whatsappReleaseGateSnapshot(7);
            setWhatsappSnapshot(payload as WhatsAppReleaseGateSnapshot);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to refresh WhatsApp release gate snapshot");
        } finally {
            setRefreshingWhatsApp(false);
        }
    }, []);

    const copyMascotEvidenceDraft = useCallback(async () => {
        try {
            setCopyingMascotEvidence(true);
            setMascotEvidenceStatus(null);
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
            setMascotEvidenceStatus(null);
            const payload = await api.admin.mascotStagingPacket(7) as MascotStagingPacket;
            await copyText(payload.markdown);
            setMascotEvidenceStatus(`Combined staging packet copied from ${new Date(payload.generated_at).toLocaleString()}.`);
        } catch (err) {
            setMascotEvidenceStatus(err instanceof Error ? err.message : "Failed to copy combined staging packet");
        } finally {
            setCopyingStagingPacket(false);
        }
    }, [copyText]);

    const riskSummary = dashboard?.student_risk_summary;
    const riskAlerts = dashboard?.student_risk_alerts || [];

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Shield className="h-3.5 w-3.5" />Institutional Oversight</PrismHeroKicker>}
                    title="Run school health from a calm academic control surface"
                    description="Review adoption, reliability, and student risk without turning the admin experience into a flashy dashboard. This page exists to protect learning quality."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Students active today</span>
                        <strong className="prism-status-value">{dashboard?.active_today ?? 0}</strong>
                        <span className="prism-status-detail">Learners currently engaging with the platform</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Queue pending</span>
                        <strong className="prism-status-value">{dashboard?.queue_pending_depth ?? 0}</strong>
                        <span className="prism-status-detail">Background work still waiting before student features catch up</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Open complaints</span>
                        <strong className="prism-status-value">{dashboard?.open_complaints ?? 0}</strong>
                        <span className="prism-status-detail">Concerns still waiting on follow-through</span>
                    </div>
                </div>

                <RoleStartPanel role="admin" />

                {error ? <ErrorRemediation error={error} scope="admin-dashboard" onRetry={() => void load()} /> : null}

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">Loading institutional overview...</p>
                    </PrismPanel>
                ) : (
                    <>
                        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
                            <MetricCard icon={Users} label="Total students" value={`${dashboard?.total_students ?? 0}`} detail="Learners provisioned in the institution" />
                            <MetricCard icon={Bot} label="AI queries today" value={`${dashboard?.ai_queries_today ?? 0}`} detail="Current daily AI activity across roles" />
                            <MetricCard icon={CalendarCheck} label="Average attendance" value={`${dashboard?.avg_attendance ?? 0}%`} detail="Institution-wide attendance baseline" />
                            <MetricCard icon={Workflow} label="Processing now" value={`${dashboard?.queue_processing_depth ?? 0}`} detail="Work actively running in the background queue" />
                            <MetricCard icon={MessageSquare} label="Queue failure rate" value={`${dashboard?.queue_failure_rate_pct ?? 0}%`} detail="Jobs failing instead of completing cleanly" />
                            <MetricCard icon={AlertTriangle} label="Average performance" value={`${dashboard?.avg_performance ?? 0}%`} detail="Current academic performance signal across graded work" />
                        </div>

                        <div className="grid gap-6 xl:grid-cols-[1.04fr_0.96fr]">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Six-month institution trend" description="Show the demo as a lived-in school, not a single-day snapshot." />
                                <div className="grid gap-3 md:grid-cols-3">
                                    {(dashboard?.monthly_trends || []).map((item, index) => (
                                        <div key={`${item.month}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{item.month}</p>
                                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{item.ai_queries} AI queries</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                {item.active_users} active users, {item.complaints_opened} complaint{item.complaints_opened === 1 ? "" : "s"} opened, {item.complaints_resolved} resolved.
                                            </p>
                                            <p className="mt-2 text-xs text-[var(--text-muted)]">
                                                {item.attendance_pct}% attendance and {item.average_marks}% average marks.
                                            </p>
                                        </div>
                                    ))}
                                </div>
                            </PrismPanel>

                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Role footprint" description="Keep the demo credible across the whole institution population." />
                                <div className="grid gap-3 sm:grid-cols-2">
                                    <InfoTile label="Students" value={`${dashboard?.role_totals?.students ?? 0}`} />
                                    <InfoTile label="Teachers" value={`${dashboard?.role_totals?.teachers ?? 0}`} />
                                    <InfoTile label="Parents" value={`${dashboard?.role_totals?.parents ?? 0}`} />
                                    <InfoTile label="Admins" value={`${dashboard?.role_totals?.admins ?? 0}`} />
                                    <InfoTile label="Resolved 30d" value={`${dashboard?.complaint_health?.resolved_last_30d ?? 0}`} />
                                    <InfoTile label="Resolution rate" value={`${dashboard?.complaint_health?.resolution_rate_pct ?? 0}%`} />
                                </div>
                                <div className="space-y-2">
                                    <InfoTile label="Last AI query" value={dashboard?.latest_milestones?.last_ai_query_at ? new Date(dashboard.latest_milestones.last_ai_query_at).toLocaleDateString() : "No data"} />
                                    <InfoTile label="Last complaint" value={dashboard?.latest_milestones?.last_complaint_at ? new Date(dashboard.latest_milestones.last_complaint_at).toLocaleDateString() : "No data"} />
                                    <InfoTile label="Last exam" value={dashboard?.latest_milestones?.last_exam_date ? new Date(dashboard.latest_milestones.last_exam_date).toLocaleDateString() : "No data"} />
                                </div>
                            </PrismPanel>
                        </div>

                        <div className="grid gap-6 xl:grid-cols-2">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="WhatsApp release gate" description="Keep this evidence close before promoting messaging workflows that reach students or parents." actions={<button type="button" onClick={() => void refreshWhatsAppSnapshot()} className="prism-action-secondary" disabled={refreshingWhatsApp}><RefreshCw className={`h-4 w-4 ${refreshingWhatsApp ? "animate-spin" : ""}`} />{refreshingWhatsApp ? "Refreshing..." : "Refresh snapshot"}</button>} />
                                {whatsappSnapshot ? (
                                    <div className="grid gap-3 md:grid-cols-2">
                                        <InfoTile label="Total messages" value={`${whatsappSnapshot.analytics.total_messages}`} />
                                        <InfoTile label="Unique users" value={`${whatsappSnapshot.analytics.unique_users}`} />
                                        <InfoTile label="Visible failure" value={`${whatsappSnapshot.derived_rates.visible_failure_pct}%`} />
                                        <InfoTile label="Routing failure" value={`${whatsappSnapshot.derived_rates.routing_failure_pct}%`} />
                                        <InfoTile label="Duplicate inbound" value={`${whatsappSnapshot.derived_rates.duplicate_inbound_pct}%`} />
                                        <InfoTile label="Retryable outbound" value={`${whatsappSnapshot.derived_rates.outbound_retryable_failure_pct}%`} />
                                    </div>
                                ) : (
                                    <EmptyState icon={MessageSquareDashed} title="WhatsApp snapshot unavailable" description="The staging evidence snapshot could not be loaded for this window." eyebrow="Evidence unavailable" />
                                )}
                            </PrismPanel>

                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Mascot release gate" description="Check action failure rates before relying on mascot flows that touch uploads, confirmations, or student-facing execution." actions={<div className="flex flex-wrap gap-2"><button type="button" onClick={() => void copyMascotEvidenceDraft()} className="prism-action-secondary" disabled={copyingMascotEvidence}>{copyingMascotEvidence ? "Copying..." : "Copy evidence"}</button><button type="button" onClick={() => void copyCombinedStagingPacket()} className="prism-action" disabled={copyingStagingPacket}>{copyingStagingPacket ? "Copying..." : "Copy staging packet"}</button></div>} />
                                {mascotSnapshot ? (
                                    <div className="grid gap-3 md:grid-cols-2">
                                        <InfoTile label="Total actions" value={`${mascotSnapshot.analytics.total_actions}`} />
                                        <InfoTile label="Unique users" value={`${mascotSnapshot.analytics.unique_users}`} />
                                        <InfoTile label="Interpretation failure" value={`${mascotSnapshot.derived_rates.interpretation_failure_pct}%`} />
                                        <InfoTile label="Execution failure" value={`${mascotSnapshot.derived_rates.execution_failure_pct}%`} />
                                        <InfoTile label="Upload failure" value={`${mascotSnapshot.derived_rates.upload_failure_pct}%`} />
                                        <InfoTile label="Overall failure" value={`${mascotSnapshot.derived_rates.overall_failure_pct}%`} />
                                    </div>
                                ) : (
                                    <EmptyState icon={Bot} title="Mascot snapshot unavailable" description="The mascot reliability snapshot could not be loaded for this window." eyebrow="Evidence unavailable" />
                                )}
                                {mascotEvidenceStatus ? <p className="text-xs text-[var(--text-secondary)]">{mascotEvidenceStatus}</p> : null}
                            </PrismPanel>
                        </div>

                        <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Student risk radar" description="Keep this list practical: who is drifting, why they are drifting, and what follow-up the school should take next." actions={<Link href="/admin/reports" className="prism-action-secondary">Open reports</Link>} />
                                <div className="grid gap-3 sm:grid-cols-4">
                                    <InfoTile label="High risk" value={`${riskSummary?.high_risk_students ?? 0}`} />
                                    <InfoTile label="Medium risk" value={`${riskSummary?.medium_risk_students ?? 0}`} />
                                    <InfoTile label="Academic high risk" value={`${riskSummary?.academic_high_risk ?? 0}`} />
                                    <InfoTile label="Fee high risk" value={`${riskSummary?.fee_high_risk ?? 0}`} />
                                </div>
                                {riskAlerts.length > 0 ? (
                                    <div className="space-y-3">
                                        {riskAlerts.map((alert) => (
                                            <div key={alert.student_id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                                <div className="flex flex-wrap items-start justify-between gap-3">
                                                    <div>
                                                        <p className="text-sm font-semibold text-[var(--text-primary)]">{alert.student_name}</p>
                                                        <p className="text-xs text-[var(--text-muted)]">{alert.class_name}</p>
                                                    </div>
                                                    <div className="flex flex-wrap gap-2">
                                                        {[
                                                            { label: "Dropout", value: alert.dropout_risk },
                                                            { label: "Academic", value: alert.academic_risk },
                                                            { label: "Fee", value: alert.fee_risk },
                                                        ].map((pill) => (
                                                            <span key={`${alert.student_id}-${pill.label}`} className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${pill.value === "high" ? "bg-error-subtle text-status-red" : pill.value === "medium" ? "bg-warning-subtle text-status-amber" : "bg-success-subtle text-status-green"}`}>{pill.label} {pill.value}</span>
                                                        ))}
                                                    </div>
                                                </div>
                                                <div className="mt-3 grid gap-2 sm:grid-cols-3">
                                                    <InfoTile compact label="Attendance" value={`${alert.attendance_pct}%`} />
                                                    <InfoTile compact label="Performance" value={alert.overall_score_pct !== null ? `${alert.overall_score_pct}%` : "Not enough data"} />
                                                    <InfoTile compact label="Suggested focus" value={alert.fee_risk === "high" ? "Fee recovery" : alert.academic_risk === "high" ? "Academic intervention" : "Attendance follow-up"} />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <EmptyState icon={AlertTriangle} title="No active student risk alerts" description="No high-priority academic, attendance, or fee risk cases are currently flagged." eyebrow="Stable" />
                                )}
                            </PrismPanel>

                            <div className="space-y-6">
                                <PrismPanel className="space-y-4 p-5">
                                <PrismSectionHeader title="Current alerts" description="These are the operational issues most likely to affect reliability, support load, or school trust." actions={<button type="button" onClick={async () => { try { setDispatchingAlerts(true); await api.admin.dispatchObservabilityAlerts(); } catch (err) { setError(err instanceof Error ? err.message : "Failed to dispatch alerts"); } finally { setDispatchingAlerts(false); } }} className="prism-action-secondary" disabled={dispatchingAlerts || (dashboard?.observability_alerts?.length ?? 0) === 0}>{dispatchingAlerts ? "Dispatching..." : "Dispatch Alerts"}</button>} />
                                    {(dashboard?.observability_alerts?.length ?? 0) > 0 ? (
                                        <div className="space-y-2">
                                            {(dashboard?.observability_alerts || []).slice(0, 5).map((alert) => (
                                                <div key={alert.code} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                    <div className="flex items-start justify-between gap-3">
                                                        <p className="text-sm text-[var(--text-primary)]">{alert.message}</p>
                                                        <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${alert.severity === "critical" ? "bg-error-subtle text-status-red" : "bg-warning-subtle text-status-amber"}`}>{alert.severity}</span>
                                                    </div>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <EmptyState icon={AlertTriangle} title="No active alerts" description="The platform does not currently show any active observability alerts." eyebrow="Stable" />
                                    )}
                                </PrismPanel>

                                <PrismPanel className="space-y-4 p-5">
                                    <PrismSectionHeader title="Security activity" description="Keep a short recent log visible so trust and access events do not disappear behind deeper admin tools." />
                                    {activity.length > 0 ? (
                                        <div className="space-y-2">
                                            {activity.slice(0, 6).map((item) => (
                                                <div key={item.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                    <p className="text-sm font-medium text-[var(--text-primary)]">{item.action}</p>
                                                    <p className="mt-1 text-xs text-[var(--text-muted)]">by {item.user} • {new Date(item.date).toLocaleString()}</p>
                                                </div>
                                            ))}
                                        </div>
                                    ) : (
                                        <EmptyState icon={Shield} title="No recent security events" description="Security activity will appear here when access, policy, or account events are recorded." eyebrow="Quiet" />
                                    )}
                                </PrismPanel>
                            </div>
                        </div>
                    </>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({ icon: Icon, label, value, detail }: { icon: typeof Users; label: string; value: string; detail: string }) {
    return (
        <PrismPanel className="p-4">
            <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                <Icon className="h-4 w-4" />
                <p className="text-xs font-semibold uppercase tracking-[0.16em]">{label}</p>
            </div>
            <p className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p>
        </PrismPanel>
    );
}

function InfoTile({ label, value, compact = false }: { label: string; value: string; compact?: boolean }) {
    return (
        <div className={`rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] ${compact ? "px-3 py-2.5" : "px-4 py-3"}`}>
            <p className="text-[10px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p>
            <p className={`mt-2 ${compact ? "text-sm" : "text-base"} font-medium text-[var(--text-primary)]`}>{value}</p>
        </div>
    );
}
