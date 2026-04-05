"use client";

import { useEffect, useMemo, useState } from "react";
import { CheckCircle2, Clock, Upload, GraduationCap, AlertCircle, FileText, Bot, UploadCloud } from "lucide-react";

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
    { id: "all", label: "All Items" },
    { id: "pending", label: "Needs Action" },
    { id: "submitted", label: "Submitted" },
    { id: "graded", label: "Graded" },
];

type OCRNote = {
    reviewRequired: boolean;
    warning: string | null;
    confidence?: number;
};

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
                [assignmentId]: payload?.ocr_review_required || payload?.ocr_warning
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
        <div className="max-w-4xl mx-auto space-y-6">
            <div className="flex flex-col md:flex-row md:items-end justify-between gap-4 mb-4">
                <div>
                    <h1 className="text-3xl font-black text-[var(--text-primary)] flex items-center gap-3 tracking-tight">
                        <FileText className="w-8 h-8 text-[var(--accent-indigo)]" />
                        Assignments Explorer
                    </h1>
                    <p className="text-sm text-[var(--text-muted)] mt-2 italic">Track deadlines, submit homework via camera or file, and review graded outcomes.</p>
                </div>
            </div>

            {error && (
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-500 shadow-md animate-in fade-in flex items-center gap-2">
                    <AlertCircle className="w-4 h-4" /> {error}
                </div>
            )}

            {/* Futuristic Tab Bar */}
            <div className="flex flex-wrap gap-2 p-1 bg-[var(--bg-card)]/50 backdrop-blur-md rounded-2xl w-fit border border-[var(--border-light)] shadow-sm">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id)}
                        className={`relative px-5 py-2 text-sm font-bold rounded-xl transition-all duration-300 ${
                            activeTab === tab.id
                                ? "text-white shadow-md shadow-indigo-500/20"
                                : "text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--bg-page)]"
                        }`}
                    >
                        {activeTab === tab.id && (
                            <div className="absolute inset-0 bg-gradient-to-r from-indigo-500 to-purple-500 rounded-xl pointer-events-none -z-10 animate-in zoom-in-95" />
                        )}
                        {tab.label}
                    </button>
                ))}
            </div>

            <div className="space-y-4">
                {loading ? (
                    <div className="flex flex-col items-center justify-center p-20 glass-panel border border-[var(--border-light)] rounded-3xl opacity-70">
                        <Clock className="w-12 h-12 text-[var(--text-muted)] mb-4 animate-spin-slow" />
                        <p className="text-sm font-medium text-[var(--text-muted)] animate-pulse">Syncing assignment ledger...</p>
                    </div>
                ) : filteredAssignments.length === 0 ? (
                    <div className="flex flex-col items-center justify-center p-20 glass-panel border border-[var(--border-light)] rounded-3xl text-center">
                        <CheckCircle2 className="w-16 h-16 text-[var(--text-muted)] opacity-30 mb-4" />
                        <h3 className="text-lg font-bold text-[var(--text-primary)] mb-1">You&apos;re all caught up!</h3>
                        <p className="text-xs font-medium text-[var(--text-muted)]">No assignments found in this category.</p>
                    </div>
                ) : (
                    filteredAssignments.map((item, idx) => {
                        const isGraded = item.status === "graded";
                        const isSubmitted = item.status === "submitted";
                        const isPending = item.status === "pending";

                        return (
                            <div key={item.id} className={`relative overflow-hidden bg-[var(--bg-card)]/90 backdrop-blur-sm rounded-2xl p-6 shadow-sm hover:shadow-lg border border-[var(--border-light)] transition-shadow duration-300 stagger-${Math.min(idx + 1, 6)} group`}>
                                {/* Abstract Status Edge Bar */}
                                <div className={`absolute top-0 left-0 w-1.5 h-full ${
                                    isGraded ? "bg-gradient-to-b from-emerald-400 to-teal-500" :
                                    isSubmitted ? "bg-gradient-to-b from-blue-400 to-indigo-500" :
                                    "bg-gradient-to-b from-amber-400 to-orange-500"
                                }`} />

                                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-6 pl-4">
                                    <div className="flex items-start gap-5">
                                        <div
                                            className={`w-12 h-12 rounded-xl flex items-center justify-center shrink-0 shadow-inner ${
                                                isGraded ? "bg-emerald-500/10 text-emerald-500"
                                                : isSubmitted ? "bg-blue-500/10 text-blue-500"
                                                : "bg-amber-500/10 text-amber-500"
                                            }`}
                                        >
                                            {isGraded ? <GraduationCap className="w-6 h-6" />
                                            : isSubmitted ? <CheckCircle2 className="w-6 h-6" />
                                            : <Clock className="w-6 h-6 animate-pulse" />}
                                        </div>
                                        <div>
                                            <div className="flex items-center gap-2 mb-1">
                                                <h3 className="text-lg font-bold text-[var(--text-primary)] group-hover:text-[var(--accent-indigo)] transition-colors">{item.title}</h3>
                                                <span className={`text-[10px] font-black uppercase tracking-wider px-2 py-0.5 rounded-md ${
                                                    isGraded ? "bg-emerald-500/10 text-emerald-600 dark:text-emerald-400"
                                                    : isSubmitted ? "bg-blue-500/10 text-blue-600 dark:text-blue-400"
                                                    : "bg-amber-500/10 text-amber-600 dark:text-amber-400"
                                                }`}>
                                                    {item.status}
                                                </span>
                                            </div>
                                            <p className="text-xs font-semibold text-[var(--text-muted)] flex flex-wrap items-center gap-2">
                                                <span className="text-[var(--text-primary)] opacity-80">{item.subject}</span>
                                                <span className="w-1 h-1 rounded-full bg-[var(--text-muted)] opacity-50" />
                                                <span>Due: {item.due || "No date set"}</span>
                                            </p>

                                            {item.submitted_at && (
                                                <p className="text-[10px] text-[var(--text-muted)] mt-2 flex items-center gap-1 opacity-70">
                                                    <UploadCloud className="w-3 h-3" /> Submitted at {item.submitted_at}
                                                </p>
                                            )}

                                            {ocrNotes[item.id] && (ocrNotes[item.id]!.reviewRequired || ocrNotes[item.id]!.warning) && (
                                                <div className="mt-3 inline-flex flex-col bg-amber-500/5 border border-amber-500/20 rounded-lg p-2.5 max-w-sm">
                                                    <p className="text-[10px] font-bold text-amber-600 dark:text-amber-400 flex items-center gap-1.5 uppercase tracking-wide">
                                                        <AlertCircle className="w-3 h-3" />
                                                        OCR Scanning Alert
                                                    </p>
                                                    <p className="text-xs text-[var(--text-secondary)] mt-1 ml-4.5 leading-snug">
                                                        {typeof ocrNotes[item.id]?.confidence === "number" && `Clarity at ${Math.round(ocrNotes[item.id]!.confidence! * 100)}%. `}
                                                        Please review your image{ocrNotes[item.id]?.warning ? `: ${ocrNotes[item.id]?.warning}` : "."}
                                                    </p>
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-3 sm:ml-auto w-full sm:w-auto flex-wrap sm:flex-nowrap pt-4 sm:pt-0 border-t border-[var(--border-light)] sm:border-0">
                                        {isGraded && (
                                            <div className="flex flex-col items-center justify-center px-4 shrink-0">
                                                <span className="text-xs font-black uppercase tracking-widest text-[var(--text-muted)] mb-1">Score</span>
                                                <span className="text-3xl font-black text-[var(--text-primary)]">
                                                    {item.grade ?? 0}<span className="text-sm opacity-50">/100</span>
                                                </span>
                                            </div>
                                        )}

                                        <a
                                            href="/student/assistant"
                                            className="px-4 py-2.5 rounded-xl bg-purple-500/10 text-purple-600 dark:text-purple-400 text-xs font-bold hover:bg-purple-500/20 transition-colors flex items-center gap-1.5 flex-1 sm:flex-initial justify-center"
                                        >
                                            <Bot className="w-4 h-4" /> Need Help?
                                        </a>

                                        <label className={`px-4 py-2.5 rounded-xl text-white text-xs font-bold cursor-pointer transition-all shadow-md flex-1 sm:flex-initial flex items-center justify-center gap-2 ${
                                            uploadingId === item.id 
                                                ? "bg-[var(--text-muted)] cursor-not-allowed"
                                                : isPending 
                                                    ? "bg-gradient-to-r from-blue-500 to-indigo-600 hover:shadow-indigo-500/20 hover:scale-105" 
                                                    : "bg-[var(--bg-page)] text-[var(--text-primary)] border border-[var(--border-light)] hover:bg-[var(--border-light)] hover:shadow-none bg-none shadow-none"
                                        }`}>
                                            {uploadingId === item.id ? (
                                                <>&nbsp;&nbsp;<Clock className="w-4 h-4 animate-spin-slow" /> Uploading...&nbsp;&nbsp;</>
                                            ) : isPending ? (
                                                <><UploadCloud className="w-4 h-4" /> Upload Homework</>
                                            ) : (
                                                <><Upload className="w-4 h-4" /> Replace File</>
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
                        );
                    })
                )}
            </div>
        </div>
    );
}
