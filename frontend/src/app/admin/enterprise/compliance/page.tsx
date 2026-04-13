"use client";

import { useEffect, useState } from "react";
import { Download, Settings, ShieldCheck, Trash2 } from "lucide-react";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismSection } from "@/components/prism/PrismPage";
import { api } from "@/lib/api";
import { logger } from "@/lib/logger";

type ComplianceSettings = {
    data_retention_days: number;
    export_retention_days: number;
};

type ComplianceExport = {
    id: string;
    export_type: string;
    scope_type: string;
    format: string;
    status: "pending" | "processing" | "completed" | "failed";
    file_path?: string | null;
    created_at: string;
    completed_at?: string | null;
};

type DeletionRequest = {
    id: string;
    target_user_id?: string | null;
    status: string;
    reason: string;
    resolution_note?: string | null;
    created_at: string;
    resolved_at?: string | null;
};

export default function CompliancePage() {
    const [activeTab, setActiveTab] = useState<"exports" | "deletions" | "settings">("exports");
    const [settings, setSettings] = useState<ComplianceSettings>({
        data_retention_days: 365,
        export_retention_days: 30,
    });
    const [exports, setExports] = useState<ComplianceExport[]>([]);
    const [deletions, setDeletions] = useState<DeletionRequest[]>([]);
    const [deletionReason, setDeletionReason] = useState("");
    const [targetUserId, setTargetUserId] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const load = async () => {
        try {
            setLoading(true);
            setError(null);
            const [settingsData, exportData, deletionData] = await Promise.all([
                api.enterprise.complianceSettings(),
                api.enterprise.complianceExports(),
                api.enterprise.deletionRequests(),
            ]);
            setSettings(settingsData);
            setExports(exportData || []);
            setDeletions(deletionData || []);
        } catch (err) {
            logger.error("Failed to load compliance data", err as Error);
            setError("Failed to load compliance data.");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void load();
    }, []);

    const handleCreateExport = async () => {
        try {
            setSaving(true);
            await api.enterprise.createComplianceExport({ scope_type: "tenant" });
            await load();
        } catch (err) {
            logger.error("Failed to queue export", err as Error);
            setError("Failed to queue compliance export.");
        } finally {
            setSaving(false);
        }
    };

    const handleCreateDeletionRequest = async () => {
        if (!deletionReason.trim()) {
            setError("Deletion reason is required.");
            return;
        }

        try {
            setSaving(true);
            await api.enterprise.createDeletionRequest({
                target_user_id: targetUserId.trim() || undefined,
                reason: deletionReason.trim(),
            });
            setDeletionReason("");
            setTargetUserId("");
            await load();
        } catch (err) {
            logger.error("Failed to create deletion request", err as Error);
            setError("Failed to create deletion request.");
        } finally {
            setSaving(false);
        }
    };

    const handleResolveDeletion = async (id: string) => {
        const note = window.prompt("Resolution note:");
        if (note === null) return;

        try {
            setSaving(true);
            await api.enterprise.resolveDeletionRequest(id, note);
            await load();
        } catch (err) {
            logger.error("Failed to resolve deletion request", err as Error);
            setError("Failed to resolve deletion request.");
        } finally {
            setSaving(false);
        }
    };

    const handleSaveSettings = async () => {
        try {
            setSaving(true);
            await api.enterprise.updateComplianceSettings(settings);
            await load();
        } catch (err) {
            logger.error("Failed to update compliance settings", err as Error);
            setError("Failed to save retention settings.");
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <PrismPage variant="dashboard" className="space-y-6 pb-8">
                <PrismSection className="space-y-6">
                    <div className="p-8 text-center text-[var(--text-muted)]">Loading compliance controls...</div>
                </PrismSection>
            </PrismPage>
        );
    }

    return (
        <PrismPage variant="dashboard" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <PrismPageIntro
                        kicker={(
                            <PrismHeroKicker>
                                <ShieldCheck className="h-3.5 w-3.5" />
                                Enterprise Compliance Surface
                            </PrismHeroKicker>
                        )}
                        title="Keep privacy and retention controls explicit"
                        description="Manage exports, deletion workflows, and retention controls for tenant data from one enterprise compliance workspace."
                    />
                </div>
                <button
                    onClick={() => void load()}
                    className="rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] px-4 py-2 text-sm text-[var(--text-secondary)] hover:bg-[var(--bg-page)]"
                >
                    Refresh
                </button>
            </div>

            {error && (
                <div className="rounded-[var(--radius)] border border-[var(--error)] bg-[var(--error-subtle)] px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}

            <div className="grid gap-4 md:grid-cols-3">
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Exports queued</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{exports.length}</p>
                </div>
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Deletion requests</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{deletions.length}</p>
                </div>
                <div className="rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                    <p className="text-xs font-medium text-[var(--text-muted)]">Retention window</p>
                    <p className="mt-2 text-2xl font-bold text-[var(--text-primary)]">{settings.data_retention_days}d</p>
                </div>
            </div>

            <div className="flex border-b border-[var(--border)]">
                {[
                    { id: "exports", label: "Exports", icon: Download },
                    { id: "deletions", label: "Deletion Requests", icon: Trash2 },
                    { id: "settings", label: "Retention Settings", icon: Settings },
                ].map((tab) => {
                    const Icon = tab.icon;
                    const selected = activeTab === tab.id;
                    return (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as typeof activeTab)}
                            className={`flex items-center gap-2 border-b-2 px-4 py-3 text-sm font-medium transition-colors ${
                                selected
                                    ? "border-[var(--primary)] text-[var(--primary)]"
                                    : "border-transparent text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                            }`}
                        >
                            <Icon className="h-4 w-4" />
                            {tab.label}
                        </button>
                    );
                })}
            </div>

            {activeTab === "exports" && (
                <div className="space-y-4">
                    <div className="flex items-center justify-between rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                        <div>
                            <h2 className="text-sm font-semibold text-[var(--text-primary)]">Create tenant export</h2>
                            <p className="text-xs text-[var(--text-muted)]">
                                Queue a compliance export for the current tenant dataset.
                            </p>
                        </div>
                        <button
                            onClick={() => void handleCreateExport()}
                            disabled={saving}
                            className="rounded-[var(--radius)] bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
                        >
                            Request Export
                        </button>
                    </div>

                    <div className="overflow-hidden rounded-[var(--radius)] bg-[var(--bg-card)] shadow-[var(--shadow-card)]">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead>
                                    <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Export</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Status</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Created</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Completed</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Artifact</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[var(--border-light)]">
                                    {exports.length === 0 ? (
                                        <tr>
                                            <td colSpan={5} className="px-6 py-10 text-center text-[var(--text-muted)]">
                                                No compliance exports have been requested yet.
                                            </td>
                                        </tr>
                                    ) : (
                                        exports.map((item) => (
                                            <tr key={item.id}>
                                                <td className="px-6 py-4">
                                                    <div className="font-medium text-[var(--text-primary)]">{item.export_type}</div>
                                                    <div className="text-xs text-[var(--text-muted)]">
                                                        Scope: {item.scope_type} • Format: {item.format}
                                                    </div>
                                                </td>
                                                <td className="px-6 py-4">
                                                    <span className="rounded-full bg-[var(--bg-page)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]">
                                                        {item.status.toUpperCase()}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-xs text-[var(--text-secondary)]">
                                                    {new Date(item.created_at).toLocaleString()}
                                                </td>
                                                <td className="px-6 py-4 text-xs text-[var(--text-secondary)]">
                                                    {item.completed_at ? new Date(item.completed_at).toLocaleString() : "Pending"}
                                                </td>
                                                <td className="px-6 py-4 text-xs text-[var(--text-muted)]">
                                                    {item.file_path || "Not generated yet"}
                                                </td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {activeTab === "deletions" && (
                <div className="space-y-4">
                    <div className="grid gap-4 rounded-[var(--radius)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)] md:grid-cols-[1fr_1fr_auto]">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Target User ID</label>
                            <input
                                value={targetUserId}
                                onChange={(event) => setTargetUserId(event.target.value)}
                                placeholder="Optional UUID"
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Reason</label>
                            <input
                                value={deletionReason}
                                onChange={(event) => setDeletionReason(event.target.value)}
                                placeholder="Reason for deletion request"
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                            />
                        </div>
                        <div className="flex items-end">
                            <button
                                onClick={() => void handleCreateDeletionRequest()}
                                disabled={saving}
                                className="w-full rounded-[var(--radius)] bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
                            >
                                Submit
                            </button>
                        </div>
                    </div>

                    <div className="overflow-hidden rounded-[var(--radius)] bg-[var(--bg-card)] shadow-[var(--shadow-card)]">
                        <div className="overflow-x-auto">
                            <table className="w-full text-left text-sm">
                                <thead>
                                    <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Target</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Reason</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Status</th>
                                        <th className="px-6 py-3 text-[var(--text-muted)]">Timeline</th>
                                        <th className="px-6 py-3 text-right text-[var(--text-muted)]">Action</th>
                                    </tr>
                                </thead>
                                <tbody className="divide-y divide-[var(--border-light)]">
                                    {deletions.length === 0 ? (
                                        <tr>
                                            <td colSpan={5} className="px-6 py-10 text-center text-[var(--text-muted)]">
                                                No deletion requests found.
                                            </td>
                                        </tr>
                                    ) : (
                                        deletions.map((item) => (
                                            <tr key={item.id}>
                                                <td className="px-6 py-4 font-medium text-[var(--text-primary)]">
                                                    {item.target_user_id || "Tenant-wide request"}
                                                </td>
                                                <td className="px-6 py-4 text-[var(--text-secondary)]">{item.reason || "No reason provided"}</td>
                                                <td className="px-6 py-4">
                                                    <span className="rounded-full bg-[var(--bg-page)] px-2 py-0.5 text-xs font-medium text-[var(--text-secondary)]">
                                                        {item.status.toUpperCase()}
                                                    </span>
                                                </td>
                                                <td className="px-6 py-4 text-xs text-[var(--text-muted)]">
                                                    <div>Requested: {new Date(item.created_at).toLocaleString()}</div>
                                                    <div>Resolved: {item.resolved_at ? new Date(item.resolved_at).toLocaleString() : "Pending"}</div>
                                                </td>
                                                <td className="px-6 py-4 text-right">
                                                    {item.status !== "resolved" && (
                                                        <button
                                                            onClick={() => void handleResolveDeletion(item.id)}
                                                            className="text-xs font-medium text-[var(--primary)] hover:underline"
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
                </div>
            )}

            {activeTab === "settings" && (
                <div className="max-w-2xl rounded-[var(--radius)] bg-[var(--bg-card)] p-6 shadow-[var(--shadow-card)]">
                    <div className="mb-4 flex items-center gap-2">
                        <ShieldCheck className="h-5 w-5 text-[var(--primary)]" />
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Retention settings</h2>
                    </div>
                    <div className="space-y-5">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Data retention days</label>
                            <input
                                type="number"
                                min={1}
                                value={settings.data_retention_days}
                                onChange={(event) => setSettings((current) => ({
                                    ...current,
                                    data_retention_days: Number(event.target.value) || 1,
                                }))}
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Export retention days</label>
                            <input
                                type="number"
                                min={1}
                                value={settings.export_retention_days}
                                onChange={(event) => setSettings((current) => ({
                                    ...current,
                                    export_retention_days: Number(event.target.value) || 1,
                                }))}
                                className="w-full rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-page)] px-3 py-2 text-sm"
                            />
                        </div>
                        <button
                            onClick={() => void handleSaveSettings()}
                            disabled={saving}
                            className="rounded-[var(--radius)] bg-[var(--primary)] px-5 py-2 text-sm font-medium text-white hover:opacity-90 disabled:opacity-60"
                        >
                            Save settings
                        </button>
                    </div>
                </div>
            )}
            </PrismSection>
        </PrismPage>
    );
}
