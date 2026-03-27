"use client";

import { useState, useEffect } from "react";
import { Minimize2, X } from "lucide-react";

interface FocusModeProps {
    onExit: () => void;
    activeTool: string;
}

export function FocusMode({ onExit, activeTool }: FocusModeProps) {
    const [showHelp, setShowHelp] = useState(false);

    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "?") {
                setShowHelp(true);
            }
            if (e.key === "Escape") {
                if (showHelp) {
                    setShowHelp(false);
                } else {
                    onExit();
                }
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [showHelp, onExit]);

    return (
        <div className="fixed inset-0 z-50 bg-[var(--bg-page)] animate-in fade-in duration-300">
            {/* Header controls */}
            <div className="absolute top-0 left-0 right-0 flex items-center justify-between px-6 py-4 bg-gradient-to-b from-[var(--bg-page)] to-transparent">
                <div className="flex items-center gap-2">
                    <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                        Focus Mode
                    </span>
                    <span className="text-[10px] text-[var(--text-muted)]">Press ? for shortcuts</span>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => setShowHelp(true)}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Keyboard shortcuts"
                    >
                        <span className="text-xs">?</span>
                    </button>
                    <button
                        onClick={onExit}
                        className="flex items-center gap-2 px-3 py-2 rounded-lg bg-[var(--bg-card)] hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] text-sm transition-colors border border-[var(--border)]"
                    >
                        <Minimize2 className="w-4 h-4" />
                        Exit Focus
                    </button>
                </div>
            </div>

            {/* Content */}
            <div className="h-full pt-16 pb-8 px-8 overflow-y-auto">
                <div className="max-w-3xl mx-auto">
                    <div className="prose prose-sm max-w-none">
                        <h1 className="text-2xl font-bold text-[var(--text-primary)] mb-4">
                            Focus Mode
                        </h1>
                        <p className="text-[var(--text-secondary)]">
                            You are in focus mode. Press <kbd className="px-1.5 py-0.5 bg-[var(--bg-page)] border border-[var(--border)] rounded text-xs">Esc</kbd> to exit or <kbd className="px-1.5 py-0.5 bg-[var(--bg-page)] border border-[var(--border)] rounded text-xs">?</kbd> for help.
                        </p>
                        <p className="text-[var(--text-muted)] text-sm mt-4">
                            Active tool: {activeTool}
                        </p>
                    </div>
                </div>
            </div>

            {/* Progress bar */}
            <div className="absolute bottom-0 left-0 right-0 h-1 bg-[var(--border)]">
                <div 
                    className="h-full bg-gradient-to-r from-indigo-500 to-violet-600 transition-all duration-300"
                    style={{ width: "0%" }} // Would be connected to reading progress
                />
            </div>

            {/* Keyboard shortcuts help modal */}
            {showHelp && (
                <div 
                    className="absolute inset-0 bg-black/50 flex items-center justify-center p-4 animate-in fade-in duration-200"
                    onClick={() => setShowHelp(false)}
                >
                    <div 
                        className="bg-[var(--bg-card)] rounded-2xl p-6 max-w-md w-full shadow-2xl border border-[var(--border)]"
                        onClick={(e) => e.stopPropagation()}
                    >
                        <div className="flex items-center justify-between mb-4">
                            <h3 className="font-semibold text-[var(--text-primary)]">Keyboard Shortcuts</h3>
                            <button
                                onClick={() => setShowHelp(false)}
                                className="p-1.5 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)]"
                            >
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                        <div className="space-y-2">
                            {[
                                { key: "F", desc: "Toggle focus mode" },
                                { key: "Esc", desc: "Exit focus mode" },
                                { key: "?", desc: "Show this help" },
                                { key: "↑ / ↓", desc: "Scroll content" },
                                { key: "Space", desc: "Page down" },
                            ].map((item) => (
                                <div key={item.key} className="flex items-center justify-between py-2 border-b border-[var(--border)]/50 last:border-0">
                                    <kbd className="px-2 py-1 text-xs bg-[var(--bg-page)] border border-[var(--border)] rounded font-mono">
                                        {item.key}
                                    </kbd>
                                    <span className="text-sm text-[var(--text-secondary)]">{item.desc}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
