"use client";

import { useEffect, useState } from "react";
import { Key, Save, ShieldCheck, Globe, UserCheck } from "lucide-react";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismSection } from "@/components/prism/PrismPage";
import { api } from "@/lib/api";
import { logger } from "@/lib/logger";

export default function SSOSettingsPage() {
    const [settings, setSettings] = useState({
        enabled: false,
        entity_id: "",
        metadata_url: "",
        attribute_email: "email",
        attribute_name: "name",
    });
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [message, setMessage] = useState<{ type: "success" | "error"; text: string } | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                const data = await api.enterprise.ssoSettings();
                if (data) setSettings(data);
            } catch (err) {
                logger.error("Failed to load SSO settings", err as Error);
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const handleSave = async (e: React.FormEvent) => {
        e.preventDefault();
        try {
            setSaving(true);
            setMessage(null);
            await api.enterprise.updateSSOSettings(settings);
            setMessage({ type: "success", text: "SSO settings updated successfully" });
        } catch (err) {
            setMessage({ type: "error", text: err instanceof Error ? err.message : "Failed to save settings" });
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <PrismPage variant="form" className="max-w-4xl space-y-6 pb-8">
                <PrismSection className="space-y-6">
                    <div className="p-8 text-center text-[var(--text-muted)]">Loading SSO configuration...</div>
                </PrismSection>
            </PrismPage>
        );
    }

    return (
        <PrismPage variant="form" className="max-w-4xl space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ShieldCheck className="h-3.5 w-3.5" />
                            Enterprise SSO Surface
                        </PrismHeroKicker>
                    )}
                    title="Manage SAML identity control without leaving the admin shell"
                    description="Configure enterprise single sign-on, metadata routing, and attribute mapping from one dedicated SSO workspace."
                />

            {message && (
                <div className={`mb-6 p-4 rounded-[var(--radius)] text-sm ${
                    message.type === "success" ? "bg-[var(--success-subtle)] text-[var(--success)]" : "bg-[var(--error-subtle)] text-[var(--error)]"
                }`}>
                    {message.text}
                </div>
            )}

            <form onSubmit={handleSave} className="space-y-6">
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
                    <div className="flex items-center justify-between mb-6">
                        <div className="flex items-center gap-3">
                            <div className="p-2 bg-[var(--primary-subtle)] rounded-lg">
                                <ShieldCheck className="w-5 h-5 text-[var(--primary)]" />
                            </div>
                            <div>
                                <h2 className="text-lg font-semibold text-[var(--text-primary)]">Authentication State</h2>
                                <p className="text-xs text-[var(--text-muted)]">Enable or disable SSO for this tenant</p>
                            </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                            <input
                                type="checkbox"
                                className="sr-only peer"
                                checked={settings.enabled}
                                onChange={(e) => setSettings({ ...settings, enabled: e.target.checked })}
                            />
                            <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-[var(--primary)]"></div>
                        </label>
                    </div>

                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)] flex items-center gap-2">
                                <Globe className="w-4 h-4" /> Entity ID (Audience Restriction)
                            </label>
                            <input
                                type="text"
                                className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius)] px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                placeholder="https://vidyaos.com/saml/metadata"
                                value={settings.entity_id}
                                onChange={(e) => setSettings({ ...settings, entity_id: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)] flex items-center gap-2">
                                <Key className="w-4 h-4" /> Metadata URL (IdP)
                            </label>
                            <input
                                type="url"
                                className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius)] px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                placeholder="https://idp.example.com/metadata.xml"
                                value={settings.metadata_url}
                                onChange={(e) => setSettings({ ...settings, metadata_url: e.target.value })}
                            />
                        </div>
                    </div>
                </div>

                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
                    <h2 className="text-lg font-semibold text-[var(--text-primary)] mb-4 flex items-center gap-2">
                        <UserCheck className="w-5 h-5 text-[var(--primary)]" /> Attribute Mapping
                    </h2>
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Email Attribute</label>
                            <input
                                type="text"
                                className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius)] px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                value={settings.attribute_email}
                                onChange={(e) => setSettings({ ...settings, attribute_email: e.target.value })}
                            />
                        </div>
                        <div className="space-y-2">
                            <label className="text-sm font-medium text-[var(--text-secondary)]">Full Name Attribute</label>
                            <input
                                type="text"
                                className="w-full bg-[var(--bg-page)] border border-[var(--border)] rounded-[var(--radius)] px-4 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                value={settings.attribute_name}
                                onChange={(e) => setSettings({ ...settings, attribute_name: e.target.value })}
                            />
                        </div>
                    </div>
                </div>

                <div className="flex justify-end">
                    <button
                        type="submit"
                        disabled={saving}
                        className="flex items-center gap-2 bg-[var(--primary)] text-white px-6 py-2 rounded-[var(--radius)] font-medium hover:opacity-90 transition-opacity disabled:opacity-50"
                    >
                        <Save className="w-4 h-4" />
                        {saving ? "Saving..." : "Save SSO Configuration"}
                    </button>
                </div>
            </form>
            </PrismSection>
        </PrismPage>
    );
}
