"use client";

import { useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Check, X, Clock, Save } from "lucide-react";

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

export default function TeacherAttendancePage() {
    const searchParams = useSearchParams();
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [selectedClassId, setSelectedClassId] = useState("");
    const [entries, setEntries] = useState<Record<string, "present" | "absent" | "late">>({});
    const [selectedDate, setSelectedDate] = useState(new Date().toISOString().split("T")[0]);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const selectedClass = useMemo(
        () => classes.find((c) => c.id === selectedClassId) || null,
        [classes, selectedClassId],
    );

    const initializeEntries = (students: StudentItem[]) => {
        const initial: Record<string, "present" | "absent" | "late"> = {};
        for (const student of students) initial[student.id] = "present";
        setEntries(initial);
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
                    const target = preferred && list.some((cls) => cls.id === preferred) ? preferred : list[0].id;
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
    }, [searchParams]);

    useEffect(() => {
        const loadExisting = async () => {
            if (!selectedClass) return;
            initializeEntries(selectedClass.students || []);
            try {
                const payload = await api.teacher.classAttendance(selectedClass.id);
                const records = (payload || []) as AttendanceRow[];
                const mapByStudent: Record<string, "present" | "absent" | "late"> = {};
                for (const record of records) {
                    if (record.date === selectedDate) {
                        mapByStudent[record.student_id] = record.status;
                    }
                }
                if (Object.keys(mapByStudent).length > 0) {
                    setEntries((prev) => ({ ...prev, ...mapByStudent }));
                }
            } catch {
                // keep defaults
            }
        };
        void loadExisting();
    }, [selectedClass, selectedDate]);

    const toggleStatus = (id: string) => {
        const cycle = { present: "absent", absent: "late", late: "present" } as const;
        setEntries((prev) => ({ ...prev, [id]: cycle[prev[id] || "present"] }));
    };

    const saveAttendance = async () => {
        if (!selectedClass) return;
        try {
            setSaving(true);
            setError(null);
            await api.teacher.submitAttendance({
                class_id: selectedClass.id,
                date: selectedDate,
                entries: (selectedClass.students || []).map((student) => ({
                    student_id: student.id,
                    status: entries[student.id] || "present",
                })),
            });
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to save attendance");
        } finally {
            setSaving(false);
        }
    };

    const statusConfig = {
        present: { icon: Check, color: "text-[var(--success)]", bg: "bg-success-subtle" },
        absent: { icon: X, color: "text-[var(--error)]", bg: "bg-error-subtle" },
        late: { icon: Clock, color: "text-[var(--warning)]", bg: "bg-warning-subtle" },
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Attendance Entry</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Mark attendance for your class</p>
                </div>
                <div className="flex gap-2">
                    <select
                        value={selectedClassId}
                        onChange={(e) => setSelectedClassId(e.target.value)}
                        className="px-4 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    >
                        {classes.map((c) => (
                            <option key={c.id} value={c.id}>{c.name}</option>
                        ))}
                    </select>
                    <input
                        type="date"
                        value={selectedDate}
                        onChange={(e) => setSelectedDate(e.target.value)}
                        className="px-4 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                    />
                </div>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[600px]">
                        <thead>
                            <tr className="border-b border-[var(--border)] bg-[var(--bg-page)]">
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Roll</th>
                                <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Name</th>
                                <th className="px-5 py-3 text-center text-xs font-medium text-[var(--text-muted)] uppercase">Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={3}>Loading students...</td>
                                </tr>
                            ) : !(selectedClass?.students.length) ? (
                                <tr>
                                    <td className="px-5 py-4 text-sm text-[var(--text-muted)]" colSpan={3}>No students in this class.</td>
                                </tr>
                            ) : selectedClass.students.map((student) => {
                                const status = entries[student.id] || "present";
                                const cfg = statusConfig[status];
                                const Icon = cfg.icon;
                                return (
                                    <tr key={student.id} className="border-b border-[var(--border-light)]">
                                        <td className="px-5 py-3 text-sm text-[var(--text-secondary)]">{student.roll_number || "-"}</td>
                                        <td className="px-5 py-3 text-sm font-medium text-[var(--text-primary)]">{student.name}</td>
                                        <td className="px-5 py-3 text-center">
                                            <button
                                                onClick={() => toggleStatus(student.id)}
                                                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs font-medium ${cfg.bg} ${cfg.color}`}
                                            >
                                                <Icon className="w-3.5 h-3.5" /> {status}
                                            </button>
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
                        onClick={() => void saveAttendance()}
                        disabled={saving || !selectedClass}
                    >
                        <Save className="w-4 h-4" /> {saving ? "Saving..." : "Save Attendance"}
                    </button>
                </div>
            </div>
            );
}
