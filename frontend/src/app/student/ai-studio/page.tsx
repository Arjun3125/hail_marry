"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import { ToolRail } from "./components/ToolRail";
import { ContextPanel } from "./components/ContextPanel";
import { LearningWorkspace } from "./components/LearningWorkspace";
import { FocusMode } from "./components/FocusMode";
import { NotebookSelector } from "./components/NotebookSelector";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { api } from "@/lib/api";
import "./ai-studio.css";

export default function AIStudioPage() {
    return (
        <Suspense fallback={<div className="flex min-h-[60vh] items-center justify-center text-sm text-[var(--text-muted)]">Loading AI Studio…</div>}>
            <AIStudioContent />
        </Suspense>
    );
}

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

function normalizeTool(rawTool: string | null) {
    if (!rawTool) return null;
    return validTools.has(rawTool) ? rawTool : null;
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
        [searchParams],
    );
    const seedPrompt = useMemo(() => searchParams.get("prompt"), [searchParams]);

    // Load active notebook from localStorage on mount
    useEffect(() => {
        queueMicrotask(() => {
            const saved = localStorage.getItem("activeNotebookId");
            if (saved) {
                setActiveNotebookId(saved);
            }
        });
    }, []);

    // Save active notebook to localStorage when it changes
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
        api.aiHistory.get(historyId).then((item) => {
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
        }).catch(() => {
            if (!cancelled) {
                setInitialExchange(null);
            }
        });

        return () => {
            cancelled = true;
        };
    }, [requestedTool, searchKey, searchParams]);

    // Initialize keyboard shortcuts
    useKeyboardShortcuts({
        onToggleFocus: () => setFocusMode((prev) => !prev),
        onToggleRail: () => setRailCollapsed((prev) => !prev),
        onTogglePanel: () => setContextCollapsed((prev) => !prev),
    });

    return (
        <div className="ai-studio-container">
            {/* Left Tool Rail */}
            <aside className={`tool-rail ${railCollapsed ? "collapsed" : ""}`}>
                {/* Notebook Selector */}
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

            {/* Center Learning Workspace */}
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

            {/* Right Context Panel */}
            <aside className={`context-panel ${contextCollapsed ? "collapsed" : ""}`}>
                <ContextPanel
                    collapsed={contextCollapsed}
                    onToggleCollapse={() => setContextCollapsed(!contextCollapsed)}
                    notebookId={activeNotebookId}
                    activeTool={activeTool}
                />
            </aside>

            {/* Focus Mode Overlay */}
            {focusMode && (
                <FocusMode
                    onExit={() => setFocusMode(false)}
                    activeTool={activeTool}
                />
            )}
        </div>
    );
}
