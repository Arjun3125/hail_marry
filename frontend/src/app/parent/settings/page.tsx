"use client";

import { useCallback, useEffect, useState } from "react";
import { Bell, Clock, MessageCircle, Mail, Smartphone, Eye, Loader2, CheckCircle2, AlertCircle } from "lucide-react";
import { api } from "@/lib/api";
import { PrismPage, PrismPageIntro, PrismPanel, PrismSectionHeader } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";

interface NotificationPreferences {
    whatsapp_enabled: boolean;
    sms_enabled: boolean;
    email_enabled: boolean;
    push_enabled: boolean;
    in_app_enabled: boolean;
    quiet_hours_start: string | null;
    quiet_hours_end: string | null;
    category_overrides: Record<string, boolean> | null;
}

const DEFAULT_PREFS: NotificationPreferences = {
    whatsapp_enabled: true,
    sms_enabled: false,
    email_enabled: true,
    push_enabled: true,
    in_app_enabled: true,
    quiet_hours_start: null,
    quiet_hours_end: null,
    category_overrides: {
        assignment_reminder: true,
        low_attendance: true,
        assessment_results: true,
    },
};

export default function ParentSettingsPage() {
    const [prefs, setPrefs] = useState<NotificationPreferences>(DEFAULT_PREFS);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState(false);

    // Fetch preferences on mount
    useEffect(() => {
        const fetchPrefs = async () => {
            try {
                setLoading(true);
                const result = await api.parent.notificationPreferences();
                setPrefs(result);
                setError(null);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load preferences");
                console.error("Error fetching preferences:", err);
            } finally {
                setLoading(false);
            }
        };
        fetchPrefs();
    }, []);

    const handleToggleChannel = useCallback(
        (channel: "whatsapp_enabled" | "sms_enabled" | "email_enabled" | "push_enabled" | "in_app_enabled") => {
            setPrefs((prev) => ({
                ...prev,
                [channel]: !prev[channel],
            }));
        },
        []
    );

    const handleToggleCategory = useCallback((category: string) => {
        setPrefs((prev) => ({
            ...prev,
            category_overrides: {
                ...prev.category_overrides,
                [category]: !prev.category_overrides?.[category],
            },
        }));
    }, []);

    const handleQuietHoursChange = useCallback((start: string, end: string) => {
        setPrefs((prev) => ({
            ...prev,
            quiet_hours_start: start && start !== "" ? start : null,
            quiet_hours_end: end && end !== "" ? end : null,
        }));
    }, []);

    const handleSave = async () => {
        try {
            setSaving(true);
            setSuccess(false);
            await api.parent.updateNotificationPreferences(prefs);
            setSuccess(true);
            setTimeout(() => setSuccess(false), 3000);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save preferences");
            console.error("Error saving preferences:", err);
        } finally {
            setSaving(false);
        }
    };

    if (loading) {
        return (
            <PrismPage>
                <PrismPageIntro title="Notification Settings" description="Coming right up..." />
                <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-6 h-6 animate-spin text-primary" />
                </div>
            </PrismPage>
        );
    }

    return (
        <PrismPage>
            <PrismPageIntro
                title="Notification Settings"
                description="Manage how you receive updates about your child's school activities"
            />

            {error && <ErrorRemediation error={error} scope="parent-settings" onRetry={() => setError(null)} />}

            {success && (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6 flex items-start gap-3">
                    <CheckCircle2 className="w-5 h-5 text-green-600 flex-shrink-0 mt-0.5" />
                    <div>
                        <h3 className="font-semibold text-green-900">Preferences saved</h3>
                        <p className="text-sm text-green-800">Your notification settings have been updated.</p>
                    </div>
                </div>
            )}

            {/* Notification Channels */}
            <PrismPanel className="mb-6">
                <PrismSectionHeader title="Communication Channels" />

                <div className="space-y-4">
                    {/* WhatsApp */}
                    <label className="flex items-center gap-4 p-4 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.whatsapp_enabled}
                            onChange={() => handleToggleChannel("whatsapp_enabled")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <MessageCircle className="w-4 h-4 text-green-600" />
                                <span className="font-semibold">WhatsApp</span>
                            </div>
                            <p className="text-sm text-secondary">Receive notifications on WhatsApp (recommended for parents in India)</p>
                        </div>
                        <div className="text-xs font-semibold text-primary">{prefs.whatsapp_enabled ? "ON" : "OFF"}</div>
                    </label>

                    {/* Email */}
                    <label className="flex items-center gap-4 p-4 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.email_enabled}
                            onChange={() => handleToggleChannel("email_enabled")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <Mail className="w-4 h-4 text-blue-600" />
                                <span className="font-semibold">Email</span>
                            </div>
                            <p className="text-sm text-secondary">Receive notifications to your email address</p>
                        </div>
                        <div className="text-xs font-semibold text-primary">{prefs.email_enabled ? "ON" : "OFF"}</div>
                    </label>

                    {/* Push Notifications */}
                    <label className="flex items-center gap-4 p-4 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.push_enabled}
                            onChange={() => handleToggleChannel("push_enabled")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <Bell className="w-4 h-4 text-orange-600" />
                                <span className="font-semibold">Push Notifications</span>
                            </div>
                            <p className="text-sm text-secondary">Receive instant alerts in your browser and app</p>
                        </div>
                        <div className="text-xs font-semibold text-primary">{prefs.push_enabled ? "ON" : "OFF"}</div>
                    </label>

                    {/* In-App */}
                    <label className="flex items-center gap-4 p-4 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.in_app_enabled}
                            onChange={() => handleToggleChannel("in_app_enabled")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <div className="flex items-center gap-2">
                                <Eye className="w-4 h-4 text-purple-600" />
                                <span className="font-semibold">In-App Notifications</span>
                            </div>
                            <p className="text-sm text-secondary">Show notification cards in the VidyaOS app</p>
                        </div>
                        <div className="text-xs font-semibold text-primary">{prefs.in_app_enabled ? "ON" : "OFF"}</div>
                    </label>
                </div>
            </PrismPanel>

            {/* Notification Types */}
            <PrismPanel className="mb-6">
                <PrismSectionHeader title="Notification Types" />

                <div className="space-y-3">
                    <label className="flex items-center gap-4 p-3 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.category_overrides?.assignment_reminder ?? true}
                            onChange={() => handleToggleCategory("assignment_reminder")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <p className="font-semibold">📝 Assignment Reminders</p>
                            <p className="text-sm text-secondary">Notified when assignments are due</p>
                        </div>
                    </label>

                    <label className="flex items-center gap-4 p-3 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.category_overrides?.assessment_results ?? true}
                            onChange={() => handleToggleCategory("assessment_results")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <p className="font-semibold">📊 Assessment Results</p>
                            <p className="text-sm text-secondary">Notified when exam results are available</p>
                        </div>
                    </label>

                    <label className="flex items-center gap-4 p-3 border border-subtle rounded-lg cursor-pointer hover:bg-accent/5 transition">
                        <input
                            type="checkbox"
                            checked={prefs.category_overrides?.low_attendance ?? true}
                            onChange={() => handleToggleCategory("low_attendance")}
                            className="w-5 h-5 rounded"
                        />
                        <div className="flex-1">
                            <p className="font-semibold">⚠️ Low Attendance Alerts</p>
                            <p className="text-sm text-secondary">Alerted if attendance drops below threshold</p>
                        </div>
                    </label>
                </div>
            </PrismPanel>

            {/* Quiet Hours */}
            <PrismPanel className="mb-6">
                <PrismSectionHeader title="Quiet Hours" />

                <p className="text-sm text-secondary mb-4">
                    Prevent notifications during these hours. Leave empty to disable quiet hours.
                </p>

                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-semibold mb-2">Start Time</label>
                        <input
                            type="time"
                            value={prefs.quiet_hours_start || ""}
                            onChange={(e) =>
                                handleQuietHoursChange(e.target.value, prefs.quiet_hours_end || "")
                            }
                            className="w-full px-3 py-2 border border-subtle rounded-lg font-mono"
                        />
                        <p className="text-xs text-secondary mt-1">e.g., 22:00 (10 PM)</p>
                    </div>

                    <div>
                        <label className="block text-sm font-semibold mb-2">End Time</label>
                        <input
                            type="time"
                            value={prefs.quiet_hours_end || ""}
                            onChange={(e) =>
                                handleQuietHoursChange(prefs.quiet_hours_start || "", e.target.value)
                            }
                            className="w-full px-3 py-2 border border-subtle rounded-lg font-mono"
                        />
                        <p className="text-xs text-secondary mt-1">e.g., 07:00 (7 AM)</p>
                    </div>
                </div>

                {prefs.quiet_hours_start && prefs.quiet_hours_end && (
                    <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded-lg flex items-start gap-2">
                        <AlertCircle className="w-4 h-4 text-blue-600 flex-shrink-0 mt-0.5" />
                        <div className="text-sm text-blue-900">
                            Quiet hours enabled from <span className="font-semibold">{prefs.quiet_hours_start}</span> to{" "}
                            <span className="font-semibold">{prefs.quiet_hours_end}</span>
                        </div>
                    </div>
                )}
            </PrismPanel>

            {/* Save Button */}
            <div className="flex gap-3">
                <button
                    onClick={handleSave}
                    disabled={saving}
                    className="px-6 py-2 bg-primary text-primary-foreground rounded-lg font-semibold hover:opacity-90 disabled:opacity-50 flex items-center gap-2"
                >
                    {saving ? <Loader2 className="w-4 h-4 animate-spin" /> : <CheckCircle2 className="w-4 h-4" />}
                    {saving ? "Saving..." : "Save Preferences"}
                </button>
            </div>
        </PrismPage>
    );
}
