"use client";

import { useCallback, useEffect, useMemo, useState, type ReactNode } from "react";
import { Clock, Loader2, Plus, Sparkles, Trash2 } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismInput, PrismSelect, PrismTableShell, PrismTextarea } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type SubjectItem = { id: string; name: string };
type ClassItem = { id: string; name: string; grade: string; subjects: SubjectItem[] };
type UserItem = { id: string; name: string; role: string; is_active: boolean };
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
};

const DAYS = [
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

    const currentClass = useMemo(() => classes.find((item) => item.id === selectedClassId) || null, [classes, selectedClassId]);
    const teachers = useMemo(() => users.filter((user) => (user.role === "teacher" || user.role === "admin") && user.is_active), [users]);

    const buildGeneratorTemplate = useCallback(() => {
        const teacherIds = teachers.map((teacher) => teacher.id);
        return {
            time_grid: { days_per_week: 5, periods_per_day: 7, day_start_time: "09:00", period_minutes: 45, breaks: [] },
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
            rules: { no_back_to_back_classes: true, no_back_to_back_teachers: true },
            apply_to_db: false,
        };
    }, [classes, teachers]);

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
                const [classPayload, userPayload] = await Promise.all([api.admin.classes(), api.admin.users()]);
                const classItems = (classPayload || []) as ClassItem[];
                setClasses(classItems);
                setUsers((userPayload || []) as UserItem[]);
                if (classItems.length > 0) setSelectedClassId((previous) => previous || classItems[0].id);
            } catch (loadError) {
                setError(loadError instanceof Error ? loadError.message : "Failed to load timetable data");
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
    }, [buildGeneratorTemplate, classes, generatorInitialized, teachers]);

    useEffect(() => {
        if (!selectedClassId) return;
        void loadTimetable(selectedClassId).catch((loadError) => {
            setError(loadError instanceof Error ? loadError.message : "Failed to load class timetable");
        });
    }, [selectedClassId]);

    useEffect(() => {
        const subjectOptions = currentClass?.subjects || [];
        if (!subjectOptions.some((subject) => subject.id === subjectId)) setSubjectId(subjectOptions[0]?.id || "");
        if (!teachers.some((teacher) => teacher.id === teacherId)) setTeacherId(teachers[0]?.id || "");
    }, [currentClass, subjectId, teacherId, teachers]);

    const rows = useMemo(() => {
        const grouped = new Map<string, { start: string; end: string }>();
        for (const slot of slots) grouped.set(`${slot.start_time}-${slot.end_time}`, { start: slot.start_time, end: slot.end_time });
        return Array.from(grouped.values()).sort((left, right) => left.start.localeCompare(right.start));
    }, [slots]);

    const getSlot = (day: number, start: string, end: string) =>
        slots.find((slot) => slot.day_of_week === day && slot.start_time === start && slot.end_time === end) || null;

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
        } catch (createError) {
            setError(createError instanceof Error ? createError.message : "Failed to create timetable slot");
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
        } catch (deleteError) {
            setError(deleteError instanceof Error ? deleteError.message : "Failed to delete timetable slot");
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
            if (applyGenerated) payload.apply_to_db = true;
            const result = await api.admin.generateTimetable(payload);
            setGeneratorResult(result as GeneratorResult);
            if ((result as GeneratorResult).applied && selectedClassId) await loadTimetable(selectedClassId);
        } catch (runError) {
            setGeneratorError(runError instanceof Error ? runError.message : "Failed to generate timetable");
        } finally {
            setGeneratorLoading(false);
        }
    };

    return (
        <PrismPage className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.12fr_0.88fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Clock className="h-3.5 w-3.5" />
                            Admin Scheduling Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Timetable Management
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                Create, review, and auto-generate class schedules from one controlled admin scheduling workspace.
                            </p>
                        </div>
                    </div>
                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <MetricCard title="Classes" value={`${classes.length}`} summary="Classes available for scheduling." accent="blue" />
                        <MetricCard title="Teachers" value={`${teachers.length}`} summary="Active teacher or admin resources available." accent="emerald" />
                        <MetricCard title="Visible slots" value={`${slots.length}`} summary={currentClass ? `Current timetable for ${currentClass.name}.` : "Select a class to inspect the schedule."} accent="amber" />
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="admin-timetable"
                        onRetry={() => {
                            if (selectedClassId) void loadTimetable(selectedClassId);
                        }}
                    />
                ) : null}

                <div className="grid gap-6 xl:grid-cols-[minmax(0,1.05fr)_minmax(360px,0.95fr)]">
                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Schedule Controls</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">Choose a class, create manual slots, and keep the timetable grid aligned with the underlying schedule data.</p>
                                </div>
                                <div className="w-full lg:w-auto lg:min-w-[240px]">
                                    <Field label="Class" htmlFor="class-selector">
                                        <PrismSelect
                                            id="class-selector"
                                            className="text-sm"
                                            value={selectedClassId}
                                            onChange={(event) => setSelectedClassId(event.target.value)}
                                            disabled={loading || classes.length === 0}
                                        >
                                            {classes.length === 0 ? <option value="">No classes</option> : classes.map((item) => (
                                                <option key={item.id} value={item.id}>{item.name} (Grade {item.grade})</option>
                                            ))}
                                        </PrismSelect>
                                    </Field>
                                </div>
                            </div>

                            <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                                <Field label="Day" htmlFor="day-selector">
                                    <PrismSelect id="day-selector" value={dayOfWeek} onChange={(event) => setDayOfWeek(Number(event.target.value))} className="text-sm">
                                        {DAYS.map((day) => <option key={day.value} value={day.value}>{day.label}</option>)}
                                    </PrismSelect>
                                </Field>
                                <Field label="Subject" htmlFor="subject-selector">
                                    <PrismSelect id="subject-selector" value={subjectId} onChange={(event) => setSubjectId(event.target.value)} className="text-sm" disabled={!currentClass || currentClass.subjects.length === 0}>
                                        {currentClass?.subjects.length ? currentClass.subjects.map((subject) => <option key={subject.id} value={subject.id}>{subject.name}</option>) : <option value="">No subjects</option>}
                                    </PrismSelect>
                                </Field>
                                <Field label="Teacher" htmlFor="teacher-selector">
                                    <PrismSelect id="teacher-selector" value={teacherId} onChange={(event) => setTeacherId(event.target.value)} className="text-sm" disabled={teachers.length === 0}>
                                        {teachers.length ? teachers.map((teacher) => <option key={teacher.id} value={teacher.id}>{teacher.name}</option>) : <option value="">No teachers</option>}
                                    </PrismSelect>
                                </Field>
                                <Field label="Start time" htmlFor="start-time">
                                    <PrismInput id="start-time" type="time" value={startTime} onChange={(event) => setStartTime(event.target.value)} className="text-sm" />
                                </Field>
                                <Field label="End time" htmlFor="end-time">
                                    <PrismInput id="end-time" type="time" value={endTime} onChange={(event) => setEndTime(event.target.value)} className="text-sm" />
                                </Field>
                                <div className="flex items-end">
                                    <button type="button" onClick={() => void createSlot()} disabled={saving || !selectedClassId || !subjectId || !teacherId} className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-3 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60">
                                        <Plus className="h-4 w-4" />
                                        Add Slot
                                    </button>
                                </div>
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Class Timetable</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">The current class timetable remains editable from the grid below.</p>
                                </div>
                                <div className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">{rows.length} time rows</div>
                            </div>

                            {loading ? (
                                <div className="mt-4 flex items-center gap-2 text-sm text-[var(--text-muted)]"><Loader2 className="h-4 w-4 animate-spin" /> Loading timetable...</div>
                            ) : rows.length === 0 ? (
                                <div className="mt-4">
                                    <EmptyState icon={Clock} title="No timetable slots found" description="Add a manual slot or apply a generated schedule to populate the grid." />
                                </div>
                            ) : (
                                <PrismTableShell className="mt-4">
                                    <table className="prism-table min-w-full">
                                        <thead>
                                            <tr>
                                                <th className="w-36">Time</th>
                                                {DAYS.map((day) => <th key={day.value}>{day.label}</th>)}
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {rows.map((row) => (
                                                <tr key={`${row.start}-${row.end}`}>
                                                    <td className="text-xs font-medium text-[var(--text-secondary)]">
                                                        <div className="flex items-center gap-2"><Clock className="h-3.5 w-3.5" />{row.start} - {row.end}</div>
                                                    </td>
                                                    {DAYS.map((day) => {
                                                        const slot = getSlot(day.value, row.start, row.end);
                                                        return (
                                                            <td key={`${day.value}-${row.start}-${row.end}`} className="align-top">
                                                                {slot ? (
                                                                    <div className="rounded-2xl border border-[rgba(96,165,250,0.18)] bg-[rgba(96,165,250,0.08)] p-3">
                                                                        <p className="text-xs font-semibold text-[var(--text-primary)]">{slot.subject}</p>
                                                                        <p className="mt-1 text-[11px] text-[var(--text-secondary)]">{slot.teacher}</p>
                                                                        <button type="button" onClick={() => void deleteSlot(slot.id)} disabled={saving} className="mt-3 inline-flex items-center gap-1 text-[11px] font-medium text-red-400 disabled:opacity-60">
                                                                            <Trash2 className="h-3 w-3" />
                                                                            Delete
                                                                        </button>
                                                                    </div>
                                                                ) : (
                                                                    <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.02)] p-3 text-xs text-[var(--text-muted)]">-</div>
                                                                )}
                                                            </td>
                                                        );
                                                    })}
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </PrismTableShell>
                            )}
                        </PrismPanel>
                    </div>

                    <div className="space-y-6 min-w-0">
                        <PrismPanel className="p-5 xl:sticky xl:top-6">
                            <div className="flex items-center gap-2">
                                <Sparkles className="h-4 w-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Auto-generate Timetable</h2>
                            </div>
                            <p className="mt-2 text-sm text-[var(--text-secondary)]">Tune teacher availability and weekly requirements directly in the payload, then generate or apply the result.</p>

                            {generatorError ? <div className="mt-4 rounded-2xl border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">{generatorError}</div> : null}

                            <PrismTextarea aria-label="Generator JSON" value={generatorJson} onChange={(event) => setGeneratorJson(event.target.value)} rows={14} className="mt-4 font-mono text-xs leading-6" />

                            <label className="mt-4 flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                                <input type="checkbox" checked={applyGenerated} onChange={(event) => setApplyGenerated(event.target.checked)} />
                                Apply generated schedule to timetable
                            </label>

                            <div className="mt-4 grid gap-3 sm:grid-cols-2">
                                <button type="button" onClick={resetGeneratorTemplate} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm font-medium text-[var(--text-primary)] transition hover:border-[rgba(96,165,250,0.28)] hover:bg-[rgba(96,165,250,0.08)]" disabled={generatorLoading}>Reset Template</button>
                                <button type="button" onClick={() => void runGenerator()} className="inline-flex items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(45,212,191,0.95),rgba(96,165,250,0.92))] px-4 py-3 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(45,212,191,0.22)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60" disabled={generatorLoading}>
                                    {generatorLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                                    Generate Timetable
                                </button>
                            </div>

                            {generatorResult ? (
                                <div className="mt-4 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4 text-sm">
                                    {generatorResult.success ? (
                                        <div className="space-y-2">
                                            <p className="font-semibold text-[var(--text-primary)]">Generated {generatorResult.assignments?.length || 0} slots{generatorResult.applied ? " and applied them." : "."}</p>
                                            <p className="text-[var(--text-secondary)]">Class balance score: {generatorResult.class_balance_score?.toFixed(2) || "0.00"}</p>
                                        </div>
                                    ) : (
                                        <div className="space-y-2">
                                            <p className="font-semibold text-[var(--text-primary)]">No feasible timetable found</p>
                                            <pre className="overflow-x-auto whitespace-pre-wrap text-xs text-[var(--text-muted)]">{JSON.stringify(generatorResult.conflicts, null, 2)}</pre>
                                        </div>
                                    )}
                                </div>
                            ) : null}
                        </PrismPanel>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({ title, value, summary, accent }: { title: string; value: string; summary: string; accent: "blue" | "emerald" | "amber" }) {
    const accentClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))]",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))]",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))]",
    } as const;
    return (
        <PrismPanel className="p-4">
            <div className={`mb-3 h-2 w-16 rounded-full ${accentClasses[accent]}`} />
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{title}</p>
            <p className="mt-2 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{summary}</p>
        </PrismPanel>
    );
}

function Field({ label, htmlFor, children }: { label: string; htmlFor: string; children: ReactNode }) {
    return (
        <div>
            <label htmlFor={htmlFor} className="mb-2 block text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</label>
            {children}
        </div>
    );
}
