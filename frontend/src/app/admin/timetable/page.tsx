"use client";

import { useEffect, useMemo, useState } from "react";
import { Clock, Trash2, Plus } from "lucide-react";

import { api } from "@/lib/api";

type SubjectItem = {
    id: string;
    name: string;
};

type ClassItem = {
    id: string;
    name: string;
    grade: string;
    subjects: SubjectItem[];
};

type UserItem = {
    id: string;
    name: string;
    role: string;
    is_active: boolean;
};

type TimetableSlot = {
    id: string;
    class_id: string;
    subject_id: string;
    subject: string;
    teacher_id: string;
    teacher: string;
    day_of_week: number;
    start_time: string;
    end_time: string;
};

const DAYS: Array<{ value: number; label: string }> = [
    { value: 0, label: "Monday" },
    { value: 1, label: "Tuesday" },
    { value: 2, label: "Wednesday" },
    { value: 3, label: "Thursday" },
    { value: 4, label: "Friday" },
    { value: 5, label: "Saturday" },
    { value: 6, label: "Sunday" },
];

export default function AdminTimetablePage() {
    const [classes, setClasses] = useState<ClassItem[]>([]);
    const [users, setUsers] = useState<UserItem[]>([]);
    const [slots, setSlots] = useState<TimetableSlot[]>([]);
    const [selectedClassId, setSelectedClassId] = useState("");

    const [dayOfWeek, setDayOfWeek] = useState(0);
    const [subjectId, setSubjectId] = useState("");
    const [teacherId, setTeacherId] = useState("");
    const [startTime, setStartTime] = useState("09:00");
    const [endTime, setEndTime] = useState("09:45");

    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState<string | null>(null);

    const currentClass = useMemo(
        () => classes.find((c) => c.id === selectedClassId) || null,
        [classes, selectedClassId],
    );
    const teachers = useMemo(
        () => users.filter((u) => (u.role === "teacher" || u.role === "admin") && u.is_active),
        [users],
    );

    const loadTimetable = async (classId: string) => {
        if (!classId) {
            setSlots([]);
            return;
        }
        const payload = await api.admin.timetable(classId);
        setSlots((payload || []) as TimetableSlot[]);
    };

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const [classPayload, userPayload] = await Promise.all([
                    api.admin.classes(),
                    api.admin.users(),
                ]);
                const classItems = (classPayload || []) as ClassItem[];
                const userItems = (userPayload || []) as UserItem[];
                setClasses(classItems);
                setUsers(userItems);
                if (classItems.length > 0) {
                    setSelectedClassId((prev) => prev || classItems[0].id);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load timetable data");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    useEffect(() => {
        if (!selectedClassId) return;
        const run = async () => {
            try {
                setError(null);
                await loadTimetable(selectedClassId);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load class timetable");
            }
        };
        void run();
    }, [selectedClassId]);

    useEffect(() => {
        const subjectOptions = currentClass?.subjects || [];
        if (!subjectOptions.some((s) => s.id === subjectId)) {
            setSubjectId(subjectOptions[0]?.id || "");
        }
        if (!teachers.some((t) => t.id === teacherId)) {
            setTeacherId(teachers[0]?.id || "");
        }
    }, [currentClass, teachers, subjectId, teacherId]);

    const rows = useMemo(() => {
        const grouped = new Map<string, { start: string; end: string }>();
        for (const slot of slots) {
            const key = `${slot.start_time}-${slot.end_time}`;
            grouped.set(key, { start: slot.start_time, end: slot.end_time });
        }
        return Array.from(grouped.values()).sort((a, b) => a.start.localeCompare(b.start));
    }, [slots]);

    const getSlot = (day: number, start: string, end: string) =>
        slots.find((s) => s.day_of_week === day && s.start_time === start && s.end_time === end) || null;

    const createSlot = async () => {
        if (!selectedClassId || !subjectId || !teacherId) return;
        try {
            setSaving(true);
            setError(null);
            await api.admin.createTimetableSlot({
                class_id: selectedClassId,
                subject_id: subjectId,
                teacher_id: teacherId,
                day_of_week: dayOfWeek,
                start_time: startTime,
                end_time: endTime,
            });
            await loadTimetable(selectedClassId);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to create timetable slot");
        } finally {
            setSaving(false);
        }
    };

    const deleteSlot = async (slotId: string) => {
        try {
            setSaving(true);
            setError(null);
            await api.admin.deleteTimetableSlot(slotId);
            await loadTimetable(selectedClassId);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to delete timetable slot");
        } finally {
            setSaving(false);
        }
    };

    return (
        <div>
            <div className="flex items-center justify-between mb-6">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Timetable Management</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Create and manage class schedules</p>
                </div>
                <select
                    className="px-4 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-white"
                    value={selectedClassId}
                    onChange={(e) => setSelectedClassId(e.target.value)}
                    disabled={loading || classes.length === 0}
                >
                    {classes.length === 0 ? (
                        <option value="">No classes</option>
                    ) : (
                        classes.map((item) => (
                            <option key={item.id} value={item.id}>
                                {item.name} (Grade {item.grade})
                            </option>
                        ))
                    )}
                </select>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 mb-6">
                <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Add Slot</h2>
                <div className="grid md:grid-cols-6 gap-2">
                    <select
                        value={dayOfWeek}
                        onChange={(e) => setDayOfWeek(Number(e.target.value))}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    >
                        {DAYS.map((day) => (
                            <option key={day.value} value={day.value}>{day.label}</option>
                        ))}
                    </select>
                    <select
                        value={subjectId}
                        onChange={(e) => setSubjectId(e.target.value)}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        disabled={!currentClass || currentClass.subjects.length === 0}
                    >
                        {currentClass?.subjects.length ? (
                            currentClass.subjects.map((subject) => (
                                <option key={subject.id} value={subject.id}>{subject.name}</option>
                            ))
                        ) : (
                            <option value="">No subjects</option>
                        )}
                    </select>
                    <select
                        value={teacherId}
                        onChange={(e) => setTeacherId(e.target.value)}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                        disabled={teachers.length === 0}
                    >
                        {teachers.length ? (
                            teachers.map((teacher) => (
                                <option key={teacher.id} value={teacher.id}>{teacher.name}</option>
                            ))
                        ) : (
                            <option value="">No teachers</option>
                        )}
                    </select>
                    <input
                        type="time"
                        value={startTime}
                        onChange={(e) => setStartTime(e.target.value)}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    />
                    <input
                        type="time"
                        value={endTime}
                        onChange={(e) => setEndTime(e.target.value)}
                        className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)]"
                    />
                    <button
                        onClick={() => void createSlot()}
                        disabled={saving || !selectedClassId || !subjectId || !teacherId}
                        className="px-3 py-2 text-sm bg-[var(--primary)] text-white rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-60 flex items-center justify-center gap-1"
                    >
                        <Plus className="w-4 h-4" /> Add
                    </button>
                </div>
            </div>

            <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                <div className="overflow-x-auto">
                    <table className="w-full min-w-[700px]">
                        <thead>
                            <tr className="border-b border-[var(--border)]">
                                <th className="px-4 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase w-32">Time</th>
                                {DAYS.map((day) => (
                                    <th key={day.value} className="px-4 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">{day.label}</th>
                                ))}
                            </tr>
                        </thead>
                        <tbody>
                            {loading ? (
                                <tr>
                                    <td colSpan={8} className="px-4 py-6 text-sm text-[var(--text-muted)]">Loading timetable...</td>
                                </tr>
                            ) : rows.length === 0 ? (
                                <tr>
                                    <td colSpan={8} className="px-4 py-6 text-sm text-[var(--text-muted)]">No timetable slots found for this class.</td>
                                </tr>
                            ) : rows.map((row) => (
                                <tr key={`${row.start}-${row.end}`} className="border-b border-[var(--border-light)]">
                                    <td className="px-4 py-3 text-xs text-[var(--text-secondary)]">
                                        <div className="flex items-center gap-1">
                                            <Clock className="w-3 h-3" />
                                            {row.start} - {row.end}
                                        </div>
                                    </td>
                                    {DAYS.map((day) => {
                                        const slot = getSlot(day.value, row.start, row.end);
                                        return (
                                            <td key={`${day.value}-${row.start}-${row.end}`} className="px-4 py-3 align-top">
                                                {slot ? (
                                                    <div className="p-2 rounded-[var(--radius-sm)] bg-[var(--primary-light)] text-[var(--primary)]">
                                                        <p className="text-xs font-semibold">{slot.subject}</p>
                                                        <p className="text-[10px] text-[var(--text-secondary)]">{slot.teacher}</p>
                                                        <button
                                                            onClick={() => void deleteSlot(slot.id)}
                                                            disabled={saving}
                                                            className="mt-1 text-[10px] text-[var(--error)] inline-flex items-center gap-1 disabled:opacity-60"
                                                        >
                                                            <Trash2 className="w-3 h-3" /> Delete
                                                        </button>
                                                    </div>
                                                ) : (
                                                    <div className="p-2 rounded-[var(--radius-sm)] bg-[var(--bg-page)] text-[var(--text-muted)] text-xs">-</div>
                                                )}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                </div>
            </div>
            );
}
