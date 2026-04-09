"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Calendar,
    ClipboardList,
    FileText,
    Plus,
    Sparkles,
    Users,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type TeacherAssignment = {
    id: string;
    title: string;
    subject: string;
    due_date: string | null;
    submissions: number;
};

type TeacherClass = {
    id: string;
    name: string;
    subjects: Array<{ id: string; name: string }>;
};

type SubjectOption = {
    id: string;
    name: string;
};

export default function TeacherAssignmentsPage() {
    const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [subjectId, setSubjectId] = useState("");
    const [title, setTitle] = useState("");
    const [description, setDescription] = useState("");
    const [dueDate, setDueDate] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

    const allSubjects = useMemo(() => {
        const seen = new Set<string>();
        const subjects: SubjectOption[] = [];
        for (const classItem of classes) {
            for (const subject of classItem.subjects) {
                if (seen.has(subject.id)) continue;
                seen.add(subject.id);
                subjects.push({ id: subject.id, name: subject.name });
            }
        }
        return subjects;
    }, [classes]);

    const selectedSubject = useMemo(
        () => allSubjects.find((subject) => subject.id === subjectId) || null,
        [allSubjects, subjectId],
    );

    const assignmentSummary = useMemo(() => {
        const total = assignments.length;
        const scheduled = assignments.filter((assignment) => Boolean(assignment.due_date)).length;
        const totalSubmissions = assignments.reduce((sum, assignment) => sum + Number(assignment.submissions || 0), 0);
        return { total, scheduled, totalSubmissions };
    }, [assignments]);

    useEffect(() => {
        if (!allSubjects.some((subject) => subject.id === subjectId)) {
            setSubjectId(allSubjects[0]?.id || "");
        }
    }, [allSubjects, subjectId]);

    const loadData = async () => {
        const [assignmentPayload, classPayload] = await Promise.all([
            api.teacher.assignments(),
            api.teacher.classes(),
        ]);
        setAssignments((assignmentPayload || []) as TeacherAssignment[]);
        setClasses((classPayload || []) as TeacherClass[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadData();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load assignments");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const createAssignment = async () => {
        if (!title.trim() || !subjectId) return;
        try {
            setSaving(true);
            setError(null);
            setSuccess(null);
            await api.teacher.createAssignment({
                title: title.trim(),
                description: description.trim(),
                subject_id: subjectId,
                due_date: dueDate || undefined,
            });
            setTitle("");
            setDescription("");
            setDueDate("");
            setSuccess(`Assignment "${title.trim()}" created successfully.`);
            await loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create assignment");
        } finally {
            setSaving(false);
        }
    };

    return (
        <PrismPage variant="workspace" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ClipboardList className="h-3.5 w-3.5" />
                            Teacher Assignment Workflow
                        </PrismHeroKicker>
                    )}
                    title="Publish classroom work from one operational assignment board"
                    description="Create the task, tie it to the right subject, set the due date if needed, and keep visible submission momentum without leaving the teaching flow."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Keep assignments lightweight and specific so students can identify the task immediately on both desktop and mobile views.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Open assignments</span>
                        <span className="prism-status-value">{assignmentSummary.total}</span>
                        <span className="prism-status-detail">Current published workload across your subjects.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">With due dates</span>
                        <span className="prism-status-value">{assignmentSummary.scheduled}</span>
                        <span className="prism-status-detail">Assignments anchored to a concrete submission date.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Submissions logged</span>
                        <span className="prism-status-value">{assignmentSummary.totalSubmissions}</span>
                        <span className="prism-status-detail">Visible learner activity across active assignments.</span>
                    </div>
                </div>

                <PrismPanel className="overflow-hidden p-0">
                    <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Assignment Composer</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Draft the work item, tie it to a subject, and publish it into the current teaching flow.
                                </p>
                            </div>
                            <button
                                onClick={() => void createAssignment()}
                                disabled={saving || !title.trim() || !subjectId}
                                className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                <Plus className="h-4 w-4" />
                                {saving ? "Creating..." : "Create Assignment"}
                            </button>
                        </div>
                    </div>

                    <div className="grid gap-6 p-5 xl:grid-cols-[1.15fr_0.85fr]">
                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <div className="mb-4">
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Assignment details</p>
                                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                        Keep the structure tight: title, subject, due date, then the teacher note students actually need.
                                    </p>
                                </div>

                                <div className="grid gap-3 md:grid-cols-[1.4fr_1fr_1fr]">
                                    <label className="space-y-2">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Title</span>
                                        <input
                                            value={title}
                                            onChange={(e) => setTitle(e.target.value)}
                                            placeholder="Assignment title"
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        />
                                    </label>
                                    <label className="space-y-2">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Subject</span>
                                        <select
                                            value={subjectId}
                                            onChange={(e) => setSubjectId(e.target.value)}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        >
                                            {allSubjects.length ? (
                                                allSubjects.map((subject) => (
                                                    <option key={subject.id} value={subject.id}>{subject.name}</option>
                                                ))
                                            ) : (
                                                <option value="">No subjects</option>
                                            )}
                                        </select>
                                    </label>
                                    <label className="space-y-2">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Due date</span>
                                        <input
                                            type="date"
                                            value={dueDate}
                                            onChange={(e) => setDueDate(e.target.value)}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        />
                                    </label>
                                </div>

                                <label className="mt-4 block space-y-2">
                                    <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Teacher brief</span>
                                    <textarea
                                        value={description}
                                        onChange={(e) => setDescription(e.target.value)}
                                        placeholder="Description (optional)"
                                        rows={5}
                                        className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                    />
                                </label>
                            </PrismPanel>

                            {error ? (
                                <ErrorRemediation
                                    error={error}
                                    scope="teacher-assignments"
                                    onRetry={() => {
                                        void loadData();
                                    }}
                                />
                            ) : null}
                            {success ? (
                                <div className="rounded-[var(--radius)] border border-[var(--success)]/30 bg-success-subtle px-4 py-3 text-sm text-[var(--success)]">
                                    {success}
                                </div>
                            ) : null}

                            <PrismPanel className="overflow-hidden p-0">
                                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                    <div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">Assignment board</p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            Review active work, due dates, and class response without leaving the flow.
                                        </p>
                                    </div>
                                    <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                        <Sparkles className="h-3.5 w-3.5" />
                                        {selectedSubject ? `${selectedSubject.name} selected for creation` : "Choose a subject to publish"}
                                    </div>
                                </div>

                                <div className="space-y-3 p-5">
                                    {loading ? (
                                        Array.from({ length: 4 }).map((_, index) => (
                                            <div key={index} className="h-24 animate-pulse rounded-2xl bg-[rgba(148,163,184,0.08)]" />
                                        ))
                                    ) : assignments.length === 0 ? (
                                        <EmptyState
                                            icon={FileText}
                                            title="No assignments created yet"
                                            description="Publish the first assignment to turn this board into the teacher’s active workload view."
                                        />
                                    ) : assignments.map((assignment) => (
                                        <AssignmentCard key={assignment.id} assignment={assignment} />
                                    ))}
                                </div>
                            </PrismPanel>
                        </div>

                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Publishing summary</p>
                                <div className="mt-4 space-y-4">
                                    <SummaryRow label="Current subject" value={selectedSubject?.name || "None selected"} />
                                    <SummaryRow label="Draft title" value={title.trim() || "Untitled assignment"} />
                                    <SummaryRow label="Due date" value={dueDate || "No deadline set"} />
                                    <SummaryRow label="Description" value={description.trim() ? "Included" : "Optional"} />
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Workflow notes</p>
                                <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>Use this surface to publish clear, lightweight work items before moving into upload, review, or insight-heavy teacher flows.</p>
                                    <p>The create/list API behavior is untouched. This pass only upgrades composition, hierarchy, and state presentation.</p>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Good assignment shape</p>
                                <div className="mt-4 space-y-3">
                                    <GuideRow label="Title" description="Specific enough for students to recognize the task immediately." />
                                    <GuideRow label="Subject" description="Anchors the assignment to the right teaching stream and dashboard grouping." />
                                    <GuideRow label="Due date" description="Optional, but useful when you want submission urgency visible at a glance." />
                                    <GuideRow label="Brief" description="Keep the instruction compact so it works on both desktop and mobile views." />
                                </div>
                            </PrismPanel>
                        </div>
                    </div>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

function AssignmentCard({ assignment }: { assignment: TeacherAssignment }) {
    return (
        <div className="rounded-3xl border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-5 transition hover:border-[var(--border-strong)] hover:bg-[rgba(148,163,184,0.06)]">
            <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
                <div className="flex items-start gap-4">
                    <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(167,139,250,0.14))]">
                        <FileText className="h-5 w-5 text-[var(--text-primary)]" />
                    </div>
                    <div>
                        <h3 className="text-base font-semibold text-[var(--text-primary)]">{assignment.title}</h3>
                        <p className="mt-1 text-sm text-[var(--text-secondary)]">{assignment.subject}</p>
                    </div>
                </div>

                <div className="flex flex-wrap items-center gap-2">
                    <StatusPill icon={Calendar} label={assignment.due_date ? `Due ${assignment.due_date}` : "No deadline"} />
                    <StatusPill icon={Users} label={`${assignment.submissions} submissions`} />
                </div>
            </div>
        </div>
    );
}

function StatusPill({ icon: Icon, label }: { icon: typeof Calendar; label: string }) {
    return (
        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
            <Icon className="h-3.5 w-3.5" />
            <span>{label}</span>
        </div>
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
                <Plus className="h-4 w-4" />
            </div>
            <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">{label}</p>
                <p className="text-xs leading-5 text-[var(--text-muted)]">{description}</p>
            </div>
        </div>
    );
}
