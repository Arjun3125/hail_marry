"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
    CheckCircle2,
    Image as ImageIcon,
    Loader2,
    Palette,
    Save,
    Sparkles,
    Type,
} from "lucide-react";

import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type BrandingForm = {
    primary_color: string;
    secondary_color: string;
    font_family: string;
    logo_url: string;
};

type Notice = {
    tone: "success" | "info";
    message: string;
} | null;

const DEFAULT_FORM: BrandingForm = {
    primary_color: "#2563eb",
    secondary_color: "#16a34a",
    font_family: "Inter",
    logo_url: "",
};

const FONT_OPTIONS = [
    { value: "Inter", label: "Inter", description: "Modern and clean for operational surfaces" },
    { value: "Merriweather", label: "Merriweather", description: "Academic serif with a more editorial feel" },
    { value: "Roboto", label: "Roboto", description: "Neutral system-style enterprise typography" },
    { value: "Poppins", label: "Poppins", description: "Friendly geometric tone for a lighter brand" },
];

export default function BrandingConfigPage() {
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [extracting, setExtracting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [notice, setNotice] = useState<Notice>(null);
    const fileInputRef = useRef<HTMLInputElement>(null);

    const [form, setForm] = useState<BrandingForm>(DEFAULT_FORM);

    const loadConfig = async () => {
        try {
            setLoading(true);
            setError(null);
            const data = await api.admin.brandingConfig();
            setForm({
                primary_color: data.primary_color || DEFAULT_FORM.primary_color,
                secondary_color: data.secondary_color || DEFAULT_FORM.secondary_color,
                font_family: data.font_family || DEFAULT_FORM.font_family,
                logo_url: data.logo_url || DEFAULT_FORM.logo_url,
            });
        } catch (loadError) {
            setError(loadError instanceof Error ? loadError.message : "Failed to load branding config");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void loadConfig();
    }, []);

    const handleSave = async () => {
        try {
            setSaving(true);
            setError(null);
            setNotice(null);
            await api.admin.saveBranding(form);
            setNotice({
                tone: "success",
                message: "Brand settings saved. Reload the app shell to see the updated identity everywhere.",
            });
        } catch (saveError) {
            setError(saveError instanceof Error ? saveError.message : "Failed to save branding configuration");
        } finally {
            setSaving(false);
        }
    };

    const handleLogoUpload = async (event: React.ChangeEvent<HTMLInputElement>) => {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            setExtracting(true);
            setError(null);
            setNotice(null);
            const formData = new FormData();
            formData.append("file", file);

            const data = await api.admin.extractBranding(formData);

            if (data?.success && data.suggested_palette) {
                setForm((previous) => ({
                    ...previous,
                    primary_color: data.suggested_palette.primary,
                    secondary_color: data.suggested_palette.secondary,
                }));
                setNotice({
                    tone: "info",
                    message: `Palette extracted: primary ${data.suggested_palette.primary}, secondary ${data.suggested_palette.secondary}.`,
                });
            }
        } catch (extractError) {
            setError(extractError instanceof Error ? extractError.message : "Failed to process logo and extract colors");
        } finally {
            setExtracting(false);
            if (fileInputRef.current) fileInputRef.current.value = "";
        }
    };

    const previewBrand = useMemo(() => ({
        institutionName: `${form.font_family} Academy`,
        statusTone: form.secondary_color,
        heroTone: form.primary_color,
    }), [form.font_family, form.primary_color, form.secondary_color]);

    if (loading) {
        return (
            <PrismPage className="pb-8">
                <PrismSection>
                    <div className="flex items-center justify-center py-20 text-[var(--text-secondary)]">
                        <Loader2 className="h-5 w-5 animate-spin" />
                    </div>
                </PrismSection>
            </PrismPage>
        );
    }

    return (
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Palette className="h-3.5 w-3.5" />
                            Admin Branding Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Branding Engine
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                Configure brand color, typography, and logo-derived palette decisions from one controlled admin workspace.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <MetricCard
                            title="Primary color"
                            value={form.primary_color}
                            summary="Core interface tone used across calls to action and emphasis surfaces."
                            accent="blue"
                        />
                        <MetricCard
                            title="Secondary color"
                            value={form.secondary_color}
                            summary="Support tone for positive states, metrics, and success framing."
                            accent="emerald"
                        />
                        <MetricCard
                            title="Font family"
                            value={form.font_family}
                            summary="Selected type system applied through the shared branding provider."
                            accent="amber"
                        />
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-branding"
                        onRetry={() => {
                            void loadConfig();
                        }}
                    />
                ) : null}

                {notice ? (
                    <PrismPanel className="p-4">
                        <div className="flex items-start gap-3">
                            <CheckCircle2 className={`mt-0.5 h-4 w-4 shrink-0 ${notice.tone === "success" ? "text-status-emerald" : "text-status-blue"}`} />
                            <p className="text-sm leading-6 text-[var(--text-secondary)]">{notice.message}</p>
                        </div>
                    </PrismPanel>
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.02fr)_minmax(360px,0.98fr)]">
                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Brand Configuration</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        Change the organization identity without altering routes, permissions, or product behavior.
                                    </p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    {saving ? "Saving" : extracting ? "Extracting palette" : "Ready"}
                                </div>
                            </div>

                            <div className="mt-5 grid gap-6">
                                <section className="space-y-3">
                                    <div className="flex items-center gap-2">
                                        <ImageIcon className="h-4 w-4 text-[var(--primary)]" />
                                        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Logo & Palette Extraction</h3>
                                    </div>
                                    <p className="text-sm leading-6 text-[var(--text-secondary)]">
                                        Upload a logo to extract a suggested palette, then tune the result before committing the brand update.
                                    </p>
                                    <input
                                        type="file"
                                        accept="image/png, image/jpeg, image/svg+xml"
                                        className="hidden"
                                        ref={fileInputRef}
                                        onChange={handleLogoUpload}
                                    />
                                    <button
                                        type="button"
                                        onClick={() => fileInputRef.current?.click()}
                                        disabled={extracting}
                                        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-dashed border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm font-medium text-[var(--text-primary)] transition hover:border-[rgba(96,165,250,0.28)] hover:bg-[rgba(96,165,250,0.08)] disabled:cursor-not-allowed disabled:opacity-60"
                                    >
                                        {extracting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                                        Upload Organization Logo
                                    </button>
                                </section>

                                <section className="space-y-4">
                                    <div className="flex items-center gap-2">
                                        <Palette className="h-4 w-4 text-[var(--primary)]" />
                                        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Theme Colors</h3>
                                    </div>
                                    <div className="grid gap-4 md:grid-cols-2">
                                        <ColorField
                                            label="Primary Brand Color"
                                            value={form.primary_color}
                                            onChange={(value) => setForm({ ...form, primary_color: value })}
                                        />
                                        <ColorField
                                            label="Secondary / Success"
                                            value={form.secondary_color}
                                            onChange={(value) => setForm({ ...form, secondary_color: value })}
                                        />
                                    </div>
                                </section>

                                <section className="space-y-4">
                                    <div className="flex items-center gap-2">
                                        <Type className="h-4 w-4 text-[var(--primary)]" />
                                        <h3 className="text-sm font-semibold text-[var(--text-primary)]">Typography</h3>
                                    </div>
                                    <select
                                        value={form.font_family}
                                        onChange={(event) => setForm({ ...form, font_family: event.target.value })}
                                        className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                                    >
                                        {FONT_OPTIONS.map((option) => (
                                            <option key={option.value} value={option.value}>
                                                {option.label} - {option.description}
                                            </option>
                                        ))}
                                    </select>
                                </section>

                                <button
                                    type="button"
                                    onClick={handleSave}
                                    disabled={saving}
                                    className="inline-flex items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-3 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                                >
                                    {saving ? <Loader2 className="h-4 w-4 animate-spin" /> : <Save className="h-4 w-4" />}
                                    Save Brand Settings
                                </button>
                            </div>
                        </PrismPanel>
                    </div>

                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5 xl:sticky xl:top-6">
                            <div className="flex items-center justify-between gap-3">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Live Interface Preview</h2>
                                    <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                        Local preview of the shared app shell using the selected branding variables.
                                    </p>
                                </div>
                                <div className="inline-flex items-center gap-1 rounded-full border border-[rgba(52,211,153,0.2)] bg-[rgba(16,185,129,0.12)] px-3 py-1 text-[11px] font-semibold uppercase tracking-[0.18em] text-status-emerald">
                                    <CheckCircle2 className="h-3.5 w-3.5" />
                                    Real-time
                                </div>
                            </div>

                            <div
                                className="mt-5 overflow-hidden rounded-[28px] border border-[var(--border)] bg-[rgba(8,15,30,0.72)] shadow-[0_20px_40px_rgba(2,6,23,0.22)]"
                                style={{
                                    ["--primary" as string]: form.primary_color,
                                    ["--success" as string]: form.secondary_color,
                                    ["--font-sans" as string]: `${form.font_family}, system-ui`,
                                }}
                            >
                                <div className="flex h-[620px] flex-col bg-[var(--bg-page)] font-sans text-[var(--text-primary)]">
                                    <div className="flex items-center justify-between border-b border-[var(--border)] bg-[var(--card)] px-5 py-4">
                                        <div className="flex items-center gap-3 font-bold text-lg text-[var(--primary)]">
                                            <span className="flex h-9 w-9 items-center justify-center rounded-2xl bg-[var(--primary)] text-sm text-white">
                                                OS
                                            </span>
                                            {previewBrand.institutionName}
                                        </div>
                                        <div className="h-9 w-9 rounded-full bg-[var(--input)]" />
                                    </div>

                                    <div className="flex-1 space-y-6 overflow-y-auto p-6">
                                        <div className="flex items-end justify-between gap-4">
                                            <div>
                                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Dashboard snapshot</p>
                                                <h3 className="mt-2 text-2xl font-bold">Good morning, Student!</h3>
                                                <p className="mt-1 text-sm text-[var(--text-muted)]">You have 2 upcoming assignments and 1 live AI study session.</p>
                                            </div>
                                            <button className="rounded-2xl bg-[var(--primary)] px-4 py-2 text-sm font-medium text-white shadow-sm">
                                                View Schedule
                                            </button>
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <PreviewCard
                                                title="Subject Performance"
                                                value="85%"
                                                badge="+5% from last week"
                                                tone="primary"
                                            />
                                            <PreviewCard
                                                title="Attendance"
                                                value="100%"
                                                badge="Perfect streak"
                                                tone="success"
                                            />
                                        </div>

                                        <div className="rounded-[24px] border border-[var(--primary)]/20 bg-[var(--primary)]/10 p-5">
                                            <p className="text-sm font-bold text-[var(--primary)]">AI Study Assistant Active</p>
                                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                                Your personalized tutor is ready to guide revision for the next assessment block.
                                            </p>
                                            <button className="mt-4 rounded-full bg-[var(--primary)] px-4 py-2 text-xs font-semibold text-white">
                                                Start Session
                                            </button>
                                        </div>

                                        <div className="rounded-[24px] border border-[var(--border)] bg-[var(--card)] p-5">
                                            <div className="flex items-center justify-between gap-3">
                                                <div>
                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Brand signal check</p>
                                                    <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                                        Primary CTA, success framing, and typography reflect the selected organization theme.
                                                    </p>
                                                </div>
                                                <div
                                                    className="h-10 w-10 rounded-full border border-white/10"
                                                    style={{ backgroundColor: previewBrand.statusTone }}
                                                />
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    title,
    value,
    summary,
    accent,
}: {
    title: string;
    value: string;
    summary: string;
    accent: "blue" | "emerald" | "amber";
}) {
    const accentClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))]",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))]",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))]",
    } as const;

    return (
        <PrismPanel className="p-4">
            <div className={`mb-3 h-2 w-16 rounded-full ${accentClasses[accent]}`} />
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 break-all text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </PrismPanel>
    );
}

function ColorField({
    label,
    value,
    onChange,
}: {
    label: string;
    value: string;
    onChange: (value: string) => void;
}) {
    return (
        <div>
            <label className="mb-2 block text-xs font-medium uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</label>
            <div className="flex items-center gap-2">
                <input
                    type="color"
                    value={value}
                    onChange={(event) => onChange(event.target.value)}
                    className="h-11 w-14 cursor-pointer rounded-2xl border-0 bg-transparent p-0"
                />
                <input
                    type="text"
                    value={value}
                    onChange={(event) => onChange(event.target.value)}
                    className="flex-1 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm font-mono text-[var(--text-primary)] outline-none transition focus:border-[rgba(96,165,250,0.4)] focus:bg-[rgba(96,165,250,0.06)]"
                />
            </div>
        </div>
    );
}

function PreviewCard({
    title,
    value,
    badge,
    tone,
}: {
    title: string;
    value: string;
    badge: string;
    tone: "primary" | "success";
}) {
    return (
        <div className="rounded-[24px] border border-[var(--border)] bg-[var(--card)] p-4 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-[0.18em] text-[var(--text-muted)]">{title}</p>
            <p className={`mt-3 text-3xl font-black ${tone === "primary" ? "text-[var(--primary)]" : "text-[var(--success)]"}`}>{value}</p>
            <div className={`mt-2 inline-block rounded-full px-2 py-1 text-xs font-medium ${tone === "primary" ? "bg-[var(--primary)]/10 text-[var(--primary)]" : "bg-[var(--success)]/10 text-[var(--success)]"}`}>
                {badge}
            </div>
        </div>
    );
}
