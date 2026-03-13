"use client";

import { useEffect, useMemo, useState } from "react";
import { Save } from "lucide-react";

import { api } from "@/lib/api";

type StudentItem = {
    id: string;
    name: string;
    roll_number: string | null;
};

type SubjectItem = {
    id: string;
    name: string;
};

type TeacherClass = {
    id: string;
    name: string;
    students: StudentItem[];
    subjects: SubjectItem[];
};

export default function TeacherMarksPage() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [selectedClassId, setSelectedClassId] = useState("");
    const [selectedSubjectId, setSelectedSubjectId] = useState("");
    const [examName, setExamName] = useState("");
    const [examDate, setExamDate] = useState(new Date().toISOString().split("T")[0]);
    const [maxMarks, setMaxMarks] = useState("100");
    const [marksByStudent, setMarksByStudent] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const selectedClass = useMemo(
        () => classes.find((c) => c.id === selectedClassId) || null,
        [classes, selectedClassId],
    );

    useEffect(() => {
        const loadClasses = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.classes();
                const list = (payload || []) as TeacherClass[];
                setClasses(list);
                if (list.length > 0) {
                    setSelectedClassId((prev) => prev || list[0].id);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes");
            } finally {
                setLoading(false);
            }
        };
        void loadClasses();
    }, []);

    useEffect(() => {
        const subjects = selectedClass?.subjects || [];
        if (!subjects.some((s) => s.id === selectedSubjectId)) {
            setSelectedSubjectId(subjects[0]?.id || "");
        }
        const initial: Record<string, string> = {};
        for (const student of selectedClass?.students || []) {
            initial[student.id] = "";
        }
        setMarksByStudent(initial);
    }, [selectedClass, selectedSubjectId]);

    const updateMarks = (studentId: string, value: string) => {
        setMarksByStudent((prev) => ({ ...prev, [studentId]: value }));
    };

    const saveMarks = async () => {
        if (!selectedClass || !selectedSubjectId || !examName.trim()) return;
        const max = Number(maxMarks);
        if (!Number.isFinite(max) || max <= 0) {
            setError("Max marks must be greater than zero");
            return;
        }

        const entries = (selectedClass.students || [])
            .map((student) => ({ student_id: student.id, raw: marksByStudent[student.id] || "" }))
            .filter((item) => item.raw !== "")
            .map((item) => ({ student_id: item.student_id, marks_obtained: Number(item.raw) }));

        if (entries.length === 0) {
            setError("Enter at least one mark before saving");
            return;
        }

        if (entries.some((entry) => !Number.isFinite(entry.marks_obtained) || entry.marks_obtained < 0 || entry.marks_obtained > max)) {
            setError(`Marks must be between 0 and ${max}`);
            return;
        }

        try {
            setSaving(true);
            setError(null);
            const exam = await api.teacher.createExam({
                name: examName.trim(),
                subject_id: selectedSubjectId,
                max_marks: max,
                exam_date: examDate,
            }) as { exam_id: string };

            await api.teacher.submitMarks({
                exam_id: exam.exam_id,
                entries,
            });

            setExamName("");
            const reset: Record<string, string> = {};
            for (const student of selectedClass.students || []) reset[student.id] = "";
            setMarksByStudent(reset);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save marks");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Marks Entry</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Enter exam marks for students</p>
                </div>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid md:grid-cols-5 gap-4 mb-6">
                <select
                    value={selectedClassId}
                    onChange={(e) => setSelectedClassId(e.target.value)}
                    className="px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                >
                    {classes.map((item) => (
                        <option key={item.id} value={item.id}>{item.name}</option>
                    ))}
                </select>
                <select
                    value={selectedSubjectId}
                    onChange={(e) => setSelectedSubjectId(e.target.value)}
                    className="px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                >
                    {(selectedClass?.subjects || []).map((subject) => (
                        <option key={subject.id} value={subject.id}>{subject.name}</option>
                    ))}
                </select>
                <input
                    type="text"
                    value={examName}
                    onChange={(e) => setExamName(e.target.value)}
                    placeholder="Exam name"
                    className="px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                />
                <input
                    type="date"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                />
                <input
                    type="number"
                    value={maxMarks}
                    onChange={(e) => setMaxMarks(e.target.value)}
                    placeholder="Max"
                    className="px-3 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                />
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[600px]">
                        <thead>
                            <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Roll</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Name</th>
                                <th className="px-5 py-3 text-center text-xs font-medium text-[var(--text-muted)] uppercase">Marks (/{maxMarks || "0"})</th>
                                <th className="px-5 py-3 text-center text-xs font-medium text-[var(--text-muted)] uppercase">%</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={4} className="px-5 py-4 text-sm text-[var(--text-muted)]">Loading students...</td>
                                </tr>
                            ) : !(selectedClass?.students.length) ? (
                                <tr>
                                    <td colSpan={4} className="px-5 py-4 text-sm text-[var(--text-muted)]">No students in selected class.</td>
                                </tr>
                            ) : selectedClass.students.map((student) => {
                                const markText = marksByStudent[student.id] || "";
                                const mark = Number(markText);
                                const max = Number(maxMarks);
                                const pct = markText !== "" && max > 0 && Number.isFinite(mark) ? Math.round((mark / max) * 100) : null;
                                return (
                                    <tr key={student.id} className="border-b border-[var(--border-light)]">
                                        <td className="px-5 py-3 text-sm text-[var(--text-secondary)]">{student.roll_number || "-"}</td>
                                        <td className="px-5 py-3 text-sm font-medium text-[var(--text-primary)]">{student.name}</td>
                                        <td className="px-5 py-3 text-center">
                                            <input
                                                type="number"
                                                value={markText}
                                                onChange={(e) => updateMarks(student.id, e.target.value)}
                                                min="0"
                                                max={maxMarks || "0"}
                                                placeholder="-"
                                                className="w-24 px-3 py-1.5 text-sm text-center border border-[var(--border)] rounded-[var(--radius-sm)]"
                                            />
                                        </td>
                                        <td className="px-5 py-3 text-center">
                                            {pct !== null ? (
                                                <span className={`text-sm font-medium ${pct >= 80 ? "text-[var(--success)]" : pct >= 50 ? "text-[var(--warning)]" : "text-[var(--error)]"}`}>
                                                    {pct}%
                                                </span>
                                            ) : (
                                                <span className="text-sm text-[var(--text-muted)]">-</span>
                                            )}
                                        </td>
                                    </tr>
                                );
                            })}
                        </tbody>
                    </table>
                </div>
                </div>

                <div className="mt-4 flex justify-end">
                    <button
                        className="px-6 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors flex items-center gap-2 disabled:opacity-60"
                        onClick={() => void saveMarks()}
                        disabled={saving || !selectedClass}
                    >
                        <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Marks"}
                    </button>
                </div>
            </div>
            );
}
