"use client";

import { useEffect, useMemo, useState } from "react";
import { Clock } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type TimetableSlot = {
    day: number;
    start: string;
    end: string;
    subject: string;
    teacher: string;
};

const dayNameByIndex: Record<number, string> = {
    0: "Monday",
    1: "Tuesday",
    2: "Wednesday",
    3: "Thursday",
    4: "Friday",
    5: "Saturday",
    6: "Sunday",
};

function toMinutes(hhmm: string) {
    const [h, m] = hhmm.split(":").map((item) => Number(item));
    return h * 60 + m;
}

export default function TimetablePage() {
    const [slots, setSlots] = useState<TimetableSlot[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.student.timetable();
                setSlots((payload || []) as TimetableSlot[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load timetable");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const days = useMemo(() => {
        const fromData = Array.from(new Set(slots.map((slot) => slot.day))).sort((a, b) => a - b);
        return fromData.length > 0 ? fromData : [0, 1, 2, 3, 4];
    }, [slots]);

    const timeRows = useMemo(() => {
        const unique = Array.from(new Set(slots.map((slot) => `${slot.start}-${slot.end}`)));
        return unique.map((value) => {
            const [start, end] = value.split("-");
            return { start, end };
        }).sort((a, b) => toMinutes(a.start) - toMinutes(b.start));
    }, [slots]);

    const slotByKey = useMemo(() => {
        const map = new Map<string, TimetableSlot>();
        for (const slot of slots) map.set(`${slot.day}-${slot.start}-${slot.end}`, slot);
        return map;
    }, [slots]);

    return (
        <PrismPage variant="report" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Clock className="h-3.5 w-3.5" />Weekly Timetable</PrismHeroKicker>}
                    title="See your class week at a glance"
                    description="Use this timetable to stay clear on which subjects arrive when, who is teaching them, and how your study week is structured."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Scheduled days</span>
                        <strong className="prism-status-value">{days.length}</strong>
                        <span className="prism-status-detail">Weekdays that currently contain timetable entries</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Time blocks</span>
                        <strong className="prism-status-value">{timeRows.length}</strong>
                        <span className="prism-status-detail">Distinct periods across the visible schedule</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Total classes</span>
                        <strong className="prism-status-value">{slots.length}</strong>
                        <span className="prism-status-detail">Scheduled classroom sessions in the current timetable</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-timetable" onRetry={() => window.location.reload()} /> : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismSectionHeader title="Weekly schedule" description="Check the matrix below to plan your study day, revision windows, and teacher follow-ups." />
                    {loading ? (
                        <p className="text-sm text-[var(--text-secondary)]">Loading timetable...</p>
                    ) : timeRows.length === 0 ? (
                        <EmptyState icon={Clock} title="No timetable entries yet" description="Your weekly timetable will appear here once the school publishes the current schedule." eyebrow="Schedule unavailable" />
                    ) : (
                        <div className="overflow-auto">
                            <table className="w-full min-w-[760px]">
                                <thead>
                                    <tr className="border-b border-[var(--border)]">
                                        <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Time</th>
                                        {days.map((day) => (
                                            <th key={day} className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{dayNameByIndex[day] || `Day ${day}`}</th>
                                        ))}
                                    </tr>
                                </thead>
                                <tbody>
                                    {timeRows.map((row) => (
                                        <tr key={`${row.start}-${row.end}`} className="border-b border-[var(--border-light)]">
                                            <td className="px-4 py-3 text-sm text-[var(--text-secondary)]">{row.start} - {row.end}</td>
                                            {days.map((day) => {
                                                const slot = slotByKey.get(`${day}-${row.start}-${row.end}`);
                                                return (
                                                    <td key={`${day}-${row.start}-${row.end}`} className="px-4 py-3 align-top">
                                                        {slot ? (
                                                            <div className="rounded-2xl bg-[var(--primary-light)] p-3">
                                                                <p className="text-sm font-medium text-[var(--primary)]">{slot.subject}</p>
                                                                <p className="text-xs text-[var(--text-muted)]">{slot.teacher}</p>
                                                            </div>
                                                        ) : (
                                                            <div className="rounded-2xl bg-[var(--bg-page)] p-3 text-xs text-[var(--text-muted)]">Free</div>
                                                        )}
                                                    </td>
                                                );
                                            })}
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}
