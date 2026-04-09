"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Loader2,
    Shield,
    ShieldAlert,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type SecurityLog = {
    id: string;
    user: string;
    action: string;
    entity_type: string;
    metadata: Record<string, unknown> | null;
    date: string;
};

function formatDateTime(value: string) {
    const parsed = new Date(value);
    return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

export default function AdminSecurityPage() {
    const [logs, setLogs] = useState<SecurityLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const loadSecurityLogs = async () => {
        try {
            setLoading(true);
            setError(null);
            const payload = await api.admin.security();
            setLogs((payload || []) as SecurityLog[]);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load security logs");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void loadSecurityLogs();
    }, []);

    const failedLogins24h = useMemo(() => {
        const cutoff = Date.now() - 24 * 60 * 60 * 1000;
        return logs.filter((log) => {
            if (!log.action.includes("login.failed")) return false;
            const parsed = new Date(log.date).getTime();
            return !Number.isNaN(parsed) && parsed >= cutoff;
        }).length;
    }, [logs]);

    const adminActions7d = useMemo(() => {
        const cutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;
        return logs.filter((log) => {
            const parsed = new Date(log.date).getTime();
            return !Number.isNaN(parsed) && parsed >= cutoff;
        }).length;
    }, [logs]);

    const impactedActors = useMemo(() => new Set(logs.map((log) => log.user).filter(Boolean)).size, [logs]);
    const highestRiskEntries = useMemo(
        () => logs.filter((log) => log.action.includes("failed") || log.action.includes("denied")).slice(0, 5),
        [logs],
    );
    const latestEntry = logs[0] ?? null;

    return (
        <PrismPage variant="dashboard" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ShieldAlert className="h-3.5 w-3.5" />
                            Admin Security Surface
                        </PrismHeroKicker>
                    )}
                    title="Keep security review disciplined and actor-focused"
                    description="Review failed access, operator activity, and recent security-sensitive events from one audit-first admin surface."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Review flow</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with failed access pressure, then confirm the affected actor and most recent high-risk action before opening the full audit trail.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Security posture</span>
                        <span className="prism-status-value">{failedLogins24h > 0 ? "Monitor" : "Secure"}</span>
                        <span className="prism-status-detail">
                            {failedLogins24h > 0
                                ? "Failed sign-ins were detected in the last 24 hours."
                                : "No failed sign-ins were detected in the last 24 hours."}
                        </span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Failed logins</span>
                        <span className="prism-status-value">{failedLogins24h}</span>
                        <span className="prism-status-detail">Rolling 24-hour count of failed authentication attempts.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Admin activity</span>
                        <span className="prism-status-value">{adminActions7d}</span>
                        <span className="prism-status-detail">{impactedActors} distinct actors recorded in the last 7 days.</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-security"
                        onRetry={() => {
                            void loadSecurityLogs();
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(340px,0.92fr)]">
                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Security summary</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Audit indicators to review before drilling into the full log trail.
                                    </p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    {loading ? "Refreshing logs" : `${logs.length} audit entries`}
                                </div>
                            </div>

                            <div className="mt-4 grid gap-4 sm:grid-cols-3">
                                <CompactMetric title="Distinct actors" value={`${impactedActors}`} />
                                <CompactMetric title="Risk entries" value={`${highestRiskEntries.length}`} />
                                <CompactMetric title="Latest event" value={latestEntry ? latestEntry.action : "No activity"} />
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Audit trail</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Chronological view of authentication and operator activity with raw metadata preserved.
                                    </p>
                                </div>
                            </div>

                            {loading ? (
                                <div className="mt-4 flex items-center gap-2 text-sm text-[var(--text-muted)]">
                                    <Loader2 className="h-4 w-4 animate-spin" /> Loading logs...
                                </div>
                            ) : logs.length === 0 ? (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={Shield}
                                        title="No audit entries found"
                                        description="Security activity will appear here once authentication and admin events are recorded."
                                        eyebrow="Audit ledger empty"
                                        scopeNote="Authentication events, permission denials, and operator changes all land in this review table."
                                    />
                                </div>
                            ) : (
                                <div className="mt-4 overflow-x-auto">
                                    <table className="min-w-full divide-y divide-[var(--border)] text-sm">
                                        <thead>
                                            <tr className="text-left text-xs uppercase tracking-wide text-[var(--text-muted)]">
                                                <th className="py-3 pr-4">User</th>
                                                <th className="py-3 pr-4">Action</th>
                                                <th className="py-3 pr-4">Entity</th>
                                                <th className="py-3 pr-4">Details</th>
                                                <th className="py-3">Time</th>
                                            </tr>
                                        </thead>
                                        <tbody className="divide-y divide-[var(--border)]">
                                            {logs.map((log) => (
                                                <tr key={log.id} className="align-top">
                                                    <td className="py-3 pr-4">
                                                        <div className="font-medium text-[var(--text-primary)]">{log.user}</div>
                                                    </td>
                                                    <td className="py-3 pr-4">
                                                        <span className="inline-flex rounded-full bg-[var(--bg-page)] px-2.5 py-1 text-xs font-medium text-[var(--text-secondary)]">
                                                            {log.action}
                                                        </span>
                                                    </td>
                                                    <td className="py-3 pr-4 text-[var(--text-secondary)]">{log.entity_type}</td>
                                                    <td className="py-3 pr-4">
                                                        <pre className="max-w-[420px] overflow-x-auto whitespace-pre-wrap rounded-2xl bg-[rgba(255,255,255,0.03)] p-3 text-xs text-[var(--text-muted)]">
                                                            {log.metadata ? JSON.stringify(log.metadata, null, 2) : "-"}
                                                        </pre>
                                                    </td>
                                                    <td className="py-3 text-xs text-[var(--text-muted)]">{formatDateTime(log.date)}</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            )}
                        </PrismPanel>
                    </div>

                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5 xl:sticky xl:top-6">
                            <div className="flex items-center gap-2">
                                <ShieldAlert className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Review priorities</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Keep the review practical: monitor failed access, identify the affected actor, and confirm the latest operator action.
                            </p>

                            <div className="mt-4 space-y-3">
                                <PriorityCard
                                    title="Failed access pressure"
                                    value={`${failedLogins24h}`}
                                    summary="Failed sign-in attempts detected over the last 24 hours."
                                />
                                <PriorityCard
                                    title="Latest actor"
                                    value={latestEntry?.user ?? "No activity"}
                                    summary="Most recent operator or user appearing in the audit ledger."
                                />
                                <PriorityCard
                                    title="Latest action"
                                    value={latestEntry?.action ?? "No activity"}
                                    summary="Most recent security-sensitive action recorded by the system."
                                />
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <h2 className="text-base font-semibold text-[var(--text-primary)]">Risk highlights</h2>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Security-relevant entries are surfaced here first so the audit table remains readable under load.
                            </p>

                            <div className="mt-4 space-y-3">
                                {highestRiskEntries.length === 0 ? (
                                    <p className="text-sm text-[var(--text-muted)]">No failed or denied actions in the current dataset.</p>
                                ) : highestRiskEntries.map((log) => (
                                    <div key={log.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <div className="flex items-start justify-between gap-3">
                                            <div>
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{log.action}</p>
                                                <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                    {log.user} · {log.entity_type}
                                                </p>
                                            </div>
                                            <span className="text-[11px] uppercase tracking-[0.18em] text-[var(--text-muted)]">
                                                {formatDateTime(log.date)}
                                            </span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function CompactMetric({ title, value }: { title: string; value: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 break-all text-sm font-semibold text-[var(--text-primary)]">{value}</p>
        </div>
    );
}

function PriorityCard({ title, value, summary }: { title: string; value: string; summary: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </div>
    );
}
