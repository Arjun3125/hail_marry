"use client";

import { Award, Bot, Clock } from "lucide-react";
import {
    Area,
    AreaChart,
    Bar,
    BarChart,
    CartesianGrid,
    ResponsiveContainer,
    Tooltip,
    XAxis,
    YAxis,
} from "recharts";

export interface Topic {
    subject: string;
    average_score: number;
    is_weak: boolean;
}

export interface ClassSchedule {
    subject: string;
    time: string;
}

export interface AcademicSnapshotProps {
    weeklyAttendance: { day: string; value: number }[];
    weeklyMarks: { day: string; value: number }[];
    upcomingClasses: ClassSchedule[];
    allTopics: Topic[];
    aiInsight?: string | null;
    loading: boolean;
    chartsReady?: boolean;
}

const chartTooltipStyle = {
    backgroundColor: "rgba(9, 15, 28, 0.94)",
    border: "1px solid rgba(148, 163, 184, 0.2)",
    borderRadius: "12px",
    color: "#e2e8f0",
    boxShadow: "0 12px 30px rgba(2, 6, 23, 0.35)",
};

export function AcademicSnapshot({
    weeklyAttendance,
    weeklyMarks,
    upcomingClasses,
    allTopics,
    aiInsight,
    loading,
    chartsReady = true,
}: AcademicSnapshotProps) {
    return (
        <div className="space-y-6">
            <div className="grid gap-6 md:grid-cols-2">
                <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.94),rgba(10,15,28,0.97))] p-5 shadow-[0_18px_38px_rgba(2,6,23,0.35)]">
                    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_90%_0%,rgba(99,102,241,0.16),transparent_55%)]" />
                    <div className="relative z-10">
                        <div className="mb-4 flex items-center justify-between">
                            <h2 className="text-sm font-semibold tracking-wide text-[var(--text-primary)]">Weekly attendance</h2>
                            <div className="rounded-full bg-indigo-400/15 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-indigo-300">
                                Trend
                            </div>
                        </div>
                        <div className="h-48 w-full">
                            {chartsReady ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={weeklyAttendance} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="attGradColor" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#818cf8" stopOpacity={0.5} />
                                                <stop offset="95%" stopColor="#818cf8" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.2)" />
                                        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <YAxis domain={[70, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <Tooltip contentStyle={chartTooltipStyle} itemStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                                        <Area type="monotone" dataKey="value" stroke="#818cf8" strokeWidth={3} fill="url(#attGradColor)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : null}
                        </div>
                    </div>
                </div>

                <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.94),rgba(10,15,28,0.97))] p-5 shadow-[0_18px_38px_rgba(2,6,23,0.35)]">
                    <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_90%_0%,rgba(168,85,247,0.14),transparent_55%)]" />
                    <div className="relative z-10">
                        <div className="mb-4 flex items-center justify-between">
                            <h2 className="text-sm font-semibold tracking-wide text-[var(--text-primary)]">Marks progression</h2>
                            <div className="rounded-full bg-violet-400/15 px-2 py-1 text-[10px] font-bold uppercase tracking-wider text-violet-300">
                                Growth
                            </div>
                        </div>
                        <div className="h-48 w-full">
                            {chartsReady ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={weeklyMarks} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="marksGradColor" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#a78bfa" stopOpacity={0.9} />
                                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.35} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="rgba(148, 163, 184, 0.2)" />
                                        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <YAxis domain={[50, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: "#94a3b8" }} />
                                        <Tooltip cursor={{ fill: "rgba(148, 163, 184, 0.06)" }} contentStyle={chartTooltipStyle} itemStyle={{ color: "#e2e8f0", fontWeight: 600 }} />
                                        <Bar dataKey="value" fill="url(#marksGradColor)" radius={[6, 6, 0, 0]} barSize={24} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : null}
                        </div>
                    </div>
                </div>
            </div>

            <div className="grid gap-6 lg:grid-cols-3">
                <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.94),rgba(10,15,28,0.97))] p-6 shadow-[0_18px_38px_rgba(2,6,23,0.35)] lg:col-span-2">
                    <h2 className="mb-4 text-base font-bold text-[var(--text-primary)]">Today&apos;s schedule</h2>
                    {loading ? (
                        <div className="space-y-4 animate-pulse">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="h-16 rounded-xl bg-[rgba(148,163,184,0.12)]" />
                            ))}
                        </div>
                    ) : upcomingClasses.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-10 opacity-70">
                            <Clock className="mb-3 h-12 w-12 text-[var(--text-muted)]" />
                            <p className="text-sm font-medium text-[var(--text-secondary)]">No classes scheduled today.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {upcomingClasses.map((cls, i) => (
                                <div
                                    key={`${cls.subject}-${i}`}
                                    className="group relative flex items-center gap-5 rounded-xl border border-[var(--border)] bg-[rgba(15,23,42,0.62)] p-4 transition-all duration-300 hover:border-indigo-400/30 hover:bg-[rgba(99,102,241,0.12)]"
                                >
                                    <div className="flex h-12 w-12 items-center justify-center rounded-lg bg-indigo-400/15 transition-transform duration-300 group-hover:scale-105">
                                        <Clock className="h-6 w-6 text-indigo-300" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-[var(--text-primary)]">{cls.subject}</p>
                                        <p className="mt-0.5 text-xs text-[var(--text-muted)]">{cls.time}</p>
                                    </div>
                                    <div className="absolute bottom-0 right-0 top-0 w-1.5 origin-center scale-y-0 rounded-l-full bg-indigo-400 transition-transform duration-300 group-hover:scale-y-100" />
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="space-y-6">
                    <div className="relative overflow-hidden rounded-3xl border border-indigo-400/20 bg-[linear-gradient(160deg,rgba(79,70,229,0.16),rgba(30,41,59,0.88))] p-5 shadow-[0_14px_32px_rgba(2,6,23,0.3)]">
                        <div className="mb-3 flex items-center gap-2">
                            <div className="rounded-md bg-indigo-400/20 p-1.5">
                                <Bot className="h-4 w-4 text-indigo-300" />
                            </div>
                            <h2 className="text-sm font-bold text-[var(--text-primary)]">AI insight</h2>
                        </div>
                        {aiInsight ? (
                            <p className="text-xs font-medium leading-relaxed text-[var(--text-secondary)]">
                                {aiInsight}
                            </p>
                        ) : (
                            <p className="text-xs italic text-[var(--text-muted)]">Gathering insights...</p>
                        )}
                    </div>

                    <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(155deg,rgba(16,26,44,0.94),rgba(10,15,28,0.97))] p-5 shadow-[0_18px_38px_rgba(2,6,23,0.35)]">
                        <h2 className="mb-4 text-sm font-bold text-[var(--text-primary)]">Performance</h2>
                        {loading ? (
                            <div className="text-xs text-[var(--text-muted)]">Loading metrics...</div>
                        ) : allTopics.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-6 opacity-70">
                                <Award className="mb-2 h-8 w-8 text-[var(--text-muted)]" />
                                <p className="text-[10px] text-[var(--text-muted)]">No subjects found</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {allTopics.map((topic) => (
                                    <div key={topic.subject} className="flex flex-col gap-1.5">
                                        <div className="flex items-center justify-between gap-2">
                                            <span className="min-w-0 flex-1 truncate text-[11px] font-semibold tracking-wide text-[var(--text-secondary)]">
                                                {topic.subject}
                                            </span>
                                            <span className={`text-[11px] font-bold ${topic.is_weak ? "text-rose-400" : topic.average_score >= 80 ? "text-emerald-400" : "text-indigo-300"}`}>
                                                {topic.average_score}%
                                            </span>
                                        </div>
                                        <div className="h-1.5 w-full overflow-hidden rounded-full bg-[rgba(148,163,184,0.2)]">
                                            <div
                                                className={`h-full rounded-full transition-all duration-1000 ease-out ${
                                                    topic.is_weak ? "bg-rose-400" : topic.average_score >= 80 ? "bg-emerald-400" : "bg-indigo-400"
                                                }`}
                                                style={{ width: `${topic.average_score}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
}
