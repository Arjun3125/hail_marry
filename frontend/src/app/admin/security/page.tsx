"use client";

import { useEffect, useMemo, useState } from "react";
import { Shield, User, AlertTriangle } from "lucide-react";

import { api } from "@/lib/api";

type SecurityLog = {
    id: string;
    user: string;
    action: string;
    entity_type: string;
    metadata: Record<string, unknown> | null;
    date: string;
};

export default function AdminSecurityPage() {
    const [logs, setLogs] = useState<SecurityLog[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
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
        void load();
    }, []);

    const failedLogins24h = useMemo(() => {
        const cutoff = Date.now() - 24 * 60 * 60 * 1000;
        return logs.filter((l) => {
            if (!l.action.includes("login.failed")) return false;
            const parsed = new Date(l.date).getTime();
            return !Number.isNaN(parsed) && parsed >= cutoff;
        }).length;
    }, [logs]);

    const adminActions7d = useMemo(() => {
        const cutoff = Date.now() - 7 * 24 * 60 * 60 * 1000;
        return logs.filter((l) => {
            const parsed = new Date(l.date).getTime();
            return !Number.isNaN(parsed) && parsed >= cutoff;
        }).length;
    }, [logs]);

    const formatDateTime = (value: string) => {
        const parsed = new Date(value);
        return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Security Monitoring</h1>
                <p className="text-sm text-[var(--text-secondary)]">Audit logs and security events</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid md:grid-cols-3 gap-4 mb-6">
                <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                    <div className="flex items-center gap-2 mb-1">
                        <Shield className="w-4 h-4 text-[var(--success)]" />
                        <span className="text-xs text-[var(--text-muted)]">Security Status</span>
                    </div>
                    <p className="text-lg font-bold text-[var(--success)]">{failedLogins24h > 0 ? "Monitor" : "Secure"}</p>
                </div>
                <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                    <div className="flex items-center gap-2 mb-1">
                        <AlertTriangle className="w-4 h-4 text-[var(--warning)]" />
                        <span className="text-xs text-[var(--text-muted)]">Failed Logins (24h)</span>
                    </div>
                    <p className="text-lg font-bold text-[var(--text-primary)]">{failedLogins24h}</p>
                </div>
                <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                    <div className="flex items-center gap-2 mb-1">
                        <User className="w-4 h-4 text-[var(--primary)]" />
                        <span className="text-xs text-[var(--text-muted)]">Admin Actions (7d)</span>
                    </div>
                    <p className="text-lg font-bold text-[var(--text-primary)]">{adminActions7d}</p>
                </div>
            </div>

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="px-5 py-3 border-b border-[var(--border)]">
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Audit Trail</h2>
                </div>
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                            <th className="px-5 py-2.5 text-left text-xs font-medium text-[var(--text-muted)]">User</th>
                            <th className="px-5 py-2.5 text-left text-xs font-medium text-[var(--text-muted)]">Action</th>
                            <th className="px-5 py-2.5 text-left text-xs font-medium text-[var(--text-muted)]">Details</th>
                            <th className="px-5 py-2.5 text-left text-xs font-medium text-[var(--text-muted)]">Time</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={4}>
                                    Loading logs...
                                </td>
                            </tr>
                        ) : logs.length === 0 ? (
                            <tr>
                                <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={4}>
                                    No audit entries found.
                                </td>
                            </tr>
                        ) : logs.map((log) => (
                            <tr key={log.id} className="border-b border-[var(--border-light)]">
                                <td className="px-5 py-3 text-sm text-[var(--text-primary)]">{log.user}</td>
                                <td className="px-5 py-3">
                                    <span className="text-xs bg-[var(--bg-page)] text-[var(--text-secondary)] px-2 py-0.5 rounded-full">{log.action}</span>
                                </td>
                                <td className="px-5 py-3 text-xs text-[var(--text-muted)]">{log.metadata ? JSON.stringify(log.metadata) : "-"}</td>
                                <td className="px-5 py-3 text-xs text-[var(--text-muted)]">{formatDateTime(log.date)}</td>
                            </tr>
                        ))}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
