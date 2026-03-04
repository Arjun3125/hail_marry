"use client";

import { useEffect, useRef, useState } from "react";
import { Bot, CheckCircle2, FileText, Loader2, Upload, XCircle } from "lucide-react";

import { api } from "@/lib/api";

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
};

const ALLOWED_EXTENSIONS = ["pdf", "docx"];
const MAX_FILE_SIZE = 25 * 1024 * 1024;

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

    const processFiles = async (fileList: FileList | File[]) => {
        const files = Array.from(fileList);
        if (files.length === 0) return;

        setError(null);

        for (const file of files) {
            const ext = file.name.split(".").pop()?.toLowerCase() || "";
            const key = `${Date.now()}-${file.name}-${Math.random().toString(36).slice(2, 8)}`;

            setActivity((prev) => [
                {
                    key,
                    name: file.name,
                    type: ext,
                    status: "uploading",
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
                };

                if (payload?.success === false) {
                    throw new Error(payload.error || "Upload failed");
                }

                setActivityStatus(key, "completed", { chunks: payload?.chunks || 0 });
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
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Upload Study Materials</h1>
                <p className="text-sm text-[var(--text-secondary)]">Upload PDF and DOCX files for AI-grounded answers.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div
                className={`border-2 border-dashed rounded-[var(--radius)] p-10 text-center transition-colors cursor-pointer ${
                    isDragging
                        ? "border-[var(--primary)] bg-[var(--primary-light)]"
                        : "border-[var(--border)] bg-white hover:border-[var(--primary)] hover:bg-blue-50/30"
                }`}
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
                    accept=".pdf,.docx"
                    className="hidden"
                    onChange={(e) => {
                        if (e.target.files) {
                            void processFiles(e.target.files);
                        }
                    }}
                />
                <Upload className="w-10 h-10 mx-auto text-[var(--primary)] mb-3" />
                <p className="text-sm font-medium text-[var(--text-primary)] mb-1">Drop files here or click to browse</p>
                <p className="text-xs text-[var(--text-muted)]">PDF, DOCX up to 25MB each</p>
            </div>

            <div className="mt-4 p-3 bg-[var(--primary-light)] rounded-[var(--radius-sm)] flex items-start gap-2">
                <Bot className="w-4 h-4 text-[var(--primary)] mt-0.5 flex-shrink-0" />
                <p className="text-xs text-[var(--primary)]">
                    Uploads are chunked and indexed for retrieval. AI answers can then cite content from your own notes.
                </p>
            </div>

            {activity.length > 0 ? (
                <div className="mt-6 space-y-2">
                    <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Recent Upload Activity</h2>
                    {activity.map((item) => (
                        <div key={item.key} className="bg-white rounded-[var(--radius-sm)] shadow-[var(--shadow-card)] p-3 flex items-center justify-between">
                            <div className="flex items-center gap-3">
                                <div className="w-8 h-8 rounded-[var(--radius-sm)] flex items-center justify-center bg-[var(--primary-light)]">
                                    <FileText className="w-4 h-4 text-[var(--primary)]" />
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-[var(--text-primary)]">{item.name}</p>
                                    <p className="text-[10px] text-[var(--text-muted)]">
                                        {item.type.toUpperCase()}
                                        {item.chunks !== undefined ? ` | ${item.chunks} chunks indexed` : ""}
                                        {item.error ? ` | ${item.error}` : ""}
                                    </p>
                                </div>
                            </div>
                            <div className="text-xs font-medium flex items-center gap-1.5">
                                {item.status === "uploading" ? (
                                    <>
                                        <Loader2 className="w-3.5 h-3.5 text-[var(--primary)] animate-spin" /> Processing
                                    </>
                                ) : item.status === "completed" ? (
                                    <>
                                        <CheckCircle2 className="w-3.5 h-3.5 text-[var(--success)]" /> Completed
                                    </>
                                ) : (
                                    <>
                                        <XCircle className="w-3.5 h-3.5 text-[var(--error)]" /> Failed
                                    </>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : null}

            <div className="mt-8 bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="px-5 py-3 border-b border-[var(--border)]">
                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Uploaded Files</h2>
                </div>
                <table className="w-full">
                    <thead>
                        <tr className="border-b border-[var(--border)]">
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">File</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Type</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Status</th>
                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Uploaded At</th>
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={4}>
                                    Loading uploads...
                                </td>
                            </tr>
                        ) : uploads.length === 0 ? (
                            <tr>
                                <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={4}>
                                    No uploaded files yet.
                                </td>
                            </tr>
                        ) : (
                            uploads.map((upload) => (
                                <tr key={upload.id} className="border-b border-[var(--border-light)]">
                                    <td className="px-5 py-3 text-sm text-[var(--text-primary)]">{upload.file_name}</td>
                                    <td className="px-5 py-3 text-xs font-medium uppercase text-[var(--text-secondary)]">{upload.file_type}</td>
                                    <td className="px-5 py-3 text-xs">
                                        <span
                                            className={`px-2 py-1 rounded-full font-medium capitalize ${
                                                upload.status === "completed"
                                                    ? "bg-green-50 text-[var(--success)]"
                                                    : upload.status === "processing"
                                                      ? "bg-blue-50 text-[var(--primary)]"
                                                      : "bg-red-50 text-[var(--error)]"
                                            }`}
                                        >
                                            {upload.status}
                                        </span>
                                    </td>
                                    <td className="px-5 py-3 text-xs text-[var(--text-secondary)]">{upload.uploaded_at}</td>
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>

            <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-3">
                {[
                    { label: "PDF", desc: "Textbooks, notes" },
                    { label: "DOCX", desc: "Reports, essays" },
                    { label: "Limit", desc: "Up to 25MB" },
                    { label: "AI", desc: "Indexed for search" },
                ].map((item) => (
                    <div key={item.label} className="bg-white rounded-[var(--radius-sm)] p-3 shadow-[var(--shadow-card)] text-center">
                        <div className="w-8 h-8 mx-auto rounded-full bg-[var(--bg-page)] flex items-center justify-center mb-2">
                            <FileText className="w-4 h-4 text-[var(--text-secondary)]" />
                        </div>
                        <p className="text-xs font-semibold text-[var(--text-primary)]">{item.label}</p>
                        <p className="text-[10px] text-[var(--text-muted)]">{item.desc}</p>
                    </div>
                ))}
            </div>
        </div>
    );
}
