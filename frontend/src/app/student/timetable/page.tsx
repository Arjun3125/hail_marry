"use client";

import { useEffect, useMemo, useState } from "react";
import { Clock } from "lucide-react";

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
        return unique
            .map((value) => {
                const [start, end] = value.split("-");
                return { start, end };
            })
            .sort((a, b) => toMinutes(a.start) - toMinutes(b.start));
    }, [slots]);

    const slotByKey = useMemo(() => {
        const map = new Map<string, TimetableSlot>();
        for (const slot of slots) {
            map.set(`${slot.day}-${slot.start}-${slot.end}`, slot);
        }
        return map;
    }, [slots]);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Timetable</h1>
                <p className="text-sm text-[var(--text-secondary)]">Your weekly class schedule.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-auto">
                <table className="w-full min-w-[760px]">
                    <thead>
                        <tr className="border-b border-[var(--border)]">
                            <th className="px-4 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase w-36">Time</th>
                            {days.map((day) => (
                                <th key={day} className="px-4 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">
                                    {dayNameByIndex[day] || `Day ${day}`}
                                </th>
                            ))}
                        </tr>
                    </thead>
                    <tbody>
                        {loading ? (
                            <tr>
                                <td className="px-4 py-4 text-sm text-[var(--text-muted)]" colSpan={days.length + 1}>
                                    Loading timetable...
                                </td>
                            </tr>
                        ) : timeRows.length === 0 ? (
                            <tr>
                                <td className="px-4 py-4 text-sm text-[var(--text-muted)]" colSpan={days.length + 1}>
                                    No timetable entries available.
                                </td>
                            </tr>
                        ) : (
                            timeRows.map((row) => (
                                <tr key={`${row.start}-${row.end}`} className="border-b border-[var(--border-light)]">
                                    <td className="px-4 py-3">
                                        <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
                                            <Clock className="w-3 h-3" />
                                            {row.start} - {row.end}
                                        </div>
                                    </td>
                                    {days.map((day) => {
                                        const slot = slotByKey.get(`${day}-${row.start}-${row.end}`);
                                        return (
                                            <td key={`${day}-${row.start}-${row.end}`} className="px-4 py-3 align-top">
                                                {slot ? (
                                                    <div className="p-2 bg-[var(--primary-light)] rounded-[var(--radius-sm)]">
                                                        <p className="text-xs font-medium text-[var(--primary)]">{slot.subject}</p>
                                                        <p className="text-[10px] text-[var(--text-muted)]">{slot.teacher}</p>
                                                    </div>
                                                ) : (
                                                    <div className="p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                                        <p className="text-xs text-[var(--text-muted)]">-</p>
                                                    </div>
                                                )}
                                            </td>
                                        );
                                    })}
                                </tr>
                            ))
                        )}
                    </tbody>
                </table>
            </div>
        </div>
    );
}
