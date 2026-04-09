"use client";

import { useEffect, useMemo, useState } from "react";
import { useRouter } from "next/navigation";
import {
    ChevronLeft,
    ChevronRight,
    FileText,
    Globe,
    History,
    Lightbulb,
    Loader2,
    Settings2,
    Sparkles,
    StickyNote,
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

const sourceExamples: Record<string, { title: string; detail: string; guidance: string }> = {
    qa: {
        title: "Verify the current answer before you reuse it",
        detail: "Confirm notebook scope, chapter, and citation path before turning the answer into revision work.",
        guidance: "Best for concept clarification and textbook-grounded explanations.",
    },
    study_guide: {
        title: "Check chapter scope before generating a guide",
        detail: "A useful study guide comes from one clear notebook or chapter boundary.",
        guidance: "Best for turning one topic into structured revision material.",
    },
    socratic: {
        title: "Keep the same concept in scope",
        detail: "Use one chapter or notebook so the guided questions deepen understanding instead of drifting.",
        guidance: "Best for guided discovery, not broad topic switching.",
    },
    quiz: {
        title: "Practice only after source scope is clear",
        detail: "The cleaner the notebook scope, the more trustworthy the quiz coverage becomes.",
        guidance: "Best for fast active recall after one focused study block.",
    },
    flashcards: {
        title: "Use stable material for card generation",
        detail: "Generate cards from chapter-linked notes so definitions and terms match what you studied.",
        guidance: "Best for repeated short review sessions.",
    },
    perturbation: {
        title: "Stress-test one problem family at a time",
        detail: "Keep the original source visible so generated variations stay aligned with the real pattern.",
        guidance: "Best for exam-style confidence building.",
    },
    debate: {
        title: "Separate grounded claims from exploratory claims",
        detail: "Use the evidence rail to decide what comes from your notes and what needs stronger support.",
        guidance: "Best for argument testing and reasoning practice.",
    },
    essay_review: {
        title: "Track what actually needs rewriting",
        detail: "Use notes to capture weak structure, missing evidence, or unclear reasoning before you revise.",
        guidance: "Best for improving structure, clarity, and source use.",
    },
    mindmap: {
        title: "Map one chapter before you widen scope",
        detail: "A narrower notebook scope produces a cleaner visual hierarchy and better revision planning.",
        guidance: "Best for dependencies, branches, and chapter structure.",
    },
    flowchart: {
        title: "Keep the process source explicit",
        detail: "Use one notebook or chapter so each step stays connected to the same process explanation.",
        guidance: "Best for ordered procedures and sequences.",
    },
    concept_map: {
        title: "Check relationship chains before memorizing them",
        detail: "Use the rail to confirm how concepts connect and where the explanation came from.",
        guidance: "Best for topic relationships and cross-links.",
    },
};

const recentStudyMoves = [
    "Stay in the same notebook if you are still working on one chapter.",
    "Turn the strongest answer into a quiz, flashcards, or a study guide.",
    "Write one scratch note before switching tools so the next session starts faster.",
];

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
    ] as const;

    const sourceMeta = sourceExamples[activeTool] || sourceExamples.qa;
    const notebookLabel = notebookId ? `Notebook ${notebookId.slice(0, 8)}` : "All available notebooks";

    useEffect(() => {
        let cancelled = false;
        queueMicrotask(() => {
            if (!cancelled) {
                setLoadingSuggestions(true);
            }
        });

        api.personalization
            .recommendations({
                active_tool: activeTool,
                notebook_id: notebookId,
                current_surface: "ai_studio_context_panel",
            })
            .then((payload) => {
                if (cancelled) return;
                const items = Array.isArray((payload as { items?: PersonalizedSuggestion[] }).items)
                    ? ((payload as { items: PersonalizedSuggestion[] }).items || [])
                    : [];
                setSuggestions(items.slice(0, 3));
            })
            .catch(() => {
                if (!cancelled) {
                    setSuggestions([]);
                }
            })
            .finally(() => {
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
            <aside className="flex h-full w-full flex-col items-center py-4">
                <button
                    onClick={onToggleCollapse}
                    className="mb-4 rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] p-2 text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                >
                    <ChevronLeft className="h-4 w-4" />
                </button>
                {tabs.map((tab) => {
                    const Icon = tab.icon;

                    return (
                        <button
                            key={tab.id}
                            onClick={() => {
                                setActiveTab(tab.id);
                                onToggleCollapse();
                            }}
                            className={`mb-2 rounded-2xl border p-2.5 transition ${
                                activeTab === tab.id
                                    ? "border-white/12 bg-[rgba(96,165,250,0.12)] text-[var(--text-primary)]"
                                    : "border-transparent text-[var(--text-muted)] hover:border-[var(--border)] hover:text-[var(--text-primary)]"
                            }`}
                            title={tab.label}
                        >
                            <Icon className="h-4 w-4" />
                        </button>
                    );
                })}
            </aside>
        );
    }

    return (
        <aside className="flex h-full flex-col">
            <div className="border-b border-[var(--border)]/80 px-4 py-4">
                <div className="flex items-start justify-between gap-3">
                    <div>
                        <p className="text-sm font-semibold text-[var(--text-primary)]">Context Lab</p>
                        <p className="mt-1 text-xs leading-5 text-[var(--text-muted)]">
                            Keep source scope, scratch notes, and next-step prompts in sight while you study.
                        </p>
                    </div>
                    <button
                        onClick={onToggleCollapse}
                        className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] p-2 text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                    >
                        <ChevronRight className="h-4 w-4" />
                    </button>
                </div>
            </div>

            <div className="border-b border-[var(--border)]/80 px-3 py-3">
                <div className="grid grid-cols-4 gap-2">
                    {tabs.map((tab) => {
                        const Icon = tab.icon;
                        const isActive = activeTab === tab.id;

                        return (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`rounded-2xl border px-2 py-2.5 text-center transition ${
                                    isActive
                                        ? "border-white/12 bg-[rgba(96,165,250,0.12)] text-[var(--text-primary)]"
                                        : "border-transparent text-[var(--text-muted)] hover:border-[var(--border)] hover:bg-[rgba(148,163,184,0.05)] hover:text-[var(--text-primary)]"
                                }`}
                            >
                                <Icon className="mx-auto mb-1 h-4 w-4" />
                                <span className="text-[10px]">{tab.label}</span>
                            </button>
                        );
                    })}
                </div>
            </div>

            <div className="flex-1 overflow-y-auto p-4">
                {activeTab === "citations" ? (
                    <div className="space-y-3">
                        <div className="prism-evidence-card">
                            <p className="prism-status-label">Evidence check</p>
                            <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">{sourceMeta.title}</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                {sourceMeta.detail}
                            </p>
                        </div>
                        <div className="prism-support-panel rounded-2xl p-3">
                            <p className="prism-status-label">Current source scope</p>
                            <p className="mt-2 text-sm font-semibold text-[var(--text-primary)]">{notebookLabel}</p>
                            <p className="mt-1 text-xs leading-5 text-[var(--text-secondary)]">{sourceMeta.guidance}</p>
                        </div>
                        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-3">
                            <div className="flex items-start gap-3">
                                <div className="flex h-9 w-9 items-center justify-center rounded-xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)]">
                                    <FileText className="h-4 w-4 text-[var(--text-muted)]" />
                                </div>
                                <div>
                                    <p className="text-sm font-medium text-[var(--text-primary)]">
                                        {notebookId ? "Notebook-linked citation" : "Biology Textbook"}
                                    </p>
                                    <p className="text-[11px] leading-5 text-[var(--text-muted)]">
                                        {notebookId ? "The next grounded answer will show notebook page and source path here." : "Page 42 • Chapter 3"}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>
                ) : null}

                {activeTab === "notes" ? (
                    <div className="space-y-3">
                        <div className="prism-evidence-card">
                            <p className="prism-status-label">Scratchpad</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Capture one weak concept, one important definition, or one follow-up prompt before you switch tools.
                            </p>
                        </div>
                        <textarea
                            placeholder="Write one takeaway, one confusion, or one next-step prompt..."
                            className="h-40 w-full resize-none rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                        />
                    </div>
                ) : null}

                {activeTab === "suggestions" ? (
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
                                        className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-3 text-left transition hover:border-[var(--primary)]/40 hover:bg-[rgba(148,163,184,0.08)]"
                                    >
                                        <div className="mb-2 flex items-center justify-between gap-2">
                                            <span className="inline-flex items-center gap-1 text-[10px] uppercase tracking-[0.22em] text-[var(--text-muted)]">
                                                <Sparkles className="h-3 w-3 text-[var(--primary)]" />
                                                {item.priority || "recommended"}
                                            </span>
                                            <span className="rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-2 py-0.5 text-[10px] text-[var(--text-secondary)]">
                                                {(item.target_tool || activeTool).replace("_", " ")}
                                            </span>
                                        </div>
                                        <p className="text-sm font-medium text-[var(--text-primary)]">{item.label}</p>
                                        <p className="mt-1 text-[11px] leading-5 text-[var(--text-muted)]">{item.description}</p>
                                    </button>
                                ))}
                            </div>
                        ) : (
                            <div className="rounded-2xl border border-dashed border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-3">
                                <p className="text-xs leading-6 text-[var(--text-muted)]">
                                    Personalized suggestions will appear after more study activity on this topic or notebook.
                                </p>
                            </div>
                        )}
                    </div>
                ) : null}

                {activeTab === "history" ? (
                    <div className="space-y-3">
                        <div className="prism-evidence-card">
                            <p className="prism-status-label">Recent study moves</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Use recent actions to decide whether to continue the same thread, switch tools, or convert the current answer into revision work.
                            </p>
                        </div>
                        <div className="space-y-2">
                            {recentStudyMoves.map((item) => (
                                <div key={item} className="prism-operational-row">
                                    <p className="text-xs leading-6 text-[var(--text-secondary)]">{item}</p>
                                </div>
                            ))}
                        </div>
                    </div>
                ) : null}
            </div>

            <div className="border-t border-[var(--border)]/80 p-4">
                <div className="mb-3 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-secondary)]">
                    <Settings2 className="h-3.5 w-3.5" />
                    Preferences
                </div>

                <div className="space-y-4">
                    <div className="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-2.5">
                        <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                            <Globe className="h-3.5 w-3.5" />
                            Language
                        </div>
                        <select
                            value={language}
                            onChange={(event) => setLanguage(event.target.value)}
                            className="rounded-lg border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-2 py-1 text-xs text-[var(--text-primary)] outline-none"
                        >
                            <option value="english">English</option>
                            <option value="hindi">Hindi</option>
                            <option value="tamil">Tamil</option>
                            <option value="telugu">Telugu</option>
                        </select>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs text-[var(--text-muted)]">Response Length</label>
                        <div className="grid grid-cols-3 gap-1.5">
                            {["brief", "default", "detailed"].map((option) => (
                                <button
                                    key={option}
                                    onClick={() => setResponseLength(option)}
                                    className={`rounded-xl px-2 py-2 text-[10px] capitalize transition ${
                                        responseLength === option
                                            ? "bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.92))] text-[#06101e]"
                                            : "border border-[var(--border)] bg-[rgba(148,163,184,0.05)] text-[var(--text-secondary)] hover:bg-[rgba(148,163,184,0.08)]"
                                    }`}
                                >
                                    {option}
                                </button>
                            ))}
                        </div>
                    </div>

                    <div className="space-y-2">
                        <label className="text-xs text-[var(--text-muted)]">Level</label>
                        <div className="grid grid-cols-3 gap-1.5">
                            {["simple", "standard", "advanced"].map((option) => (
                                <button
                                    key={option}
                                    onClick={() => setExpertiseLevel(option)}
                                    className={`rounded-xl px-2 py-2 text-[10px] capitalize transition ${
                                        expertiseLevel === option
                                            ? "bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.92))] text-[#06101e]"
                                            : "border border-[var(--border)] bg-[rgba(148,163,184,0.05)] text-[var(--text-secondary)] hover:bg-[rgba(148,163,184,0.08)]"
                                    }`}
                                >
                                    {option}
                                </button>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </aside>
    );
}
