"use client";

import { useEffect, useMemo, useState } from "react";
import { BookOpen, Plus, Users } from "lucide-react";

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

type SubjectItem = {
    id: string;
    name: string;
};

type ClassItem = {
    id: string;
    name: string;
    grade: string;
    students: number;
    subjects: SubjectItem[];
};

export default function AdminClassesPage() {
    const [items, setItems] = useState<ClassItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [busy, setBusy] = useState(false);

    const [className, setClassName] = useState("");
    const [gradeLevel, setGradeLevel] = useState("");
    const [subjectName, setSubjectName] = useState("");
    const [subjectClassId, setSubjectClassId] = useState("");

    const loadClasses = async () => {
        const payload = await api.admin.classes();
        setItems((payload || []) as ClassItem[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                await loadClasses();
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const classOptions = useMemo(() => items.map((item) => ({ id: item.id, label: item.name })), [items]);

    useEffect(() => {
        if (!classOptions.some((item) => item.id === subjectClassId)) {
            setSubjectClassId(classOptions[0]?.id || "");
        }
    }, [classOptions, subjectClassId]);

    const createClass = async () => {
        if (!className.trim() || !gradeLevel.trim()) return;
        try {
            setBusy(true);
            setError(null);
            await api.admin.createClass({
                name: className.trim(),
                grade_level: gradeLevel.trim(),
            });
            setClassName("");
            setGradeLevel("");
            await loadClasses();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create class");
        } finally {
            setBusy(false);
        }
    };

    const createSubject = async () => {
        if (!subjectName.trim() || !subjectClassId) return;
        try {
            setBusy(true);
            setError(null);
            await api.admin.createSubject({
                name: subjectName.trim(),
                class_id: subjectClassId,
            });
            setSubjectName("");
            await loadClasses();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create subject");
        } finally {
            setBusy(false);
        }
    };

    return (
        <PrismPage variant="workspace" className="space-y-10">
            <PrismSection className="space-y-10">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Users className="h-3.5 w-3.5" />
                            Class Structure Setup
                        </PrismHeroKicker>
                    )}
                    title="Build the class and subject map students will actually learn inside"
                    description="Set up class groups, attach subjects, and keep the academic structure tidy before attendance, results, and AI study tools rely on it."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Classes</span>
                        <strong className="prism-status-value">{items.length}</strong>
                        <span className="prism-status-detail">Configured classroom groups in the institution</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Students mapped</span>
                        <strong className="prism-status-value">{items.reduce((sum, item) => sum + item.students, 0)}</strong>
                        <span className="prism-status-detail">Students currently attached to the available classes</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Subjects</span>
                        <strong className="prism-status-value">{items.reduce((sum, item) => sum + item.subjects.length, 0)}</strong>
                        <span className="prism-status-detail">Academic subjects available across all configured classes</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation error={error} scope="admin-classes" onRetry={() => window.location.reload()} />
                ) : null}

                <div className="grid gap-10 lg:grid-cols-2">
                    <PrismPanel className="p-8">
                        <PrismSectionHeader
                            title="Add class"
                            description="Create the learning group first so attendance, results, and student access all share the same academic structure."
                        />
                        <div className="mt-6 grid gap-6 sm:grid-cols-[1fr_140px_auto]">
                            <input
                                value={className}
                                onChange={(e) => setClassName(e.target.value)}
                                placeholder="Class name"
                                className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-4 text-sm text-[var(--text-primary)]"
                            />
                            <input
                                value={gradeLevel}
                                onChange={(e) => setGradeLevel(e.target.value)}
                                placeholder="Grade"
                                className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-4 text-sm text-[var(--text-primary)]"
                            />
                            <button
                                className="prism-action"
                                onClick={() => void createClass()}
                                disabled={busy}
                                type="button"
                            >
                                <Plus className="h-4 w-4" />
                                Add
                            </button>
                        </div>
                    </PrismPanel>

                    <PrismPanel className="p-8">
                        <PrismSectionHeader
                            title="Add subject"
                            description="Attach subjects to a class so the downstream teacher, student, and reporting flows can reference the right academic context."
                        />
                        <div className="mt-6 grid gap-6 sm:grid-cols-[1fr_1fr_auto]">
                            <input
                                value={subjectName}
                                onChange={(e) => setSubjectName(e.target.value)}
                                placeholder="Subject name"
                                className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-4 text-sm text-[var(--text-primary)]"
                            />
                            <select
                                value={subjectClassId}
                                onChange={(e) => setSubjectClassId(e.target.value)}
                                className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-4 text-sm text-[var(--text-primary)]"
                                disabled={classOptions.length === 0}
                            >
                                {classOptions.length === 0 ? (
                                    <option value="">No classes</option>
                                ) : (
                                    classOptions.map((opt) => (
                                        <option key={opt.id} value={opt.id}>{opt.label}</option>
                                    ))
                                )}
                            </select>
                            <button
                                className="prism-action"
                                onClick={() => void createSubject()}
                                disabled={busy || !subjectClassId}
                                type="button"
                            >
                                <Plus className="h-4 w-4" />
                                Add
                            </button>
                        </div>
                    </PrismPanel>
                </div>

                <PrismPanel className="space-y-8 p-8">
                    <PrismSectionHeader
                        title="Current class map"
                        description="Review the live academic structure and confirm subjects are attached to the right groups before students and teachers start using it."
                    />

                    {loading ? (
                        <p className="text-sm text-[var(--text-secondary)]">Loading classes...</p>
                    ) : items.length === 0 ? (
                        <EmptyState
                            icon={Users}
                            title="No classes configured yet"
                            description="Add the first class to start building the academic structure for attendance, subjects, and student learning flows."
                            eyebrow="Academic structure empty"
                        />
                    ) : (
                        <div className="grid gap-8 md:grid-cols-2 xl:grid-cols-3">
                            {items.map((item) => (
                                <div key={item.id} className="rounded-3xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-6">
                                    <div className="mb-3 flex items-center justify-between gap-3">
                                        <div>
                                            <h3 className="text-base font-semibold text-[var(--text-primary)]">{item.name}</h3>
                                            <p className="text-xs text-[var(--text-muted)]">Grade {item.grade}</p>
                                        </div>
                                        <span className="rounded-full bg-[var(--primary-light)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--primary)]">
                                            {item.students} students
                                        </span>
                                    </div>
                                    <div className="flex flex-wrap gap-2">
                                        {item.subjects.length ? item.subjects.map((subject) => (
                                            <span key={subject.id} className="inline-flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.1em] text-[var(--text-secondary)]">
                                                <BookOpen className="h-3 w-3" />
                                                {subject.name}
                                            </span>
                                        )) : (
                                            <span className="text-xs text-[var(--text-muted)]">No subjects assigned yet.</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}
