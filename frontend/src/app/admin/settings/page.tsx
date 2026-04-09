"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Database, Save, Settings, Shield, Sparkles } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type TenantSettings = {
    name: string;
    plan_tier: string;
    max_students: number;
    ai_daily_limit: number;
    domain: string;
};

export default function AdminSettingsPage() {
    const [settings, setSettings] = useState<TenantSettings | null>(null);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.admin.settings();
                setSettings(payload as TenantSettings);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load settings");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const saveSettings = async () => {
        if (!settings) return;
        try {
            setSaving(true);
            setError(null);
            setSuccess(null);
            await api.admin.updateSettings({
                name: settings.name,
                ai_daily_limit: settings.ai_daily_limit,
            });
            setSuccess("Tenant configuration was updated successfully.");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save settings");
        } finally {
            setSaving(false);
        }
    };

    const summary = useMemo(() => ({
        plan: settings?.plan_tier || "-",
        capacity: settings ? `${settings.max_students}` : "-",
        aiLimit: settings ? `${settings.ai_daily_limit}` : "-",
    }), [settings]);

    return (
        <PrismPage variant="form" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Shield className="h-3.5 w-3.5" />
                            Admin Settings Surface
                        </PrismHeroKicker>
                    )}
                    title="Keep tenant controls explicit and reviewable"
                    description="Adjust institution identity and AI allowance without losing sight of plan limits, capacity, and the active network domain."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Update scope</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                This surface is for controlled tenant-level changes only. Treat plan tier and capacity as reference constraints, not editable runtime switches.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Plan tier</span>
                        <span className="prism-status-value">{summary.plan}</span>
                        <span className="prism-status-detail">Current commercial and infrastructure tier for this tenant.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Capacity</span>
                        <span className="prism-status-value">{summary.capacity}</span>
                        <span className="prism-status-detail">Maximum student volume currently allocated to the tenant.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">AI daily limit</span>
                        <span className="prism-status-value">{summary.aiLimit}</span>
                        <span className="prism-status-detail">Per-student daily AI allowance currently configured.</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-settings"
                        onRetry={() => {
                            window.location.reload();
                        }}
                    />
                ) : null}

                {success ? (
                    <div className="rounded-2xl border border-success-subtle bg-success-subtle px-5 py-4 text-sm text-[var(--success)] flex items-center gap-3">
                        <CheckCircle2 className="h-5 w-5 shrink-0" />
                        {success}
                    </div>
                ) : null}

                {loading ? (
                    <PrismPanel className="p-10">
                        <div className="flex items-center gap-3 text-sm text-[var(--text-muted)]">
                            <Settings className="h-4 w-4 animate-pulse" />
                            Loading tenant configuration...
                        </div>
                    </PrismPanel>
                ) : !settings ? (
                    <EmptyState
                        icon={Settings}
                        title="Settings are unavailable"
                        description="The tenant configuration could not be loaded for this environment."
                        eyebrow="Configuration unavailable"
                        scopeNote="This surface depends on the admin settings endpoint being available and returning tenant metadata."
                    />
                ) : (
                    <div className="grid gap-6 xl:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
                        <PrismPanel className="p-6">
                            <div className="space-y-6">
                                <div>
                                    <h2 className="text-lg font-semibold text-[var(--text-primary)]">Tenant configuration</h2>
                                    <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                        Update the institution label and AI allowance while keeping infrastructure limits visible.
                                    </p>
                                </div>

                                <div className="space-y-5">
                                    <div>
                                        <label className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                            Institution name
                                        </label>
                                        <input
                                            type="text"
                                            value={settings.name}
                                            onChange={(event) => setSettings({ ...settings, name: event.target.value })}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                        />
                                    </div>

                                    <div>
                                        <label className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                            <Sparkles className="h-3.5 w-3.5 text-amber-500" />
                                            AI daily limit
                                        </label>
                                        <input
                                            type="number"
                                            value={settings.ai_daily_limit}
                                            onChange={(event) => setSettings({ ...settings, ai_daily_limit: Number(event.target.value) || 0 })}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                        />
                                    </div>
                                </div>

                                <div className="flex justify-end">
                                    <button
                                        className="prism-action inline-flex items-center gap-2"
                                        onClick={() => void saveSettings()}
                                        disabled={saving}
                                    >
                                        <Save className="h-4 w-4" />
                                        {saving ? "Saving configuration..." : "Save configuration"}
                                    </button>
                                </div>
                            </div>
                        </PrismPanel>

                        <div className="space-y-6">
                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Database className="h-4 w-4 text-[var(--primary)]" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Infrastructure reference</h2>
                                </div>
                                <div className="mt-4 space-y-3">
                                    <ReferenceCard title="Plan tier" value={settings.plan_tier} summary="Current commercial and support tier." />
                                    <ReferenceCard title="Maximum students" value={`${settings.max_students}`} summary="Allocated student capacity for this tenant." />
                                    <ReferenceCard title="Network domain" value={settings.domain || "N/A"} summary="Current public domain or tenant routing label." />
                                </div>
                            </PrismPanel>
                        </div>
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function ReferenceCard({ title, value, summary }: { title: string; value: string; summary: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
            <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 break-all text-sm font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </div>
    );
}
