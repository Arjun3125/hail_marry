"use client";

import { useEffect, useMemo, useState } from "react";
import {
    AlertTriangle,
    Loader2,
    Shield,
    ShieldAlert,
    User,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
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

    const impactedActors = useMemo(() => {
        return new Set(logs.map((log) => log.user).filter(Boolean)).size;
    }, [logs]);

    const highestRiskEntries = useMemo(() => {
        return logs.filter((log) => log.action.includes("failed") || log.action.includes("denied")).slice(0, 5);
    }, [logs]);

    const latestEntry = logs[0] ?? null;

    return (
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <ShieldAlert className="h-3.5 w-3.5" />
                            Admin Security Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Security Monitoring
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                Review audit activity, identify failed access patterns, and keep operator visibility on recent security-sensitive actions.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <MetricCard
                            icon={Shield}
                            title="Security posture"
                            value={failedLogins24h > 0 ? "Monitor" : "Secure"}
                            summary={failedLogins24h > 0 ? "Failed sign-ins were detected in the last 24 hours." : "No failed sign-ins detected in the last 24 hours."}
                            accent={failedLogins24h > 0 ? "amber" : "emerald"}
                        />
                        <MetricCard
                            icon={AlertTriangle}
                            title="Failed logins"
                            value={`${failedLogins24h}`}
                            summary="Count of login failures detected inside the rolling 24-hour window."
                            accent="amber"
                        />
                        <MetricCard
                            icon={User}
                            title="Admin activity"
                            value={`${adminActions7d}`}
                            summary={`${impactedActors} distinct actors recorded in the last 7 days.`}
                            accent="blue"
                        />
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
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Security Summary</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        High-level audit indicators for security review before drilling into the log trail.
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
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Audit Trail</h2>
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
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Review Priorities</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">
                                Keep the security review practical: monitor failed access, identify the affected actor, and confirm the latest operator action.
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
                            <h2 className="text-base font-semibold text-[var(--text-primary)]">Risk Highlights</h2>
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

function MetricCard({
    icon: Icon,
    title,
    value,
    summary,
    accent,
}: {
    icon: typeof Shield;
    title: string;
    value: string;
    summary: string;
    accent: "blue" | "emerald" | "amber";
}) {
    const accentClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))] text-status-blue",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))] text-status-emerald",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))] text-status-amber",
    } as const;

    return (
        <PrismPanel className="p-4">
            <div className={`mb-3 flex h-11 w-11 items-center justify-center rounded-2xl ${accentClasses[accent]}`}>
                <Icon className="h-5 w-5" />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </PrismPanel>
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
