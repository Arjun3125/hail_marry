"use client";

import { useState } from "react";
import {
    FileText,
    StickyNote,
    Lightbulb,
    History,
    Settings2,
    ChevronRight,
    ChevronLeft,
    Globe,
} from "lucide-react";

interface ContextPanelProps {
    collapsed: boolean;
    onToggleCollapse: () => void;
    notebookId: string | null;
}

export function ContextPanel({ collapsed, onToggleCollapse, notebookId }: ContextPanelProps) {
    const [activeTab, setActiveTab] = useState<"citations" | "notes" | "suggestions" | "history">("citations");
    const [language, setLanguage] = useState("english");
    const [responseLength, setResponseLength] = useState("default");
    const [expertiseLevel, setExpertiseLevel] = useState("standard");

    const tabs = [
        { id: "citations", label: "Sources", icon: FileText },
        { id: "notes", label: "Notes", icon: StickyNote },
        { id: "suggestions", label: "Hints", icon: Lightbulb },
        { id: "history", label: "Recent", icon: History },
    ];

    if (collapsed) {
        return (
            <aside className="w-12 flex flex-col items-center py-4 border-l border-[var(--border)] bg-[var(--bg-card)]">
                <button
                    onClick={onToggleCollapse}
                    className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] mb-4"
                >
                    <ChevronLeft className="w-4 h-4" />
                </button>
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => {
                            setActiveTab(tab.id as typeof activeTab);
                            onToggleCollapse();
                        }}
                        className={`p-2 rounded-lg mb-2 transition-colors ${
                            activeTab === tab.id ? "bg-[var(--primary-light)] text-[var(--primary)]" : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                        }`}
                        title={tab.label}
                    >
                        <tab.icon className="w-4 h-4" />
                    </button>
                ))}
            </aside>
        );
    }

    return (
        <aside className="w-80 flex flex-col border-l border-[var(--border)] bg-[var(--bg-card)]">
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
                <span className="font-semibold text-[var(--text-primary)]">Context</span>
                <button
                    onClick={onToggleCollapse}
                    className="p-1.5 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)]"
                >
                    <ChevronRight className="w-4 h-4" />
                </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-[var(--border)]">
                {tabs.map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as typeof activeTab)}
                        className={`flex-1 flex flex-col items-center py-3 text-xs transition-colors ${
                            activeTab === tab.id
                                ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
                                : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                        }`}
                    >
                        <tab.icon className="w-4 h-4 mb-1" />
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            <div className="flex-1 overflow-y-auto p-4">
                {activeTab === "citations" && (
                    <div className="space-y-3">
                        <p className="text-xs text-[var(--text-muted)]">Sources from your materials will appear here</p>
                        <div className="p-3 rounded-lg bg-[var(--bg-page)] border border-[var(--border)]/50">
                            <div className="flex items-start gap-2">
                                <FileText className="w-4 h-4 text-[var(--text-muted)] mt-0.5" />
                                <div>
                                    <p className="text-xs font-medium text-[var(--text-primary)]">Biology Textbook</p>
                                    <p className="text-[10px] text-[var(--text-muted)]">Page 42 • Chapter 3</p>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === "notes" && (
                    <div className="space-y-3">
                        <textarea
                            placeholder="Type quick notes here..."
                            className="w-full h-32 p-3 text-sm bg-[var(--bg-page)] border border-[var(--border)] rounded-lg resize-none focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/50"
                        />
                    </div>
                )}

                {activeTab === "suggestions" && (
                    <div className="space-y-3">
                        <p className="text-xs text-[var(--text-muted)]">AI suggestions will appear after responses</p>
                    </div>
                )}

                {activeTab === "history" && (
                    <div className="space-y-2">
                        <p className="text-xs text-[var(--text-muted)]">Recent activity</p>
                    </div>
                )}
            </div>

            {/* Settings Section */}
            <div className="border-t border-[var(--border)] p-4 space-y-4">
                <div className="flex items-center gap-2 text-xs font-medium text-[var(--text-secondary)] uppercase tracking-wider">
                    <Settings2 className="w-3.5 h-3.5" />
                    Preferences
                </div>

                {/* Language */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                        <Globe className="w-3.5 h-3.5" />
                        Language
                    </div>
                    <select
                        value={language}
                        onChange={(e) => setLanguage(e.target.value)}
                        className="text-xs bg-[var(--bg-page)] border border-[var(--border)] rounded px-2 py-1"
                    >
                        <option value="english">English</option>
                        <option value="hindi">Hindi</option>
                        <option value="tamil">Tamil</option>
                        <option value="telugu">Telugu</option>
                    </select>
                </div>

                {/* Response Length */}
                <div className="space-y-2">
                    <label className="text-xs text-[var(--text-muted)]">Response Length</label>
                    <div className="flex gap-1">
                        {["brief", "default", "detailed"].map((opt) => (
                            <button
                                key={opt}
                                onClick={() => setResponseLength(opt)}
                                className={`flex-1 px-2 py-1.5 text-[10px] rounded capitalize transition-colors ${
                                    responseLength === opt
                                        ? "bg-[var(--primary)] text-white"
                                        : "bg-[var(--bg-page)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]"
                                }`}
                            >
                                {opt}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Expertise */}
                <div className="space-y-2">
                    <label className="text-xs text-[var(--text-muted)]">Level</label>
                    <div className="flex gap-1">
                        {["simple", "standard", "advanced"].map((opt) => (
                            <button
                                key={opt}
                                onClick={() => setExpertiseLevel(opt)}
                                className={`flex-1 px-2 py-1.5 text-[10px] rounded capitalize transition-colors ${
                                    expertiseLevel === opt
                                        ? "bg-[var(--primary)] text-white"
                                        : "bg-[var(--bg-page)] text-[var(--text-secondary)] hover:bg-[var(--surface-hover)]"
                                }`}
                            >
                                {opt}
                            </button>
                        ))}
                    </div>
                </div>
            </div>
        </aside>
    );
}
