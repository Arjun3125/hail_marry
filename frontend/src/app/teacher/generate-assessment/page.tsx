"use client";

import { useEffect, useMemo, useState } from "react";
import { Loader2, Sparkles, ClipboardList, BookOpen } from "lucide-react";

import { api } from "@/lib/api";

type Subject = { id: string; name: string };
type ClassData = { id: string; name: string; subjects: Subject[] };
type AIJobStatus = "queued" | "running" | "completed" | "failed";

export default function GenerateAssessmentPage() {
    const [classes, setClasses] = useState<ClassData[]>([]);
    const [selectedSubject, setSelectedSubject] = useState("");
    const [topic, setTopic] = useState("");
    const [numQuestions, setNumQuestions] = useState(5);
    const [loading, setLoading] = useState(false);
    const [loadingClasses, setLoadingClasses] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<string | null>(null);
    const [jobId, setJobId] = useState<string | null>(null);
    const [jobStatus, setJobStatus] = useState<AIJobStatus | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                const data = (await api.teacher.classes()) as ClassData[];
                setClasses(data || []);
            } catch {
                /* ignore */
            } finally {
                setLoadingClasses(false);
            }
        };
        void load();
    }, []);

    const allSubjects = useMemo(() => {
        const subjects: Subject[] = [];
        for (const cls of classes) {
            for (const subj of cls.subjects || []) {
                if (!subjects.find((s) => s.id === subj.id)) {
                    subjects.push(subj);
                }
            }
        }
        return subjects;
    }, [classes]);

    useEffect(() => {
        if (!jobId) return;

        let cancelled = false;
        let timer: ReturnType<typeof setTimeout> | null = null;

        const poll = async () => {
            try {
                const job = (await api.ai.jobStatus(jobId)) as {
                    status: AIJobStatus;
                    error?: string;
                    result?: { assessment?: string };
                    poll_after_ms?: number;
                };

                if (cancelled) return;
                setJobStatus(job.status);

                if (job.status === "completed") {
                    setResult(job.result?.assessment || "No assessment generated.");
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                if (job.status === "failed") {
                    setError(job.error || "Failed to generate assessment");
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                timer = setTimeout(() => {
                    void poll();
                }, job.poll_after_ms ?? 2000);
            } catch (err) {
                if (cancelled) return;
                setError(err instanceof Error ? err.message : "Failed to load job status");
                setLoading(false);
                setJobId(null);
            }
        };

        void poll();

        return () => {
            cancelled = true;
            if (timer) clearTimeout(timer);
        };
    }, [jobId]);

    const generate = async () => {
        if (!selectedSubject || !topic.trim()) return;
        try {
            setLoading(true);
            setError(null);
            setResult(null);
            setJobStatus("queued");
            const payload = (await api.teacher.generateAssessment({
                subject_id: selectedSubject,
                topic: topic.trim(),
                num_questions: numQuestions,
            })) as { job_id: string; status: AIJobStatus };
            setJobId(payload.job_id);
            setJobStatus(payload.status);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate assessment");
            setLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center gap-3 mb-1">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 shadow-lg">
                        <ClipboardList className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                            AI Assessment Generator
                        </h1>
                        <p className="text-xs text-[var(--text-muted)]">
                            NCERT-aligned • Auto-generated from uploaded materials
                        </p>
                    </div>
                </div>
            </div>

            {error ? (
                <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {/* Config Card */}
            <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-6 mb-6 border border-[var(--border)]/50">
                <div className="grid md:grid-cols-3 gap-4 mb-5">
                    <div>
                        <label className="block text-[10px] font-bold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Subject</label>
                        {loadingClasses ? (
                            <div className="text-xs text-[var(--text-muted)] py-2">Loading...</div>
                        ) : (
                            <select
                                value={selectedSubject}
                                onChange={(e) => setSelectedSubject(e.target.value)}
                                className="w-full px-3 py-2.5 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                            >
                                <option value="">Select subject</option>
                                {allSubjects.map((s) => (
                                    <option key={s.id} value={s.id}>{s.name}</option>
                                ))}
                            </select>
                        )}
                    </div>
                    <div>
                        <label className="block text-[10px] font-bold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Topic</label>
                        <input
                            value={topic}
                            onChange={(e) => setTopic(e.target.value)}
                            onKeyDown={(e) => { if (e.key === "Enter") void generate(); }}
                            placeholder="e.g. Photosynthesis, Quadratic Equations..."
                            className="w-full px-3 py-2.5 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                        />
                    </div>
                    <div>
                        <label className="block text-[10px] font-bold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Questions</label>
                        <select
                            value={numQuestions}
                            onChange={(e) => setNumQuestions(Number(e.target.value))}
                            className="w-full px-3 py-2.5 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
                        >
                            {[3, 5, 8, 10, 15].map((n) => (
                                <option key={n} value={n}>{n} questions</option>
                            ))}
                        </select>
                    </div>
                </div>
                <button
                    onClick={() => void generate()}
                    disabled={loading || !selectedSubject || !topic.trim()}
                    className="w-full px-5 py-3 bg-gradient-to-r from-indigo-500 to-blue-600 text-white text-sm font-bold rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-40 flex items-center justify-center gap-2 hover:scale-[1.01]"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                    Generate Assessment
                </button>
            </div>

            {/* Loading State */}
            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-12 text-center border border-[var(--border)]/50">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-indigo-500 to-blue-600 flex items-center justify-center animate-pulse">
                        <Sparkles className="w-6 h-6 text-white" />
                    </div>
                    <p className="text-sm font-medium text-[var(--text-primary)]">
                        {jobStatus === "queued" ? "Queued assessment generation..." : "Generating assessment..."}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">
                        {jobStatus === "queued"
                            ? "Waiting for the AI worker to pick up this request"
                            : "Searching uploaded materials and creating MCQs"}
                    </p>
                </div>
            ) : null}

            {/* Result */}
            {!loading && result ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-6 border border-[var(--border)]/50">
                    <div className="flex items-center gap-2 mb-4">
                        <BookOpen className="w-4 h-4 text-indigo-500" />
                        <h3 className="text-sm font-bold text-[var(--text-primary)] uppercase tracking-wider">Generated Assessment</h3>
                    </div>
                    <div className="prose prose-sm max-w-none text-[var(--text-primary)] whitespace-pre-wrap leading-relaxed">
                        {result}
                    </div>
                </div>
            ) : null}
        </div>
    );
}
