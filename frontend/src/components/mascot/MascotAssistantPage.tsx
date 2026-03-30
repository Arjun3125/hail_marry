"use client";

import { Bot, Compass, GraduationCap, ShieldCheck, Sparkles, Users } from "lucide-react";

import { MascotLauncher } from "./MascotLauncher";

const ROLE_CONTENT: Record<
    string,
    {
        eyebrow: string;
        title: string;
        description: string;
        highlights: string[];
        icon: typeof GraduationCap;
    }
> = {
    student: {
        eyebrow: "Student Copilot",
        title: "Plan, learn, and build study outputs from one place.",
        description: "Use natural language to create notebooks, ingest material, and generate grounded study tools without hopping across pages.",
        highlights: ["Create notebooks", "Generate flashcards and quizzes", "Open AI Studio with the right notebook"],
        icon: GraduationCap,
    },
    teacher: {
        eyebrow: "Teacher Operator",
        title: "Run class workflows, imports, and assessments through conversation.",
        description: "The mascot can summarize class signals, prepare assessments, and guide roster, attendance, and marks workflows with the right page context.",
        highlights: ["Import attendance and marks", "Generate grounded assessments", "Review class insights and weak topics"],
        icon: Users,
    },
    admin: {
        eyebrow: "Admin Control Layer",
        title: "Operate onboarding, review queues, and release checks conversationally.",
        description: "Use the mascot to inspect setup progress, import data safely, and navigate key operational checkpoints without losing context.",
        highlights: ["Review setup progress", "Import teachers and students", "Check WhatsApp release-gate health"],
        icon: ShieldCheck,
    },
    parent: {
        eyebrow: "Parent Guide",
        title: "Track child progress and reports with guided prompts.",
        description: "The mascot can summarize linked-child performance, open the right parent views, and keep the conversation grounded in the current context.",
        highlights: ["See attendance status", "Open reports quickly", "Ask for progress summaries"],
        icon: Compass,
    },
};

export function MascotAssistantPage({ role }: { role: string }) {
    const content = ROLE_CONTENT[role] || {
        eyebrow: "Mascot Assistant",
        title: "Operate the platform from one conversational workspace.",
        description: "Use the mascot to navigate, trigger workflows, and act on the current page context.",
        highlights: ["Ask a question", "Open a workflow", "Generate grounded outputs"],
        icon: Bot,
    };
    const Icon = content.icon;

    return (
        <div className="min-h-[calc(100vh-6rem)] bg-[radial-gradient(circle_at_top_left,_rgba(251,191,36,0.18),_transparent_38%),linear-gradient(180deg,var(--bg-page),var(--bg-page))] px-4 py-6 sm:px-6 lg:px-8">
            <div className="mx-auto flex max-w-7xl flex-col gap-6">
                <section className="overflow-hidden rounded-[32px] border border-[var(--border)] bg-[var(--bg-card)] shadow-[var(--shadow-card)]">
                    <div className="grid gap-6 px-6 py-6 lg:grid-cols-[1.3fr_0.7fr] lg:px-8">
                        <div>
                            <div className="mb-3 inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1 text-xs font-medium text-[var(--text-secondary)]">
                                <Sparkles className="h-3.5 w-3.5 text-[var(--primary)]" />
                                {content.eyebrow}
                            </div>
                            <h1 className="max-w-3xl text-3xl font-semibold tracking-tight text-[var(--text-primary)] sm:text-4xl">
                                {content.title}
                            </h1>
                            <p className="mt-3 max-w-2xl text-sm leading-6 text-[var(--text-secondary)] sm:text-base">
                                {content.description}
                            </p>
                        </div>
                        <div className="grid gap-3 rounded-[28px] border border-[var(--border)] bg-[var(--bg-page)] p-5">
                            <div className="flex items-center gap-3">
                                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-orange-500 to-amber-500 text-white">
                                    <Icon className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Best starting points</p>
                                    <p className="text-xs text-[var(--text-muted)]">The mascot adapts to your role and current page context.</p>
                                </div>
                            </div>
                            <div className="space-y-2">
                                {content.highlights.map((item) => (
                                    <div key={item} className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-3 text-sm text-[var(--text-secondary)]">
                                        {item}
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                </section>

                <section className="min-h-[720px]">
                    <MascotLauncher role={role} fullPage />
                </section>
            </div>
        </div>
    );
}
