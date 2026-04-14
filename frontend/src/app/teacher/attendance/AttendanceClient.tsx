"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { useVidyaContext } from "@/providers/VidyaContextProvider";
import {
    CalendarCheck,
    Check,
    CheckCircle2,
    Clock,
    Save,
    Send,
    Upload,
    Users,
    X,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismTableShell } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type StudentItem = {
    id: string;
    name: string;
    roll_number: string | null;
};

type TeacherClass = {
    id: string;
    name: string;
    students: StudentItem[];
};

type AttendanceRow = {
    student_id: string;
    date: string;
    status: "present" | "absent" | "late";
};

type AttendanceImportResponse = {
    imported?: number;
    errors?: string[];
    ocr_review_required?: boolean;
    ocr_warning?: string | null;
    ocr_confidence?: number | null;
    ocr_unmatched_lines?: number;
};

type AttendanceStatus = "present" | "absent" | "late";

const statusConfig: Record<
    AttendanceStatus,
    {
        icon: typeof Check;
        color: string;
        bg: string;
        ring: string;
        label: string;
        summary: string;
    }
> = {
    present: {
        icon: Check,
        color: "text-[var(--success)]",
        bg: "bg-success-subtle",
        ring: "border-[var(--success)]/25",
        label: "Present",
        summary: "On track for the session",
    },
    absent: {
        icon: X,
        color: "text-[var(--error)]",
        bg: "bg-error-subtle",
        ring: "border-[var(--error)]/25",
        label: "Absent",
        summary: "Needs follow-up",
    },
    late: {
        icon: Clock,
        color: "text-[var(--warning)]",
        bg: "bg-warning-subtle",
        ring: "border-[var(--warning)]/25",
        label: "Late",
        summary: "Present with delay",
    },
};

export default function TeacherAttendanceClient() {
    const searchParams = useSearchParams();
    const { activeClassId, mergeContext } = useVidyaContext();
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [selectedClassId, setSelectedClassId] = useState("");
    const [entries, setEntries] = useState<Record<string, AttendanceStatus>>({});
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [importing, setImporting] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [success, setSuccess] = useState<string | null>(null);
    const [parentNoticeQueued, setParentNoticeQueued] = useState(false);
    const [notifyingParents, setNotifyingParents] = useState(false);

    const selectedClass = useMemo(
        () => classes.find((c) => c.id === selectedClassId) || null,
        [classes, selectedClassId],
    );

    const studentCount = selectedClass?.students.length || 0;

    const attendanceCounts = useMemo(() => {
        const tally = { present: 0, absent: 0, late: 0 };
        if (!selectedClass) return tally;
        for (const student of selectedClass.students) {
            tally[entries[student.id] || "present"] += 1;
        }
        return tally;
    }, [entries, selectedClass]);
    const presentPercent = studentCount > 0 ? Math.round((attendanceCounts.present / studentCount) * 100) : 0;

    const initializeEntries = useCallback((students: StudentItem[]) => {
        const initial: Record<string, AttendanceStatus> = {};
        for (const student of students) initial[student.id] = "present";
        setEntries(initial);
    }, []);

    const loadAttendanceRecords = useCallback(async (classItem: TeacherClass | null, dateValue: string) => {
        if (!classItem) return;
        initializeEntries(classItem.students || []);
        try {
            const payload = await api.teacher.classAttendance(classItem.id);
            const records = (payload || []) as AttendanceRow[];
            const mapByStudent: Record<string, AttendanceStatus> = {};
            for (const record of records) {
                if (record.date === dateValue) {
                    mapByStudent[record.student_id] = record.status;
                }
            }
            if (Object.keys(mapByStudent).length > 0) {
                setEntries((prev) => ({ ...prev, ...mapByStudent }));
            }
        } catch {
            // Keep default all-present entries when no historical data is available.
        }
    }, [initializeEntries]);

    const formatImportNotice = (payload: AttendanceImportResponse) => {
        const imported = Number(payload.imported || 0);
        const errors = Array.isArray(payload.errors) ? payload.errors : [];
        const parts = [`Imported ${imported} attendance row${imported === 1 ? "" : "s"}.`];
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

    useEffect(() => {
        const loadClasses = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.classes();
                const list = (payload || []) as TeacherClass[];
                setClasses(list);
                if (list.length > 0) {
                    const preferred = searchParams.get("classId");
                    const target = preferred && list.some((cls) => cls.id === preferred)
                        ? preferred
                        : activeClassId && list.some((cls) => cls.id === activeClassId)
                          ? activeClassId
                          : list[0].id;
                    setSelectedClassId(target);
                    const selected = list.find((cls) => cls.id === target);
                    if (selected) initializeEntries(selected.students || []);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes");
            } finally {
                setLoading(false);
            }
        };
        void loadClasses();
    }, [activeClassId, initializeEntries, searchParams]);

    useEffect(() => {
        const loadExisting = async () => {
            if (!selectedClass) return;
            initializeEntries(selectedClass.students || []);
            await loadAttendanceRecords(selectedClass, selectedDate);
        };
        void loadExisting();
    }, [initializeEntries, loadAttendanceRecords, selectedClass, selectedDate]);

    useEffect(() => {
        if (!selectedClass) return;
        mergeContext({
            lastRole: "teacher",
            activeClassId: selectedClass.id,
            activeClassLabel: selectedClass.name,
        });
    }, [mergeContext, selectedClass]);

    useEffect(() => {
        if (typeof window === "undefined") return;
        window.localStorage.setItem(
            "mascotPageContext",
            JSON.stringify({
                route: "/teacher/attendance",
                current_page_entity: "class",
                current_page_entity_id: selectedClassId || null,
                metadata: {
                    class_id: selectedClassId || null,
                    date: selectedDate,
                },
            }),
        );
    }, [selectedClassId, selectedDate]);

    const toggleStatus = (id: string) => {
        const cycle = { present: "absent", absent: "late", late: "present" } as const;
        setEntries((prev) => ({ ...prev, [id]: cycle[prev[id] || "present"] }));
    };

    const saveAttendance = async () => {
        if (!selectedClass) return;
        try {
            setSaving(true);
            setError(null);
            setSuccess(null);
            setParentNoticeQueued(false);
            await api.teacher.submitAttendance({
                class_id: selectedClass.id,
                date: selectedDate,
                entries: (selectedClass.students || []).map((student) => ({
                    student_id: student.id,
                    status: entries[student.id] || "present",
                })),
            });
            setSuccess(`Attendance recorded for ${selectedClass.name}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save attendance");
        } finally {
            setSaving(false);
        }
    };

    const notifyAbsentParents = async () => {
        if (!selectedClass) return;
        const absentStudentIds = selectedClass.students
            .filter((student) => (entries[student.id] || "present") === "absent")
            .map((student) => student.id);
        if (!absentStudentIds.length) return;
        try {
            setNotifyingParents(true);
            setError(null);
            const payload = await api.teacher.notifyAbsentParents({
                class_id: selectedClass.id,
                date: selectedDate,
                absent_student_ids: absentStudentIds,
            }) as { sent?: number; skipped?: number; failed?: number };
            setParentNoticeQueued(true);
            setSuccess(`WhatsApp follow-up sent to ${payload.sent || 0} parent${payload.sent === 1 ? "" : "s"}${payload.skipped ? ` • ${payload.skipped} skipped` : ""}${payload.failed ? ` • ${payload.failed} failed` : ""}`);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to send WhatsApp parent follow-up");
        } finally {
            setNotifyingParents(false);
        }
    };

    const handleAttendanceImport = async (file: File) => {
        if (!selectedClass) {
            setError("Select a class before importing attendance.");
            return;
        }
        try {
            setImporting(true);
            setError(null);
            setSuccess(null);
            setParentNoticeQueued(false);
            const formData = new FormData();
            formData.append("file", file);
            const payload = await api.teacher.importAttendanceCsv(selectedClass.id, selectedDate, formData) as AttendanceImportResponse;
            setSuccess(formatImportNotice(payload));
            await loadAttendanceRecords(selectedClass, selectedDate);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to import attendance");
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
                            <CalendarCheck className="h-3.5 w-3.5" />
                            Teacher Attendance Workflow
                        </PrismHeroKicker>
                    )}
                    title="Mark Attendance"
                    description="Choose the class, confirm the date, import OCR-led registers when needed, and keep absent or late exceptions visible without slowing down the session."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with OCR import if you have a register image or sheet, then sweep the roster for the few students who need manual attention.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Class size</span>
                        <span className="prism-status-value">{studentCount}</span>
                        <span className="prism-status-detail">{selectedClass ? `${selectedClass.name} roster loaded` : "Choose a class to load the roster."}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Marked present</span>
                        <span className="prism-status-value">{attendanceCounts.present}</span>
                        <span className="prism-status-detail">{studentCount > 0 ? "Default-ready for rapid confirmation." : "Waiting for the roster to load."}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Needs attention</span>
                        <span className="prism-status-value">{attendanceCounts.absent + attendanceCounts.late}</span>
                        <span className="prism-status-detail">Absent and late students grouped for follow-up.</span>
                    </div>
                </div>

                <PrismPanel className="overflow-hidden p-0">
                    <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Operations Bar</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Choose a class, set the register date, then import or mark manually before saving.
                                </p>
                            </div>
                            <button
                                className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                                onClick={() => void saveAttendance()}
                                disabled={saving || importing || !selectedClass}
                            >
                                <Save className="h-4 w-4" />
                                {saving ? "Saving..." : "Save Attendance"}
                            </button>
                        </div>
                    </div>

                    <div className="grid gap-6 p-5 xl:grid-cols-[1.6fr_0.9fr]">
                        <div className="space-y-4">
                            <div className="grid gap-3 md:grid-cols-[1.2fr_1fr_auto]">
                                <label className="space-y-2">
                                    <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Class roster</span>
                                    <select
                                        value={selectedClassId}
                                        onChange={(e) => setSelectedClassId(e.target.value)}
                                        className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                    >
                                        {classes.map((c) => (
                                            <option key={c.id} value={c.id}>
                                                {c.name}
                                            </option>
                                        ))}
                                    </select>
                                </label>

                                <label className="space-y-2">
                                    <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Register date</span>
                                    <input
                                        type="date"
                                        value={selectedDate}
                                        onChange={(e) => setSelectedDate(e.target.value)}
                                        className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                    />
                                </label>

                                <label className="space-y-2">
                                    <span className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">OCR import</span>
                                    <span className="inline-flex cursor-pointer items-center justify-center gap-2 rounded-2xl border border-[var(--primary)]/20 bg-[var(--primary-light)] px-4 py-3 text-sm font-medium text-[var(--primary)] transition-colors hover:bg-[var(--primary)] hover:text-white">
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
                                                    void handleAttendanceImport(file);
                                                }
                                            }}
                                        />
                                    </span>
                                </label>
                            </div>

                            {error ? (
                                <ErrorRemediation
                                    error={error}
                                    scope="teacher-attendance"
                                    onRetry={() => {
                                        if (selectedClass) {
                                            void loadAttendanceRecords(selectedClass, selectedDate);
                                        }
                                    }}
                                />
                            ) : null}

                            {success ? (
                                <div className="rounded-[1.5rem] border border-[var(--success)]/30 bg-success-subtle p-4">
                                    <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                                        <div className="min-w-0">
                                            <p className="flex items-center gap-2 text-sm font-semibold text-[var(--success)]">
                                                <CheckCircle2 className="h-4 w-4" />
                                                {success}
                                            </p>
                                            <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">
                                                {presentPercent}% present today • {attendanceCounts.absent} absent • {attendanceCounts.late} late
                                            </p>
                                            <p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">
                                                Parent follow-up is available for absent students before the day closes.
                                            </p>
                                        </div>
                                        <button
                                            type="button"
                                            onClick={() => void notifyAbsentParents()}
                                            disabled={attendanceCounts.absent === 0 || parentNoticeQueued || notifyingParents}
                                            className="inline-flex min-h-[44px] items-center justify-center gap-2 rounded-2xl border border-[var(--success)]/30 bg-[rgba(16,185,129,0.12)] px-4 py-2.5 text-xs font-bold text-[var(--success)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-55"
                                        >
                                            <Send className="h-4 w-4" />
                                            {attendanceCounts.absent === 0
                                                ? "No absent parent follow-up needed"
                                                : parentNoticeQueued
                                                  ? "WhatsApp follow-up sent"
                                                  : notifyingParents
                                                    ? "Sending WhatsApp..."
                                                  : "Send WhatsApp to absent parents"}
                                        </button>
                                    </div>
                                    {parentNoticeQueued ? (
                                        <p className="mt-3 rounded-2xl border border-[var(--success)]/20 bg-[rgba(16,185,129,0.08)] px-3 py-2 text-xs leading-5 text-[var(--text-secondary)]">
                                            Follow-up has been handed to the configured WhatsApp provider for linked parent phone numbers.
                                        </p>
                                    ) : null}
                                </div>
                            ) : null}

                            <PrismPanel className="overflow-hidden p-0">
                                <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                    <div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">Live roster register</p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            Click a status pill to cycle Present, Absent, and Late for each student.
                                        </p>
                                    </div>
                                    <div className="flex flex-wrap items-center gap-2">
                                        {(["present", "absent", "late"] as AttendanceStatus[]).map((status) => (
                                            <LegendPill
                                                key={status}
                                                status={status}
                                                count={attendanceCounts[status]}
                                            />
                                        ))}
                                    </div>
                                </div>

                                {loading ? (
                                    <div className="grid gap-3 p-5">
                                        {Array.from({ length: 6 }).map((_, index) => (
                                            <div key={index} className="h-16 animate-pulse rounded-2xl bg-[rgba(148,163,184,0.08)]" />
                                        ))}
                                    </div>
                                ) : !selectedClass?.students.length ? (
                                    <div className="p-5">
                                        <EmptyState
                                            icon={Users}
                                            title="No students in this class"
                                            description="Choose a different class or add students before taking attendance."
                                            eyebrow="Roster unavailable"
                                            scopeNote="Attendance entry only becomes useful after the selected class has an active student roster."
                                        />
                                    </div>
                                ) : (
                                    <PrismTableShell>
                                        <table className="prism-table w-full min-w-[720px]">
                                            <thead>
                                                <tr>
                                                    <th>Roll</th>
                                                    <th>Student</th>
                                                    <th>Current signal</th>
                                                    <th className="text-center">Cycle status</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                {selectedClass.students.map((student) => {
                                                    const status = entries[student.id] || "present";
                                                    const cfg = statusConfig[status];
                                                    const Icon = cfg.icon;
                                                    return (
                                                        <tr key={student.id} className="border-b border-[var(--border-light)]/80">
                                                            <td className="text-sm text-[var(--text-secondary)]">{student.roll_number || "-"}</td>
                                                            <td>
                                                                <div>
                                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{student.name}</p>
                                                                    <p className="mt-1 text-xs text-[var(--text-muted)]">Ready for today&apos;s register</p>
                                                                </div>
                                                            </td>
                                                            <td>
                                                                <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${cfg.bg} ${cfg.color} ${cfg.ring}`}>
                                                                    <Icon className="h-3.5 w-3.5" />
                                                                    <span>{cfg.label}</span>
                                                                </div>
                                                                <p className="mt-2 text-xs text-[var(--text-muted)]">{cfg.summary}</p>
                                                            </td>
                                                            <td className="text-center">
                                                                <button
                                                                    onClick={() => toggleStatus(student.id)}
                                                                    className={`inline-flex min-h-[44px] items-center gap-1.5 rounded-full border px-4 py-3 text-xs font-medium transition hover:-translate-y-0.5 ${cfg.bg} ${cfg.color} ${cfg.ring}`}
                                                                >
                                                                    <Icon className="h-3.5 w-3.5" />
                                                                    {status}
                                                                </button>
                                                            </td>
                                                        </tr>
                                                    );
                                                })}
                                            </tbody>
                                        </table>
                                    </PrismTableShell>
                                )}
                            </PrismPanel>
                        </div>

                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Operational summary</p>
                                <div className="mt-4 space-y-4">
                                    <SummaryRow label="Active class" value={selectedClass?.name || "None selected"} />
                                    <SummaryRow label="Register date" value={selectedDate} />
                                    <SummaryRow label="Roster loaded" value={`${studentCount} students`} />
                                    <SummaryRow label="Follow-up list" value={`${attendanceCounts.absent + attendanceCounts.late} students`} />
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Workflow notes</p>
                                <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>Start with OCR import if you have a handwritten or printed register, then sweep the roster for late and absent exceptions.</p>
                                    <p>Saving sends the same attendance payload already used by the existing workflow, so this redesign stays presentation-only.</p>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Status guide</p>
                                <div className="mt-4 space-y-3">
                                    {(["present", "absent", "late"] as AttendanceStatus[]).map((status) => {
                                        const cfg = statusConfig[status];
                                        const Icon = cfg.icon;
                                        return (
                                            <div key={status} className="flex items-start gap-3">
                                                <div className={`mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl ${cfg.bg} ${cfg.color}`}>
                                                    <Icon className="h-4 w-4" />
                                                </div>
                                                <div>
                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{cfg.label}</p>
                                                    <p className="text-xs leading-5 text-[var(--text-muted)]">{cfg.summary}</p>
                                                </div>
                                            </div>
                                        );
                                    })}
                                </div>
                            </PrismPanel>
                        </div>
                    </div>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

function LegendPill({ status, count }: { status: AttendanceStatus; count: number }) {
    const cfg = statusConfig[status];
    const Icon = cfg.icon;

    return (
        <div className={`inline-flex items-center gap-2 rounded-full border px-3 py-1.5 text-xs font-medium ${cfg.bg} ${cfg.color} ${cfg.ring}`}>
            <Icon className="h-3.5 w-3.5" />
            <span>{cfg.label}</span>
            <span className="rounded-full bg-black/5 px-2 py-0.5 text-[10px]">{count}</span>
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
