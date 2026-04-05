"use client";

import { Award, Bot, Clock } from "lucide-react";
import {
    ResponsiveContainer,
    AreaChart,
    Area,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
    BarChart,
    Bar,
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
            {/* Charts Row */}
            <div className="grid md:grid-cols-2 gap-6">
                {/* Attendance Chart */}
                <div className="relative overflow-hidden rounded-2xl bg-white/5 backdrop-blur-md border-0 p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)]">
                    <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/5 via-transparent to-transparent z-0 pointer-events-none" />
                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-sm font-semibold tracking-wide text-foreground">Weekly Attendance</h2>
                            <div className="px-2 py-1 text-[10px] font-bold rounded-full bg-indigo-500/10 text-indigo-500 uppercase tracking-wider">
                                Trend
                            </div>
                        </div>
                        <div className="h-48 w-full">
                            {chartsReady ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={weeklyAttendance} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="attGradColor" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#6366f1" stopOpacity={0.4} />
                                                <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" strokeOpacity={0.1} />
                                        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'currentColor', opacity: 0.5 }} />
                                        <YAxis domain={[70, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'currentColor', opacity: 0.5 }} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)', border: 'none', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            itemStyle={{ color: '#1e293b', fontWeight: 600 }}
                                        />
                                        <Area type="monotone" dataKey="value" stroke="#6366f1" strokeWidth={3} fill="url(#attGradColor)" />
                                    </AreaChart>
                                </ResponsiveContainer>
                            ) : null}
                        </div>
                    </div>
                </div>

                {/* Marks Chart */}
                <div className="relative overflow-hidden rounded-2xl bg-white/5 backdrop-blur-md border-0 p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)]">
                    <div className="absolute inset-0 bg-gradient-to-br from-violet-500/5 via-transparent to-transparent z-0 pointer-events-none" />
                    <div className="relative z-10">
                        <div className="flex items-center justify-between mb-4">
                            <h2 className="text-sm font-semibold tracking-wide text-foreground">Marks Progression</h2>
                            <div className="px-2 py-1 text-[10px] font-bold rounded-full bg-violet-500/10 text-violet-500 uppercase tracking-wider">
                                Growth
                            </div>
                        </div>
                        <div className="h-48 w-full">
                            {chartsReady ? (
                                <ResponsiveContainer width="100%" height="100%">
                                    <BarChart data={weeklyMarks} margin={{ top: 10, right: 0, left: -20, bottom: 0 }}>
                                        <defs>
                                            <linearGradient id="marksGradColor" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.9} />
                                                <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.3} />
                                            </linearGradient>
                                        </defs>
                                        <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="currentColor" strokeOpacity={0.1} />
                                        <XAxis dataKey="day" axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'currentColor', opacity: 0.5 }} />
                                        <YAxis domain={[50, 100]} axisLine={false} tickLine={false} tick={{ fontSize: 11, fill: 'currentColor', opacity: 0.5 }} />
                                        <Tooltip
                                            cursor={{ fill: 'currentColor', opacity: 0.05 }}
                                            contentStyle={{ backgroundColor: 'rgba(255,255,255,0.9)', backdropFilter: 'blur(8px)', border: 'none', borderRadius: '12px', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }}
                                            itemStyle={{ color: '#1e293b', fontWeight: 600 }}
                                        />
                                        <Bar dataKey="value" fill="url(#marksGradColor)" radius={[6, 6, 0, 0]} barSize={24} />
                                    </BarChart>
                                </ResponsiveContainer>
                            ) : null}
                        </div>
                    </div>
                </div>
            </div>

            {/* Bottom Info Grid */}
            <div className="grid lg:grid-cols-3 gap-6">
                {/* Schedule Card */}
                <div className="lg:col-span-2 relative overflow-hidden rounded-2xl bg-white/5 backdrop-blur-md border-0 p-6 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)]">
                    <h2 className="text-base font-bold text-foreground mb-4">Today&apos;s Schedule</h2>
                    {loading ? (
                        <div className="animate-pulse space-y-4">
                            {[1, 2, 3].map((i) => (
                                <div key={i} className="h-16 bg-white/5 rounded-xl block" />
                            ))}
                        </div>
                    ) : upcomingClasses.length === 0 ? (
                        <div className="flex flex-col items-center justify-center py-10 opacity-50">
                            <Clock className="w-12 h-12 mb-3" />
                            <p className="text-sm font-medium">No classes scheduled today.</p>
                        </div>
                    ) : (
                        <div className="space-y-3">
                            {upcomingClasses.map((cls, i) => (
                                <div
                                    key={`${cls.subject}-${i}`}
                                    className="group relative flex items-center gap-5 p-4 rounded-xl bg-white/40 dark:bg-black/20 hover:bg-white/60 dark:hover:bg-black/40 transition-all duration-300"
                                >
                                    <div className="w-12 h-12 rounded-lg bg-indigo-500/10 flex items-center justify-center group-hover:scale-105 transition-transform duration-300">
                                        <Clock className="w-6 h-6 text-indigo-500" />
                                    </div>
                                    <div className="flex-1">
                                        <p className="text-sm font-bold text-foreground">{cls.subject}</p>
                                        <p className="text-xs text-muted-foreground mt-0.5">{cls.time}</p>
                                    </div>
                                    <div className="w-1.5 h-full absolute right-0 top-0 bottom-0 bg-indigo-500 scale-y-0 group-hover:scale-y-100 transition-transform origin-center duration-300 rounded-l-full" />
                                </div>
                            ))}
                        </div>
                    )}
                </div>

                <div className="space-y-6">
                    {/* Insights Card */}
                    <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-indigo-500/10 to-violet-500/5 border border-indigo-500/10 p-5 shadow-lg">
                        <div className="flex items-center gap-2 mb-3">
                            <div className="p-1.5 bg-indigo-500/20 rounded-md">
                                <Bot className="w-4 h-4 text-indigo-600 dark:text-indigo-400" />
                            </div>
                            <h2 className="text-sm font-bold text-foreground">AI Insight</h2>
                        </div>
                        {aiInsight ? (
                            <div>
                                <p className="text-xs text-foreground/80 leading-relaxed font-medium">
                                    {aiInsight}
                                </p>
                            </div>
                        ) : (
                            <p className="text-xs text-muted-foreground italic">Gathering insights...</p>
                        )}
                    </div>

                    {/* Subject Performance */}
                    <div className="relative overflow-hidden rounded-2xl bg-white/5 backdrop-blur-md border-0 p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] dark:shadow-[0_8px_30px_rgb(0,0,0,0.2)]">
                        <h2 className="text-sm font-bold text-foreground mb-4">Performance</h2>
                        {loading ? (
                            <div className="text-xs opacity-50">Loading metrics...</div>
                        ) : allTopics.length === 0 ? (
                            <div className="flex flex-col items-center justify-center py-6 opacity-40">
                                <Award className="w-8 h-8 mb-2" />
                                <p className="text-[10px]">No subjects found</p>
                            </div>
                        ) : (
                            <div className="space-y-4">
                                {allTopics.map((topic) => (
                                    <div key={topic.subject} className="flex flex-col gap-1.5">
                                        <div className="flex items-center justify-between">
                                            <span className="text-[11px] font-semibold text-foreground/80 tracking-wide truncate max-w-[120px]">
                                                {topic.subject}
                                            </span>
                                            <span className={`text-[11px] font-bold ${topic.is_weak ? "text-rose-500" : topic.average_score >= 80 ? "text-emerald-500" : "text-indigo-500"}`}>
                                                {topic.average_score}%
                                            </span>
                                        </div>
                                        <div className="h-1.5 w-full bg-black/5 dark:bg-white/10 rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full transition-all duration-1000 ease-out ${
                                                    topic.is_weak ? "bg-rose-500" : topic.average_score >= 80 ? "bg-emerald-500" : "bg-indigo-500"
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
