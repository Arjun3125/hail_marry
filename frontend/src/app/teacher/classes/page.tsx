"use client";

import { useEffect, useState } from "react";
import { Users, BookOpen, CheckSquare, BarChart3 } from "lucide-react";

import { api } from "@/lib/api";

type TeacherClass = {
    id: string;
    name: string;
    grade: string;
    students: Array<{ id: string; name: string; email: string; roll_number: string | null }>;
    subjects: Array<{ id: string; name: string }>;
};

export default function TeacherClassesPage() {
    const [classes, setClasses] = useState<TeacherClass[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.classes();
                setClasses((payload || []) as TeacherClass[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load classes");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">My Classes</h1>
                <p className="text-sm text-[var(--text-secondary)]">Manage your classes and view student details</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            <div className="grid md:grid-cols-2 gap-4">
                {loading ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        Loading classes...
                    </div>
                ) : classes.length === 0 ? (
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5 text-sm text-[var(--text-muted)]">
                        No classes assigned.
                    </div>
                ) : classes.map((cls) => (
                    <div key={cls.id} className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="text-lg font-semibold text-[var(--text-primary)]">{cls.name}</h3>
                            <span className="flex items-center gap-1 text-sm text-[var(--text-secondary)]">
                                <Users className="w-4 h-4" /> {cls.students.length}
                            </span>
                        </div>
                        <div className="flex flex-wrap gap-2">
                            {cls.subjects.map((subject) => (
                                <span key={subject.id} className="text-xs bg-[var(--primary-light)] text-[var(--primary)] px-2.5 py-1 rounded-full font-medium">
                                    {subject.name}
                                </span>
                            ))}
                        </div>
                        <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">
                            <div className="text-center p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                <CheckSquare className="w-4 h-4 mx-auto text-[var(--success)] mb-1" />
                                <p className="text-[10px] text-[var(--text-muted)]">Attendance</p>
                            </div>
                            <div className="text-center p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                <BookOpen className="w-4 h-4 mx-auto text-[var(--primary)] mb-1" />
                                <p className="text-[10px] text-[var(--text-muted)]">Marks</p>
                            </div>
                            <div className="text-center p-2 bg-[var(--bg-page)] rounded-[var(--radius-sm)]">
                                <BarChart3 className="w-4 h-4 mx-auto text-[var(--warning)] mb-1" />
                                <p className="text-[10px] text-[var(--text-muted)]">Insights</p>
                            </div>
                        </div>
                    </div>
                ))}
            </div>
        </div>
    );
}
