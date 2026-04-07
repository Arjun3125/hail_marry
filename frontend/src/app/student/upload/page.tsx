"use client";

import Link from "next/link";
import { useEffect, useMemo, useRef, useState } from "react";
import { Bot, CheckCircle2, FileText, Loader2, ScanSearch, Sparkles, Upload, XCircle } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismTableShell } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type UploadRecord = {
    id: string;
    file_name: string;
    file_type: string;
    status: "processing" | "completed" | "failed";
    uploaded_at: string;
};

type UploadListPayload = {
    items: UploadRecord[];
};

type ActivityItem = {
    key: string;
    name: string;
    type: string;
    status: "uploading" | "completed" | "failed";
    chunks?: number;
    error?: string;
    ocrWarning?: string;
    ocrReviewRequired?: boolean;
    ocrPending?: boolean;
    ocrProcessed?: boolean;
    ocrConfidence?: number;
};

const ALLOWED_EXTENSIONS = ["pdf", "docx", "pptx", "xlsx", "jpg", "jpeg", "png"];
const MAX_FILE_SIZE = 25 * 1024 * 1024;

function buildMascotPromptHref(prompt: string) {
    return `/student/assistant?prompt=${encodeURIComponent(prompt)}`;
}

export default function StudentUploadPage() {
    const [uploads, setUploads] = useState<UploadRecord[]>([]);
    const [activity, setActivity] = useState<ActivityItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [isDragging, setIsDragging] = useState(false);
    const inputRef = useRef<HTMLInputElement>(null);

    const loadUploads = async () => {
        const payload = (await api.student.uploads()) as UploadListPayload;
        setUploads(payload.items || []);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadUploads();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load uploads");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const setActivityStatus = (key: string, status: ActivityItem["status"], extras?: Partial<ActivityItem>) => {
        setActivity((prev) =>
            prev.map((item) =>
                item.key === key
                    ? {
                        ...item,
                        status,
                        ...extras,
                    }
                    : item,
            ),
        );
    };

    const latestCompletedActivity = activity.find((item) => item.status === "completed");
    const summary = useMemo(() => {
        const completed = uploads.filter((item) => item.status === "completed").length;
        const processing = uploads.filter((item) => item.status === "processing").length;
        const imageWork = activity.filter((item) => item.ocrPending || item.ocrProcessed || item.ocrReviewRequired).length;
        return {
            total: uploads.length,
            completed,
            processing,
            imageWork,
        };
    }, [activity, uploads]);

    const processFiles = async (fileList: FileList | File[]) => {
        const files = Array.from(fileList);
        if (files.length === 0) return;

        setError(null);

        for (const file of files) {
            const ext = file.name.split(".").pop()?.toLowerCase() || "";
            const key = `${Date.now()}-${file.name}-${Math.random().toString(36).slice(2, 8)}`;
            const isImage = ["jpg", "jpeg", "png"].includes(ext);

            setActivity((prev) => [
                {
                    key,
                    name: file.name,
                    type: ext,
                    status: "uploading",
                    ocrPending: isImage,
                },
                ...prev,
            ]);

            if (!ALLOWED_EXTENSIONS.includes(ext)) {
                setActivityStatus(key, "failed", { error: "Unsupported file type" });
                continue;
            }

            if (file.size > MAX_FILE_SIZE) {
                setActivityStatus(key, "failed", { error: "File exceeds 25MB" });
                continue;
            }

            try {
                const formData = new FormData();
                formData.append("file", file);

                const payload = (await api.student.upload(formData)) as {
                    success?: boolean;
                    chunks?: number;
                    error?: string;
                    ocr_processed?: boolean;
                    ocr_review_required?: boolean;
                    ocr_warning?: string;
                    ocr_confidence?: number;
                };

                if (payload?.success === false) {
                    throw new Error(payload.error || "Upload failed");
                }

                setActivityStatus(key, "completed", {
                    chunks: payload?.chunks || 0,
                    ocrProcessed: payload?.ocr_processed,
                    ocrReviewRequired: payload?.ocr_review_required,
                    ocrWarning: payload?.ocr_warning,
                    ocrConfidence: typeof payload?.ocr_confidence === "number" ? payload.ocr_confidence : undefined,
                });
            } catch (err) {
                setActivityStatus(key, "failed", {
                    error: err instanceof Error ? err.message : "Upload failed",
                });
            }
        }

        try {
            await loadUploads();
        } catch {
            // Keep local activity visible even if upload list refresh fails.
        }
    };

    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <div className="grid gap-6 xl:grid-cols-[1.15fr_0.85fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student ingestion flow
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Bring notes, slides, and photos into one <span className="premium-gradient">study-ready intake surface</span>
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                This route now frames uploads as the start of the learning loop: drop files, monitor OCR and indexing, then move directly into quiz, assistant, or AI Studio flows.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <UploadMetric
                            icon={Upload}
                            label="Stored files"
                            value={`${summary.total}`}
                            detail="All uploaded material currently available in your study base."
                            tint="from-sky-400/20 to-indigo-500/10"
                            iconClass="text-status-blue"
                        />
                        <UploadMetric
                            icon={CheckCircle2}
                            label="Ready for study"
                            value={`${summary.completed}`}
                            detail="Uploads that finished indexing and can ground AI answers."
                            tint="from-emerald-400/20 to-teal-500/10"
                            iconClass="text-status-emerald"
                        />
                        <UploadMetric
                            icon={ScanSearch}
                            label="OCR surfaces"
                            value={`${summary.imageWork}`}
                            detail="Recent image-based uploads that passed through OCR or review."
                            tint="from-amber-300/20 to-orange-500/10"
                            iconClass="text-status-amber"
                        />
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="student-upload"
                        onRetry={() => {
                            void (async () => {
                                try {
                                    setLoading(true);
                                    setError(null);
                                    await loadUploads();
                                } catch (err) {
                                    setError(err instanceof Error ? err.message : "Failed to load uploads");
                                } finally {
                                    setLoading(false);
                                }
                            })();
                        }}
                        simplifiedModeHref="/student/tools"
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[1fr_0.92fr]">
                    <PrismPanel className="space-y-5 p-5">
                        <div className="space-y-1">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Upload zone</p>
                            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Drop files, camera captures, or scanned pages</h2>
                            <p className="text-sm leading-6 text-[var(--text-secondary)]">
                                PDFs and office documents index directly. Images pass through OCR so assistant responses can cite your own source material.
                            </p>
                        </div>

                        <div
                            className={cn(
                                "cursor-pointer rounded-[calc(var(--radius)*1.05)] border-2 border-dashed p-10 text-center transition-all",
                                isDragging
                                    ? "border-[var(--primary)] bg-[linear-gradient(180deg,rgba(96,165,250,0.16),rgba(129,140,248,0.08))]"
                                    : "border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02))] hover:border-[var(--primary)]/60 hover:bg-[linear-gradient(180deg,rgba(255,255,255,0.07),rgba(255,255,255,0.03))]"
                            )}
                            onDragOver={(e) => {
                                e.preventDefault();
                                setIsDragging(true);
                            }}
                            onDragLeave={() => setIsDragging(false)}
                            onDrop={(e) => {
                                e.preventDefault();
                                setIsDragging(false);
                                void processFiles(e.dataTransfer.files);
                            }}
                            onClick={() => inputRef.current?.click()}
                        >
                            <input
                                ref={inputRef}
                                type="file"
                                multiple
                                accept=".pdf,.docx,.pptx,.xlsx,image/*"
                                capture="environment"
                                className="hidden"
                                onChange={(e) => {
                                    if (e.target.files) {
                                        void processFiles(e.target.files);
                                    }
                                }}
                            />
                            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-3xl border border-white/10 bg-white/5">
                                <Upload className="h-7 w-7 text-[var(--primary)]" />
                            </div>
                            <p className="text-base font-semibold text-[var(--text-primary)]">Drop files here or click to browse</p>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">PDF, DOCX, PPTX, XLSX, JPG, PNG up to 25MB each</p>
                        </div>

                        <div className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-[linear-gradient(135deg,rgba(96,165,250,0.14),rgba(129,140,248,0.08))] p-4">
                            <div className="flex items-start gap-3">
                                <Bot className="mt-0.5 h-4 w-4 flex-shrink-0 text-[var(--primary)]" />
                                <p className="text-sm leading-6 text-[var(--text-secondary)]">
                                    Uploads are chunked and indexed for retrieval. Once ready, your study tools and assistant can answer from your own material instead of generic context.
                                </p>
                            </div>
                        </div>
                    </PrismPanel>

                    <PrismPanel className="space-y-5 p-5">
                        <div className="space-y-1">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Recent activity</p>
                            <h2 className="text-lg font-semibold text-[var(--text-primary)]">Track processing, OCR, and failures</h2>
                        </div>

                        {activity.length === 0 ? (
                            <EmptyState
                                icon={Upload}
                                title="No upload activity yet"
                                description="Your most recent uploads, OCR checks, and indexing results will appear here once you start adding materials."
                            />
                        ) : (
                            <div className="space-y-3">
                                {activity.map((item) => (
                                    <div key={item.key} className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-black/10 p-4">
                                        <div className="flex items-start justify-between gap-3">
                                            <div className="flex items-start gap-3">
                                                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-white/5">
                                                    <FileText className="h-4 w-4 text-[var(--primary)]" />
                                                </div>
                                                <div className="space-y-1">
                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{item.name}</p>
                                                    <p className="text-xs leading-5 text-[var(--text-secondary)]">
                                                        {item.type.toUpperCase()}
                                                        {item.chunks !== undefined ? ` | ${item.chunks} chunks indexed` : ""}
                                                        {item.status === "uploading" && item.ocrPending ? " | OCR in progress" : ""}
                                                        {item.status === "completed" && item.ocrProcessed ? " | OCR completed" : ""}
                                                        {item.ocrReviewRequired ? " | OCR review recommended" : ""}
                                                        {typeof item.ocrConfidence === "number" ? ` | OCR confidence ${Math.round(item.ocrConfidence * 100)}%` : ""}
                                                        {item.ocrWarning ? ` | ${item.ocrWarning}` : ""}
                                                        {item.error ? ` | ${item.error}` : ""}
                                                    </p>
                                                </div>
                                            </div>
                                            <ActivityStatus status={item.status} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </PrismPanel>
                </div>

                {latestCompletedActivity ? (
                    <PrismPanel className="space-y-4 p-5">
                        <div className="flex items-start gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(129,140,248,0.08))] text-[var(--primary)]">
                                <Bot className="h-5 w-5" />
                            </div>
                            <div className="min-w-0 flex-1">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Next study steps</p>
                                <h2 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">Your latest upload is ready to drive the next study action</h2>
                                <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                                    Turn <span className="font-medium text-[var(--text-primary)]">{latestCompletedActivity.name}</span> into a guided explanation, quick quiz, or deeper AI Studio session.
                                </p>
                            </div>
                        </div>
                        <div className="grid gap-3 md:grid-cols-3">
                            <Link
                                href={buildMascotPromptHref(`Summarize my latest upload "${latestCompletedActivity.name}" and tell me the best next study step.`)}
                                className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-black/10 p-4 transition hover:-translate-y-0.5 hover:border-white/15"
                            >
                                <p className="text-sm font-semibold text-[var(--text-primary)]">Ask and understand</p>
                                <p className="mt-1 text-xs leading-6 text-[var(--text-secondary)]">Open the mascot with a guided summary prompt and get the best next action.</p>
                            </Link>
                            <Link
                                href={buildMascotPromptHref(`Create a short quiz from my latest upload "${latestCompletedActivity.name}" and focus on the weakest concepts first.`)}
                                className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-black/10 p-4 transition hover:-translate-y-0.5 hover:border-white/15"
                            >
                                <p className="text-sm font-semibold text-[var(--text-primary)]">Practice immediately</p>
                                <p className="mt-1 text-xs leading-6 text-[var(--text-secondary)]">Start a mastery-aware quiz flow without manually switching tools first.</p>
                            </Link>
                            <Link
                                href="/student/ai-studio"
                                className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-black/10 p-4 transition hover:-translate-y-0.5 hover:border-white/15"
                            >
                                <p className="text-sm font-semibold text-[var(--text-primary)]">Go deeper in AI Studio</p>
                                <p className="mt-1 text-xs leading-6 text-[var(--text-secondary)]">Continue with the full AI workspace when you want a longer multi-step study session.</p>
                            </Link>
                        </div>
                    </PrismPanel>
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[1.08fr_0.92fr]">
                    <PrismPanel className="overflow-hidden p-0">
                        <div className="flex items-center justify-between gap-3 border-b border-white/8 px-5 py-4">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Uploaded files</p>
                                <h2 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">Indexed material ledger</h2>
                            </div>
                            <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-[var(--text-secondary)]">
                                {summary.processing} processing
                            </div>
                        </div>
                        <PrismTableShell>
                            <table className="prism-table w-full min-w-[640px]">
                                <thead>
                                    <tr>
                                        <th>File</th>
                                        <th>Type</th>
                                        <th>Status</th>
                                        <th>Uploaded</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {loading ? (
                                        <tr>
                                            <td className="py-8 text-sm text-[var(--text-muted)]" colSpan={4}>
                                                Loading uploads...
                                            </td>
                                        </tr>
                                    ) : uploads.length === 0 ? (
                                        <tr>
                                            <td className="py-8 text-sm text-[var(--text-muted)]" colSpan={4}>
                                                No uploaded files yet.
                                            </td>
                                        </tr>
                                    ) : (
                                        uploads.map((upload) => (
                                            <tr key={upload.id} className="border-b border-white/6">
                                                <td className="text-sm font-medium text-[var(--text-primary)]">{upload.file_name}</td>
                                                <td className="text-xs font-semibold uppercase text-[var(--text-secondary)]">{upload.file_type}</td>
                                                <td className="text-xs">
                                                    <UploadStatusBadge status={upload.status} />
                                                </td>
                                                <td className="text-xs text-[var(--text-secondary)]">{upload.uploaded_at}</td>
                                            </tr>
                                        ))
                                    )}
                                </tbody>
                            </table>
                        </PrismTableShell>
                    </PrismPanel>

                    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1">
                        {[
                            { label: "PDF", desc: "Textbooks and chapter notes" },
                            { label: "DOCX", desc: "Reports, essays, and handouts" },
                            { label: "Images", desc: "OCR from photos and scans" },
                            { label: "Limit", desc: "Up to 25MB per file" },
                        ].map((item) => (
                            <PrismPanel key={item.label} className="p-4">
                                <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-white/5">
                                    <FileText className="h-4 w-4 text-[var(--text-secondary)]" />
                                </div>
                                <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{item.label}</p>
                                <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">{item.desc}</p>
                            </PrismPanel>
                        ))}
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function UploadMetric({
    icon: Icon,
    label,
    value,
    detail,
    tint,
    iconClass,
}: {
    icon: typeof Upload;
    label: string;
    value: string;
    detail: string;
    tint: string;
    iconClass: string;
}) {
    return (
        <PrismPanel className="p-4">
            <div className={cn("mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,var(--tw-gradient-stops))]", tint)}>
                <Icon className={cn("h-5 w-5", iconClass)} />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p>
        </PrismPanel>
    );
}

function ActivityStatus({ status }: { status: ActivityItem["status"] }) {
    if (status === "uploading") {
        return (
            <div className="inline-flex items-center gap-1.5 rounded-full bg-blue-500/10 px-3 py-1 text-xs font-semibold text-status-blue">
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
                Processing
            </div>
        );
    }

    if (status === "completed") {
        return (
            <div className="inline-flex items-center gap-1.5 rounded-full bg-emerald-500/10 px-3 py-1 text-xs font-semibold text-status-emerald">
                <CheckCircle2 className="h-3.5 w-3.5" />
                Completed
            </div>
        );
    }

    return (
        <div className="inline-flex items-center gap-1.5 rounded-full bg-red-500/10 px-3 py-1 text-xs font-semibold text-[var(--error)]">
            <XCircle className="h-3.5 w-3.5" />
            Failed
        </div>
    );
}

function UploadStatusBadge({ status }: { status: UploadRecord["status"] }) {
    if (status === "completed") {
        return <span className="rounded-full bg-emerald-500/10 px-3 py-1 font-semibold text-status-emerald">completed</span>;
    }
    if (status === "processing") {
        return <span className="rounded-full bg-blue-500/10 px-3 py-1 font-semibold text-status-blue">processing</span>;
    }
    return <span className="rounded-full bg-red-500/10 px-3 py-1 font-semibold text-[var(--error)]">failed</span>;
}
