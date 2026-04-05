"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
    FileText,
    StickyNote,
    Lightbulb,
    History,
    Settings2,
    ChevronRight,
    ChevronLeft,
    Globe,
    Loader2,
    Sparkles,
} from "lucide-react";
import { api } from "@/lib/api";

interface ContextPanelProps {
    collapsed: boolean;
    onToggleCollapse: () => void;
    notebookId: string | null;
    activeTool: string;
}

type PersonalizedSuggestion = {
    id: string;
    label: string;
    description: string;
    prompt: string;
    target_tool?: string;
    priority?: string;
    reason?: string;
};

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

export function ContextPanel({ collapsed, onToggleCollapse, notebookId, activeTool }: ContextPanelProps) {
    const router = useRouter();
    const [activeTab, setActiveTab] = useState<"citations" | "notes" | "suggestions" | "history">("citations");
    const [language, setLanguage] = useState("english");
    const [responseLength, setResponseLength] = useState("default");
    const [expertiseLevel, setExpertiseLevel] = useState("standard");
    const [suggestions, setSuggestions] = useState<PersonalizedSuggestion[]>([]);
    const [loadingSuggestions, setLoadingSuggestions] = useState(false);

    const tabs = [
        { id: "citations", label: "Sources", icon: FileText },
        { id: "notes", label: "Notes", icon: StickyNote },
        { id: "suggestions", label: "Hints", icon: Lightbulb },
        { id: "history", label: "Recent", icon: History },
    ];

    useEffect(() => {
        let cancelled = false;
        queueMicrotask(() => {
            if (!cancelled) {
                setLoadingSuggestions(true);
            }
        });
        api.personalization.recommendations({
            active_tool: activeTool,
            notebook_id: notebookId,
            current_surface: "ai_studio_context_panel",
        }).then((payload) => {
            if (cancelled) return;
            const items = Array.isArray((payload as { items?: PersonalizedSuggestion[] }).items)
                ? ((payload as { items: PersonalizedSuggestion[] }).items || [])
                : [];
            setSuggestions(items.slice(0, 3));
        }).catch(() => {
            if (!cancelled) {
                setSuggestions([]);
            }
        }).finally(() => {
            if (!cancelled) {
                setLoadingSuggestions(false);
            }
        });

        return () => {
            cancelled = true;
        };
    }, [activeTool, notebookId]);

    const recommendationHref = useMemo(() => {
        return (item: PersonalizedSuggestion) => {
            const params = new URLSearchParams();
            const targetTool = item.target_tool && validTools.has(item.target_tool) ? item.target_tool : activeTool;
            params.set("tool", targetTool);
            params.set("prompt", item.prompt);
            if (notebookId) {
                params.set("notebook_id", notebookId);
            }
            return `/student/ai-studio?${params.toString()}`;
        };
    }, [activeTool, notebookId]);

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
                        <div className="flex items-center justify-between gap-2">
                            <p className="text-xs text-[var(--text-muted)]">Personalized next steps for this tool.</p>
                            {loadingSuggestions ? <Loader2 className="h-3.5 w-3.5 animate-spin text-[var(--text-muted)]" /> : null}
                        </div>
                        {suggestions.length > 0 ? (
                            <div className="space-y-2">
                                {suggestions.map((item) => (
                                    <button
                                        key={item.id}
                                        type="button"
                                        onClick={() => router.push(recommendationHref(item))}
                                        className="w-full rounded-lg border border-[var(--border)] bg-[var(--bg-page)] p-3 text-left transition-colors hover:border-[var(--primary)]/40 hover:bg-[var(--surface-hover)]"
                                    >
                                        <div className="mb-2 flex items-center justify-between gap-2">
                                            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-widest text-[var(--text-muted)]">
                                                <Sparkles className="h-3 w-3 text-[var(--primary)]" />
                                                {item.priority || "recommended"}
                                            </span>
                                            <span className="rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-2 py-0.5 text-[10px] text-[var(--text-secondary)]">
                                                {(item.target_tool || activeTool).replace("_", " ")}
                                            </span>
                                        </div>
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{item.label}</p>
                                        <p className="mt-1 text-[11px] leading-relaxed text-[var(--text-muted)]">{item.description}</p>
                                    </button>
                                ))}
                            </div>
                        ) : (
                            <div className="rounded-lg border border-dashed border-[var(--border)] bg-[var(--bg-page)] p-3">
                                <p className="text-xs text-[var(--text-muted)]">
                                    Personalized suggestions will appear after more study activity on this topic or notebook.
                                </p>
                            </div>
                        )}
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
