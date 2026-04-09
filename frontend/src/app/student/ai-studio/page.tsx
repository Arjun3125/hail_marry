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
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
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
        <PrismPage variant="workspace" className="space-y-5 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student AI Workspace
                        </PrismHeroKicker>
                    )}
                    title="Ask, revise, and build answers from your own study material"
                    description="Keep your notebook, active thread, and source context in one study desk so the next action is always visible and grounded."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Study posture</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Use one focused thread at a time, keep notebook scope explicit, and verify every answer against the evidence rail before moving on.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <Bot className="h-4 w-4 text-status-blue" />
                            <span className="prism-status-label">Active mode</span>
                        </div>
                        <p className="prism-status-value">{activeToolMeta.label}</p>
                        <p className="prism-status-detail">{activeToolMeta.summary}</p>
                    </div>
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <BookMarked className="h-4 w-4 text-status-emerald" />
                            <span className="prism-status-label">Notebook scope</span>
                        </div>
                        <p className="prism-status-value">{activeNotebookId ? "Notebook scoped" : "Open scope"}</p>
                        <p className="prism-status-detail">{notebookStatus}</p>
                    </div>
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <Command className="h-4 w-4 text-status-violet" />
                            <span className="prism-status-label">Flow controls</span>
                        </div>
                        <p className="prism-status-value">Keyboard ready</p>
                        <p className="prism-status-detail">Toggle focus mode, rail, and context without breaking the study thread.</p>
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
