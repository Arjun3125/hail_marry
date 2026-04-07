"use client";

import { useEffect, useMemo, useState } from "react";
import {
    AlertCircle,
    Bot,
    CheckCircle2,
    Clock,
    GraduationCap,
    Sparkles,
    Upload,
    UploadCloud,
} from "lucide-react";

import { api } from "@/lib/api";
import { PrismTabButton, PrismTabList } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";

type AssignmentItem = {
    id: string;
    title: string;
    subject: string;
    due: string | null;
    status: "pending" | "submitted" | "graded";
    grade?: number | null;
    has_submission?: boolean;
    submitted_at?: string | null;
};

type Tab = "all" | "pending" | "submitted" | "graded";

const tabs: Array<{ id: Tab; label: string; summary: string }> = [
    { id: "all", label: "All Items", summary: "Full assignment ledger" },
    { id: "pending", label: "Needs Action", summary: "Upload or complete soon" },
    { id: "submitted", label: "Submitted", summary: "Awaiting review or replacement" },
    { id: "graded", label: "Graded", summary: "Returned with score" },
];

type OCRNote = {
    reviewRequired: boolean;
    warning: string | null;
    confidence?: number;
};

function statusAccent(status: AssignmentItem["status"]) {
    if (status === "graded") {
        return {
            stripe: "from-emerald-400 to-teal-500",
            badge: "bg-emerald-500/10 text-status-emerald",
            iconWrap: "bg-emerald-500/12 text-status-emerald",
        };
    }

    if (status === "submitted") {
        return {
            stripe: "from-sky-400 to-indigo-500",
            badge: "bg-blue-500/10 text-status-blue",
            iconWrap: "bg-blue-500/12 text-status-blue",
        };
    }

    return {
        stripe: "from-amber-300 to-orange-500",
        badge: "bg-amber-500/10 text-status-amber",
        iconWrap: "bg-amber-500/12 text-status-amber",
    };
}

export default function AssignmentsPage() {
    const [assignments, setAssignments] = useState<AssignmentItem[]>([]);
    const [activeTab, setActiveTab] = useState<Tab>("all");
    const [loading, setLoading] = useState(true);
    const [uploadingId, setUploadingId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [ocrNotes, setOcrNotes] = useState<Record<string, OCRNote | null>>({});

    const loadAssignments = async () => {
        const payload = await api.student.assignments();
        setAssignments((payload || []) as AssignmentItem[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadAssignments();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load assignments");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const filteredAssignments = useMemo(() => {
        if (activeTab === "all") return assignments;
        return assignments.filter((item) => item.status === activeTab);
    }, [assignments, activeTab]);

    const summary = useMemo(() => {
        const pending = assignments.filter((item) => item.status === "pending").length;
        const submitted = assignments.filter((item) => item.status === "submitted").length;
        const graded = assignments.filter((item) => item.status === "graded").length;
        const averageGrade =
            graded > 0
                ? Math.round(
                      assignments
                          .filter((item) => item.status === "graded")
                          .reduce((sum, item) => sum + (item.grade ?? 0), 0) / graded
                  )
                : null;

        return { pending, submitted, graded, averageGrade };
    }, [assignments]);

    const submitAssignment = async (assignmentId: string, file: File | null) => {
        if (!file) return;
        try {
            setUploadingId(assignmentId);
            setError(null);
            const formData = new FormData();
            formData.append("file", file);
            const payload = (await api.student.submitAssignment(assignmentId, formData)) as {
                ocr_review_required?: boolean;
                ocr_warning?: string | null;
                ocr_confidence?: number;
            };
            setOcrNotes((prev) => ({
                ...prev,
                [assignmentId]:
                    payload?.ocr_review_required || payload?.ocr_warning
                        ? {
                              reviewRequired: Boolean(payload?.ocr_review_required),
                              warning: payload?.ocr_warning ?? null,
                              confidence: typeof payload?.ocr_confidence === "number" ? payload.ocr_confidence : undefined,
                          }
                        : null,
            }));
            await loadAssignments();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to submit assignment");
        } finally {
            setUploadingId(null);
        }
    };

    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student Submission Flow
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Keep deadlines, uploads, and grades inside one{" "}
                                <span className="premium-gradient">clear assignment ledger</span>
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                This page is now organized around student action: see what needs attention, submit from camera or file, and quickly understand what has already been graded.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <PrismPanel className="p-4">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.18),rgba(249,115,22,0.08))]">
                                <Clock className="h-5 w-5 text-status-amber" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Needs action</p>
                            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{summary.pending}</p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Assignments still waiting for submission or follow-up.</p>
                        </PrismPanel>
                        <PrismPanel className="p-4">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(99,102,241,0.08))]">
                                <UploadCloud className="h-5 w-5 text-status-blue" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Submitted</p>
                            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{summary.submitted}</p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Work already uploaded and waiting for teacher review.</p>
                        </PrismPanel>
                        <PrismPanel className="p-4">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(45,212,191,0.18),rgba(16,185,129,0.08))]">
                                <GraduationCap className="h-5 w-5 text-status-emerald" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Average score</p>
                            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">
                                {summary.averageGrade !== null ? (
                                    <>
                                        {summary.averageGrade}
                                        <span className="ml-1 text-sm opacity-50">/100</span>
                                    </>
                                ) : (
                                    "--"
                                )}
                            </p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Latest graded work, normalized into a quick progress signal.</p>
                        </PrismPanel>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="student-assignments"
                        onRetry={() => {
                            void (async () => {
                                try {
                                    setLoading(true);
                                    setError(null);
                                    await loadAssignments();
                                } catch (err) {
                                    setError(err instanceof Error ? err.message : "Failed to load assignments");
                                } finally {
                                    setLoading(false);
                                }
                            })();
                        }}
                    />
                ) : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismTabList>
                        {tabs.map((tab) => {
                            const isActive = activeTab === tab.id;
                            const count =
                                tab.id === "all"
                                    ? assignments.length
                                    : assignments.filter((item) => item.status === tab.id).length;

                            return (
                                <PrismTabButton
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    active={isActive}
                                    className="min-w-[220px] flex-1 px-4 py-3 text-left"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="text-left">
                                            <p className="text-sm font-semibold">{tab.label}</p>
                                            <p className="text-[11px] leading-5 text-[var(--text-muted)]">{tab.summary}</p>
                                        </div>
                                        <span className="ml-auto rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-2 py-0.5 text-[10px] font-semibold text-[var(--text-secondary)]">
                                            {count}
                                        </span>
                                    </div>
                                </PrismTabButton>
                            );
                        })}
                    </PrismTabList>

                    {loading ? (
                        <div className="flex flex-col items-center justify-center rounded-[1.75rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-20 text-center">
                            <Clock className="mb-4 h-12 w-12 animate-spin text-[var(--text-muted)]" />
                            <p className="text-sm font-medium text-[var(--text-muted)]">Syncing assignment ledger...</p>
                        </div>
                    ) : filteredAssignments.length === 0 ? (
                        <div className="flex flex-col items-center justify-center rounded-[1.75rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-20 text-center">
                            <CheckCircle2 className="mb-4 h-16 w-16 text-[var(--text-muted)] opacity-30" />
                            <h3 className="mb-1 text-lg font-bold text-[var(--text-primary)]">You&apos;re all caught up</h3>
                            <p className="text-xs font-medium text-[var(--text-muted)]">No assignments found in this category.</p>
                        </div>
                    ) : (
                        <div className="space-y-4">
                            {filteredAssignments.map((item) => {
                                const isGraded = item.status === "graded";
                                const isSubmitted = item.status === "submitted";
                                const isPending = item.status === "pending";
                                const accent = statusAccent(item.status);

                                return (
                                    <div
                                        key={item.id}
                                        className="relative overflow-hidden rounded-[1.75rem] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-6 shadow-[0_20px_42px_rgba(2,6,23,0.1)]"
                                    >
                                        <div className={`absolute inset-y-0 left-0 w-1.5 bg-gradient-to-b ${accent.stripe}`} />

                                        <div className="flex flex-col gap-6 pl-4 lg:flex-row lg:items-start lg:justify-between">
                                            <div className="flex min-w-0 items-start gap-4">
                                                <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl ${accent.iconWrap}`}>
                                                    {isGraded ? (
                                                        <GraduationCap className="h-6 w-6" />
                                                    ) : isSubmitted ? (
                                                        <CheckCircle2 className="h-6 w-6" />
                                                    ) : (
                                                        <Clock className="h-6 w-6" />
                                                    )}
                                                </div>

                                                <div className="min-w-0">
                                                    <div className="mb-2 flex flex-wrap items-center gap-2">
                                                        <h3 className="text-xl font-bold text-[var(--text-primary)]">{item.title}</h3>
                                                        <span className={`rounded-md px-2 py-1 text-[10px] font-black uppercase tracking-[0.16em] ${accent.badge}`}>
                                                            {item.status}
                                                        </span>
                                                    </div>

                                                    <p className="flex flex-wrap items-center gap-2 text-xs font-semibold text-[var(--text-muted)]">
                                                        <span className="text-[var(--text-primary)]/85">{item.subject}</span>
                                                        <span className="h-1 w-1 rounded-full bg-[var(--text-muted)]/50" />
                                                        <span>Due: {item.due || "No date set"}</span>
                                                    </p>

                                                    {item.submitted_at ? (
                                                        <p className="mt-2 flex items-center gap-1 text-[11px] text-[var(--text-muted)]">
                                                            <UploadCloud className="h-3 w-3" />
                                                            Submitted at {item.submitted_at}
                                                        </p>
                                                    ) : null}

                                                    {ocrNotes[item.id] && (ocrNotes[item.id]!.reviewRequired || ocrNotes[item.id]!.warning) ? (
                                                        <div className="mt-4 max-w-md rounded-2xl border border-amber-500/20 bg-amber-500/6 p-3">
                                                            <p className="flex items-center gap-1.5 text-[10px] font-bold uppercase tracking-[0.16em] text-status-amber">
                                                                <AlertCircle className="h-3 w-3" />
                                                                OCR scanning alert
                                                            </p>
                                                            <p className="mt-1 text-xs leading-6 text-[var(--text-secondary)]">
                                                                {typeof ocrNotes[item.id]?.confidence === "number"
                                                                    ? `Clarity at ${Math.round(ocrNotes[item.id]!.confidence! * 100)}%. `
                                                                    : ""}
                                                                Please review your image
                                                                {ocrNotes[item.id]?.warning ? `: ${ocrNotes[item.id]?.warning}` : "."}
                                                            </p>
                                                        </div>
                                                    ) : null}
                                                </div>
                                            </div>

                                            <div className="flex w-full flex-col gap-3 lg:w-auto lg:min-w-[18rem]">
                                                {isGraded ? (
                                                    <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-center">
                                                        <p className="mb-1 text-[10px] font-black uppercase tracking-[0.18em] text-[var(--text-muted)]">Score</p>
                                                        <p className="text-3xl font-black text-[var(--text-primary)]">
                                                            {item.grade ?? 0}
                                                            <span className="ml-1 text-sm opacity-50">/100</span>
                                                        </p>
                                                    </div>
                                                ) : null}

                                                <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-1">
                                                    <a
                                                        href="/student/assistant"
                                                        className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(167,139,250,0.08)] px-4 py-3 text-xs font-bold text-status-violet transition hover:bg-[rgba(167,139,250,0.14)]"
                                                    >
                                                        <Bot className="h-4 w-4" />
                                                        Need help?
                                                    </a>

                                                    <label
                                                        className={`inline-flex cursor-pointer items-center justify-center gap-2 rounded-2xl px-4 py-3 text-xs font-bold transition ${
                                                            uploadingId === item.id
                                                                ? "bg-[var(--text-muted)] text-white"
                                                                : isPending
                                                                  ? "bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(79,70,229,0.92))] text-[#06101e] shadow-[0_18px_32px_rgba(59,130,246,0.18)]"
                                                                  : "border border-[var(--border)] bg-[rgba(148,163,184,0.05)] text-[var(--text-primary)] hover:bg-[rgba(148,163,184,0.08)]"
                                                        }`}
                                                    >
                                                        {uploadingId === item.id ? (
                                                            <>
                                                                <Clock className="h-4 w-4 animate-spin" />
                                                                Uploading...
                                                            </>
                                                        ) : isPending ? (
                                                            <>
                                                                <UploadCloud className="h-4 w-4" />
                                                                Upload homework
                                                            </>
                                                        ) : (
                                                            <>
                                                                <Upload className="h-4 w-4" />
                                                                Replace file
                                                            </>
                                                        )}
                                                        <input
                                                            type="file"
                                                            accept=".pdf,.docx,image/*"
                                                            capture="environment"
                                                            className="hidden"
                                                            disabled={uploadingId !== null}
                                                            onChange={(event) => {
                                                                const file = event.target.files?.[0] || null;
                                                                void submitAssignment(item.id, file);
                                                                event.target.value = "";
                                                            }}
                                                        />
                                                    </label>
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    )}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}
