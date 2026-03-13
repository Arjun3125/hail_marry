"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, FileText, Calendar, Users } from "lucide-react";

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

    const allSubjects = useMemo(
        () => classes.flatMap((c) => c.subjects).map((s) => ({ id: s.id, name: s.name })),
        [classes],
    );

    useEffect(() => {
        if (!allSubjects.some((s) => s.id === subjectId)) {
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
            await api.teacher.createAssignment({
                title: title.trim(),
                description: description.trim(),
                subject_id: subjectId,
                due_date: dueDate || undefined,
            });
            setTitle("");
            setDescription("");
            setDueDate("");
            await loadData();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create assignment");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Assignments</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Create and manage assignments</p>
                </div>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-5">
                <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">New Assignment</h2>
                <div className="grid md:grid-cols-4 gap-2 mb-2">
                    <input
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Assignment title"
                        className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    />
                    <select
                        value={subjectId}
                        onChange={(e) => setSubjectId(e.target.value)}
                        className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    >
                        {allSubjects.length ? allSubjects.map((s) => (
                            <option key={s.id} value={s.id}>{s.name}</option>
                        )) : <option value="">No subjects</option>}
                    </select>
                    <input
                        type="date"
                        value={dueDate}
                        onChange={(e) => setDueDate(e.target.value)}
                        className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    />
                    <button
                        onClick={() => void createAssignment()}
                        disabled={saving || !title.trim() || !subjectId}
                        className="px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors flex items-center justify-center gap-2 disabled:opacity-60"
                    >
                        <Plus className="w-4 h-4" /> Create
                    </button>
                </div>
                <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    placeholder="Description (optional)"
                    rows={3}
                    className="w-full px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                />
            </div>

            <div className="space-y-3">
                {loading ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                        Loading assignments...
                    </div>
                ) : assignments.length === 0 ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                        No assignments created yet.
                    </div>
                ) : assignments.map((assignment) => (
                    <div key={assignment.id} className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] flex items-center justify-between">
                        <div className="flex items-start gap-4">
                            <div className="w-10 h-10 bg-[var(--primary-light)] rounded-[var(--radius-sm)] flex items-center justify-center">
                                <FileText className="w-5 h-5 text-[var(--primary)]" />
                            </div>
                            <div>
                                <h3 className="text-sm font-semibold text-[var(--text-primary)]">{assignment.title}</h3>
                                <p className="text-xs text-[var(--text-muted)]">{assignment.subject}</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-6">
                            <div className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
                                <Calendar className="w-3.5 h-3.5" /> Due: {assignment.due_date || "-"}
                            </div>
                            <div className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)]">
                                <Users className="w-3.5 h-3.5" /> {assignment.submissions} submissions
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
