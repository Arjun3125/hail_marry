"use client";

import { useEffect, useMemo, useState } from "react";
import { Plus, Users, BookOpen } from "lucide-react";

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

    const classOptions = useMemo(() => items.map((c) => ({ id: c.id, label: c.name })), [items]);

    useEffect(() => {
        if (!classOptions.some((c) => c.id === subjectClassId)) {
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
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Class & Subject Setup</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Manage classes and assign subjects</p>
                </div>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid lg:grid-cols-2 gap-4 mb-6">
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                    <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Add Class</h2>
                    <div className="grid grid-cols-[1fr_120px_auto] gap-2">
                        <input
                            value={className}
                            onChange={(e) => setClassName(e.target.value)}
                            placeholder="Class name"
                            className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        />
                        <input
                            value={gradeLevel}
                            onChange={(e) => setGradeLevel(e.target.value)}
                            placeholder="Grade"
                            className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        />
                        <button
                            className="px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] flex items-center gap-2 disabled:opacity-60"
                            onClick={() => void createClass()}
                            disabled={busy}
                        >
                            <Plus className="w-4 h-4" /> Add
                        </button>
                    </div>
                </div>

                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                    <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Add Subject</h2>
                    <div className="grid grid-cols-[1fr_1fr_auto] gap-2">
                        <input
                            value={subjectName}
                            onChange={(e) => setSubjectName(e.target.value)}
                            placeholder="Subject name"
                            className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        />
                        <select
                            value={subjectClassId}
                            onChange={(e) => setSubjectClassId(e.target.value)}
                            className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
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
                            className="px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] flex items-center gap-2 disabled:opacity-60"
                            onClick={() => void createSubject()}
                            disabled={busy || !subjectClassId}
                        >
                            <Plus className="w-4 h-4" /> Add
                        </button>
                    </div>
                </div>
            </div>

            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {loading ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        Loading classes...
                    </div>
                ) : items.length === 0 ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        No classes found.
                    </div>
                ) : items.map((item) => (
                    <div key={item.id} className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-base font-semibold text-[var(--text-primary)]">{item.name}</h3>
                            <span className="text-xs bg-[var(--primary-light)] text-[var(--primary)] px-2 py-0.5 rounded-full">Grade {item.grade}</span>
                        </div>
                        <div className="flex items-center gap-1.5 text-xs text-[var(--text-secondary)] mb-3">
                            <Users className="w-3.5 h-3.5" /> {item.students} students
                        </div>
                        <div className="flex flex-wrap gap-1.5">
                            {item.subjects.map((subject) => (
                                <span key={subject.id} className="text-[10px] bg-[var(--bg-page)] text-[var(--text-muted)] px-2 py-0.5 rounded-full flex items-center gap-1">
                                    <BookOpen className="w-2.5 h-2.5" /> {subject.name}
                                </span>
                            ))}
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
