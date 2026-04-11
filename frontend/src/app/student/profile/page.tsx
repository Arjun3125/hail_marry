"use client";

import { useEffect, useState } from "react";
import { Calendar, Mail, Save, Shield, User } from "lucide-react";

import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type MePayload = {
    id: string;
    email: string;
    full_name: string | null;
    role: string;
    is_active: boolean;
};

type StudentProfileSummary = {
    days_active: number;
    uploads: number;
    assignments_submitted: number;
    study_sessions: number;
    ai_requests: number;
    attendance_average: number;
    generated_artifacts: number;
    reviews_completed: number;
    latest_milestones: {
        last_upload_at?: string | null;
        last_submission_at?: string | null;
        last_study_session_at?: string | null;
        last_ai_request_at?: string | null;
        last_generated_artifact_at?: string | null;
        last_review_completed_at?: string | null;
    };
};

export default function ProfilePage() {
    const [profile, setProfile] = useState<MePayload | null>(null);
    const [summary, setSummary] = useState<StudentProfileSummary | null>(null);
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
                    api.student.profileSummary() as Promise<StudentProfileSummary>,
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
            setMessage("Profile updated");
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to update profile");
        } finally {
            setSaving(false);
        }
    };

    return (
        <PrismPage variant="form" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><User className="h-3.5 w-3.5" />Student Profile</PrismHeroKicker>}
                    title="Keep your student account details clear and current"
                    description="This page keeps the basics simple: your name, email, role, and whether your account is active for school use."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Account name</span>
                        <strong className="prism-status-value">{loading ? "Loading" : (profile?.full_name || "—")}</strong>
                        <span className="prism-status-detail">The name shown across the learning workspace</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Role</span>
                        <strong className="prism-status-value">{loading ? "Loading" : (profile?.role || "—")}</strong>
                        <span className="prism-status-detail">Current account role assigned by the school</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Account status</span>
                        <strong className="prism-status-value">{profile ? (profile.is_active ? "Active" : "Inactive") : "Loading"}</strong>
                        <span className="prism-status-detail">Whether the school account is currently enabled</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Active days</span>
                        <strong className="prism-status-value">{summary?.days_active ?? "Loading"}</strong>
                        <span className="prism-status-detail">Days with uploads, study sessions, submissions, or AI activity over the last six months</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-profile" onRetry={() => window.location.reload()} /> : null}
                {message ? <PrismPanel className="p-4"><p className="text-sm text-[var(--success)]">{message}</p></PrismPanel> : null}

                {summary ? (
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        {[
                            { label: "Uploads", value: summary.uploads, detail: "Files added into the study base over six months" },
                            { label: "Assignments", value: summary.assignments_submitted, detail: "Submitted coursework tracked in this demo account" },
                            { label: "AI requests", value: summary.ai_requests, detail: "Grounded AI interactions already visible in history" },
                            { label: "Attendance", value: `${summary.attendance_average}%`, detail: "Attendance average across the seeded academic window" },
                        ].map((item) => (
                            <PrismPanel key={item.label} className="p-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{item.label}</p>
                                <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{item.value}</p>
                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{item.detail}</p>
                            </PrismPanel>
                        ))}
                    </div>
                ) : null}

                <PrismPanel className="max-w-2xl p-6">
                    <PrismSectionHeader title="Profile details" description="Update your display name here. The rest of the account details are managed by the school setup." />
                    {loading || !profile ? (
                        <p className="mt-4 text-sm text-[var(--text-secondary)]">Loading profile...</p>
                    ) : (
                        <div className="mt-5 space-y-4">
                            <Field icon={User} label="Full name" htmlFor="student-full-name">
                                <input id="student-full-name" value={fullName} onChange={(e) => setFullName(e.target.value)} className="mt-1 w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3 text-sm text-[var(--text-primary)]" placeholder="Enter your name" />
                            </Field>
                            <Field icon={Mail} label="Email"><p className="text-sm font-medium text-[var(--text-primary)]">{profile.email}</p></Field>
                            <Field icon={Shield} label="Role"><p className="text-sm font-medium capitalize text-[var(--text-primary)]">{profile.role}</p></Field>
                            <Field icon={Calendar} label="Account status"><p className="text-sm font-medium text-[var(--text-primary)]">{profile.is_active ? "Active" : "Inactive"}</p></Field>
                            {summary ? (
                                <Field icon={Calendar} label="Latest milestones">
                                    <div className="mt-1 space-y-1 text-sm text-[var(--text-secondary)]">
                                        <p>Last upload: {formatDate(summary.latest_milestones.last_upload_at)}</p>
                                        <p>Last AI request: {formatDate(summary.latest_milestones.last_ai_request_at)}</p>
                                        <p>Last review completion: {formatDate(summary.latest_milestones.last_review_completed_at)}</p>
                                    </div>
                                </Field>
                            ) : null}
                            <button onClick={() => void saveProfile()} disabled={saving} className="prism-action" type="button">
                                <Save className="h-4 w-4" />
                                {saving ? "Saving..." : "Save profile"}
                            </button>
                        </div>
                    )}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

function formatDate(value?: string | null) {
    if (!value) return "Not available";
    return new Date(value).toLocaleDateString();
}

function Field({ icon: Icon, label, htmlFor, children }: { icon: typeof User; label: string; htmlFor?: string; children: React.ReactNode }) {
    return (
        <div className="flex items-start gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <Icon className="mt-0.5 h-4 w-4 text-[var(--text-muted)]" />
            <div className="flex-1">
                {htmlFor ? (
                    <label htmlFor={htmlFor} className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</label>
                ) : (
                    <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</p>
                )}
                <div className="mt-1">{children}</div>
            </div>
        </div>
    );
}
