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

type GeneratorResult = {
    success: boolean;
    status?: string;
    class_balance_score?: number;
    assignments?: Array<{
        class_id: string;
        subject_id: string;
        teacher_id: string;
        day: number;
        period: number;
        start_time?: string;
        end_time?: string;
    }>;
    conflicts?: Record<string, unknown>;
    applied?: boolean;
    created?: number;
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

    const [generatorJson, setGeneratorJson] = useState("");
    const [generatorInitialized, setGeneratorInitialized] = useState(false);
    const [generatorLoading, setGeneratorLoading] = useState(false);
    const [generatorError, setGeneratorError] = useState<string | null>(null);
    const [generatorResult, setGeneratorResult] = useState<GeneratorResult | null>(null);
    const [applyGenerated, setApplyGenerated] = useState(false);

    const currentClass = useMemo(
        () => classes.find((c) => c.id === selectedClassId) || null,
        [classes, selectedClassId],
    );
    const teachers = useMemo(
        () => users.filter((u) => (u.role === "teacher" || u.role === "admin") && u.is_active),
        [users],
    );

    const buildGeneratorTemplate = () => {
        const teacherIds = teachers.map((teacher) => teacher.id);
        return {
            time_grid: {
                days_per_week: 5,
                periods_per_day: 7,
                day_start_time: "09:00",
                period_minutes: 45,
                breaks: [],
            },
            teachers: teachers.map((teacher) => ({
                id: teacher.id,
                name: teacher.name,
                max_periods_per_week: 25,
                max_periods_per_day: 5,
            })),
            requirements: classes.flatMap((cls) =>
                (cls.subjects || []).map((subject) => ({
                    class_id: cls.id,
                    subject_id: subject.id,
                    required_periods_per_week: 0,
                    allowed_teachers: teacherIds,
                })),
            ),
            fixed_lessons: [],
            rules: {
                no_back_to_back_classes: true,
                no_back_to_back_teachers: true,
            },
            apply_to_db: false,
        };
    };

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
        if (!generatorInitialized && classes.length > 0 && teachers.length > 0) {
            setGeneratorJson(JSON.stringify(buildGeneratorTemplate(), null, 2));
            setGeneratorInitialized(true);
        }
    }, [classes, teachers, generatorInitialized]);

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

    const resetGeneratorTemplate = () => {
        setGeneratorJson(JSON.stringify(buildGeneratorTemplate(), null, 2));
        setGeneratorResult(null);
        setGeneratorError(null);
    };

    const runGenerator = async () => {
        try {
            setGeneratorLoading(true);
            setGeneratorError(null);
            let payload: Record<string, unknown>;
            try {
                payload = JSON.parse(generatorJson || "{}");
            } catch {
                setGeneratorError("Invalid JSON in generator input");
                return;
            }
            if (applyGenerated) {
                payload.apply_to_db = true;
            }
            const result = await api.admin.generateTimetable(payload);
            setGeneratorResult(result as GeneratorResult);
            if ((result as GeneratorResult).applied && selectedClassId) {
                await loadTimetable(selectedClassId);
            }
        } catch (err) {
            setGeneratorError(err instanceof Error ? err.message : "Failed to generate timetable");
        } finally {
            setGeneratorLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-6 flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                <div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">Timetable Management</h1>
                    <p className="text-sm text-[var(--text-secondary)]">Create and manage class schedules</p>
                </div>
                <select
                    className="w-full sm:w-auto px-4 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--bg-card)]"
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
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 mb-6 space-y-4">
                <div>
                    <h2 className="text-sm font-semibold text-[var(--text-primary)]">Auto-generate timetable</h2>
                    <p className="text-xs text-[var(--text-muted)]">
                        Edit the JSON payload below to set teacher availability and weekly requirements. Required periods per week should be set per class/subject.
                    </p>
                </div>
                {generatorError ? (
                    <div className="rounded-[var(--radius-sm)] border border-[var(--error)]/30 bg-error-subtle px-3 py-2 text-xs text-[var(--error)]">
                        {generatorError}
                    </div>
                ) : null}
                <textarea
                    value={generatorJson}
                    onChange={(e) => setGeneratorJson(e.target.value)}
                    rows={12}
                    className="w-full text-xs font-mono rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-page)] p-3"
                />
                <div className="flex flex-wrap items-center gap-3">
                    <label className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
                        <input
                            type="checkbox"
                            checked={applyGenerated}
                            onChange={(e) => setApplyGenerated(e.target.checked)}
                        />
                        Apply generated schedule to timetable
                    </label>
                    <button
                        onClick={resetGeneratorTemplate}
                        className="px-3 py-2 text-xs border border-[var(--border)] rounded-[var(--radius-sm)] hover:bg-[var(--bg-hover)]"
                        disabled={generatorLoading}
                    >
                        Reset Template
                    </button>
                    <button
                        onClick={() => void runGenerator()}
                        className="px-3 py-2 text-xs bg-[var(--primary)] text-white rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-60"
                        disabled={generatorLoading}
                    >
                        {generatorLoading ? "Generating..." : "Generate Timetable"}
                    </button>
                </div>
                {generatorResult ? (
                    <div className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[var(--bg-page)] p-3 text-xs space-y-2">
                        {generatorResult.success ? (
                            <>
                                <div className="font-semibold text-[var(--text-primary)]">
                                    Generated {generatorResult.assignments?.length || 0} slots
                                    {generatorResult.applied ? " and applied to timetable." : "."}
                                </div>
                                <div className="text-[var(--text-muted)]">
                                    Class balance score: {generatorResult.class_balance_score?.toFixed(2) || "0.00"}
                                </div>
                            </>
                        ) : (
                            <>
                                <div className="font-semibold text-[var(--text-primary)]">No feasible timetable found</div>
                                <pre className="text-[10px] text-[var(--text-muted)] whitespace-pre-wrap">
                                    {JSON.stringify(generatorResult.conflicts, null, 2)}
                                </pre>
                            </>
                        )}
                    </div>
                ) : null}
            </div>

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 mb-6">
                <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-3">Add Slot</h2>
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-6 gap-2">
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

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
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
