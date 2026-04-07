"use client";

import { Suspense } from "react";
import { Compass, FileText, MessageSquare, ShieldCheck } from "lucide-react";

import { RoleStartPanel } from "@/components/RoleStartPanel";
import { MascotLauncher } from "@/components/mascot/MascotLauncher";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

const STARTING_POINTS = [
    {
        title: "Progress summary",
        description: "Ask the assistant for a plain-language summary of recent attendance, marks, and monthly report signals.",
        icon: MessageSquare,
    },
    {
        title: "Open the right page",
        description: "Use quick prompts to jump into attendance, results, or reports without hunting through the parent navigation.",
        icon: Compass,
    },
    {
        title: "Supportive next steps",
        description: "Keep the conversation focused on what a parent should notice next rather than raw operational detail.",
        icon: ShieldCheck,
    },
];

export default function ParentAssistantPage() {
    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.08fr_0.92fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Compass className="h-3.5 w-3.5" />
                            Parent Assistant Surface
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black text-[var(--text-primary)] md:text-5xl">
                                Parent Assistant
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                A guided assistant for understanding progress, opening the right parent views, and keeping the conversation grounded in family-friendly language.
                            </p>
                        </div>
                    </div>
                    <PrismPanel className="p-5">
                        <div className="flex items-center gap-2">
                            <FileText className="h-4 w-4 text-status-amber" />
                            <h2 className="text-base font-semibold text-[var(--text-primary)]">Best ways to use it</h2>
                        </div>
                        <div className="mt-4 space-y-3">
                            {STARTING_POINTS.map((item) => (
                                <div key={item.title} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                    <div className="flex items-center gap-3">
                                        <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(245,158,11,0.2),rgba(249,115,22,0.08))] text-status-amber">
                                            <item.icon className="h-4 w-4" />
                                        </div>
                                        <div>
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{item.description}</p>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </PrismPanel>
                </div>

                <RoleStartPanel role="parent" />

                <PrismPanel className="overflow-hidden p-4 sm:p-5">
                    <Suspense fallback={<div className="rounded-3xl border border-[var(--border)] bg-[var(--bg-card)] p-8 text-sm text-[var(--text-secondary)]">Loading assistant...</div>}>
                        <MascotLauncher role="parent" fullPage />
                    </Suspense>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}
