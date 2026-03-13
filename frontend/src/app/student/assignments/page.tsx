"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Clock, Upload } from "lucide-react";

import { api } from "@/lib/api";

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

const tabs: Array<{ id: Tab; label: string }> = [
    { id: "all", label: "All" },
    { id: "pending", label: "Pending" },
    { id: "submitted", label: "Submitted" },
    { id: "graded", label: "Graded" },
];

export default function AssignmentsPage() {
    const [assignments, setAssignments] = useState<AssignmentItem[]>([]);
    const [activeTab, setActiveTab] = useState<Tab>("all");
    const [loading, setLoading] = useState(true);
    const [uploadingId, setUploadingId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

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

    const submitAssignment = async (assignmentId: string, file: File | null) => {
        if (!file) return;
        try {
            setUploadingId(assignmentId);
            setError(null);
            const formData = new FormData();
            formData.append("file", file);
            await api.student.submitAssignment(assignmentId, formData);
            await loadAssignments();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to submit assignment");
        } finally {
            setUploadingId(null);
        }
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Assignments</h1>
                <p className="text-sm text-[var(--text-secondary)]">Track status, submit work, and review graded assignments.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="mb-4 flex flex-wrap gap-2">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                            activeTab === tab.id
                                ? "bg-[var(--primary)] text-white border-[var(--primary)]"
                                : "bg-[var(--bg-card)] text-[var(--text-secondary)] border-[var(--border)] hover:border-[var(--primary)]"
                        }`}
                    >
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="space-y-3">
                {loading ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                        Loading assignments...
                    </div>
                ) : filteredAssignments.length === 0 ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                        No assignments in this tab.
                    </div>
                ) : (
                    filteredAssignments.map((item) => (
                        <div key={item.id} className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] flex items-center justify-between gap-3">
                            <div className="flex items-start gap-4">
                                <div
                                    className={`w-10 h-10 rounded-[var(--radius-sm)] flex items-center justify-center ${
                                        item.status === "graded"
                                            ? "bg-success-subtle"
                                            : item.status === "submitted"
                                              ? "bg-info-subtle"
                                              : "bg-warning-subtle"
                                    }`}
                                >
                                    {item.status === "graded" ? (
                                        <CheckCircle2 className="w-5 h-5 text-[var(--success)]" />
                                    ) : item.status === "submitted" ? (
                                        <Upload className="w-5 h-5 text-[var(--primary)]" />
                                    ) : (
                                        <Clock className="w-5 h-5 text-[var(--warning)]" />
                                    )}
                                </div>
                                <div>
                                    <h3 className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</h3>
                                    <p className="text-xs text-[var(--text-muted)]">
                                        {item.subject} | Due: {item.due || "-"}
                                    </p>
                                    {item.submitted_at ? (
                                        <p className="text-[11px] text-[var(--text-muted)] mt-1">Submitted: {item.submitted_at}</p>
                                    ) : null}
                                </div>
                            </div>

                            <div className="flex items-center gap-3 flex-wrap justify-end">
                                {item.status === "graded" ? (
                                    <span className="text-sm font-bold text-[var(--success)]">{item.grade ?? 0}/100</span>
                                ) : null}

                                <span
                                    className={`text-xs font-medium px-2.5 py-1 rounded-full capitalize ${
                                        item.status === "graded"
                                            ? "bg-success-subtle text-[var(--success)]"
                                            : item.status === "submitted"
                                              ? "bg-info-subtle text-[var(--primary)]"
                                              : "bg-warning-subtle text-[var(--warning)]"
                                    }`}
                                >
                                    {item.status}
                                </span>

                                <a
                                    href={`/student/ai?q=${encodeURIComponent(`Help me with: ${item.title}`)}`}
                                    className="text-xs font-medium text-[var(--primary)] hover:underline"
                                >
                                    AI Help
                                </a>

                                <label className="text-xs font-medium text-[var(--primary)] hover:underline cursor-pointer">
                                    {uploadingId === item.id ? "Uploading..." : item.status === "pending" ? "Upload Submission" : "Replace Submission"}
                                    <input
                                        type="file"
                                        accept=".pdf,.docx"
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
                    ))
                )}
            </div>
        </div>
    );
}
