"use client";

import { useEffect, useMemo, useState } from "react";
import {
    Award,
    ClipboardCheck,
    FileSpreadsheet,
    Save,
    Upload,
    Users,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
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

    const selectedSubject = useMemo(
        () => (selectedClass?.subjects || []).find((subject) => subject.id === selectedSubjectId) || null,
        [selectedClass, selectedSubjectId],
    );

    const marksSummary = useMemo(() => {
        const max = Number(maxMarks);
        const parsed = Object.values(marksByStudent)
            .map((value) => value.trim())
            .filter((value) => value !== "")
            .map((value) => Number(value))
            .filter((value) => Number.isFinite(value));

        const entered = parsed.length;
        const average = entered > 0 ? parsed.reduce((sum, value) => sum + value, 0) / entered : null;
        const topScore = entered > 0 ? Math.max(...parsed) : null;
        const validAveragePct = average !== null && Number.isFinite(max) && max > 0 ? Math.round((average / max) * 100) : null;

        return {
            entered,
            average,
            topScore,
            averagePct: validAveragePct,
        };
    }, [marksByStudent, maxMarks]);

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
        <PrismPage variant="workspace" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <ClipboardCheck className="h-3.5 w-3.5" />
                            Teacher Assessment Workflow
                        </PrismHeroKicker>
                    )}
                    title="Enter marks from one assessment control surface"
                    description="Set the exam context, import OCR-led score sheets when available, and keep grading progress readable while preserving the fast manual entry path."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Lock the class, subject, exam name, and max marks first. Then use the same assessment frame for either OCR import or manual score entry.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Roster size</span>
                        <span className="prism-status-value">{selectedClass?.students.length || 0}</span>
                        <span className="prism-status-detail">{selectedClass ? `${selectedClass.name} ready for entry.` : "Choose a class to begin."}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Marks entered</span>
                        <span className="prism-status-value">{marksSummary.entered}</span>
                        <span className="prism-status-detail">{selectedClass ? "Live draft across the current roster." : "Waiting for roster."}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Draft average</span>
                        <span className="prism-status-value">{marksSummary.averagePct !== null ? `${marksSummary.averagePct}%` : "-"}</span>
                        <span className="prism-status-detail">{marksSummary.average !== null ? `Average ${marksSummary.average.toFixed(1)} / ${maxMarks || "0"}.` : "Appears as marks are entered."}</span>
                    </div>
                </div>

                <PrismPanel className="overflow-hidden p-0">
                    <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Assessment Bar</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Set the exam context first, then import or enter student marks before pushing the final submission.
                                </p>
                            </div>
                            <div className="flex flex-wrap items-center gap-2">
                                <label className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-2xl border border-[var(--primary)]/20 bg-[var(--primary-light)] px-4 py-2.5 text-sm font-medium text-[var(--primary)] transition-colors hover:bg-[var(--primary)] hover:text-white">
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
                                <button
                                    className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                                    onClick={() => void saveMarks()}
                                    disabled={saving || importing || !selectedClass}
                                >
                                    <Save className="h-4 w-4" />
                                    {saving ? "Saving..." : "Save Marks"}
                                </button>
                            </div>
                        </div>
                    </div>

                    <div className="grid gap-6 p-5 xl:grid-cols-[1.55fr_0.95fr]">
                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <div className="mb-4">
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Exam setup</p>
                                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                        These values drive both OCR imports and manual submissions, so set them before entering marks.
                                    </p>
                                </div>
                                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-5">
                                    <label className="space-y-2 xl:col-span-1">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Class</span>
                                        <select
                                            value={selectedClassId}
                                            onChange={(e) => setSelectedClassId(e.target.value)}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        >
                                            {classes.map((item) => (
                                                <option key={item.id} value={item.id}>{item.name}</option>
                                            ))}
                                        </select>
                                    </label>
                                    <label className="space-y-2 xl:col-span-1">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Subject</span>
                                        <select
                                            value={selectedSubjectId}
                                            onChange={(e) => setSelectedSubjectId(e.target.value)}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        >
                                            {(selectedClass?.subjects || []).map((subject) => (
                                                <option key={subject.id} value={subject.id}>{subject.name}</option>
                                            ))}
                                        </select>
                                    </label>
                                    <label className="space-y-2 xl:col-span-1">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Exam name</span>
                                        <input
                                            type="text"
                                            value={examName}
                                            onChange={(e) => setExamName(e.target.value)}
                                            placeholder="Exam name"
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        />
                                    </label>
                                    <label className="space-y-2 xl:col-span-1">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Exam date</span>
                                        <input
                                            type="date"
                                            value={examDate}
                                            onChange={(e) => setExamDate(e.target.value)}
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        />
                                    </label>
                                    <label className="space-y-2 xl:col-span-1">
                                        <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Max marks</span>
                                        <input
                                            type="number"
                                            value={maxMarks}
                                            onChange={(e) => setMaxMarks(e.target.value)}
                                            placeholder="Max"
                                            className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                        />
                                    </label>
                                </div>
                            </PrismPanel>

                            {error ? (
                                <ErrorRemediation
                                    error={error}
                                    scope="teacher-marks"
                                    onRetry={() => {
                                        setError(null);
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
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">Marks register</p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            Enter only the scores you want to submit. Percentages calculate live against the current max marks.
                                        </p>
                                    </div>
                                    <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                        <FileSpreadsheet className="h-3.5 w-3.5" />
                                        {selectedSubject ? `${selectedSubject.name} assessment` : "Select a subject"}
                                    </div>
                                </div>

                                {loading ? (
                                    <div className="grid gap-3 p-5">
                                        {Array.from({ length: 6 }).map((_, index) => (
                                            <div key={index} className="h-16 animate-pulse rounded-2xl bg-[rgba(148,163,184,0.08)]" />
                                        ))}
                                    </div>
                                ) : !(selectedClass?.students.length) ? (
                                    <div className="p-5">
                                        <EmptyState
                                            icon={Users}
                                            title="No students in selected class"
                                            description="Choose another class or add students before entering assessment scores."
                                        />
                                    </div>
                                ) : (
                                    <div className="overflow-x-auto">
                                        <table className="w-full min-w-[760px]">
                                            <thead>
                                                <tr className="border-b border-[var(--border)] bg-[rgba(148,163,184,0.04)]">
                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Roll</th>
                                                    <th className="px-5 py-3 text-left text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Student</th>
                                                    <th className="px-5 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Score / {maxMarks || "0"}</th>
                                                    <th className="px-5 py-3 text-center text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Performance</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {selectedClass.students.map((student) => {
                                                    const markText = marksByStudent[student.id] || "";
                                                    const mark = Number(markText);
                                                    const max = Number(maxMarks);
                                                    const pct = markText !== "" && max > 0 && Number.isFinite(mark) ? Math.round((mark / max) * 100) : null;
                                                    const pctTone = pct !== null
                                                        ? pct >= 80
                                                            ? "text-[var(--success)]"
                                                            : pct >= 50
                                                                ? "text-[var(--warning)]"
                                                                : "text-[var(--error)]"
                                                        : "text-[var(--text-muted)]";

                                                    return (
                                                        <tr key={student.id} className="border-b border-[var(--border-light)]/80">
                                                            <td className="px-5 py-4 text-sm text-[var(--text-secondary)]">{student.roll_number || "-"}</td>
                                                            <td className="px-5 py-4">
                                                                <div>
                                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{student.name}</p>
                                                                    <p className="mt-1 text-xs text-[var(--text-muted)]">Ready for scored submission</p>
                                                                </div>
                                                            </td>
                                                            <td className="px-5 py-4 text-center">
                                                                <input
                                                                    type="number"
                                                                    value={markText}
                                                                    onChange={(e) => updateMarks(student.id, e.target.value)}
                                                                    min="0"
                                                                    max={maxMarks || "0"}
                                                                    placeholder="-"
                                                                    className="w-28 rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-3 py-2 text-center text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                                                />
                                                            </td>
                                                            <td className="px-5 py-4 text-center">
                                                                {pct !== null ? (
                                                                    <div className="space-y-1">
                                                                        <span className={`text-sm font-semibold ${pctTone}`}>{pct}%</span>
                                                                        <p className="text-[11px] text-[var(--text-muted)]">
                                                                            {pct >= 80 ? "Strong" : pct >= 50 ? "Watch" : "Needs intervention"}
                                                                        </p>
                                                                    </div>
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
                                )}
                            </PrismPanel>
                        </div>

                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Assessment snapshot</p>
                                <div className="mt-4 space-y-4">
                                    <SummaryRow label="Current class" value={selectedClass?.name || "None selected"} />
                                    <SummaryRow label="Subject" value={selectedSubject?.name || "None selected"} />
                                    <SummaryRow label="Exam draft" value={examName.trim() || "Untitled assessment"} />
                                    <SummaryRow label="Top entered score" value={marksSummary.topScore !== null ? `${marksSummary.topScore}` : "-"} />
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Workflow notes</p>
                                <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>Create the exam payload once, then use the same context for either OCR import or manual score entry.</p>
                                    <p>This redesign only upgrades composition and hierarchy. The API contract and exam creation flow remain unchanged.</p>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Performance guide</p>
                                <div className="mt-4 space-y-3">
                                    <GuideRow tone="success" label="80% and above" description="Strong understanding. Suitable for enrichment or advanced follow-up." />
                                    <GuideRow tone="warning" label="50% to 79%" description="Moderate mastery. Review gaps before the next assessment." />
                                    <GuideRow tone="error" label="Below 50%" description="Immediate intervention candidate for revision or remedial support." />
                                </div>
                            </PrismPanel>
                        </div>
                    </div>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
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

function GuideRow({
    tone,
    label,
    description,
}: {
    tone: "success" | "warning" | "error";
    label: string;
    description: string;
}) {
    const toneClasses = {
        success: "bg-success-subtle text-[var(--success)]",
        warning: "bg-warning-subtle text-[var(--warning)]",
        error: "bg-error-subtle text-[var(--error)]",
    } as const;

    return (
        <div className="flex items-start gap-3">
            <div className={`mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl ${toneClasses[tone]}`}>
                <Award className="h-4 w-4" />
            </div>
            <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">{label}</p>
                <p className="text-xs leading-5 text-[var(--text-muted)]">{description}</p>
            </div>
        </div>
    );
}
