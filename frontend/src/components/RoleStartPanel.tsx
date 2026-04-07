"use client";

import Link from "next/link";
import { useMemo, useState } from "react";
import { CheckCircle2, Circle, HelpCircle, X } from "lucide-react";

type RoleKey = "admin" | "teacher" | "student" | "parent";

type ChecklistItem = {
    label: string;
    href: string;
};

type HelpItem = {
    title: string;
    detail: string;
};

const roleConfig: Record<RoleKey, { title: string; checklist: ChecklistItem[]; todayTasks: ChecklistItem[]; help: HelpItem[] }> = {
    admin: {
        title: "Admin first-run checklist",
        checklist: [
            { label: "Set up classes and subjects", href: "/admin/classes" },
            { label: "Import teachers and students", href: "/admin/users" },
            { label: "Review queue and AI health", href: "/admin/queue" },
        ],
        todayTasks: [
            { label: "Today’s tasks: resolve open complaints", href: "/admin/complaints" },
            { label: "Set up class timetable", href: "/admin/timetable" },
            { label: "Review AI usage", href: "/admin/ai-usage" },
        ],
        help: [
            { title: "Onboarding", detail: "Complete class, user, and timetable setup first so teacher workflows succeed." },
            { title: "AI reliability", detail: "If AI load is high, use queue controls and operations summary before contacting support." },
        ],
    },
    teacher: {
        title: "Teacher first-run checklist",
        checklist: [
            { label: "Confirm your assigned classes", href: "/teacher/classes" },
            { label: "Upload first learning material", href: "/teacher/upload" },
            { label: "Generate first assessment", href: "/teacher/generate-assessment" },
        ],
        todayTasks: [
            { label: "Today’s tasks: mark attendance", href: "/teacher/attendance" },
            { label: "Assign assessment", href: "/teacher/assignments" },
            { label: "Review class insights", href: "/teacher/insights" },
        ],
        help: [
            { title: "Assessment quality", detail: "Preview generated questions and rubric before assigning to students." },
            { title: "AI fallback", detail: "When queue is busy, start with concise prompts for faster turnaround." },
        ],
    },
    student: {
        title: "Student first-run checklist",
        checklist: [
            { label: "Check timetable and assignments", href: "/student/timetable" },
            { label: "Open the mascot study assistant", href: "/student/assistant" },
            { label: "Upload study material", href: "/student/upload" },
        ],
        todayTasks: [
            { label: "Today’s tasks: complete pending assignment", href: "/student/assignments" },
            { label: "Revise weak topics", href: "/student/reviews" },
            { label: "Continue in AI Studio", href: "/student/ai-studio" },
        ],
        help: [
            { title: "Study workflow", detail: "Start in the mascot assistant, then continue deeper practice in AI Studio." },
            { title: "If AI is delayed", detail: "Switch to brief responses or retry after queue estimate updates." },
        ],
    },
    parent: {
        title: "Parent first-run checklist",
        checklist: [
            { label: "Review attendance trend", href: "/parent/attendance" },
            { label: "Review latest results", href: "/parent/results" },
            { label: "Download report", href: "/parent/reports" },
        ],
        todayTasks: [
            { label: "Today’s tasks: check weekly attendance", href: "/parent/attendance" },
            { label: "Review results and action points", href: "/parent/results" },
            { label: "Open narrative report", href: "/parent/dashboard" },
        ],
        help: [
            { title: "Low attendance guidance", detail: "Contact class teacher when attendance drops below threshold for two weeks." },
            { title: "Performance follow-up", detail: "Use result trends to plan one weekly improvement action with your child." },
        ],
    },
};

export function RoleStartPanel({ role }: { role: RoleKey }) {
    const [showHelp, setShowHelp] = useState(false);
    const config = useMemo(() => roleConfig[role], [role]);

    return (
        <section className="glass-panel mb-6 rounded-[calc(var(--radius)*1.05)] p-4">
            <div className="flex items-start justify-between gap-4">
                <div>
                    <p className="text-xs font-bold uppercase tracking-[0.24em] text-[var(--text-muted)]">Getting started</p>
                    <h2 className="text-lg font-semibold text-[var(--text-primary)]">{config.title}</h2>
                </div>
                <button
                    onClick={() => setShowHelp((v) => !v)}
                    className="inline-flex items-center gap-1 rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-3 py-1 text-xs text-[var(--text-secondary)] hover:border-[var(--primary)]"
                >
                    {showHelp ? <X className="h-3.5 w-3.5" /> : <HelpCircle className="h-3.5 w-3.5" />} Help
                </button>
            </div>

            <div className="mt-3 grid gap-4 md:grid-cols-2">
                <div>
                    <p className="mb-2 text-xs font-semibold text-[var(--text-secondary)]">First-run checklist</p>
                    <ul className="space-y-2">
                        {config.checklist.map((item) => (
                            <li key={item.label}>
                                <Link href={item.href} className="inline-flex items-center gap-2 text-sm text-[var(--text-primary)] hover:text-[var(--primary)]">
                                    <Circle className="h-4 w-4" /> {item.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
                <div>
                    <p className="mb-2 text-xs font-semibold text-[var(--text-secondary)]">Task-first navigation</p>
                    <ul className="space-y-2">
                        {config.todayTasks.map((item) => (
                            <li key={item.label}>
                                <Link href={item.href} className="inline-flex items-center gap-2 text-sm text-[var(--text-primary)] hover:text-[var(--primary)]">
                                    <CheckCircle2 className="h-4 w-4 text-status-emerald" /> {item.label}
                                </Link>
                            </li>
                        ))}
                    </ul>
                </div>
            </div>

            {showHelp && (
                <div className="mt-4 rounded-xl border border-[var(--primary)]/20 bg-[rgba(148,163,184,0.06)] p-3">
                    <p className="mb-2 text-xs font-semibold text-[var(--text-secondary)]">Quick help overlays</p>
                    <div className="space-y-2">
                        {config.help.map((h) => (
                            <div key={h.title}>
                                <p className="text-sm font-medium text-[var(--text-primary)]">{h.title}</p>
                                <p className="text-xs text-[var(--text-muted)]">{h.detail}</p>
                            </div>
                        ))}
                    </div>
                </div>
            )}
        </section>
    );
}
