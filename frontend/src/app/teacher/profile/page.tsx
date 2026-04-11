"use client";

import { useEffect, useState } from "react";
import { Calendar, Mail, Save, Shield, User } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type MePayload = {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    is_active: boolean;
};

type TeacherProfileSummary = {
    classes_in_scope: number;
    students_supported: number;
    documents_uploaded: number;
    lectures_indexed: number;
    assignments_created: number;
    ai_requests: number;
    latest_milestones: {
        last_upload_at?: string | null;
        last_lecture_at?: string | null;
    };
};

export default function TeacherProfilePage() {
    const [profile, setProfile] = useState<MePayload | null>(null);
    const [summary, setSummary] = useState<TeacherProfileSummary | null>(null);
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
                const [payload, summaryPayload] = await Promise.all([
                    api.auth.me() as Promise<MePayload>,
                    api.teacher.profileSummary() as Promise<TeacherProfileSummary>,
                ]);
                setProfile(payload);
                setSummary(summaryPayload);
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
            setMessage("Profile updated.");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update profile");
        } finally {
            setSaving(false);
        }
    };

    return (
        <PrismPage variant="form" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <User className="h-3.5 w-3.5" />
                            Teacher Profile Surface
                        </PrismHeroKicker>
                    )}
                    title="Keep your teacher identity current and reviewable"
                    description="Update your display name while keeping email, role, and account status visible in one profile workspace."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">What changes here</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                This page is for personal account details only. Operational permissions and role access are still managed elsewhere.
                            </p>
                        </div>
                    )}
                />

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="teacher-profile"
                        onRetry={() => window.location.reload()}
                    />
                ) : null}

                {message ? (
                    <div className="rounded-2xl border border-success-subtle bg-success-subtle px-5 py-4 text-sm text-[var(--success)]">
                        {message}
                    </div>
                ) : null}

                {loading ? (
                    <PrismPanel className="p-10">
                        <div className="flex items-center gap-3 text-sm text-[var(--text-muted)]">
                            <User className="h-4 w-4 animate-pulse" />
                            Loading profile...
                        </div>
                    </PrismPanel>
                ) : !profile ? (
                    <EmptyState
                        icon={User}
                        title="Profile is unavailable"
                        description="Your account details could not be loaded for this session."
                        eyebrow="Profile unavailable"
                        scopeNote="This surface depends on the authenticated teacher profile endpoint being available."
                    />
                ) : (
                    <>
                        <div className="prism-status-strip">
                            <div className="prism-status-item">
                                <span className="prism-status-label">Role</span>
                                <span className="prism-status-value capitalize">{profile.role}</span>
                                <span className="prism-status-detail">Current permission tier attached to this account.</span>
                            </div>
                            <div className="prism-status-item">
                                <span className="prism-status-label">Account status</span>
                                <span className="prism-status-value">{profile.is_active ? "Active" : "Inactive"}</span>
                                <span className="prism-status-detail">Whether the account is currently allowed to sign in.</span>
                            </div>
                            <div className="prism-status-item">
                                <span className="prism-status-label">Primary email</span>
                                <span className="prism-status-value">{profile.email}</span>
                                <span className="prism-status-detail">Login identity and notification address for this profile.</span>
                            </div>
                            <div className="prism-status-item">
                                <span className="prism-status-label">Students supported</span>
                                <span className="prism-status-value">{summary?.students_supported ?? "—"}</span>
                                <span className="prism-status-detail">Distinct students across the teacher&apos;s current class scope over the seeded demo window.</span>
                            </div>
                        </div>

                        {summary ? (
                            <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                                {[
                                    { label: "Classes", value: summary.classes_in_scope, detail: "Classes assigned to this teacher" },
                                    { label: "Uploads", value: summary.documents_uploaded, detail: "Documents added into the teaching knowledge base" },
                                    { label: "Lectures", value: summary.lectures_indexed, detail: "Indexed lecture resources ready for discovery" },
                                    { label: "AI requests", value: summary.ai_requests, detail: "Teacher-side AI interactions already present in the six-month demo story" },
                                ].map((item) => (
                                    <PrismPanel key={item.label} className="p-4">
                                        <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{item.label}</p>
                                        <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{item.value}</p>
                                        <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{item.detail}</p>
                                    </PrismPanel>
                                ))}
                            </div>
                        ) : null}

                        <PrismPanel className="max-w-3xl p-6">
                            <div className="space-y-6">
                                <div className="flex items-center gap-4">
                                    <div className="flex h-16 w-16 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--primary-light)] text-[var(--primary)]">
                                        <User className="h-8 w-8" />
                                    </div>
                                    <div>
                                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Account details</h2>
                                        <p className="text-sm text-[var(--text-secondary)]">
                                            Keep your visible teacher identity accurate across the product.
                                        </p>
                                    </div>
                                </div>

                                <div className="space-y-4">
                                    <Field icon={User} label="Full name" htmlFor="teacher-full-name">
                                        <input
                                            id="teacher-full-name"
                                            value={fullName}
                                            onChange={(e) => setFullName(e.target.value)}
                                            className="mt-1 w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                            placeholder="Enter your name"
                                        />
                                    </Field>

                                    <Field icon={Mail} label="Email">
                                        <p className="mt-1 text-sm font-medium text-[var(--text-primary)]">{profile.email}</p>
                                    </Field>

                                    <Field icon={Shield} label="Role">
                                        <p className="mt-1 text-sm font-medium capitalize text-[var(--text-primary)]">{profile.role}</p>
                                    </Field>

                                    <Field icon={Calendar} label="Account status">
                                        <p className="mt-1 text-sm font-medium text-[var(--text-primary)]">{profile.is_active ? "Active" : "Inactive"}</p>
                                    </Field>

                                    {summary ? (
                                        <Field icon={Calendar} label="Latest milestones">
                                            <div className="mt-1 space-y-1 text-sm text-[var(--text-secondary)]">
                                                <p>Last upload: {formatDate(summary.latest_milestones.last_upload_at)}</p>
                                                <p>Last lecture indexed: {formatDate(summary.latest_milestones.last_lecture_at)}</p>
                                                <p>Assignments created: {summary.assignments_created}</p>
                                            </div>
                                        </Field>
                                    ) : null}
                                </div>

                                <div className="pt-2">
                                    <button
                                        onClick={() => void saveProfile()}
                                        disabled={saving}
                                        className="prism-action inline-flex items-center gap-2"
                                    >
                                        <Save className="h-4 w-4" /> {saving ? "Saving..." : "Save profile"}
                                    </button>
                                </div>
                            </div>
                        </PrismPanel>
                    </>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function formatDate(value?: string | null) {
    if (!value) return "Not available";
    return new Date(value).toLocaleDateString();
}

function Field({
    icon: Icon,
    label,
    htmlFor,
    children,
}: {
    icon: typeof User;
    label: string;
    htmlFor?: string;
    children: React.ReactNode;
}) {
    return (
        <div className="flex items-start gap-3">
            <Icon className="mt-1 h-4 w-4 text-[var(--text-muted)]" />
            <div className="flex-1">
                {htmlFor ? (
                    <label htmlFor={htmlFor} className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</label>
                ) : (
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p>
                )}
                {children}
            </div>
        </div>
    );
}
