"use client";

import { useEffect, useMemo, useState } from "react";
import {
    BookOpen,
    ClipboardList,
    FileText,
    Loader2,
    Sparkles,
    Wand2,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
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
                // Keep the page usable even if class metadata is unavailable.
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

    const selectedSubjectMeta = useMemo(
        () => allSubjects.find((subject) => subject.id === selectedSubject) || null,
        [allSubjects, selectedSubject],
    );

    useEffect(() => {
        if (!allSubjects.some((subject) => subject.id === selectedSubject)) {
            setSelectedSubject(allSubjects[0]?.id || "");
        }
    }, [allSubjects, selectedSubject]);

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
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]"
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Teacher Assessment Generator
                        </PrismHeroKicker>
                    )}
                    title="Generate Assessment"
                    description="Turn a topic into a draft assessment with a controlled teacher workflow: choose the subject, set the question depth, then review the generated output before it moves anywhere else."
                    aside={(
                        <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                            <MetricCard
                                icon={BookOpen}
                                title="Subjects ready"
                                value={`${allSubjects.length}`}
                                accent="blue"
                                summary="Available curriculum streams pulled from your classes"
                            />
                            <MetricCard
                                icon={ClipboardList}
                                title="Question count"
                                value={`${numQuestions}`}
                                accent="emerald"
                                summary="Current depth for the generated draft"
                            />
                            <MetricCard
                                icon={Wand2}
                                title="Generator state"
                                value={loading ? (jobStatus === "queued" ? "Queued" : "Running") : result ? "Ready" : "Idle"}
                                accent="amber"
                                summary={selectedSubjectMeta ? `${selectedSubjectMeta.name} selected` : "Choose a subject to begin"}
                            />
                        </div>
                    )}
                />

                <PrismPanel className="overflow-hidden p-0">
                    <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Generation Controls</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Choose the instructional context first, then launch a queued generation job from the same teacher workflow surface.
                                </p>
                            </div>
                            <button
                                onClick={() => void generate()}
                                disabled={loading || !selectedSubject || !topic.trim()}
                                className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                                Generate Assessment
                            </button>
                        </div>
                    </div>

                    <div className="grid gap-6 p-5 xl:grid-cols-[1.15fr_0.85fr]">
                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <PrismSectionHeader
                                    className="mb-4"
                                    kicker="Brief"
                                    title="Assessment brief"
                                    description="Keep the request focused so the draft stays useful in a real classroom workflow."
                                />

                                <div className="grid gap-3 md:grid-cols-3">
                                    <label className="space-y-2">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Subject</span>
                                        {loadingClasses ? (
                                            <div className="rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-muted)]">
                                                Loading subjects...
                                            </div>
                                        ) : (
                                            <select
                                                value={selectedSubject}
                                                onChange={(e) => setSelectedSubject(e.target.value)}
                                                className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                            >
                                                <option value="">Select subject</option>
                                                {allSubjects.map((subject) => (
                                                    <option key={subject.id} value={subject.id}>{subject.name}</option>
                                                ))}
                                            </select>
                                        )}
                                    </label>

                                    <label className="space-y-2 md:col-span-2">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Topic</span>
                                        <input
                                            value={topic}
                                            onChange={(e) => setTopic(e.target.value)}
                                            onKeyDown={(e) => {
                                                if (e.key === "Enter") void generate();
                                            }}
                                            placeholder="e.g. Photosynthesis, Quadratic Equations..."
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        />
                                    </label>
                                </div>

                                <label className="mt-4 block space-y-2">
                                    <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Question depth</span>
                                    <select
                                        value={numQuestions}
                                        onChange={(e) => setNumQuestions(Number(e.target.value))}
                                        className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                    >
                                        {[3, 5, 8, 10, 15].map((count) => (
                                            <option key={count} value={count}>{count} questions</option>
                                        ))}
                                    </select>
                                </label>
                            </PrismPanel>

                            {error ? (
                                <ErrorRemediation
                                    error={error}
                                    scope="teacher-generate-assessment"
                                    onRetry={() => {
                                        if (!loading && selectedSubject && topic.trim()) {
                                            void generate();
                                        }
                                    }}
                                />
                            ) : null}

                            {loading ? (
                                <PrismPanel className="p-8">
                                    <div className="flex flex-col items-center justify-center text-center">
                                        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))]">
                                            <Sparkles className="h-6 w-6 animate-pulse text-[#06101e]" />
                                        </div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">
                                            {jobStatus === "queued" ? "Queued assessment generation..." : "Generating assessment..."}
                                        </p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            {jobStatus === "queued"
                                                ? "Waiting for the AI worker to pick up this request."
                                                : "Searching uploaded materials and building a classroom-ready draft."}
                                        </p>
                                    </div>
                                </PrismPanel>
                            ) : result ? (
                                <PrismPanel className="p-0 overflow-hidden">
                                    <div className="flex items-center gap-2 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                        <BookOpen className="h-4 w-4 text-status-blue" />
                                        <h2 className="text-sm font-semibold uppercase tracking-[0.22em] text-[var(--text-primary)]">Generated Assessment</h2>
                                    </div>
                                    <div className="px-5 py-5">
                                        <div className="whitespace-pre-wrap text-sm leading-7 text-[var(--text-primary)]">
                                            {result}
                                        </div>
                                    </div>
                                </PrismPanel>
                            ) : (
                                <EmptyState
                                    icon={FileText}
                                    title="No assessment draft yet"
                                    description="Pick a subject, define the topic, and run the generator to create the first draft."
                                />
                            )}
                        </div>

                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <PrismSectionHeader
                                    kicker="Overview"
                                    title="Generation summary"
                                    description="Track the current setup before or during generation."
                                />
                                <div className="mt-4 space-y-4">
                                    <SummaryRow label="Selected subject" value={selectedSubjectMeta?.name || "None selected"} />
                                    <SummaryRow label="Current topic" value={topic.trim() || "No topic yet"} />
                                    <SummaryRow label="Question count" value={`${numQuestions}`} />
                                    <SummaryRow label="Job status" value={jobStatus || "Idle"} />
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <PrismSectionHeader
                                    kicker="Notes"
                                    title="Workflow notes"
                                    description="What this surface does and what stays outside it."
                                />
                                <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>This surface is for draft generation only. It gives teachers a clean queue-to-output workflow without changing the underlying AI job lifecycle.</p>
                                    <p>The backend contract stays exactly the same: start a generation job, poll until completion, then present the resulting assessment text.</p>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <PrismSectionHeader
                                    kicker="Guidance"
                                    title="Good prompt shape"
                                    description="Use tighter inputs so the generated draft stays classroom-ready."
                                />
                                <div className="mt-4 space-y-3">
                                    <GuideRow label="Specific topic" description="Use a tight concept or chapter name instead of a full syllabus block." />
                                    <GuideRow label="Appropriate depth" description="Match the question count to the classroom use case: quick check, revision quiz, or fuller assessment." />
                                    <GuideRow label="Subject alignment" description="Choose the correct curriculum stream so the generation context stays grounded." />
                                </div>
                            </PrismPanel>
                        </div>
                    </div>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    icon: Icon,
    title,
    value,
    summary,
    accent,
}: {
    icon: typeof BookOpen;
    title: string;
    value: string;
    summary: string;
    accent: "blue" | "emerald" | "amber";
}) {
    const accentClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))] text-status-blue",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))] text-status-emerald",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))] text-status-amber",
    } as const;

    return (
        <PrismPanel className="p-4">
            <div className={`mb-3 flex h-11 w-11 items-center justify-center rounded-2xl ${accentClasses[accent]}`}>
                <Icon className="h-5 w-5" />
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </PrismPanel>
    );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-4 py-3">
            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</span>
            <span className="text-sm font-medium text-[var(--text-primary)]">{value}</span>
        </div>
    );
}

function GuideRow({ label, description }: { label: string; description: string }) {
    return (
        <div className="flex items-start gap-3">
            <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(167,139,250,0.14))] text-[var(--text-primary)]">
                <Sparkles className="h-4 w-4" />
            </div>
            <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">{label}</p>
                <p className="text-xs leading-5 text-[var(--text-muted)]">{description}</p>
            </div>
        </div>
    );
}
