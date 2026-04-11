"use client";

import { useEffect, useMemo, useState } from "react";
import { useVidyaContext } from "@/providers/VidyaContextProvider";
import { useLanguage } from "@/i18n/LanguageProvider";
import {
    AlertCircle,
    Bot,
    Camera,
    CheckCircle2,
    Clock,
    FileUp,
    GraduationCap,
    Keyboard,
    Send,
    Sparkles,
    UploadCloud,
} from "lucide-react";

import { api } from "@/lib/api";
import { PrismTabButton, PrismTabList } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import EmptyState from "@/components/EmptyState";
import { SkeletonList } from "@/components/Skeleton";
import CameraPreviewModal from "./components/CameraPreviewModal";

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
type SubmissionMode = "camera" | "file" | "type";

// Tab configuration now uses i18n keys
const getTabsConfig = (t: (key: string) => string): Array<{ id: Tab; labelKey: string; summaryKey: string }> => [
    { id: "all", labelKey: "assignments.all_items", summaryKey: "assignments.all_items_summary" },
    { id: "pending", labelKey: "assignments.pending", summaryKey: "assignments.pending" },
    { id: "submitted", labelKey: "assignments.submitted", summaryKey: "assignments.submitted" },
    { id: "graded", labelKey: "assignments.graded", summaryKey: "assignments.graded" },
];

type OCRNote = {
    reviewRequired: boolean;
    warning: string | null;
    confidence?: number;
};

const submissionModes: Array<{
    id: SubmissionMode;
    label: string;
    detail: string;
    icon: typeof Camera;
}> = [
    { id: "camera", label: "Camera", detail: "Scan notebook work", icon: Camera },
    { id: "file", label: "File", detail: "Upload PDF, DOCX, image", icon: FileUp },
    { id: "type", label: "Type answer", detail: "Write directly here", icon: Keyboard },
];

function formatDueLabel(due: string | null, status: AssignmentItem["status"]) {
    if (status === "submitted") return "SUBMITTED";
    if (status === "graded") return "GRADED";
    if (!due) return "NO DUE DATE";

    const dueDate = new Date(due);
    if (Number.isNaN(dueDate.getTime())) return "DUE DATE SET";

    const today = new Date();
    today.setHours(0, 0, 0, 0);
    dueDate.setHours(0, 0, 0, 0);
    const diffDays = Math.ceil((dueDate.getTime() - today.getTime()) / 86_400_000);

    if (diffDays < 0) return `OVERDUE BY ${Math.abs(diffDays)} DAY${Math.abs(diffDays) === 1 ? "" : "S"}`;
    if (diffDays === 0) return "DUE TODAY";
    if (diffDays === 1) return "DUE TOMORROW";
    return `DUE IN ${diffDays} DAYS`;
}

function safeFilePart(value: string) {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/(^-|-$)/g, "") || "assignment";
}

function typedAnswerFile(item: AssignmentItem, answer: string) {
    const body = [
        `Assignment: ${item.title}`,
        `Subject: ${item.subject}`,
        `Submitted through VidyaOS typed answer`,
        "",
        answer,
    ].join("\n");

    return new File([body], `${safeFilePart(item.title)}-typed-answer.txt`, {
        type: "text/plain",
    });
}

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
    const { t } = useLanguage();
    const { activeSubject, mergeContext } = useVidyaContext();
    const [assignments, setAssignments] = useState<AssignmentItem[]>([]);
    const [activeTab, setActiveTab] = useState<Tab>("all");
    const [selectedSubject, setSelectedSubject] = useState<string>(activeSubject || "all");
    const [loading, setLoading] = useState(true);
    const [uploadingId, setUploadingId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [ocrNotes, setOcrNotes] = useState<Record<string, OCRNote | null>>({});
    const [activeSubmissionId, setActiveSubmissionId] = useState<string | null>(null);
    const [submissionModeById, setSubmissionModeById] = useState<Record<string, SubmissionMode>>({});
    const [typedAnswers, setTypedAnswers] = useState<Record<string, string>>({});
    const [submissionSuccess, setSubmissionSuccess] = useState<{
        assignmentId: string;
        message: string;
        detail: string;
    } | null>(null);
    const [cameraPreviewOpen, setCameraPreviewOpen] = useState(false);
    const [cameraAssignmentId, setCameraAssignmentId] = useState<string | null>(null);
    const subjects = useMemo(
        () => Array.from(new Set(assignments.map((assignment) => assignment.subject))).sort(),
        [assignments],
    );
    const tabs = useMemo(() => getTabsConfig(t), [t]);

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

    useEffect(() => {
        if (activeSubject && selectedSubject === "all" && subjects.includes(activeSubject)) {
            setSelectedSubject(activeSubject);
        }
    }, [activeSubject, selectedSubject, subjects]);

    useEffect(() => {
        if (selectedSubject !== "all" && !subjects.includes(selectedSubject)) {
            setSelectedSubject("all");
        }
    }, [selectedSubject, subjects]);

    useEffect(() => {
        if (selectedSubject === "all") {
            mergeContext({ lastRole: "student" });
            return;
        }
        mergeContext({
            lastRole: "student",
            activeSubject: selectedSubject,
        });
    }, [mergeContext, selectedSubject]);

    const filteredAssignments = useMemo(() => {
        const subjectScoped =
            selectedSubject === "all"
                ? assignments
                : assignments.filter((item) => item.subject === selectedSubject);
        if (activeTab === "all") return subjectScoped;
        return subjectScoped.filter((item) => item.status === activeTab);
    }, [assignments, activeTab, selectedSubject]);

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

    const submitAssignment = async (assignment: AssignmentItem, file: File | null, mode: SubmissionMode) => {
        if (!file) return;
        try {
            setUploadingId(assignment.id);
            setError(null);
            setSubmissionSuccess(null);
            const formData = new FormData();
            formData.append("file", file);
            const payload = (await api.student.submitAssignment(assignment.id, formData)) as {
                ocr_review_required?: boolean;
                ocr_warning?: string | null;
                ocr_confidence?: number;
            };
            setOcrNotes((prev) => ({
                ...prev,
                [assignment.id]:
                    payload?.ocr_review_required || payload?.ocr_warning
                        ? {
                              reviewRequired: Boolean(payload?.ocr_review_required),
                              warning: payload?.ocr_warning ?? null,
                              confidence: typeof payload?.ocr_confidence === "number" ? payload.ocr_confidence : undefined,
                          }
                        : null,
            }));
            setSubmissionSuccess({
                assignmentId: assignment.id,
                message: `Work submitted for ${assignment.title}`,
                detail: mode === "camera"
                    ? "Camera scan added to the teacher review queue."
                    : mode === "file"
                      ? "File uploaded and linked to this assignment."
                      : "Typed answer saved as a text submission for teacher review.",
            });
            setActiveSubmissionId(null);
            setSubmissionModeById((prev) => ({ ...prev, [assignment.id]: mode }));
            if (mode === "type") {
                setTypedAnswers((prev) => ({ ...prev, [assignment.id]: "" }));
            }
            await loadAssignments();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to submit assignment");
        } finally {
            setUploadingId(null);
        }
    };

    const submitTypedAnswer = async (assignment: AssignmentItem) => {
        const answer = (typedAnswers[assignment.id] || "").trim();
        if (!answer) {
            setError(`Type your answer for ${assignment.title} before submitting.`);
            return;
        }
        await submitAssignment(assignment, typedAnswerFile(assignment, answer), "type");
    };

    return (
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student submission flow
                        </PrismHeroKicker>
                    )}
                    title="Track due work in one clear assignment ledger"
                    description="See what needs action, submit from camera or file, and understand what has already been graded without leaving the study workflow."
                    aside={(
                        <div className="prism-status-strip">
                        <PrismPanel className="p-6">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.18),rgba(249,115,22,0.08))]">
                                <Clock className="h-5 w-5 text-status-amber" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Needs action</p>
                            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{summary.pending}</p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Assignments still waiting for submission or follow-up.</p>
                        </PrismPanel>
                        <PrismPanel className="p-6">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(99,102,241,0.08))]">
                                <UploadCloud className="h-5 w-5 text-status-blue" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Submitted</p>
                            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{summary.submitted}</p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Work already uploaded and waiting for teacher review.</p>
                        </PrismPanel>
                        <PrismPanel className="p-6">
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
                    )}
                />

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

                <PrismPanel className="space-y-6 p-6">
                    <div className="flex flex-wrap items-center justify-between gap-4">
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Assignment scope</p>
                            <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                Keep one subject in focus and it will follow you into AI Studio and adjacent study screens.
                            </p>
                        </div>
                        <select
                            value={selectedSubject}
                            onChange={(event) => {
                                const nextSubject = event.target.value;
                                setSelectedSubject(nextSubject);
                                if (nextSubject === "all") {
                                    mergeContext({
                                        lastRole: "student",
                                        activeSubject: null,
                                    });
                                }
                            }}
                            className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-2 text-sm text-[var(--text-primary)]"
                        >
                            <option value="all">{t("assignments.all_subjects")}</option>
                            {subjects.map((subject) => (
                                <option key={subject} value={subject}>
                                    {subject}
                                </option>
                            ))}
                        </select>
                    </div>

                    <PrismTabList>
                        {tabs.map((tab) => {
                            const isActive = activeTab === tab.id;
                            const subjectScopedAssignments =
                                selectedSubject === "all"
                                    ? assignments
                                    : assignments.filter((item) => item.subject === selectedSubject);
                            const count =
                                tab.id === "all"
                                    ? subjectScopedAssignments.length
                                    : subjectScopedAssignments.filter((item) => item.status === tab.id).length;

                            return (
                                <PrismTabButton
                                    key={tab.id}
                                    onClick={() => setActiveTab(tab.id)}
                                    active={isActive}
                                    className="min-w-[220px] flex-1 px-5 py-4 text-left"
                                >
                                    <div className="flex items-center gap-3">
                                        <div className="text-left">
                                            <p className="text-sm font-semibold">{t(tab.labelKey)}</p>
                                            <p className="text-[11px] leading-5 text-[var(--text-muted)]">{t(tab.summaryKey)}</p>
                                        </div>
                                        <span className="ml-auto rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-2 py-0.5 text-[10px] font-semibold text-[var(--text-secondary)]">
                                            {count}
                                        </span>
                                    </div>
                                </PrismTabButton>
                            );
                        })}
                    </PrismTabList>

                    {submissionSuccess ? (
                        <div className="rounded-[1.5rem] border border-[var(--success)]/30 bg-success-subtle p-4">
                            <p className="flex items-center gap-2 text-sm font-semibold text-[var(--success)]">
                                <CheckCircle2 className="h-4 w-4" />
                                {submissionSuccess.message}
                            </p>
                            <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{submissionSuccess.detail}</p>
                        </div>
                    ) : null}

                    {loading ? (
                        <div className="rounded-[1.75rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-6">
                            <p className="text-sm font-semibold text-[var(--text-primary)]">Checking your work for today...</p>
                            <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                                Looking for due homework, submitted files, and anything your teacher has already graded.
                            </p>
                            <div className="mt-5">
                                <SkeletonList items={3} />
                            </div>
                        </div>
                    ) : assignments.length === 0 ? (
                        <EmptyState
                            icon={CheckCircle2}
                            eyebrow="No work assigned"
                            title="No homework has been assigned yet"
                            description="When your teacher shares homework, diagrams, worksheets, or typed-answer tasks, they will appear here with one clear submit action."
                            scopeNote="Until then, you can add study material and ask AI questions from your own notes."
                            action={{ label: "Add study material", href: "/student/upload" }}
                            secondaryAction={{ label: "Open AI Studio", href: "/student/ai-studio" }}
                        />
                    ) : filteredAssignments.length === 0 ? (
                        <EmptyState
                            icon={CheckCircle2}
                            eyebrow="Nothing in this view"
                            title="No work matches this filter"
                            description="This subject or status is clear. Switch to all subjects or another status to see the rest of your homework."
                            action={{ label: "View all work", href: "/student/assignments" }}
                        />
                    ) : (
                        <div className="space-y-4">
                            {filteredAssignments.map((item) => {
                                const isGraded = item.status === "graded";
                                const isSubmitted = item.status === "submitted";
                                const isPending = item.status === "pending";
                                const accent = statusAccent(item.status);
                                const activeMode = submissionModeById[item.id] || "camera";
                                const ActiveModeIcon = submissionModes.find((mode) => mode.id === activeMode)?.icon || Camera;
                                const submissionOpen = activeSubmissionId === item.id;

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

                                                    <p className="mb-3 text-[11px] font-black uppercase tracking-[0.2em] text-status-amber">
                                                        {formatDueLabel(item.due, item.status)}
                                                    </p>

                                                    <p className="flex flex-wrap items-center gap-2 text-xs font-semibold text-[var(--text-muted)]">
                                                        <span className="text-[var(--text-primary)]/85">{item.subject}</span>
                                                        <span className="h-1 w-1 rounded-full bg-[var(--text-muted)]/50" />
                                                        <span>Teacher review queue</span>
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

                                            <div className="flex w-full flex-col gap-3 lg:w-auto lg:min-w-[20rem]">
                                                {isGraded ? (
                                                    <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-center">
                                                        <p className="mb-1 text-[10px] font-black uppercase tracking-[0.18em] text-[var(--text-muted)]">Score</p>
                                                        <p className="text-3xl font-black text-[var(--text-primary)]">
                                                            {item.grade ?? 0}
                                                            <span className="ml-1 text-sm opacity-50">/100</span>
                                                        </p>
                                                    </div>
                                                ) : null}

                                                <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(8,15,30,0.64)] p-3">
                                                    {!isGraded ? (
                                                        <button
                                                            type="button"
                                                            onClick={() => setActiveSubmissionId((prev) => prev === item.id ? null : item.id)}
                                                            className={`flex w-full items-center justify-center gap-2 rounded-2xl px-4 py-3 text-sm font-black uppercase tracking-[0.16em] transition ${
                                                                isPending
                                                                    ? "bg-[linear-gradient(135deg,rgba(96,165,250,0.98),rgba(79,70,229,0.94))] text-[#06101e] shadow-[0_18px_32px_rgba(59,130,246,0.2)] hover:-translate-y-0.5"
                                                                    : "border border-[var(--border)] bg-[rgba(148,163,184,0.07)] text-[var(--text-primary)] hover:bg-[rgba(148,163,184,0.11)]"
                                                            }`}
                                                            disabled={uploadingId !== null}
                                                        >
                                                            {uploadingId === item.id ? (
                                                                <>
                                                                    <Clock className="h-4 w-4 animate-spin" />
                                                                    Submitting work...
                                                                </>
                                                            ) : (
                                                                <>
                                                                    <UploadCloud className="h-4 w-4" />
                                                                    {isPending ? "SUBMIT WORK" : "REPLACE WORK"}
                                                                </>
                                                            )}
                                                        </button>
                                                    ) : (
                                                        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-4 py-3 text-center text-xs font-semibold text-[var(--text-secondary)]">
                                                            Graded work is locked. Ask your teacher before resubmitting.
                                                        </div>
                                                    )}

                                                    <a
                                                        href={`/student/ai-studio?subject=${encodeURIComponent(item.subject)}&prompt=${encodeURIComponent(`Help me understand the assignment ${item.title}`)}`}
                                                        className="mt-3 inline-flex w-full items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(167,139,250,0.08)] px-4 py-2.5 text-xs font-semibold text-status-violet transition hover:bg-[rgba(167,139,250,0.14)]"
                                                    >
                                                        <Bot className="h-4 w-4" />
                                                        Need help?
                                                    </a>

                                                    {submissionOpen ? (
                                                        <div className="mt-4 space-y-3">
                                                            <div className="grid gap-2 sm:grid-cols-3">
                                                                {submissionModes.map((mode) => {
                                                                    const Icon = mode.icon;
                                                                    const active = activeMode === mode.id;
                                                                    return (
                                                                        <button
                                                                            key={mode.id}
                                                                            type="button"
                                                                            onClick={() => setSubmissionModeById((prev) => ({ ...prev, [item.id]: mode.id }))}
                                                                            className={`rounded-2xl border px-3 py-3 text-left transition ${
                                                                                active
                                                                                    ? "border-[rgba(96,165,250,0.5)] bg-[rgba(96,165,250,0.12)] text-[var(--text-primary)]"
                                                                                    : "border-[var(--border)] bg-[rgba(148,163,184,0.04)] text-[var(--text-secondary)] hover:bg-[rgba(148,163,184,0.08)]"
                                                                            }`}
                                                                        >
                                                                            <Icon className="mb-2 h-4 w-4" />
                                                                            <span className="block text-xs font-bold">{mode.label}</span>
                                                                            <span className="mt-1 block text-[10px] leading-4 text-[var(--text-muted)]">{mode.detail}</span>
                                                                        </button>
                                                                    );
                                                                })}
                                                            </div>

                                                            {activeMode === "camera" ? (
                                                                <label className="flex cursor-pointer items-center justify-center gap-2 rounded-2xl border border-[rgba(96,165,250,0.28)] bg-[rgba(96,165,250,0.09)] px-4 py-3 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(96,165,250,0.14)]">
                                                                    <ActiveModeIcon className="h-4 w-4" />
                                                                    Open camera and submit notebook photo
                                                                    <input
                                                                        type="file"
                                                                        accept="image/*"
                                                                        capture="environment"
                                                                        className="hidden"
                                                                        disabled={uploadingId !== null}
                                                                        onChange={(event) => {
                                                                            const file = event.target.files?.[0] || null;
                                                                            if (file) {
                                                                                setCameraAssignmentId(item.id);
                                                                                setCameraPreviewOpen(true);
                                                                            }
                                                                            event.target.value = "";
                                                                        }}
                                                                    />
                                                                </label>
                                                            ) : null}

                                                            {activeMode === "file" ? (
                                                                <label className="flex cursor-pointer items-center justify-center gap-2 rounded-2xl border border-[rgba(96,165,250,0.28)] bg-[rgba(96,165,250,0.09)] px-4 py-3 text-xs font-bold text-[var(--text-primary)] transition hover:bg-[rgba(96,165,250,0.14)]">
                                                                    <ActiveModeIcon className="h-4 w-4" />
                                                                    Choose file from phone or laptop
                                                                    <input
                                                                        type="file"
                                                                        accept=".pdf,.docx,.pptx,.xlsx,.txt,image/*"
                                                                        className="hidden"
                                                                        disabled={uploadingId !== null}
                                                                        onChange={(event) => {
                                                                            const file = event.target.files?.[0] || null;
                                                                            void submitAssignment(item, file, "file");
                                                                            event.target.value = "";
                                                                        }}
                                                                    />
                                                                </label>
                                                            ) : null}

                                                            {activeMode === "type" ? (
                                                                <div className="space-y-3">
                                                                    <textarea
                                                                        value={typedAnswers[item.id] || ""}
                                                                        onChange={(event) => setTypedAnswers((prev) => ({ ...prev, [item.id]: event.target.value }))}
                                                                        placeholder="Type your answer here. Include steps, diagrams explained in words, or final working."
                                                                        className="min-h-32 w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm leading-6 text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                                                    />
                                                                    <button
                                                                        type="button"
                                                                        onClick={() => void submitTypedAnswer(item)}
                                                                        disabled={uploadingId !== null || !(typedAnswers[item.id] || "").trim()}
                                                                        className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(79,70,229,0.92))] px-4 py-3 text-xs font-bold text-[#06101e] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
                                                                    >
                                                                        <Send className="h-4 w-4" />
                                                                        Submit typed answer
                                                                    </button>
                                                                </div>
                                                            ) : null}
                                                        </div>
                                                    ) : null}
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

            <CameraPreviewModal
                isOpen={cameraPreviewOpen}
                isLoading={uploadingId === cameraAssignmentId}
                onConfirm={async (file) => {
                    if (cameraAssignmentId) {
                        const assignment = assignments.find((a) => a.id === cameraAssignmentId);
                        if (assignment) {
                            await submitAssignment(assignment, file, "camera");
                            setCameraPreviewOpen(false);
                            setCameraAssignmentId(null);
                        }
                    }
                }}
                onCancel={() => {
                    setCameraPreviewOpen(false);
                    setCameraAssignmentId(null);
                }}
            />
        </PrismPage>
    );
}
