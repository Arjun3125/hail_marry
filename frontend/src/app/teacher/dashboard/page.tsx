"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Bot, TrendingUp, Users, CalendarCheck, ClipboardCheck, LayoutDashboard, Sparkles, AlertCircle, ArrowRight } from "lucide-react";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    CartesianGrid,
} from "recharts";

import { api } from "@/lib/api";
import { AnimatedCounter, ProgressRing } from "@/components/ui/SharedUI";
import { RoleStartPanel } from "@/components/RoleStartPanel";

type TeacherClass = {
    id: string;
    name: string;
    students: number;
    avg_attendance: number;
    avg_marks: number;
};

type TodayClass = {
    class_id: string;
    class_name: string;
    subject: string;
    start_time: string;
    end_time: string;
};

export default function TeacherDashboard() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [todayClasses, setTodayClasses] = useState<TodayClass[]>([]);
    const [pendingReviews, setPendingReviews] = useState(0);
    const [openAssignments, setOpenAssignments] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [chartsReady, setChartsReady] = useState(false);

    const load = useCallback(async () => {
        try {
            setLoading(true);
            setError(null);
            const dashboardData = await api.teacher.dashboard();
            setClasses((dashboardData?.classes || []) as TeacherClass[]);
            setTodayClasses((dashboardData?.today_classes || []) as TodayClass[]);
            setPendingReviews(Number(dashboardData?.pending_reviews || 0));
            setOpenAssignments(Number(dashboardData?.open_assignments || 0));
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
        setChartsReady(true);
    }, [load]);

    const weakestClass = useMemo(() => {
        if (classes.length === 0) return null;
        return [...classes].sort((a, b) => a.avg_marks - b.avg_marks)[0];
    }, [classes]);

    const chartData = useMemo(
        () =>
            classes.map((c) => ({
                name: c.name.length > 10 ? c.name.slice(0, 10) + "…" : c.name,
                attendance: c.avg_attendance,
                marks: c.avg_marks,
            })),
        [classes],
    );

    return (
        <div className="max-w-6xl mx-auto space-y-8">
            <RoleStartPanel role="teacher" />

            {error && (
                <div className="rounded-xl border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] shadow-lg animate-in fade-in">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 animate-pulse">
                    {Array.from({ length: 6 }).map((_, i) => (
                        <div key={i} className="h-48 bg-[var(--bg-card)] rounded-2xl" />
                    ))}
                </div>
            ) : (
                <>
                    {/* ─── Command Center Hero ─── */}
                    <div className="relative overflow-hidden rounded-3xl glass-panel border border-[var(--border-light)] shadow-2xl isolate stagger-1 flex flex-col lg:flex-row gap-8">
                        {/* Interactive Gradients */}
                        <div className="absolute inset-0 bg-gradient-to-r from-blue-600/10 via-indigo-500/5 to-purple-600/10 z-[-1]" />
                        <div className="absolute top-1/2 left-0 w-72 h-72 bg-blue-500/20 blur-[120px] rounded-full -translate-y-1/2 -ml-10 z-[-1]" />
                        
                        <div className="p-8 lg:w-1/2 flex flex-col justify-center">
                            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-blue-500/10 border border-blue-500/20 text-[10px] uppercase tracking-widest font-bold text-blue-500 mb-4 w-fit">
                                <LayoutDashboard className="w-3 h-3" />
                                Educator Console
                            </div>
                            <h1 className="text-4xl font-black text-[var(--text-primary)] tracking-tight leading-tight mb-2">
                                Welcome back to class
                            </h1>
                            <p className="text-sm text-[var(--text-muted)] mb-6 max-w-sm">
                                You have {todayClasses.length} sessions scheduled for today and {pendingReviews} submissions awaiting your review.
                            </p>
                            
                            <div className="flex gap-4">
                                <a
                                    href={todayClasses[0] ? `/teacher/attendance?classId=${todayClasses[0].class_id}` : "/teacher/attendance"}
                                    className="group relative inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-bold rounded-xl text-white overflow-hidden shadow-lg transition-transform hover:scale-105"
                                >
                                    <div className="absolute inset-0 bg-gradient-to-r from-blue-600 to-indigo-600 transition-opacity group-hover:opacity-90" />
                                    <span className="relative flex items-center gap-2"><ClipboardCheck className="w-4 h-4" /> Start Roll Call</span>
                                </a>
                                <a
                                    href="/teacher/generate-assessment"
                                    className="inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-bold rounded-xl bg-[var(--bg-page)] text-[var(--text-primary)] border border-[var(--border-light)] hover:bg-[var(--border-light)] transition-colors shadow-sm"
                                >
                                    <Sparkles className="w-4 h-4 text-purple-500" /> Auto-Assess
                                </a>
                            </div>
                        </div>

                        {/* Schedule Quick View */}
                        <div className="lg:w-1/2 p-8 border-t lg:border-t-0 lg:border-l border-[var(--border-light)] bg-gradient-to-br from-[var(--bg-card)]/50 to-transparent backdrop-blur-sm relative">
                            <div className="flex items-center justify-between mb-6">
                                <h2 className="text-sm font-bold text-[var(--text-primary)] flex items-center gap-2">
                                    <CalendarCheck className="w-4 h-4 text-blue-500" />
                                    Up Next
                                </h2>
                                <span className="text-[10px] uppercase font-bold tracking-wider text-[var(--text-muted)]">Today</span>
                            </div>
                            
                            {todayClasses.length ? (
                                <div className="space-y-3 px-2">
                                    {todayClasses.slice(0, 3).map((slot, idx) => (
                                        <div key={`${slot.class_id}-${idx}`} className="flex items-center gap-4 group p-3 rounded-xl hover:bg-blue-500/5 transition-colors border border-transparent hover:border-blue-500/10">
                                            <div className="flex flex-col items-center justify-center px-4 py-2 bg-blue-500/10 rounded-lg shrink-0">
                                                <span className="text-xs font-black text-blue-500">{slot.start_time.split(':')[0]}:{slot.start_time.split(':')[1]}</span>
                                            </div>
                                            <div className="flex-1">
                                                <h3 className="text-sm font-bold text-[var(--text-primary)]">{slot.class_name}</h3>
                                                <p className="text-xs text-[var(--text-muted)]">{slot.subject}</p>
                                            </div>
                                            <ArrowRight className="w-4 h-4 text-blue-500 opacity-0 group-hover:opacity-100 transition-all transform -translate-x-2 group-hover:translate-x-0" />
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-10 text-center opacity-60">
                                    <CalendarCheck className="w-10 h-10 text-[var(--text-muted)] mb-3" />
                                    <p className="text-sm font-semibold text-[var(--text-muted)]">Your schedule is clear</p>
                                </div>
                            )}
                        </div>
                    </div>

                    {/* ─── Operational Metrics ─── */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 stagger-2">
                        {/* Needs Grading */}
                        <div className="bg-[var(--bg-card)]/80 backdrop-blur-md rounded-2xl p-6 shadow-[var(--shadow-card)] border border-[var(--border-light)] card-hover flex items-center justify-between">
                            <div>
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest mb-1 flex items-center gap-1.5">
                                    <AlertCircle className="w-3 h-3 text-rose-500" /> Action Required
                                </p>
                                <h3 className="text-lg font-bold text-[var(--text-primary)]">Pending Reviews</h3>
                            </div>
                            <div className="flex items-end gap-2">
                                <span className={`text-4xl font-black ${pendingReviews > 5 ? "text-rose-500" : "text-[var(--text-primary)]"}`}>
                                    {pendingReviews}
                                </span>
                                <span className="text-sm text-[var(--text-muted)] mb-1">items</span>
                            </div>
                        </div>

                        {/* Active Assignments */}
                        <div className="bg-[var(--bg-card)]/80 backdrop-blur-md rounded-2xl p-6 shadow-[var(--shadow-card)] border border-[var(--border-light)] card-hover flex items-center justify-between">
                            <div>
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-widest mb-1 flex items-center gap-1.5">
                                    <Users className="w-3 h-3 text-emerald-500" /> Ongoing
                                </p>
                                <h3 className="text-lg font-bold text-[var(--text-primary)]">Open Assignments</h3>
                            </div>
                            <div className="flex items-end gap-2">
                                <span className="text-4xl font-black text-[var(--text-primary)]">
                                    {openAssignments}
                                </span>
                                <span className="text-sm text-[var(--text-muted)] mb-1">active</span>
                            </div>
                        </div>
                    </div>

                    {/* ─── Class Performance Grid ─── */}
                    <div className="space-y-4 stagger-3">
                        <h2 className="text-sm font-bold text-[var(--text-muted)] uppercase tracking-widest px-1">Your Classes</h2>
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                            {classes.map((cls, i) => {
                                const colors = [
                                    "from-blue-500 to-cyan-500", 
                                    "from-purple-500 to-pink-500", 
                                    "from-emerald-500 to-teal-500", 
                                    "from-amber-500 to-orange-500"
                                ];
                                const colorGrad = colors[i % colors.length];
                                
                                return (
                                    <div key={cls.id} className="relative bg-[var(--bg-card)] rounded-2xl p-6 shadow-[var(--shadow-card)] border border-[var(--border-light)] overflow-hidden group hover:-translate-y-1 transition-transform duration-300">
                                        <div className={`absolute top-0 left-0 w-full h-1 bg-gradient-to-r ${colorGrad}`} />
                                        
                                        <div className="flex items-start justify-between mb-6">
                                            <div>
                                                <h3 className="text-lg font-black text-[var(--text-primary)] tracking-tight">{cls.name}</h3>
                                                <span className="flex items-center gap-1.5 text-xs font-semibold text-[var(--text-muted)] mt-1">
                                                    <Users className="w-3.5 h-3.5 opacity-60" /> {cls.students} Enrolled
                                                </span>
                                            </div>
                                            <div className={`w-8 h-8 rounded-full bg-gradient-to-r ${colorGrad} opacity-10 group-hover:opacity-20 transition-opacity`} />
                                        </div>

                                        <div className="grid grid-cols-2 gap-4">
                                            <div className="bg-[var(--bg-page)] rounded-xl p-3 flex flex-col items-center text-center">
                                                <ProgressRing
                                                    value={cls.avg_attendance}
                                                    size={48}
                                                    strokeWidth={4}
                                                    color={cls.avg_attendance >= 80 ? "var(--success)" : "var(--error)"}
                                                >
                                                    <span className="text-[10px] font-bold">{cls.avg_attendance}%</span>
                                                </ProgressRing>
                                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider mt-2">Attendance</p>
                                            </div>
                                            <div className="bg-[var(--bg-page)] rounded-xl p-3 flex flex-col items-center justify-center text-center">
                                                <span className={`text-2xl font-black ${cls.avg_marks >= 70 ? "text-emerald-500" : "text-amber-500"}`}>
                                                    <AnimatedCounter value={cls.avg_marks} suffix="%" />
                                                </span>
                                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider mt-2">Avg Score</p>
                                            </div>
                                        </div>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* ─── AI Insights & Analytics ─── */}
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 stagger-4">
                        {/* Multi-class Chart */}
                        {chartData.length > 0 && (
                            <div className="lg:col-span-2 bg-[var(--bg-card)] rounded-2xl p-6 shadow-[var(--shadow-card)] border border-[var(--border-light)] glass-panel">
                                <h2 className="text-sm font-bold text-[var(--text-primary)] flex items-center gap-2 mb-6">
                                    <TrendingUp className="w-4 h-4 text-blue-500" />
                                    Performance Matrix
                                </h2>
                                <div className="h-56">
                                    {chartsReady ? (
                                        <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={160}>
                                        <BarChart data={chartData} margin={{ top: 0, right: 0, left: -20, bottom: 0 }}>
                                            <defs>
                                                <linearGradient id="barAtt" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stopColor="#3b82f6" stopOpacity={1} />
                                                    <stop offset="100%" stopColor="#3b82f6" stopOpacity={0.6} />
                                                </linearGradient>
                                                <linearGradient id="barMark" x1="0" y1="0" x2="0" y2="1">
                                                    <stop offset="0%" stopColor="#8b5cf6" stopOpacity={1} />
                                                    <stop offset="100%" stopColor="#8b5cf6" stopOpacity={0.6} />
                                                </linearGradient>
                                            </defs>
                                            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="var(--border-light)" />
                                            <XAxis dataKey="name" tickLine={false} axisLine={false} tick={{ fontSize: 11, fill: "var(--text-muted)", fontWeight: 600 }} dy={10} />
                                            <YAxis tickLine={false} axisLine={false} domain={[0, 100]} tick={{ fontSize: 11, fill: "var(--text-muted)" }} />
                                            <Tooltip
                                                cursor={{ fill: 'var(--bg-page)', opacity: 0.4 }}
                                                contentStyle={{ background: "rgba(var(--bg-card-rgb), 0.9)", backdropFilter: "blur(8px)", border: "1px solid var(--border-light)", borderRadius: 12, boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)", fontSize: 12 }}
                                                itemStyle={{ fontWeight: 700 }}
                                                labelStyle={{ color: "var(--text-primary)", fontWeight: 800, marginBottom: 8 }}
                                            />
                                            <Bar dataKey="attendance" name="Attendance" fill="url(#barAtt)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                                            <Bar dataKey="marks" name="Average Marks" fill="url(#barMark)" radius={[4, 4, 0, 0]} maxBarSize={40} />
                                        </BarChart>
                                        </ResponsiveContainer>
                                    ) : (
                                        <div className="h-full rounded-2xl bg-[var(--bg-page)] animate-pulse" />
                                    )}
                                </div>
                            </div>
                        )}

                        {/* AI Summary */}
                        <div className="bg-[var(--bg-card)] rounded-2xl p-6 shadow-[var(--shadow-card)] border border-[var(--border-light)] glass-panel flex flex-col">
                            <div className="flex items-center gap-2 mb-4">
                                <span className="flex items-center justify-center w-8 h-8 rounded-full bg-purple-500/10 shrink-0">
                                    <Bot className="w-4 h-4 text-purple-500" />
                                </span>
                                <h2 className="text-sm font-bold text-[var(--text-primary)]">Copilot Insights</h2>
                            </div>
                            
                            <div className="flex-1 bg-gradient-to-br from-[var(--bg-page)] to-transparent rounded-xl p-4 border border-[var(--border-light)] relative overflow-hidden">
                                <div className="absolute -right-4 -top-4 w-16 h-16 bg-purple-500/10 rounded-full blur-xl pointer-events-none" />
                                <p className="text-sm text-[var(--text-primary)] leading-relaxed font-medium relative z-10">
                                    {weakestClass ? (
                                        <>
                                            Your class <span className="text-purple-500 font-bold">{weakestClass.name}</span> has the lowest overall performance right now at <strong>{weakestClass.avg_marks}%</strong>. Consider deploying a targeted revision assessment.
                                        </>
                                    ) : (
                                        "Synthesizing your classroom metadata to find actionable coaching opportunities..."
                                    )}
                                </p>
                            </div>
                            
                            <button className="mt-4 w-full py-3 bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-primary)] text-xs font-bold rounded-xl hover:bg-[var(--border-light)] transition-colors shadow-sm flex items-center justify-center gap-2 group">
                                <Sparkles className="w-3.5 h-3.5 text-purple-500 group-hover:animate-spin" />
                                Generate Study Guide
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
