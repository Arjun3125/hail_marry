"use client";

import { useState, useEffect } from "react";
import { ToolRail } from "./components/ToolRail";
import { ContextPanel } from "./components/ContextPanel";
import { LearningWorkspace } from "./components/LearningWorkspace";
import { FocusMode } from "./components/FocusMode";
import { NotebookSelector } from "./components/NotebookSelector";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import "./ai-studio.css";

export default function AIStudioPage() {
    const [activeTool, setActiveTool] = useState("qa");
    const [railCollapsed, setRailCollapsed] = useState(false);
    const [contextCollapsed, setContextCollapsed] = useState(false);
    const [focusMode, setFocusMode] = useState(false);
    const [activeNotebookId, setActiveNotebookId] = useState<string | null>(null);

    // Load active notebook from localStorage on mount
    useEffect(() => {
        const saved = localStorage.getItem("activeNotebookId");
        if (saved) {
            setActiveNotebookId(saved);
        }
    }, []);

    // Save active notebook to localStorage when it changes
    useEffect(() => {
        if (activeNotebookId) {
            localStorage.setItem("activeNotebookId", activeNotebookId);
        } else {
            localStorage.removeItem("activeNotebookId");
        }
    }, [activeNotebookId]);

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
                    activeTool={activeTool} 
                    notebookId={activeNotebookId}
                />
            </main>

            {/* Right Context Panel */}
            <aside className={`context-panel ${contextCollapsed ? "collapsed" : ""}`}>
                <ContextPanel
                    collapsed={contextCollapsed}
                    onToggleCollapse={() => setContextCollapsed(!contextCollapsed)}
                    notebookId={activeNotebookId}
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
