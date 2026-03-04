"use client";

import { useEffect, useMemo, useState } from "react";
import { FileText, Bot } from "lucide-react";

import { api } from "@/lib/api";

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

export default function TeacherDashboard() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [assignments, setAssignments] = useState<TeacherAssignment[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const [dashboardData, assignmentData] = await Promise.all([
                    api.teacher.dashboard(),
                    api.teacher.assignments(),
                ]);
                setClasses((dashboardData?.classes || []) as TeacherClass[]);
                setAssignments((assignmentData || []) as TeacherAssignment[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            } finally {
                setLoading(false);
            }
        };

        void load();
    }, []);

    const weakestClass = useMemo(() => {
        if (classes.length === 0) {
            return null;
        }
        return [...classes].sort((a, b) => a.avg_marks - b.avg_marks)[0];
    }, [classes]);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Teacher Dashboard</h1>
                <p className="text-sm text-[var(--text-secondary)]">Overview of your classes and students</p>
            </div>

            {error ? (
                <div className="mb-6 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="text-sm text-[var(--text-muted)]">Loading dashboard...</div>
            ) : (
                <>
                    <div className="grid md:grid-cols-2 gap-4 mb-6">
                        {classes.map((cls) => (
                            <div key={cls.id} className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                                <div className="flex items-center justify-between mb-4">
                                    <h3 className="text-base font-semibold text-[var(--text-primary)]">{cls.name}</h3>
                                    <span className="text-xs text-[var(--text-muted)]">{cls.students} students</span>
                                </div>
                                <div className="grid grid-cols-2 gap-4">
                                    <div>
                                        <p className="text-xs text-[var(--text-muted)] mb-1">Avg Attendance</p>
                                        <p className="text-lg font-bold" style={{ color: cls.avg_attendance >= 80 ? "var(--success)" : "var(--error)" }}>
                                            {cls.avg_attendance}%
                                        </p>
                                    </div>
                                    <div>
                                        <p className="text-xs text-[var(--text-muted)] mb-1">Avg Marks</p>
                                        <p className="text-lg font-bold" style={{ color: cls.avg_marks >= 70 ? "var(--success)" : "var(--warning)" }}>
                                            {cls.avg_marks}%
                                        </p>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>

                    <div className="grid lg:grid-cols-2 gap-6">
                        <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center gap-2 mb-4">
                                <FileText className="w-4 h-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Recent Assignments</h2>
                            </div>
                            <div className="space-y-3">
                                {assignments.slice(0, 5).map((item) => (
                                    <div key={item.id} className="flex items-center justify-between p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]">
                                        <div>
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{item.title}</p>
                                            <p className="text-xs text-[var(--text-muted)]">{item.subject}</p>
                                        </div>
                                        <span className="text-xs text-[var(--text-muted)]">{item.submissions} submissions</span>
                                    </div>
                                ))}
                                {assignments.length === 0 ? (
                                    <p className="text-sm text-[var(--text-muted)]">No assignments yet.</p>
                                ) : null}
                            </div>
                        </div>

                        <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center gap-2 mb-4">
                                <Bot className="w-4 h-4 text-[var(--primary)]" />
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">AI Class Analytics</h2>
                            </div>
                            <div className="p-4 bg-[var(--primary-light)] rounded-[var(--radius-sm)]">
                                <p className="text-sm text-[var(--text-primary)] leading-relaxed">
                                    {weakestClass
                                        ? `Lowest-performing class right now is ${weakestClass.name} at ${weakestClass.avg_marks}% average marks.`
                                        : "No class performance data available yet."}
                                </p>
                            </div>
                            <button className="mt-4 w-full py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors">
                                Generate Class Study Guide
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
