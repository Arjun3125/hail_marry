"use client";

import { useEffect, useState } from "react";
import { BookOpenCheck, CheckCircle2, ChevronRight, GraduationCap, Sparkles, UploadCloud } from "lucide-react";
import Link from "next/link";
import { usePathname } from "next/navigation";

const CHECKLIST = [
    { id: "profile-ready", label: "Your profile is ready", route: "/student/profile", fixedDone: true, icon: GraduationCap },
    { id: "upload-material", label: "Upload your first study material", route: "/student/upload", icon: UploadCloud },
    { id: "ask-ai", label: "Ask your AI assistant one question", route: "/student/ai-studio", icon: Sparkles },
    { id: "read-timetable", label: "Check your timetable", route: "/student/timetable", icon: BookOpenCheck },
];

export function OnboardingGate({ children }: { children: React.ReactNode }) {
    const [mounted, setMounted] = useState(false);
    const [doneTasks, setDoneTasks] = useState<Record<string, boolean>>({});
    const pathname = usePathname();

    useEffect(() => {
        // eslint-disable-next-line react-hooks/set-state-in-effect
        setMounted(true);
        try {
            const raw = localStorage.getItem("student-onboarding");
            if (raw) {
                setDoneTasks(JSON.parse(raw));
            }
        } catch (e) {
            console.error(e);
        }
    }, []);

    // Auto-complete based on navigation
    useEffect(() => {
        if (!mounted) return;
        let changed = false;
        const newTasks = { ...doneTasks };

        CHECKLIST.forEach((task) => {
            if ((task.fixedDone || pathname === task.route) && !newTasks[task.id]) {
                newTasks[task.id] = true;
                changed = true;
            }
        });

        if (changed) {
            // eslint-disable-next-line react-hooks/set-state-in-effect
            setDoneTasks(newTasks);
            localStorage.setItem("student-onboarding", JSON.stringify(newTasks));
        }
    }, [pathname, mounted, doneTasks]);

    if (!mounted) return null; // Avoid hydration mismatch

    const tasksCompleted = CHECKLIST.filter(t => doneTasks[t.id]).length;
    const isComplete = tasksCompleted === CHECKLIST.length;

    // If complete or currently doing a checklist task route, show the app
    const isDoingTask = CHECKLIST.some(t => t.route === pathname);
    
    if (isComplete || isDoingTask) {
        return <>{children}</>;
    }

    return (
        <div className="fixed inset-0 z-[100] flex items-center justify-center bg-[var(--bg-page)] p-6">
            <div className="w-full max-w-xl rounded-[var(--radius-lg)] border border-[var(--border)] bg-[var(--bg-card)] p-8 shadow-2xl">
                <div className="mb-6 flex items-center gap-3">
                    <div className="flex h-12 w-12 items-center justify-center rounded-2xl" style={{ background: "linear-gradient(135deg, var(--role-student), rgba(255,255,255,0.92))" }}>
                        <GraduationCap className="h-6 w-6 text-[#06101e]" />
                    </div>
                    <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Student first run</p>
                        <p className="text-sm font-semibold text-[var(--text-primary)]">{tasksCompleted} / {CHECKLIST.length} complete</p>
                    </div>
                </div>
                
                <h1 className="mb-2 text-2xl font-bold text-[var(--text-primary)]">Welcome to VidyaOS.</h1>
                <p className="mb-8 text-sm leading-6 text-[var(--text-secondary)]">
                    Let&apos;s set up your study space in 3 minutes. The full dashboard opens after these first actions so your workspace starts with useful context.
                </p>

                <div className="mb-4 flex items-center justify-between text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">
                    <span>Task checklist</span>
                    <span>{tasksCompleted} / {CHECKLIST.length} done</span>
                </div>

                <div className="space-y-3">
                    {CHECKLIST.map((task) => {
                        const Icon = task.icon;
                        return (
                        <Link 
                            key={task.id} 
                            href={task.route}
                            className={`flex items-center justify-between rounded-xl border p-4 transition-all ${
                                doneTasks[task.id] 
                                ? "border-success-subtle bg-success-subtle/30" 
                                : "border-[var(--border)] bg-[rgba(255,255,255,0.02)] hover:border-[var(--role-student)]"
                            }`}
                        >
                            <div className="flex items-center gap-3">
                                {doneTasks[task.id] ? (
                                    <CheckCircle2 className="h-5 w-5 text-status-emerald" />
                                ) : (
                                    <Icon className="h-5 w-5 text-[var(--text-muted)]" />
                                )}
                                <span className={`text-sm font-medium ${doneTasks[task.id] ? "text-[var(--text-muted)] line-through" : "text-[var(--text-primary)]"}`}>
                                    {task.label}
                                </span>
                            </div>
                            {!doneTasks[task.id] && <ChevronRight className="h-4 w-4 text-[var(--text-muted)]" />}
                        </Link>
                        );
                    })}
                </div>
                
                <p className="mt-8 text-center text-xs text-[var(--text-muted)]">Click a task to continue. Dashboard access stays gated until setup is complete.</p>
            </div>
        </div>
    );
}
