"use client";

import { Suspense, useEffect, useState } from "react";
import Image from "next/image";
import { Compass, GraduationCap, ShieldCheck, Sparkles, Users } from "lucide-react";

import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import { MascotLauncher } from "./MascotLauncher";
import { api } from "@/lib/api";

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
        icon: Sparkles,
    };
    const Icon = content.icon;

    const [liveGreeting, setLiveGreeting] = useState<string | null>(null);
    const [greetingLoading, setGreetingLoading] = useState(true);

    useEffect(() => {
        api.mascot
            .greeting()
            .then((res: any) => setLiveGreeting((res as { greeting?: string }).greeting || null))
            .catch(() => {/* fall through to static description */})
            .finally(() => setGreetingLoading(false));
    }, []);

    return (
        <PrismPage variant="workspace" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                {/* Mascot Hero Profile */}
                <div className="rounded-3xl border border-cyan-500/30 bg-gradient-to-br from-slate-900/50 to-slate-800/50 p-8 md:p-12">
                    <div className="flex flex-col md:flex-row items-center gap-8 md:gap-12">
                        <div className="flex-shrink-0">
                            <div className="relative w-40 h-40 md:w-48 md:h-48 flex items-center justify-center">
                                <Image
                                    src="/images/mascot-owl-bg.png"
                                    alt="VidyaOS Mascot"
                                    width={200}
                                    height={240}
                                    priority
                                    className="drop-shadow-2xl object-contain"
                                    style={{
                                        filter: "drop-shadow(0 0 20px rgba(0, 212, 255, 0.3))",
                                    }}
                                />
                            </div>
                        </div>
                        <div className="flex-1 text-center md:text-left">
                            <div className="inline-flex items-center gap-2 rounded-full border border-cyan-500/40 bg-cyan-500/10 px-4 py-2 mb-4">
                                <Sparkles className="h-4 w-4 text-cyan-400" />
                                <span className="text-sm font-semibold text-cyan-300">{content.eyebrow}</span>
                            </div>
                            <h1 className="text-3xl md:text-4xl font-black text-[var(--text-primary)] mb-3">{content.title}</h1>
                            {greetingLoading ? (
                                <div className="h-5 w-2/3 rounded-full bg-[var(--bg-card)] animate-pulse mb-6" />
                            ) : (
                                <p className="text-base text-[var(--text-secondary)] leading-relaxed mb-6">
                                    {liveGreeting || content.description}
                                </p>
                            )}
                            <div className="flex flex-wrap gap-2 justify-center md:justify-start">
                                {content.highlights.map((item, idx) => (
                                    <span key={item} className="rounded-full border border-cyan-500/30 bg-cyan-500/5 px-4 py-2 text-sm text-cyan-300">
                                        {item}
                                    </span>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>

                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Start here
                        </PrismHeroKicker>
                    )}
                    title="What the mascot can do for you"
                    description="Ask questions, generate content, or navigate the platform—all through conversation."
                    aside={(
                        <PrismPanel className="prism-briefing-panel p-5">
                            <div className="flex items-center gap-3">
                                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 text-white">
                                    <Icon className="h-5 w-5" />
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Role-adapted</p>
                                    <p className="text-xs text-[var(--text-muted)]">Personalized for {role}s</p>
                                </div>
                            </div>
                            <div className="mt-4 space-y-2">
                                <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-3 text-sm text-[var(--text-secondary)]">
                                    💡 Works via WhatsApp too
                                </div>
                                <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-3 text-sm text-[var(--text-secondary)]">
                                    🔐 Grounded in your school data
                                </div>
                                <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] px-4 py-3 text-sm text-[var(--text-secondary)]">
                                    ⚡ Context-aware suggestions
                                </div>
                            </div>
                        </PrismPanel>
                    )}
                />

                <section className="min-h-[720px]">
                    <Suspense fallback={<div className="rounded-3xl border border-[var(--border)] bg-[var(--bg-card)] p-8 text-sm text-[var(--text-secondary)]">Loading assistant...</div>}>
                        <MascotLauncher role={role} fullPage />
                    </Suspense>
                </section>
            </PrismSection>
        </PrismPage>
    );
}
