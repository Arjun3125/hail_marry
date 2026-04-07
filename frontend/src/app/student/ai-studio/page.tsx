"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { BookMarked, Bot, Command, PanelsTopLeft, Sparkles } from "lucide-react";

import { ToolRail } from "./components/ToolRail";
import { ContextPanel } from "./components/ContextPanel";
import { LearningWorkspace } from "./components/LearningWorkspace";
import { FocusMode } from "./components/FocusMode";
import { NotebookSelector } from "./components/NotebookSelector";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { api } from "@/lib/api";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import "./ai-studio.css";

const validTools = new Set([
    "qa",
    "study_guide",
    "socratic",
    "quiz",
    "flashcards",
    "perturbation",
    "debate",
    "essay_review",
    "mindmap",
    "flowchart",
    "concept_map",
]);

const toolDetails: Record<string, { label: string; summary: string }> = {
    qa: { label: "Q&A", summary: "Grounded answers across your current notes and textbooks." },
    study_guide: { label: "Study Guide", summary: "Build structured revision packs for the current topic." },
    socratic: { label: "Socratic Tutor", summary: "Work through a concept through guided questioning." },
    quiz: { label: "Quiz", summary: "Test your understanding with quick active recall." },
    flashcards: { label: "Flashcards", summary: "Turn a topic into spaced repetition prompts." },
    perturbation: { label: "Exam Prep", summary: "Stress-test concepts with question variations." },
    debate: { label: "Debate", summary: "Challenge reasoning and sharpen arguments." },
    essay_review: { label: "Essay Review", summary: "Refine long-form writing with targeted feedback." },
    mindmap: { label: "Mind Map", summary: "See topic hierarchy and relationships spatially." },
    flowchart: { label: "Flowchart", summary: "Understand stepwise processes visually." },
    concept_map: { label: "Concept Map", summary: "Link concepts, dependencies, and explanations." },
};

function normalizeTool(rawTool: string | null) {
    if (!rawTool) return null;
    return validTools.has(rawTool) ? rawTool : null;
}

function LoadingFallback() {
    return (
        <PrismPage className="pb-8">
            <PrismSection>
                <PrismPanel className="flex min-h-[60vh] items-center justify-center p-8 text-sm text-[var(--text-muted)]">
                    Loading AI Studio...
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

export default function AIStudioPage() {
    return (
        <Suspense fallback={<LoadingFallback />}>
            <AIStudioContent />
        </Suspense>
    );
}

function AIStudioContent() {
    const searchParams = useSearchParams();
    const [activeTool, setActiveTool] = useState("qa");
    const [railCollapsed, setRailCollapsed] = useState(false);
    const [contextCollapsed, setContextCollapsed] = useState(false);
    const [focusMode, setFocusMode] = useState(false);
    const [activeNotebookId, setActiveNotebookId] = useState<string | null>(null);
    const [requestOptions, setRequestOptions] = useState<{
        language?: string;
        responseLength?: string;
        expertiseLevel?: string;
    }>({});
    const [initialExchange, setInitialExchange] = useState<{
        query: string;
        response: {
            answer: string;
            citations: Array<{ source?: string; page?: string | null; url?: string | null; text?: string }>;
            mode: string;
        };
    } | null>(null);

    const searchKey = searchParams.toString();
    const requestedTool = useMemo(
        () => normalizeTool(searchParams.get("tool") || searchParams.get("mode")),
        [searchParams]
    );
    const seedPrompt = useMemo(() => searchParams.get("prompt"), [searchParams]);

    useEffect(() => {
        queueMicrotask(() => {
            const saved = localStorage.getItem("activeNotebookId");
            if (saved) {
                setActiveNotebookId(saved);
            }
        });
    }, []);

    useEffect(() => {
        if (activeNotebookId) {
            localStorage.setItem("activeNotebookId", activeNotebookId);
        } else {
            localStorage.removeItem("activeNotebookId");
        }
    }, [activeNotebookId]);

    useEffect(() => {
        queueMicrotask(() => {
            if (requestedTool) {
                setActiveTool(requestedTool);
            }

            const notebookId = searchParams.get("notebook_id");
            if (notebookId) {
                setActiveNotebookId(notebookId);
            }

            setRequestOptions((prev) => ({
                language: searchParams.get("language") || prev.language,
                responseLength: searchParams.get("response_length") || prev.responseLength,
                expertiseLevel: searchParams.get("expertise_level") || prev.expertiseLevel,
            }));
        });
    }, [requestedTool, searchKey, searchParams]);

    useEffect(() => {
        const historyId = searchParams.get("history");
        if (!historyId) {
            queueMicrotask(() => {
                setInitialExchange(null);
            });
            return;
        }

        let cancelled = false;
        api.aiHistory
            .get(historyId)
            .then((item) => {
                if (cancelled) return;
                const historyItem = item as { mode?: string; query_text?: string; response_text?: string };
                const historyMode = normalizeTool(historyItem.mode || null);
                if (!requestedTool && historyMode) {
                    setActiveTool(historyMode);
                }
                setInitialExchange({
                    query: historyItem.query_text || "",
                    response: {
                        answer: historyItem.response_text || "No response received.",
                        citations: [],
                        mode: historyMode || requestedTool || "qa",
                    },
                });
            })
            .catch(() => {
                if (!cancelled) {
                    setInitialExchange(null);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [requestedTool, searchKey, searchParams]);

    useKeyboardShortcuts({
        onToggleFocus: () => setFocusMode((prev) => !prev),
        onToggleRail: () => setRailCollapsed((prev) => !prev),
        onTogglePanel: () => setContextCollapsed((prev) => !prev),
    });

    const activeToolMeta = toolDetails[activeTool] || toolDetails.qa;
    const notebookStatus = activeNotebookId
        ? `Notebook linked: ${activeNotebookId.slice(0, 8)}`
        : "All notebooks available";

    return (
        <PrismPage className="space-y-6 pb-10">
            <PrismSection className="space-y-6">
                <div className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student AI Workspace
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Study inside a <span className="premium-gradient">single intelligence surface</span> instead of fragmented tools
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                This route is the Phase 3 student flagship. The layout now keeps learning mode, notebook context, and active thread in one deliberate workspace so students can move from questions to revision artifacts without losing momentum.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <PrismPanel className="p-4">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.08))]">
                                <Bot className="h-5 w-5 text-status-blue" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Active mode</p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{activeToolMeta.label}</p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{activeToolMeta.summary}</p>
                        </PrismPanel>
                        <PrismPanel className="p-4">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(45,212,191,0.2),rgba(20,184,166,0.08))]">
                                <BookMarked className="h-5 w-5 text-status-emerald" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Context</p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">
                                {activeNotebookId ? "Notebook scoped" : "Open scope"}
                            </p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{notebookStatus}</p>
                        </PrismPanel>
                        <PrismPanel className="p-4">
                            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(167,139,250,0.2),rgba(129,140,248,0.08))]">
                                <Command className="h-5 w-5 text-status-violet" />
                            </div>
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Flow controls</p>
                            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">Keyboard-ready</p>
                            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">
                                Toggle focus mode, rail, and context quickly without breaking study momentum.
                            </p>
                        </PrismPanel>
                    </div>
                </div>

                <PrismPanel className="overflow-hidden p-0">
                    <div className="flex flex-wrap items-center gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.08)] px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
                            <PanelsTopLeft className="h-3.5 w-3.5" />
                            Deep Work Layout
                        </div>
                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.04)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                            Left rail: tools and notebooks
                        </div>
                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.04)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                            Center: active learning thread
                        </div>
                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.04)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                            Right: sources, notes, hints
                        </div>
                    </div>

                    <div className="ai-studio-container">
                        <aside className={`tool-rail ${railCollapsed ? "collapsed" : ""}`}>
                            <NotebookSelector
                                activeNotebookId={activeNotebookId}
                                onNotebookChange={setActiveNotebookId}
                            />
                            <ToolRail
                                activeTool={activeTool}
                                onToolChange={setActiveTool}
                                collapsed={railCollapsed}
                                onToggleCollapse={() => setRailCollapsed(!railCollapsed)}
                            />
                        </aside>

                        <main className="learning-workspace">
                            <LearningWorkspace
                                key={`${activeTool}:${activeNotebookId ?? "none"}`}
                                activeTool={activeTool}
                                notebookId={activeNotebookId}
                                requestOptions={requestOptions}
                                initialExchange={initialExchange}
                                seedPrompt={seedPrompt}
                            />
                        </main>

                        <aside className={`context-panel ${contextCollapsed ? "collapsed" : ""}`}>
                            <ContextPanel
                                collapsed={contextCollapsed}
                                onToggleCollapse={() => setContextCollapsed(!contextCollapsed)}
                                notebookId={activeNotebookId}
                                activeTool={activeTool}
                            />
                        </aside>
                    </div>
                </PrismPanel>

                {focusMode ? <FocusMode onExit={() => setFocusMode(false)} activeTool={activeTool} /> : null}
            </PrismSection>
        </PrismPage>
    );
}
