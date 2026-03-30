"use client";

import { useEffect, useMemo, useState } from "react";
import { Save, Upload } from "lucide-react";

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

type MarksImportResponse = {
    imported?: number;
    errors?: string[];
    ocr_review_required?: boolean;
    ocr_warning?: string | null;
    ocr_confidence?: number | null;
    ocr_unmatched_lines?: number;
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
    const [importing, setImporting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);

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

    useEffect(() => {
        if (typeof window === "undefined") return;
        window.localStorage.setItem(
            "mascotPageContext",
            JSON.stringify({
                route: "/teacher/marks",
                current_page_entity: "subject",
                current_page_entity_id: selectedSubjectId || null,
                metadata: {
                    class_id: selectedClassId || null,
                    subject_id: selectedSubjectId || null,
                    exam_name: examName,
                    exam_date: examDate,
                    max_marks: maxMarks,
                },
            }),
        );
    }, [selectedClassId, selectedSubjectId, examName, examDate, maxMarks]);

    const updateMarks = (studentId: string, value: string) => {
        setMarksByStudent((prev) => ({ ...prev, [studentId]: value }));
    };

    const buildMarksImportNotice = (payload: MarksImportResponse) => {
        const imported = Number(payload.imported || 0);
        const errors = Array.isArray(payload.errors) ? payload.errors : [];
        const parts = [`Imported ${imported} marks row${imported === 1 ? "" : "s"}.`];
        if (typeof payload.ocr_confidence === "number") {
            parts.push(`OCR confidence ${(payload.ocr_confidence * 100).toFixed(0)}%.`);
        }
        if (payload.ocr_review_required) {
            parts.push("OCR review recommended.");
        }
        if (payload.ocr_unmatched_lines) {
            parts.push(`${payload.ocr_unmatched_lines} OCR line${payload.ocr_unmatched_lines === 1 ? "" : "s"} need manual cleanup.`);
        }
        if (payload.ocr_warning) {
            parts.push(payload.ocr_warning);
        }
        if (errors.length) {
            parts.push(errors.join(" "));
        }
        return parts.join(" ");
    };

    const buildExamPayload = () => {
        if (!selectedClass || !selectedSubjectId || !examName.trim()) {
            throw new Error("Select a class and subject, then enter an exam name before importing marks.");
        }
        const max = Number(maxMarks);
        if (!Number.isFinite(max) || max <= 0) {
            throw new Error("Max marks must be greater than zero");
        }
        return {
            name: examName.trim(),
            subject_id: selectedSubjectId,
            max_marks: max,
            exam_date: examDate,
        };
    };

    const resetMarksInputs = () => {
        setExamName("");
        const reset: Record<string, string> = {};
        for (const student of selectedClass?.students || []) reset[student.id] = "";
        setMarksByStudent(reset);
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
            setSuccess(null);
            const exam = await api.teacher.createExam(buildExamPayload()) as { exam_id: string };

            await api.teacher.submitMarks({
                exam_id: exam.exam_id,
                entries,
            });

            setSuccess("Marks saved successfully.");
            resetMarksInputs();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save marks");
        } finally {
            setSaving(false);
        }
    };

    const handleMarksImport = async (file: File) => {
        try {
            setImporting(true);
            setError(null);
            setSuccess(null);
            const exam = await api.teacher.createExam(buildExamPayload()) as { exam_id: string };
            const formData = new FormData();
            formData.append("file", file);
            const payload = await api.teacher.importMarksCsv(exam.exam_id, formData) as MarksImportResponse;
            setSuccess(buildMarksImportNotice(payload));
            resetMarksInputs();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to import marks");
        } finally {
            setImporting(false);
        }
    };

    return (
        <div>
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Marks Entry</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Enter exam marks for students</p>
                </div>
                <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-[var(--radius-sm)] border border-[var(--primary)]/20 bg-[var(--primary-light)] px-4 py-2 text-sm font-medium text-[var(--primary)] transition-colors hover:bg-[var(--primary)] hover:text-white">
                    <Upload className="h-4 w-4" />
                    {importing ? "Importing..." : "Import OCR / CSV"}
                    <input
                        type="file"
                        accept=".csv,.txt,.jpg,.jpeg,.png"
                        className="hidden"
                        disabled={importing}
                        onChange={(e) => {
                            const file = e.target.files?.[0];
                            e.currentTarget.value = "";
                            if (file) {
                                void handleMarksImport(file);
                            }
                        }}
                    />
                </label>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}
            {success ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--success)]/30 bg-success-subtle px-4 py-3 text-sm text-[var(--success)]">
                    {success}
                </div>
            ) : null}

            <div className="mb-6 grid gap-4 md:grid-cols-5">
                <select
                    value={selectedClassId}
                    onChange={(e) => setSelectedClassId(e.target.value)}
                    className="rounded-[var(--radius-sm)] border border-[var(--border)] px-4 py-2.5 text-sm"
                >
                    {classes.map((item) => (
                        <option key={item.id} value={item.id}>{item.name}</option>
                    ))}
                </select>
                <select
                    value={selectedSubjectId}
                    onChange={(e) => setSelectedSubjectId(e.target.value)}
                    className="rounded-[var(--radius-sm)] border border-[var(--border)] px-4 py-2.5 text-sm"
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
                    className="rounded-[var(--radius-sm)] border border-[var(--border)] px-4 py-2.5 text-sm"
                />
                <input
                    type="date"
                    value={examDate}
                    onChange={(e) => setExamDate(e.target.value)}
                    className="rounded-[var(--radius-sm)] border border-[var(--border)] px-4 py-2.5 text-sm"
                />
                <input
                    type="number"
                    value={maxMarks}
                    onChange={(e) => setMaxMarks(e.target.value)}
                    placeholder="Max"
                    className="rounded-[var(--radius-sm)] border border-[var(--border)] px-3 py-2.5 text-sm"
                />
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[600px]">
                        <thead>
                            <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-[var(--text-muted)]">Roll</th>
                                <th className="px-5 py-3 text-left text-xs font-medium uppercase text-[var(--text-muted)]">Name</th>
                                <th className="px-5 py-3 text-center text-xs font-medium uppercase text-[var(--text-muted)]">Marks (/{maxMarks || "0"})</th>
                                <th className="px-5 py-3 text-center text-xs font-medium uppercase text-[var(--text-muted)]">%</th>
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
                                                className="w-24 rounded-[var(--radius-sm)] border border-[var(--border)] px-3 py-1.5 text-center text-sm"
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
                    className="flex items-center gap-2 rounded-[var(--radius-sm)] bg-[var(--primary)] px-6 py-2.5 text-sm font-medium text-white transition-colors hover:bg-[var(--primary-hover)] disabled:opacity-60"
                    onClick={() => void saveMarks()}
                    disabled={saving || importing || !selectedClass}
                >
                    <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Marks"}
                </button>
            </div>
        </div>
    );
}
