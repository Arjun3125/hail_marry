"use client";

import { useEffect, useState } from "react";
import { AlertCircle, CheckCircle2, Clock3, RefreshCw, ShieldAlert, Siren, Waypoints } from "lucide-react";
import { api } from "@/lib/api";

type Incident = {
    id: string;
    alert_code: string;
    severity: "critical" | "warning" | "info";
    status: "active" | "acknowledged" | "resolved";
    title: string;
    summary: string;
    trace_id?: string | null;
    created_at: string;
    updated_at: string;
    acknowledged_at?: string | null;
    resolved_at?: string | null;
};

type IncidentRoute = {
    id: string;
    name: string;
    channel_type: string;
    target: string;
    severity_filter: string;
    escalation_channel_type?: string | null;
    escalation_target?: string | null;
    escalation_after_minutes?: number | null;
    is_active: boolean;
    created_at: string;
};

type RouteForm = {
    name: string;
    channel_type: string;
    target: string;
    severity_filter: string;
};

const DEFAULT_ROUTE_FORM: RouteForm = {
    name: "",
    channel_type: "email",
    target: "",
    severity_filter: "all",
};

export default function IncidentManagementPage() {
    const [incidents, setIncidents] = useState<Incident[]>([]);
    const [routes, setRoutes] = useState<IncidentRoute[]>([]);
    const [routeForm, setRouteForm] = useState<RouteForm>(DEFAULT_ROUTE_FORM);
    const [loading, setLoading] = useState(true);
    const [refreshing, setRefreshing] = useState(false);
    const [savingRoute, setSavingRoute] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const load = async () => {
        try {
            setRefreshing(true);
            setError(null);
            const [incidentData, routeData] = await Promise.all([
                api.enterprise.incidents(),
                api.enterprise.incidentRoutes(),
            ]);
            setIncidents(incidentData || []);
            setRoutes(routeData || []);
        } catch (err) {
            console.error("Failed to load incident data", err);
            setError("Failed to load incident data.");
        } finally {
            setLoading(false);
            setRefreshing(false);
        }
    };

    useEffect(() => {
        void load();
    }, []);

    const handleSync = async () => {
        try {
            setRefreshing(true);
            setError(null);
            await api.enterprise.syncIncidents();
            await load();
        } catch (err) {
            console.error("Failed to sync incidents", err);
            setError("Failed to sync incidents.");
            setRefreshing(false);
        }
    };

    const handleAcknowledge = async (id: string) => {
        try {
            await api.enterprise.acknowledgeIncident(id);
            await load();
        } catch (err) {
            console.error("Failed to acknowledge incident", err);
            setError("Failed to acknowledge incident.");
        }
    };

    const handleResolve = async (id: string) => {
        const note = window.prompt("Resolution note:");
        if (note === null) return;

        try {
            await api.enterprise.resolveIncident(id, note);
            await load();
        } catch (err) {
            console.error("Failed to resolve incident", err);
            setError("Failed to resolve incident.");
        }
    };

    const handleCreateRoute = async () => {
        if (!routeForm.name.trim() || !routeForm.target.trim()) {
            setError("Route name and target are required.");
            return;
        }

        try {
            setSavingRoute(true);
            setError(null);
            await api.enterprise.createIncidentRoute({
                name: routeForm.name.trim(),
                channel_type: routeForm.channel_type,
                target: routeForm.target.trim(),
                severity_filter: routeForm.severity_filter,
            });
            setRouteForm(DEFAULT_ROUTE_FORM);
            await load();
        } catch (err) {
            console.error("Failed to create incident route", err);
            setError("Failed to create incident route.");
        } finally {
            setSavingRoute(false);
        }
    };

    if (loading) {
        return <div className="p-8 text-center text-[var(--text-muted)]">Loading incident controls...</div>;
    }

    return (
        <div className="space-y-6">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Incident Management</h1>
                    <p className="text-sm text-[var(--text-secondary)]">
                        Monitor operational alerts, acknowledge incidents, and manage notification routes.
                    </p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => void handleSync()}
                        disabled={refreshing}
                        className="rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-page)] disabled:opacity-60"
                    >
                        Sync Alerts
                    </button>
                    <button
                        onClick={() => void load()}
                        disabled={refreshing}
                        className="flex items-center gap-2 rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-page)] disabled:opacity-60"
                    >
                        <RefreshCw className={`h-4 w-4 ${refreshing ? "animate-spin" : ""}`} />
                        Refresh
                    </button>
                </div>
            </div>

            {error && (
                <div className="rounded-[var(--radius)] border border-[var(--error)] bg-[var(--error-subtle)] px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}

            <div className="grid gap-4 md:grid-cols-4">
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Active</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter((incident) => incident.status === "active").length}
                    </p>
                </div>
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Critical open</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter((incident) => incident.severity === "critical" && incident.status !== "resolved").length}
                    </p>
                </div>
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Acknowledged</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">
                        {incidents.filter((incident) => incident.status === "acknowledged").length}
                    </p>
                </div>
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Routes</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{routes.length}</p>
                </div>
            </div>

            <div className="overflow-hidden rounded-[var(--radius)] bg-[var(--bg-card)] shadow-[var(--shadow-card)]">
                <div className="border-b border-[var(--border)] px-6 py-4">
                    <div className="flex items-center gap-2">
                        <Siren className="h-5 w-5 text-[var(--primary)]" />
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Incidents</h2>
                    </div>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full text-left text-sm">
                        <thead>
                            <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                                <th className="px-6 py-3 text-[var(--text-muted)]">Severity</th>
                                <th className="px-6 py-3 text-[var(--text-muted)]">Incident</th>
                                <th className="px-6 py-3 text-[var(--text-muted)]">Status</th>
                                <th className="px-6 py-3 text-[var(--text-muted)]">Trace</th>
                                <th className="px-6 py-3 text-[var(--text-muted)]">Updated</th>
                                <th className="px-6 py-3 text-right text-[var(--text-muted)]">Actions</th>
                            </tr>
                        </thead>
                        <tbody className="divide-y divide-[var(--border-light)]">
                            {incidents.length === 0 ? (
                                <tr>
                                    <td colSpan={6} className="px-6 py-10 text-center text-[var(--text-muted)]">
                                        No incidents recorded.
                                    </td>
                                </tr>
                            ) : (
                                incidents.map((incident) => (
                                    <tr key={incident.id}>
                                        <td className="px-6 py-4">
                                            {incident.severity === "critical" ? (
                                                <span className="flex items-center gap-1.5 font-semibold text-[var(--error)]">
                                                    <ShieldAlert className="h-4 w-4" /> CRITICAL
                                                </span>
                                            ) : incident.severity === "warning" ? (
                                                <span className="flex items-center gap-1.5 font-semibold text-[var(--warning)]">
                                                    <AlertCircle className="h-4 w-4" /> WARNING
                                                </span>
                                            ) : (
                                                <span className="flex items-center gap-1.5 font-semibold text-[var(--primary)]">
                                                    <CheckCircle2 className="h-4 w-4" /> INFO
                                                </span>
                                            )}
                                        </td>
                                        <td className="px-6 py-4">
                                            <div className="font-medium text-[var(--text-primary)]">{incident.title}</div>
                                            <div className="text-xs text-[var(--text-muted)]">{incident.summary || incident.alert_code}</div>
                                        </td>
                                        <td className="px-6 py-4">
                                            <span className="rounded-full bg-[var(--bg-page)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]">
                                                {incident.status.toUpperCase()}
                                            </span>
                                        </td>
                                        <td className="px-6 py-4 text-xs text-[var(--text-muted)]">{incident.trace_id || "N/A"}</td>
                                        <td className="px-6 py-4 text-xs text-[var(--text-muted)]">
                                            <div className="flex items-center gap-1">
                                                <Clock3 className="h-3 w-3" />
                                                {new Date(incident.updated_at).toLocaleString()}
                                            </div>
                                        </td>
                                        <td className="px-6 py-4 text-right">
                                            {incident.status === "active" && (
                                                <button
                                                    onClick={() => void handleAcknowledge(incident.id)}
                                                    className="text-xs font-medium text-[var(--primary)] hover:underline"
                                                >
                                                    Acknowledge
                                                </button>
                                            )}
                                            {incident.status !== "resolved" && (
                                                <button
                                                    onClick={() => void handleResolve(incident.id)}
                                                    className="ml-3 text-xs font-medium text-[var(--success)] hover:underline"
                                                >
                                                    Resolve
                                                </button>
                                            )}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-[1.2fr_1fr]">
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-6 shadow-[var(--shadow-card)]">
                    <div className="mb-4 flex items-center gap-2">
                        <Waypoints className="h-5 w-5 text-[var(--primary)]" />
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Incident routes</h2>
                    </div>
                    <div className="space-y-3">
                        {routes.length === 0 ? (
                            <div className="rounded-[var(--radius)] border border-dashed border-[var(--border)] px-4 py-8 text-center text-sm text-[var(--text-muted)]">
                                No escalation routes configured yet.
                            </div>
                        ) : (
                            routes.map((route) => (
                                <div key={route.id} className="rounded-[var(--radius)] border border-[var(--border)] p-4">
                                    <div className="flex items-center justify-between gap-4">
                                        <div>
                                            <div className="font-medium text-[var(--text-primary)]">{route.name}</div>
                                            <div className="text-xs text-[var(--text-muted)]">
                                                {route.channel_type} to {route.target}
                                            </div>
                                        </div>
                                        <span className="rounded-full bg-[var(--bg-page)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]">
                                            {route.severity_filter}
                                        </span>
                                    </div>
                                    <div className="mt-3 text-xs text-[var(--text-muted)]">
                                        Active: {route.is_active ? "Yes" : "No"} • Created {new Date(route.created_at).toLocaleString()}
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                </div>

                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-6 shadow-[var(--shadow-card)]">
                    <h2 className="text-lg font-semibold text-[var(--text-primary)]">Add route</h2>
                    <div className="mt-4 space-y-4">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Name</label>
                            <input
                                value={routeForm.name}
                                onChange={(event) => setRouteForm((current) => ({ ...current, name: event.target.value }))}
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                                placeholder="Primary on-call email"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Channel</label>
                            <select
                                value={routeForm.channel_type}
                                onChange={(event) => setRouteForm((current) => ({ ...current, channel_type: event.target.value }))}
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                            >
                                <option value="email">Email</option>
                                <option value="webhook">Webhook</option>
                                <option value="slack">Slack</option>
                            </select>
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Target</label>
                            <input
                                value={routeForm.target}
                                onChange={(event) => setRouteForm((current) => ({ ...current, target: event.target.value }))}
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                                placeholder="alerts@example.com"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Severity filter</label>
                            <select
                                value={routeForm.severity_filter}
                                onChange={(event) => setRouteForm((current) => ({ ...current, severity_filter: event.target.value }))}
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                            >
                                <option value="all">All</option>
                                <option value="critical">Critical</option>
                                <option value="warning">Warning</option>
                                <option value="info">Info</option>
                            </select>
                        </div>
                        <button
                            onClick={() => void handleCreateRoute()}
                            disabled={savingRoute}
                            className="w-full rounded-[var(--radius)] bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
                        >
                            Create route
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}
