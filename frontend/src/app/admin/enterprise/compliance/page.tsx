"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle, Clock, Filter, RefreshCw, ShieldAlert } from "lucide-react";
import { api } from "@/lib/api";

type Incident = {
    id: string;
    alert_code: string;
    severity: "critical" | "warning" | "info";
    status: "active" | "acknowledged" | "resolved";
    message: string;
    occurrence_count: number;
    last_seen_at: string;
};

export default function IncidentManagementPage() {
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);

    const load = async () => {
        try {
            setRefreshing(true);
            const data = await api.enterprise.incidents();
            setIncidents(data || []);
        } catch (err) {
            console.error("Failed to load incidents", err);
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        void load();
    }, []);

    const handleAcknowledge = async (id: string) => {
        try {
            await api.enterprise.acknowledgeIncident(id);
            void load();
        } catch (err) {
            console.error("Failed to acknowledge incident", err);
        }
    };

    const handleResolve = async (id: string) => {
        try {
            const note = prompt("Resolution Note (Required):");
            if (!note) return;
            await api.enterprise.resolveIncident(id, note);
            void load();
        } catch (err) {
            console.error("Failed to resolve incident", err);
        }
    };

    if (loading) return <div className="p-8 text-center text-[var(--text-muted)]">Loading Incidents...</div>;

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Incident Management</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Monitor and respond to platform security alerts</p>
                </div>
                <button
                    onClick={() => void load()}
                    disabled={refreshing}
                    className="flex items-center gap-2 text-sm bg-[var(--bg-card)] border border-[var(--border)] px-4 py-2 rounded-[var(--radius)] hover:bg-[var(--bg-page)] transition-colors"
                >
                    <RefreshCw className={`w-4 h-4 ${refreshing ? "animate-spin" : ""}`} />
                    Refresh
                </button>
            </div>

            <div className="grid md:grid-cols-4 gap-4 mb-8">
                <div className="bg-[var(--bg-card)] p-4 rounded-[var(--radius)] shadow-[var(--shadow-card)] border-l-4 border-[var(--error)]">
                    <p className="text-xs text-[var(--text-muted)] font-medium">Critical</p>
                    <p className="text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter(i => i.severity === "critical" && i.status !== "resolved").length}
                    </p>
                </div>
                <div className="bg-[var(--bg-card)] p-4 rounded-[var(--radius)] shadow-[var(--shadow-card)] border-l-4 border-[var(--warning)]">
                    <p className="text-xs text-[var(--text-muted)] font-medium">Warning</p>
                    <p className="text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter(i => i.severity === "warning" && i.status !== "resolved").length}
                    </p>
                </div>
                <div className="bg-[var(--bg-card)] p-4 rounded-[var(--radius)] shadow-[var(--shadow-card)] border-l-4 border-[var(--primary)]">
                    <p className="text-xs text-[var(--text-muted)] font-medium">Active</p>
                    <p className="text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter(i => i.status === "active").length}
                    </p>
                </div>
                <div className="bg-[var(--bg-card)] p-4 rounded-[var(--radius)] shadow-[var(--shadow-card)] border-l-4 border-[var(--success)]">
                    <p className="text-xs text-[var(--text-muted)] font-medium">Resolved (24h)</p>
                    <p className="text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter(i => i.status === "resolved").length}
                    </p>
                </div>
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full text-left">
                        <thead>
                            <tr className="bg-[var(--bg-page)] border-b border-[var(--border)]">
                                <th className="px-6 py-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Severity</th>
                                <th className="px-6 py-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Alert</th>
                                <th className="px-6 py-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Status</th>
                                <th className="px-6 py-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Occurrences</th>
                                <th className="px-6 py-3 text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Last Seen</th>
                                <th className="px-6 py-3 text-right text-xs font-semibold text-[var(--text-muted)] uppercase tracking-wider">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--border-light)]">
                            {incidents.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-12 text-center text-[var(--text-muted)]">No incidents recorded.</td>
                                </tr>
                            ) : incidents.map((incident) => (
                                <tr key={incident.id} className="hover:bg-[var(--bg-page)] transition-colors">
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        {incident.severity === "critical" ? (
                                            <span className="flex items-center gap-1.5 text-[var(--error)] font-semibold">
                                                <ShieldAlert className="w-4 h-4" /> CRITICAL
                                            </span>
                                        ) : (
                                            <span className="flex items-center gap-1.5 text-[var(--warning)] font-semibold">
                                                <AlertCircle className="w-4 h-4" /> WARNING
                                            </span>
                                        )}
                                    </td>
                                    <td className="px-6 py-4">
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{incident.alert_code}</p>
                                        <p className="text-xs text-[var(--text-muted)] line-clamp-1">{incident.message}</p>
                                    </td>
                                    <td className="px-6 py-4 whitespace-nowrap">
                                        <span className={`text-xs px-2 py-0.5 rounded-full font-medium ${
                                            incident.status === "active" ? "bg-[var(--error-subtle)] text-[var(--error)]" :
                                            incident.status === "acknowledged" ? "bg-[var(--warning-subtle)] text-[var(--warning)]" :
                                            "bg-[var(--success-subtle)] text-[var(--success)]"
                                        }`}>
                                            {incident.status.toUpperCase()}
                                        </span>
                                    </td>
                                    <td className="px-6 py-4 text-sm text-[var(--text-secondary)]">{incident.occurrence_count}</td>
                                    <td className="px-6 py-4 text-xs text-[var(--text-muted)]">
                                        <div className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {new Date(incident.last_seen_at).toLocaleString()}
                                        </div>
                                    </td>
                                    <td className="px-6 py-4 text-right">
                                        {incident.status === "active" && (
                                            <button
                                                onClick={() => handleAcknowledge(incident.id)}
                                                className="text-xs text-[var(--primary)] hover:underline font-medium"
                                            >
                                                Acknowledge
                                            </button>
                                        )}
                                        {incident.status !== "resolved" && (
                                            <button
                                                onClick={() => handleResolve(incident.id)}
                                                className="ml-3 text-xs text-[var(--success)] hover:underline font-medium"
                                            >
                                                Resolve
                                            </button>
                                        )}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    );
}
