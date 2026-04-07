"use client";

import { useEffect, useMemo, useState } from "react";
import { CalendarCheck, Clock, ShieldCheck } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type AttendanceItem = {
    date: string;
    day: string;
    status: string;
};

function formatStatus(status: string) {
    return status.replace(/_/g, " ");
}

export default function ParentAttendancePage() {
    const [items, setItems] = useState<AttendanceItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const data = await api.parent.attendance();
                setItems((data || []) as AttendanceItem[]);
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
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <CalendarCheck className="h-3.5 w-3.5" />
                            Parent Attendance Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black text-[var(--text-primary)] md:text-5xl">
                                Attendance
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                A simple attendance story focused on consistency, missed days, and whether follow-up is needed this week.
                            </p>
                        </div>
                    </div>
                    <PrismPanel className="p-5">
                        <h2 className="text-base font-semibold text-[var(--text-primary)]">Attendance overview</h2>
                        <div className="mt-4 grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                            <MetricCard label="Present" value={`${summary.present}`} tone="emerald" />
                            <MetricCard label="Absent" value={`${summary.absent}`} tone="amber" />
                            <MetricCard label="Late" value={`${summary.late}`} tone="blue" />
                        </div>
                    </PrismPanel>
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
                )}
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    label,
    value,
    tone,
}: {
    label: string;
    value: string;
    tone: "blue" | "emerald" | "amber";
}) {
    const toneClasses = {
        blue: "bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))]",
        emerald: "bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(16,185,129,0.08))]",
        amber: "bg-[linear-gradient(135deg,rgba(251,191,36,0.2),rgba(245,158,11,0.08))]",
    } as const;

    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <div className={`mb-3 h-2 w-14 rounded-full ${toneClasses[tone]}`} />
            <p className="text-xs font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
