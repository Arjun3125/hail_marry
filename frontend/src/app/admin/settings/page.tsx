"use client";

import { useEffect, useState } from "react";
import { Settings, Save } from "lucide-react";

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
            setSuccess("Settings saved.");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save settings");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Tenant Settings</h1>
                <p className="text-sm text-[var(--text-secondary)]">Configure your institution&apos;s settings</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}
            {success ? (
                <div className="rounded-[var(--radius)] border border-success-subtle bg-success-subtle px-4 py-3 text-sm text-status-green mb-4">
                    {success}
                </div>
            ) : null}

            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading settings...</p>
            ) : settings ? (
                <div className="max-w-lg space-y-6">
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                        <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                            <Settings className="w-4 h-4" /> General
                        </h2>
                        <div className="space-y-4">
                            <div>
                                <label className="text-xs text-[var(--text-muted)] mb-1 block">School Name</label>
                                <input
                                    type="text"
                                    value={settings.name}
                                    onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-[var(--text-muted)] mb-1 block">AI Queries Per Student Per Day</label>
                                <input
                                    type="number"
                                    value={settings.ai_daily_limit}
                                    onChange={(e) => setSettings({ ...settings, ai_daily_limit: Number(e.target.value) || 0 })}
                                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-[var(--text-muted)] mb-1 block">Max Students</label>
                                <input
                                    type="number"
                                    value={settings.max_students}
                                    disabled
                                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--bg-page)] text-[var(--text-muted)]"
                                />
                                <p className="text-[10px] text-[var(--text-muted)] mt-1">Contact support to change this limit</p>
                            </div>
                            <div>
                                <label className="text-xs text-[var(--text-muted)] mb-1 block">Plan Tier</label>
                                <input
                                    type="text"
                                    value={settings.plan_tier}
                                    disabled
                                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--bg-page)] text-[var(--text-muted)]"
                                />
                            </div>
                            <div>
                                <label className="text-xs text-[var(--text-muted)] mb-1 block">Domain</label>
                                <input
                                    type="text"
                                    value={settings.domain || ""}
                                    disabled
                                    className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--bg-page)] text-[var(--text-muted)]"
                                />
                            </div>
                        </div>
                    </div>

                    <button
                        className="px-6 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] flex items-center gap-2 disabled:opacity-60"
                        onClick={() => void saveSettings()}
                        disabled={saving}
                    >
                        <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Settings"}
                    </button>
                </div>
            ) : (
                <p className="text-sm text-[var(--text-muted)]">No settings found.</p>
            )}
        </div>
    );
}
