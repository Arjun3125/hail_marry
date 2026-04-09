"use client";

import { useEffect, useMemo, useState } from "react";
import { CalendarCheck, Clock, ShieldCheck } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type AttendanceItem = {
    date: string;
    day: string;
    status: string;
};

type AttendancePayload = {
    items: AttendanceItem[];
    summary: {
        present: number;
        absent: number;
        late: number;
        marked_days: number;
        attendance_pct: number;
    };
    monthly_activity: Array<{
        month: string;
        present: number;
        absent: number;
        late: number;
        attendance_pct: number;
        marked_days: number;
    }>;
};

function normalizeAttendancePayload(payload: unknown): AttendancePayload {
    if (Array.isArray(payload)) {
        const items = payload as AttendanceItem[];
        const present = items.filter((item) => item.status.toLowerCase() === "present").length;
        const absent = items.filter((item) => item.status.toLowerCase() === "absent").length;
        const late = items.filter((item) => item.status.toLowerCase().includes("late")).length;
        const markedDays = items.length;
        return {
            items,
            summary: {
                present,
                absent,
                late,
                marked_days: markedDays,
                attendance_pct: markedDays > 0 ? Math.round((present / markedDays) * 100) : 0,
            },
            monthly_activity: [],
        };
    }
    if (!payload || typeof payload !== "object") {
        return {
            items: [],
            summary: {
                present: 0,
                absent: 0,
                late: 0,
                marked_days: 0,
                attendance_pct: 0,
            },
            monthly_activity: [],
        };
    }
    const candidate = payload as Partial<AttendancePayload>;
    return {
        items: candidate.items ?? [],
        summary: {
            present: candidate.summary?.present ?? 0,
            absent: candidate.summary?.absent ?? 0,
            late: candidate.summary?.late ?? 0,
            marked_days: candidate.summary?.marked_days ?? 0,
            attendance_pct: candidate.summary?.attendance_pct ?? 0,
        },
        monthly_activity: candidate.monthly_activity ?? [],
    };
}

function formatStatus(status: string) {
    return status.replace(/_/g, " ");
}

export default function ParentAttendancePage() {
    const [items, setItems] = useState<AttendanceItem[]>([]);
    const [monthlyActivity, setMonthlyActivity] = useState<AttendancePayload["monthly_activity"]>([]);
    const [attendancePct, setAttendancePct] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = normalizeAttendancePayload(await api.parent.attendance());
                setItems(data.items);
                setMonthlyActivity(data.monthly_activity);
                setAttendancePct(data.summary.attendance_pct);
            } catch (loadError) {
                setError(loadError instanceof Error ? loadError.message : "Failed to load attendance");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const summary = useMemo(() => {
        const present = items.filter((item) => item.status.toLowerCase() === "present").length;
        const absent = items.filter((item) => item.status.toLowerCase() === "absent").length;
        const late = items.filter((item) => item.status.toLowerCase().includes("late")).length;
        return { present, absent, late };
    }, [items]);

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <CalendarCheck className="h-3.5 w-3.5" />
                            Parent Attendance Surface
                        </PrismHeroKicker>
                    )}
                    title="See the attendance story without operational noise"
                    description="Track consistency, missed days, and whether a short family follow-up may be needed this week."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">How to read this</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Focus on absence patterns and recent marked days first. This view is designed for quick parent understanding, not raw attendance operations.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Present</span>
                        <span className="prism-status-value">{summary.present}</span>
                        <span className="prism-status-detail">Marked days where attendance was recorded as present across the six-month demo window.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Absent</span>
                        <span className="prism-status-value">{summary.absent}</span>
                        <span className="prism-status-detail">Recorded absences visible in the seeded history.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Six-month rate</span>
                        <span className="prism-status-value">{attendancePct}%</span>
                        <span className="prism-status-detail">Attendance percentage across the loaded six-month story.</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="parent-attendance"
                        onRetry={() => window.location.reload()}
                    />
                ) : null}

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">Loading attendance records...</p>
                    </PrismPanel>
                ) : (
                    <>
                        <div className="grid gap-4 lg:grid-cols-[1.02fr_0.98fr]">
                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <Clock className="h-4 w-4 text-status-blue" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent record</h2>
                                </div>
                                {items.length > 0 ? (
                                    <div className="mt-4 space-y-3">
                                        {items.map((item) => (
                                            <div key={`${item.date}-${item.status}`} className="flex items-center justify-between gap-4 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                                <div>
                                                    <p className="text-sm font-medium text-[var(--text-primary)]">{item.date}</p>
                                                    <p className="mt-1 text-xs text-[var(--text-muted)]">{item.day}</p>
                                                </div>
                                                <span className="rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-3 py-1 text-xs font-semibold uppercase tracking-[0.14em] text-[var(--text-secondary)]">
                                                    {formatStatus(item.status)}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <div className="mt-4">
                                        <EmptyState
                                            icon={CalendarCheck}
                                            title="No attendance records found"
                                            description="Attendance entries will appear here once the school records the next marked day."
                                            eyebrow="No attendance yet"
                                            scopeNote="Once marked days are recorded by the school, this page keeps the story simple: present, absent, late, and whether any follow-up may be needed."
                                        />
                                    </div>
                                )}
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <div className="flex items-center gap-2">
                                    <ShieldCheck className="h-4 w-4 text-status-amber" />
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">What this means</h2>
                                </div>
                                <div className="mt-4 space-y-4 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>
                                        The attendance view keeps the story simple: whether attendance has stayed consistent, where absences appeared, and if the week needs a check-in.
                                    </p>
                                    <p>
                                        {summary.absent > 0
                                            ? `There ${summary.absent === 1 ? "is" : "are"} ${summary.absent} recorded absence${summary.absent === 1 ? "" : "s"} in the current list, so this week may need a short follow-up conversation.`
                                            : "There are no recorded absences in the current list, which suggests good routine and consistency."}
                                    </p>
                                </div>
                            </PrismPanel>
                        </div>

                        <PrismPanel className="p-5">
                            <div className="flex items-center gap-2">
                                <CalendarCheck className="h-4 w-4 text-status-blue" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Monthly attendance rhythm</h2>
                            </div>
                            <div className="mt-4 grid gap-3 md:grid-cols-3">
                                {monthlyActivity.map((item, index) => (
                                    <div key={`${item.month}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{item.month}</p>
                                        <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{item.attendance_pct}%</p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            {item.present} present, {item.absent} absent, {item.late} late across {item.marked_days} marked day{item.marked_days === 1 ? "" : "s"}.
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>
                    </>
                )}
            </PrismSection>
        </PrismPage>
    );
}
