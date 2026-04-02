"use client";

import { useEffect, useState } from "react";
import { Settings, Save, Shield, Database, Sparkles, CheckCircle2 } from "lucide-react";

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
            setSuccess("Infrastructure parameters successfully synced.");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save settings");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div className="relative max-w-4xl mx-auto py-8">
            {/* Ambient Background Glow */}
            <div className="absolute top-0 right-0 w-96 h-96 bg-gradient-to-bl from-[var(--primary)]/10 to-transparent blur-[120px] -z-10 rounded-full pointer-events-none" />
            <div className="absolute bottom-0 left-0 w-[500px] h-[500px] bg-gradient-to-tr from-cyan-500/5 to-transparent blur-[120px] -z-10 rounded-full pointer-events-none" />
            
            <div className="mb-10 stagger-1">
                <div className="inline-flex items-center gap-2 px-3 py-1 mb-4 rounded-full glass-panel border-[var(--border)] text-[var(--text-secondary)] text-sm font-medium shadow-sm">
                    <Shield className="w-4 h-4 text-[var(--primary)]" />
                    Global Configuration
                </div>
                <h1 className="text-3xl md:text-5xl font-extrabold text-[var(--text-primary)] tracking-tight">
                    Tenant <span className="premium-gradient">Settings</span>
                </h1>
                <p className="text-base text-[var(--text-secondary)] mt-4 max-w-xl font-light leading-relaxed">
                    Fine-tune your institution&apos;s digital infrastructure, AI token allocation, and core identity parameters across the VidyaOS network.
                </p>
            </div>

            <div className="stagger-2 mb-8">
                {error && (
                    <div className="rounded-2xl border border-[var(--error)]/30 bg-error-subtle px-5 py-4 text-sm text-[var(--error)] flex items-center gap-3 shadow-lg shadow-[var(--error)]/5">
                        <div className="w-2 h-2 rounded-full bg-[var(--error)] animate-pulse shrink-0" />
                        {error}
                    </div>
                )}
                {success && (
                    <div className="rounded-2xl border border-success-subtle bg-success-subtle px-5 py-4 text-sm text-[var(--success)] flex items-center gap-3 shadow-lg shadow-[var(--success)]/5">
                        <CheckCircle2 className="w-5 h-5 shrink-0" />
                        {success}
                    </div>
                )}
            </div>

            {loading ? (
                <div className="glass-panel rounded-3xl p-12 flex flex-col items-center justify-center text-center stagger-3 shadow-inner">
                    <div className="w-12 h-12 border-4 border-[var(--border-strong)] border-t-[var(--primary)] rounded-full animate-spin mb-4" />
                    <p className="text-sm font-semibold text-[var(--text-muted)] animate-pulse">Initializing Configuration Matrix...</p>
                </div>
            ) : settings ? (
                <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 stagger-3">
                    <div className="lg:col-span-2 space-y-6">
                        {/* Main Settings Card */}
                        <div className="glass-panel border border-[var(--border-strong)] rounded-3xl shadow-xl shadow-[var(--primary)]/5 p-6 sm:p-8 relative overflow-hidden group">
                            {/* Decorative Top Glow */}
                            <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-transparent via-[var(--primary)]/30 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-700" />
                            
                            <h2 className="text-lg font-bold text-[var(--text-primary)] mb-6 flex items-center gap-3">
                                <div className="p-2 glass-panel rounded-xl text-[var(--primary)] shadow-inner">
                                    <Settings className="w-5 h-5" />
                                </div>
                                System Parameters
                            </h2>
                            
                            <div className="space-y-6">
                                <div>
                                    <label className="text-xs font-bold tracking-wider uppercase text-[var(--text-muted)] mb-2 block">Institution Identifier</label>
                                    <input
                                        type="text"
                                        value={settings.name}
                                        onChange={(e) => setSettings({ ...settings, name: e.target.value })}
                                        className="w-full px-5 py-3.5 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-2xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition-all shadow-inner text-[var(--text-primary)] font-medium"
                                    />
                                </div>
                                <div>
                                    <label className="text-xs font-bold tracking-wider uppercase text-[var(--text-muted)] mb-2 block flex items-center gap-2">
                                        <Sparkles className="w-3.5 h-3.5 text-amber-500" />
                                        AI Query Allocation (Per Student/Day)
                                    </label>
                                    <input
                                        type="number"
                                        value={settings.ai_daily_limit}
                                        onChange={(e) => setSettings({ ...settings, ai_daily_limit: Number(e.target.value) || 0 })}
                                        className="w-full px-5 py-3.5 text-sm bg-[var(--bg-page)]/50 border border-[var(--border-strong)] rounded-2xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent transition-all shadow-inner text-[var(--text-primary)] font-medium"
                                    />
                                </div>
                            </div>
                        </div>

                        {/* Save Actions */}
                        <div className="flex justify-end p-2">
                            <button
                                className="px-8 py-3.5 bg-[var(--primary)] text-white text-sm font-bold rounded-full hover:bg-[var(--primary-hover)] transition-all flex items-center gap-3 shadow-xl shadow-[var(--primary)]/30 disabled:opacity-60 hover:-translate-y-0.5"
                                onClick={() => void saveSettings()}
                                disabled={saving}
                            >
                                <Save className="w-4 h-4" /> 
                                {saving ? "Ammending Matrix..." : "Commit Configuration"}
                            </button>
                        </div>
                    </div>

                    {/* Sidebar / Readonly Specs */}
                    <div className="space-y-6">
                        <div className="glass-panel border border-[var(--border-strong)] rounded-3xl shadow-lg p-6 relative group overflow-hidden">
                            <div className="absolute inset-0 bg-gradient-to-br from-[var(--bg-page)] to-transparent -z-10" />
                            <h2 className="text-sm font-bold text-[var(--text-primary)] mb-5 flex items-center gap-2">
                                <Database className="w-4 h-4 text-[var(--text-secondary)]" />
                                Hardware & Licensing
                            </h2>

                            <div className="space-y-5">
                                <div className="p-4 rounded-2xl bg-[var(--bg-page)]/50 border border-[var(--border)]">
                                    <label className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] block mb-1">Active Plan Tier</label>
                                    <p className="text-sm font-black premium-text capitalize">{settings.plan_tier}</p>
                                </div>

                                <div className="p-4 rounded-2xl bg-[var(--bg-page)]/50 border border-[var(--border)]">
                                    <label className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] block mb-1 flex items-center gap-2">Max User Nodes</label>
                                    <p className="text-sm font-bold text-[var(--text-primary)] font-mono">{settings.max_students}</p>
                                    <p className="text-[10px] text-[var(--text-muted)] mt-1.5 font-medium leading-relaxed">Hard limit reached. Scale infrastructure via enterprise support.</p>
                                </div>

                                <div className="p-4 rounded-2xl bg-[var(--bg-page)]/50 border border-[var(--border)]">
                                    <label className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)] block mb-1">Network Domain</label>
                                    <p className="text-sm font-semibold text-[var(--text-secondary)] font-mono truncate">{settings.domain || "N/A"}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            ) : (
                <div className="glass-panel rounded-3xl p-12 flex items-center justify-center border-dashed border-2 border-[var(--border)] stagger-3">
                    <p className="text-sm font-medium text-[var(--text-muted)]">Configuration node offline.</p>
                </div>
            )}
        </div>
    );
}
