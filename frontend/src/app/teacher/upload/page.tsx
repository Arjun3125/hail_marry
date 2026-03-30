"use client";

import { useEffect, useMemo, useState } from "react";
import { AlertCircle, CheckCircle2, FileText, Loader2, Upload, Youtube } from "lucide-react";

import { api } from "@/lib/api";

type SubjectItem = {
    id: string;
    name: string;
};

type TeacherClass = {
    id: string;
    name: string;
    subjects: SubjectItem[];
};

type UploadActivity = {
    id: string;
    name: string;
    type: "document" | "youtube";
    status: "processing" | "completed" | "failed";
    detail?: string;
    ocrWarning?: string;
    ocrReviewRequired?: boolean;
    ocrPending?: boolean;
    ocrProcessed?: boolean;
    ocrConfidence?: number;
};
type AIJobStatus = "queued" | "running" | "completed" | "failed";

const ALLOWED_EXTENSIONS = ["pdf", "docx", "pptx", "xlsx", "jpg", "jpeg", "png"];
const MAX_FILE_SIZE = 50 * 1024 * 1024;

export default function UploadPage() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [subjectId, setSubjectId] = useState("");
    const [youtubeUrl, setYoutubeUrl] = useState("");
    const [youtubeTitle, setYoutubeTitle] = useState("");
    const [activities, setActivities] = useState<UploadActivity[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const allSubjects = useMemo(() => {
        const map = new Map<string, SubjectItem>();
        for (const cls of classes) {
            for (const subject of cls.subjects || []) {
                if (!map.has(subject.id)) {
                    map.set(subject.id, subject);
                }
            }
        }
        return Array.from(map.values());
    }, [classes]);

    useEffect(() => {
        if (!allSubjects.some((subject) => subject.id === subjectId)) {
            setSubjectId(allSubjects[0]?.id || "");
        }
    }, [allSubjects, subjectId]);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.classes();
                setClasses((payload || []) as TeacherClass[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes and subjects");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const pushActivity = (item: UploadActivity) => {
        setActivities((prev) => [item, ...prev]);
    };

    const updateActivity = (id: string, patch: Partial<UploadActivity>) => {
        setActivities((prev) => prev.map((item) => (item.id === id ? { ...item, ...patch } : item)));
    };

    const pollJob = async (activityId: string, jobId: string, onComplete: (result?: Record<string, unknown>) => void) => {
        try {
            const job = (await api.ai.jobStatus(jobId)) as {
                status: AIJobStatus;
                error?: string;
                result?: Record<string, unknown>;
                poll_after_ms?: number;
            };

            if (job.status === "completed") {
                onComplete(job.result);
                return;
            }

            if (job.status === "failed") {
                updateActivity(activityId, {
                    status: "failed",
                    detail: job.error || "Ingestion failed",
                });
                return;
            }

            setTimeout(() => {
                void pollJob(activityId, jobId, onComplete);
            }, job.poll_after_ms ?? 2000);
        } catch (err) {
            updateActivity(activityId, {
                status: "failed",
                detail: err instanceof Error ? err.message : "Ingestion failed",
            });
        }
    };

    const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
        const fileList = e.target.files;
        if (!fileList) return;

        for (const file of Array.from(fileList)) {
            const ext = file.name.split(".").pop()?.toLowerCase() || "";
            const id = `${Date.now()}-${file.name}-${Math.random().toString(36).slice(2, 8)}`;
            const isImage = ["jpg", "jpeg", "png"].includes(ext);
            pushActivity({
                id,
                name: file.name,
                type: "document",
                status: "processing",
                ocrPending: isImage,
            });

            if (!ALLOWED_EXTENSIONS.includes(ext)) {
                updateActivity(id, {
                    status: "failed",
                    detail: "Only PDF, DOCX, PPTX, XLSX, JPG, PNG are allowed",
                });
                continue;
            }

            if (file.size > MAX_FILE_SIZE) {
                updateActivity(id, {
                    status: "failed",
                    detail: "File exceeds 50MB limit",
                });
                continue;
            }

            try {
                const formData = new FormData();
                formData.append("file", file);

                const payload = (await api.teacher.uploadDocument(formData)) as {
                    success?: boolean;
                    job_id?: string;
                    status?: AIJobStatus;
                    error?: string;
                    ocr_processed?: boolean;
                    ocr_review_required?: boolean;
                    ocr_warning?: string;
                    ocr_confidence?: number;
                };

                if (payload?.success === false) {
                    throw new Error(payload.error || "Upload failed");
                }

                if (!payload.job_id) {
                    updateActivity(id, {
                        status: "completed",
                        detail: "Ingested",
                        ocrProcessed: payload.ocr_processed,
                        ocrReviewRequired: payload.ocr_review_required,
                        ocrWarning: payload.ocr_warning,
                        ocrConfidence: typeof payload.ocr_confidence === "number" ? payload.ocr_confidence : undefined,
                    });
                } else {
                    updateActivity(id, {
                        status: "processing",
                        detail: "Queued for ingestion",
                    });

                    void pollJob(id, payload.job_id, (result) => {
                        updateActivity(id, {
                            status: "completed",
                            detail: `Ingested (${Number(result?.chunks ?? 0)} chunks)`,
                            ocrProcessed: payload.ocr_processed,
                            ocrReviewRequired: payload.ocr_review_required,
                            ocrWarning: payload.ocr_warning,
                            ocrConfidence: typeof payload.ocr_confidence === "number" ? payload.ocr_confidence : undefined,
                        });
                    });
                }
            } catch (err) {
                updateActivity(id, {
                    status: "failed",
                    detail: err instanceof Error ? err.message : "Upload failed",
                });
            }
        }

        e.target.value = "";
    };

    const handleYoutubeSubmit = async (e: React.FormEvent) => {
        e.preventDefault();

        if (!youtubeUrl.trim() || !youtubeTitle.trim() || !subjectId) {
            setError("YouTube URL, title, and subject are required");
            return;
        }

        setError(null);
        const id = `${Date.now()}-youtube-${Math.random().toString(36).slice(2, 8)}`;
        pushActivity({
            id,
            name: youtubeTitle.trim(),
            type: "youtube",
            status: "processing",
            detail: youtubeUrl.trim(),
        });

        try {
            const payload = (await api.teacher.ingestYoutube({
                url: youtubeUrl.trim(),
                title: youtubeTitle.trim(),
                subject_id: subjectId,
            })) as { success?: boolean; job_id?: string; status?: AIJobStatus; error?: string };

            if (payload?.success === false) {
                throw new Error(payload.error || "YouTube ingestion failed");
            }

            if (!payload.job_id) {
                throw new Error("YouTube ingestion job was not created");
            }

            updateActivity(id, {
                status: "processing",
                detail: "Queued transcript ingestion",
            });

            void pollJob(id, payload.job_id, (result) => {
                updateActivity(id, {
                    status: "completed",
                    detail: `Transcript ingested (${Number(result?.chunks ?? 0)} chunks)`,
                });
            });

            setYoutubeUrl("");
            setYoutubeTitle("");
        } catch (err) {
            updateActivity(id, {
                status: "failed",
                detail: err instanceof Error ? err.message : "YouTube ingestion failed",
            });
        }
    };

    const statusIcon = {
        processing: <Loader2 className="w-4 h-4 text-[var(--primary)] animate-spin" />,
        completed: <CheckCircle2 className="w-4 h-4 text-[var(--success)]" />,
        failed: <AlertCircle className="w-4 h-4 text-[var(--error)]" />,
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Upload Notes</h1>
                <p className="text-sm text-[var(--text-secondary)]">Upload PDFs, documents, or photos. Images are converted with OCR for AI retrieval.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="grid lg:grid-cols-2 gap-6 mb-6">
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-6 shadow-[var(--shadow-card)]">
                    <div className="flex items-center gap-2 mb-4">
                        <Upload className="w-5 h-5 text-[var(--primary)]" />
                        <h2 className="text-base font-semibold text-[var(--text-primary)]">Upload Document</h2>
                    </div>
                    <label className="block border-2 border-dashed border-[var(--border)] rounded-[var(--radius)] p-8 text-center cursor-pointer hover:border-[var(--primary)] hover:bg-[var(--primary-light)] transition-all">
                        <FileText className="w-10 h-10 text-[var(--text-muted)] mx-auto mb-3" />
                        <p className="text-sm font-medium text-[var(--text-primary)]">Click to upload or drag files</p>
                        <p className="text-xs text-[var(--text-muted)] mt-1">PDF, DOCX, PPTX, XLSX, JPG, PNG (max 50MB)</p>
                        <input
                            type="file"
                            accept=".pdf,.docx,.pptx,.xlsx,image/*"
                            capture="environment"
                            multiple
                            onChange={handleFileUpload}
                            className="hidden"
                        />
                    </label>
                </div>

                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-6 shadow-[var(--shadow-card)]">
                    <div className="flex items-center gap-2 mb-4">
                        <Youtube className="w-5 h-5 text-[var(--error)]" />
                        <h2 className="text-base font-semibold text-[var(--text-primary)]">YouTube Lecture</h2>
                    </div>
                    <form onSubmit={(e) => void handleYoutubeSubmit(e)} className="space-y-3">
                        <select
                            value={subjectId}
                            onChange={(e) => setSubjectId(e.target.value)}
                            className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                            disabled={loading || allSubjects.length === 0}
                        >
                            {allSubjects.length === 0 ? (
                                <option value="">No subjects assigned</option>
                            ) : (
                                allSubjects.map((subject) => (
                                    <option key={subject.id} value={subject.id}>
                                        {subject.name}
                                    </option>
                                ))
                            )}
                        </select>
                        <input
                            type="text"
                            value={youtubeTitle}
                            onChange={(e) => setYoutubeTitle(e.target.value)}
                            placeholder="Lecture title"
                            className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                        />
                        <input
                            type="url"
                            value={youtubeUrl}
                            onChange={(e) => setYoutubeUrl(e.target.value)}
                            placeholder="Paste YouTube URL..."
                            className="w-full px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                        />
                        <button
                            type="submit"
                            className="w-full py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors disabled:opacity-60"
                            disabled={loading || !subjectId || !youtubeUrl.trim() || !youtubeTitle.trim()}
                        >
                            Ingest Lecture
                        </button>
                    </form>
                </div>
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="px-5 py-3 border-b border-[var(--border)]">
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent Upload Activity</h2>
                </div>
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[600px]">
                        <thead>
                            <tr className="border-b border-[var(--border)]">
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Name</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Type</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Status</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            {activities.length === 0 ? (
                                <tr>
                                    <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={4}>
                                        No uploads in this session yet.
                                    </td>
                                </tr>
                            ) : (
                                activities.map((activity) => (
                                    <tr key={activity.id} className="border-b border-[var(--border-light)] hover:bg-[var(--bg-page)]">
                                        <td className="px-5 py-3 text-sm text-[var(--text-primary)]">{activity.name}</td>
                                        <td className="px-5 py-3">
                                            <span className="text-xs font-medium uppercase text-[var(--text-muted)] bg-[var(--bg-page)] px-2 py-1 rounded">
                                                {activity.type}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3">
                                            <span className="flex items-center gap-1.5 text-xs font-medium capitalize">
                                                {statusIcon[activity.status]}
                                                {activity.status}
                                            </span>
                                        </td>
                                        <td className="px-5 py-3 text-xs text-[var(--text-secondary)]">
                                            {activity.detail || "-"}
                                            {activity.status === "processing" && activity.ocrPending ? " | OCR in progress" : ""}
                                            {activity.status === "completed" && activity.ocrProcessed ? " | OCR completed" : ""}
                                            {activity.ocrReviewRequired ? " | OCR review recommended" : ""}
                                            {typeof activity.ocrConfidence === "number" ? ` | OCR confidence ${Math.round(activity.ocrConfidence * 100)}%` : ""}
                                            {activity.ocrWarning ? ` | ${activity.ocrWarning}` : ""}
                                        </td>
                                    </tr>
                                ))
                            )}
                        </tbody>
                    </table>
                </div>
                </div>
            </div>
            );
}
