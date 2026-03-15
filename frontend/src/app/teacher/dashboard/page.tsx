"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { FileText, Bot, TrendingUp, Users, CalendarCheck, ClipboardCheck } from "lucide-react";
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
import { SkeletonCard } from "@/components/Skeleton";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { AnimatedCounter, ProgressRing } from "@/components/ui/SharedUI";
import { RoleStartPanel } from "@/components/RoleStartPanel";

type TeacherClass = {
    id: string;
    name: string;
    students: number;
    avg_attendance: number;
    avg_marks: number;
};

type TeacherAssignment = {
    id: string;
    title: string;
    subject: string;
    due_date: string | null;
    submissions: number;
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
    const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
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
            const [dashboardData, assignmentData] = await Promise.all([
                api.teacher.dashboard(),
                api.teacher.assignments(),
            ]);
            setClasses((dashboardData?.classes || []) as TeacherClass[]);
            setTodayClasses((dashboardData?.today_classes || []) as TodayClass[]);
            setPendingReviews(Number(dashboardData?.pending_reviews || 0));
            setOpenAssignments(Number(dashboardData?.open_assignments || 0));
            setAssignments((assignmentData || []) as TeacherAssignment[]);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load dashboard");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

    useEffect(() => {
        setChartsReady(true);
    }, []);

    const weakestClass = useMemo(() => {
        if (classes.length === 0) return null;
        return [...classes].sort((a, b) => a.avg_marks - b.avg_marks)[0];
    }, [classes]);

    // Chart data from classes
    const chartData = useMemo(
        () =>
            classes.map((c) => ({
                name: c.name.length > 10 ? c.name.slice(0, 10) + "â€¦" : c.name,
                attendance: c.avg_attendance,
                marks: c.avg_marks,
            })),
        [classes],
    );
    const onboardingChecklist = [
        { id: "today-classes", label: "Review today's classes" },
        { id: "attendance", label: "Mark attendance for first class" },
        { id: "assignment", label: "Create or review one assignment" },
    ];

    const taskFirstLinks = [
        { label: "Mark attendance", href: todayClasses[0] ? `/teacher/attendance?classId=${todayClasses[0].class_id}` : "/teacher/attendance", priority: "high" as const },
        { label: "Assign assessment", href: "/teacher/generate-assessment", priority: "medium" as const },
        { label: "Review class insights", href: "/teacher/insights", priority: "low" as const },
    ];


    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Teacher Dashboard</h1>
                <p className="text-sm text-[var(--text-secondary)]">Overview of your classes and students</p>
            </div>

            <RoleStartPanel role="teacher" />

            {error && (
                <div className="mb-6 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="grid md:grid-cols-2 gap-4 mb-6">
                    {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
                </div>
            ) : (
                <>
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 mb-6">
                        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                            <div>
                                <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-2">Today&apos;s Classes</p>
                                {todayClasses.length ? (
                                    <div className="space-y-1 text-sm text-[var(--text-secondary)]">
                                        {todayClasses.slice(0, 3).map((slot) => (
                                            <div key={`${slot.class_id}-${slot.start_time}`} className="flex items-center gap-2">
                                                <CalendarCheck className="w-4 h-4 text-status-blue" />
                                                <span className="font-medium text-[var(--text-primary)]">{slot.class_name}</span>
                                                <span className="text-xs text-[var(--text-muted)]">
                                                    {slot.subject} â€¢ {slot.start_time}-{slot.end_time}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                ) : (
                                    <p className="text-sm text-[var(--text-muted)]">No classes scheduled today.</p>
                                )}
                            </div>
                            <a
                                href={todayClasses[0] ? `/teacher/attendance?classId=${todayClasses[0].class_id}` : "/teacher/attendance"}
                                className="inline-flex items-center justify-center gap-2 px-4 py-2 text-sm font-semibold rounded-[var(--radius-sm)] bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)] shadow-sm"
                            >
                                <ClipboardCheck className="w-4 h-4" /> Mark Attendance
                            </a>
                        </div>
                        <div className="mt-4 grid gap-3 sm:grid-cols-2">
                            <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-3">
                                <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Pending Reviews</p>
                                <p className="text-lg font-bold text-[var(--text-primary)]">{pendingReviews}</p>
                                <p className="text-xs text-[var(--text-muted)]">Submissions to grade</p>
                            </div>
                            <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-3">
                                <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Open Assignments</p>
                                <p className="text-lg font-bold text-[var(--text-primary)]">{openAssignments}</p>
                                <p className="text-xs text-[var(--text-muted)]">Active assignments</p>
                            </div>
                        </div>
                    </div>

                    {/* â”€â”€â”€ Glass Class Cards â”€â”€â”€ */}
                    <div className="grid md:grid-cols-2 gap-4 mb-6">
                        {classes.map((cls, i) => {
                            const colors = ["glass-stat-blue", "glass-stat-green", "glass-stat-purple", "glass-stat-amber"];
                            return (
                                <div key={cls.id} className={`glass-stat ${colors[i % colors.length]} stagger-${Math.min(i + 1, 6)}`}>
                                    <div className="flex items-center justify-between mb-4">
                                        <h3 className="text-sm font-bold text-[var(--text-primary)]">{cls.name}</h3>
                                        <span className="flex items-center gap-1 text-xs text-[var(--text-muted)]">
                                            <Users className="w-3 h-3" />
                                            {cls.students}
                                        </span>
                                    </div>
                                    <div className="grid grid-cols-2 gap-4">
                                        <div className="flex items-center gap-3">
                                            <ProgressRing
                                                value={cls.avg_attendance}
                                                size={44}
                                                strokeWidth={4}
                                                color={cls.avg_attendance >= 80 ? "var(--success)" : "var(--error)"}
                                            >
                                                <span className="text-[8px] font-bold">{cls.avg_attendance}%</span>
                                            </ProgressRing>
                                            <div>
                                                <p className="text-[10px] text-[var(--text-muted)] uppercase">Attendance</p>
                                                <p className="text-lg font-bold" style={{ color: cls.avg_attendance >= 80 ? "var(--success)" : "var(--error)" }}>
                                                    <AnimatedCounter value={cls.avg_attendance} suffix="%" />
                                                </p>
                                            </div>
                                        </div>
                                        <div>
                                            <p className="text-[10px] text-[var(--text-muted)] uppercase">Avg Marks</p>
                                            <p className="text-lg font-bold" style={{ color: cls.avg_marks >= 70 ? "var(--success)" : "var(--warning)" }}>
                                                <AnimatedCounter value={cls.avg_marks} suffix="%" />
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* â”€â”€â”€ Chart Row â”€â”€â”€ */}
                    {chartData.length > 0 && (
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] mb-6 card-hover">
                            <h2 className="text-sm font-semibold text-[var(--text-primary)] mb-4">ðŸ“Š Class Comparison</h2>
                            <div className="h-48">
                                {chartsReady ? (
                                    <ResponsiveContainer width="100%" height="100%" minWidth={0} minHeight={160}>
                                    <BarChart data={chartData}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="var(--border-light)" />
                                        <XAxis dataKey="name" tick={{ fontSize: 10, fill: "var(--text-muted)" }} />
                                        <YAxis domain={[0, 100]} tick={{ fontSize: 10, fill: "var(--text-muted)" }} />
                                        <Tooltip
                                            contentStyle={{ background: "var(--bg-card)", border: "1px solid var(--border)", borderRadius: 8, fontSize: 12 }}
                                            labelStyle={{ color: "var(--text-primary)", fontWeight: 600 }}
                                        />
                                        <Bar dataKey="attendance" name="Attendance %" fill="#22c55e" radius={[3, 3, 0, 0]} />
                                        <Bar dataKey="marks" name="Avg Marks %" fill="#3b82f6" radius={[3, 3, 0, 0]} />
                                    </BarChart>
                                    </ResponsiveContainer>
                                ) : (
                                    <div className="h-full rounded-[var(--radius-sm)] bg-[var(--bg-page)]" />
                                )}
                            </div>
                        </div>
                    )}

                    {/* â”€â”€â”€ Bottom Row â”€â”€â”€ */}
                    <div className="grid lg:grid-cols-2 gap-6">
                        {/* Recent Assignments */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center gap-2 mb-4">
                                <FileText className="w-4 h-4 text-[var(--primary)]" />
                                <h2 className="text-sm font-semibold text-[var(--text-primary)]">Recent Assignments</h2>
                            </div>
                            <div className="space-y-2">
                                {assignments.slice(0, 5).map((item) => (
                                    <div key={item.id} className="flex items-center justify-between p-3 rounded-lg bg-[var(--bg-page)] card-hover">
                                        <div>
                                            <p className="text-xs font-medium text-[var(--text-primary)]">{item.title}</p>
                                            <p className="text-[10px] text-[var(--text-muted)]">{item.subject}</p>
                                        </div>
                                        <span className="text-[10px] px-2 py-0.5 rounded-full bg-info-badge dark:bg-blue-900/20 text-status-blue dark:text-blue-400 font-medium">
                                            {item.submissions} submitted
                                        </span>
                                    </div>
                                ))}
                                {assignments.length === 0 && (
                                    <div className="py-6 text-center">
                                        <FileText className="w-8 h-8 mx-auto text-[var(--text-muted)] mb-2 opacity-30" />
                                        <p className="text-xs text-[var(--text-muted)]">No assignments yet.</p>
                                    </div>
                                )}
                            </div>
                        </div>

                        {/* AI Class Analytics */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] gradient-border">
                            <div className="flex items-center gap-2 mb-4">
                                <Bot className="w-4 h-4 text-[var(--accent-purple)]" />
                                <h2 className="text-sm font-semibold text-[var(--text-primary)]">AI Class Analytics</h2>
                            </div>
                            <div className="p-4 bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/10 dark:to-indigo-900/10 rounded-lg">
                                <p className="text-xs text-[var(--text-primary)] leading-relaxed">
                                    {weakestClass ? (
                                        <>
                                            <TrendingUp className="w-3 h-3 inline mr-1 text-[var(--accent-purple)]" />
                                            Lowest-performing class: <strong>{weakestClass.name}</strong> at {weakestClass.avg_marks}% average marks.
                                        </>
                                    ) : "No class performance data available yet."}
                                </p>
                            </div>
                            <button className="mt-4 w-full py-2.5 bg-gradient-to-r from-indigo-500 to-purple-500 text-white text-xs font-medium rounded-lg hover:from-indigo-600 hover:to-purple-600 transition-all shadow-md hover:shadow-lg">
                                âœ¨ Generate Class Study Guide
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
