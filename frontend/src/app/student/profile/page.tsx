"use client";

import { useEffect, useState } from "react";
import { Calendar, Mail, Save, Shield, User } from "lucide-react";

import { api } from "@/lib/api";

type MePayload = {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    is_active: boolean;
};

export default function ProfilePage() {
    const [profile, setProfile] = useState<MePayload | null>(null);
    const [fullName, setFullName] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = (await api.auth.me()) as MePayload;
                setProfile(payload);
                setFullName(payload.full_name || "");
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load profile");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const saveProfile = async () => {
        if (!profile) return;

        try {
            setSaving(true);
            setError(null);
            setMessage(null);
            const trimmed = fullName.trim();
            await api.auth.updateProfile({ full_name: trimmed || undefined });
            setProfile({ ...profile, full_name: trimmed || null });
            setMessage("Profile updated");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update profile");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Profile</h1>
                <p className="text-sm text-[var(--text-secondary)]">Your account information.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {message ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--success)]/30 bg-green-50 px-4 py-3 text-sm text-[var(--success)]">
                    {message}
                </div>
            ) : null}

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6 max-w-lg">
                <div className="w-16 h-16 bg-[var(--primary-light)] rounded-full flex items-center justify-center mb-4">
                    <User className="w-8 h-8 text-[var(--primary)]" />
                </div>

                {loading || !profile ? (
                    <p className="text-sm text-[var(--text-muted)]">Loading profile...</p>
                ) : (
                    <div className="space-y-4">
                        <div className="flex items-center gap-3">
                            <User className="w-4 h-4 text-[var(--text-muted)]" />
                            <div className="flex-1">
                                <p className="text-xs text-[var(--text-muted)]">Full Name</p>
                                <input
                                    value={fullName}
                                    onChange={(e) => setFullName(e.target.value)}
                                    className="mt-1 w-full px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                                    placeholder="Enter your name"
                                />
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <Mail className="w-4 h-4 text-[var(--text-muted)]" />
                            <div>
                                <p className="text-xs text-[var(--text-muted)]">Email</p>
                                <p className="text-sm font-medium text-[var(--text-primary)]">{profile.email}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <Shield className="w-4 h-4 text-[var(--text-muted)]" />
                            <div>
                                <p className="text-xs text-[var(--text-muted)]">Role</p>
                                <p className="text-sm font-medium text-[var(--text-primary)] capitalize">{profile.role}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-3">
                            <Calendar className="w-4 h-4 text-[var(--text-muted)]" />
                            <div>
                                <p className="text-xs text-[var(--text-muted)]">Account Status</p>
                                <p className="text-sm font-medium text-[var(--text-primary)] capitalize">{profile.is_active ? "Active" : "Inactive"}</p>
                            </div>
                        </div>

                        <div className="pt-2">
                            <button
                                onClick={() => void saveProfile()}
                                disabled={saving}
                                className="px-4 py-2 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-60 flex items-center gap-2"
                            >
                                <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Profile"}
                            </button>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
}
