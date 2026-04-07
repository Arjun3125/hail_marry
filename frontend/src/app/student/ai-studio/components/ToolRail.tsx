"use client";

import {
    BookOpen,
    Brain,
    ChevronLeft,
    ChevronRight,
    GitBranch,
    HelpCircle,
    Layers,
    MessageSquare,
    Network,
    PenLine,
    Shuffle,
    Sparkles,
    Swords,
} from "lucide-react";

interface ToolRailProps {
    activeTool: string;
    onToolChange: (tool: string) => void;
    collapsed: boolean;
    onToggleCollapse: () => void;
}

const toolGroups = [
    {
        id: "learning",
        label: "Learning",
        description: "Grounded understanding and guided discovery",
        color: "from-indigo-500 to-violet-600",
        bgColor: "bg-indigo-500/12",
        textColor: "text-status-violet",
        tools: [
            { id: "qa", label: "Q&A", icon: HelpCircle, desc: "Ask anything" },
            { id: "study_guide", label: "Study Guide", icon: BookOpen, desc: "Topic summaries" },
            { id: "socratic", label: "Socratic", icon: MessageSquare, desc: "Guided discovery" },
        ],
    },
    {
        id: "practice",
        label: "Practice",
        description: "Recall, repetition, and exam readiness",
        color: "from-emerald-500 to-teal-500",
        bgColor: "bg-emerald-500/12",
        textColor: "text-status-emerald",
        tools: [
            { id: "quiz", label: "Quiz", icon: Sparkles, desc: "Test yourself" },
            { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Spaced repetition" },
            { id: "perturbation", label: "Exam Prep", icon: Shuffle, desc: "Question variations" },
        ],
    },
    {
        id: "thinking",
        label: "Thinking",
        description: "Reasoning, argument, and writing refinement",
        color: "from-amber-400 to-orange-500",
        bgColor: "bg-amber-500/12",
        textColor: "text-status-amber",
        tools: [
            { id: "debate", label: "Debate", icon: Swords, desc: "Challenge ideas" },
            { id: "essay_review", label: "Essay Review", icon: PenLine, desc: "Writing feedback" },
        ],
    },
    {
        id: "visual",
        label: "Visual",
        description: "Spatial understanding and process mapping",
        color: "from-cyan-500 to-blue-500",
        bgColor: "bg-cyan-500/12",
        textColor: "text-status-blue",
        tools: [
            { id: "mindmap", label: "Mind Map", icon: Brain, desc: "Hierarchies" },
            { id: "flowchart", label: "Flowchart", icon: GitBranch, desc: "Processes" },
            { id: "concept_map", label: "Concept Map", icon: Network, desc: "Relationships" },
        ],
    },
];

export function ToolRail({ activeTool, onToolChange, collapsed, onToggleCollapse }: ToolRailProps) {
    return (
        <aside className="flex h-full flex-col">
            <div className="border-b border-[var(--border)]/80 px-4 py-4">
                <div className="flex items-start justify-between gap-3">
                    {collapsed ? (
                        <div className="mx-auto flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.92),rgba(129,140,248,0.9))] shadow-[0_18px_30px_rgba(59,130,246,0.18)]">
                            <Sparkles className="h-5 w-5 text-[#06101e]" />
                        </div>
                    ) : (
                        <div className="space-y-2">
                            <div className="flex items-center gap-3">
                                <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.92),rgba(129,140,248,0.9))] shadow-[0_18px_30px_rgba(59,130,246,0.18)]">
                                    <Sparkles className="h-5 w-5 text-[#06101e]" />
                                </div>
                                <div>
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">AI Studio</p>
                                    <p className="text-xs text-[var(--text-muted)]">Choose the learning mode before you ask.</p>
                                </div>
                            </div>
                            <div className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-3 py-2 text-[11px] leading-5 text-[var(--text-secondary)]">
                                Tools are grouped by study intent, not by technical feature.
                            </div>
                        </div>
                    )}

                    <button
                        onClick={onToggleCollapse}
                        className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] p-2 text-[var(--text-muted)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                        title={collapsed ? "Expand tool rail" : "Collapse tool rail"}
                    >
                        {collapsed ? <ChevronRight className="h-4 w-4" /> : <ChevronLeft className="h-4 w-4" />}
                    </button>
                </div>
            </div>

            <div className="flex-1 overflow-y-auto px-3 py-4">
                {toolGroups.map((group) => (
                    <section key={group.id} className="mb-5">
                        {collapsed ? null : (
                            <div className="mb-2 px-2">
                                <div className="mb-1 flex items-center gap-2">
                                    <div className={`h-2 w-2 rounded-full bg-gradient-to-br ${group.color}`} />
                                    <p className={`text-[11px] font-semibold uppercase tracking-[0.22em] ${group.textColor}`}>{group.label}</p>
                                </div>
                                <p className="text-[11px] leading-5 text-[var(--text-muted)]">{group.description}</p>
                            </div>
                        )}

                        <div className="space-y-1.5">
                            {group.tools.map((tool) => {
                                const isActive = activeTool === tool.id;
                                const Icon = tool.icon;

                                return (
                                    <button
                                        key={tool.id}
                                        onClick={() => onToolChange(tool.id)}
                                        className={`group flex w-full items-center gap-3 rounded-2xl border px-3 py-3 text-left transition-all ${
                                            isActive
                                                ? `border-white/12 ${group.bgColor} text-[var(--text-primary)] shadow-[0_16px_30px_rgba(2,6,23,0.12)]`
                                                : "border-transparent text-[var(--text-secondary)] hover:border-[var(--border)] hover:bg-[rgba(148,163,184,0.06)] hover:text-[var(--text-primary)]"
                                        }`}
                                        title={collapsed ? tool.label : undefined}
                                    >
                                        <div
                                            className={`flex h-10 w-10 shrink-0 items-center justify-center rounded-2xl ${
                                                isActive
                                                    ? `bg-gradient-to-br ${group.color} text-[#06101e]`
                                                    : "border border-[var(--border)] bg-[rgba(148,163,184,0.05)] text-[var(--text-muted)] group-hover:text-[var(--text-primary)]"
                                            }`}
                                        >
                                            <Icon className="h-4 w-4" />
                                        </div>
                                        {collapsed ? null : (
                                            <div className="min-w-0">
                                                <p className="truncate text-sm font-medium">{tool.label}</p>
                                                <p className="truncate text-[11px] leading-5 text-[var(--text-muted)]">{tool.desc}</p>
                                            </div>
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    </section>
                ))}
            </div>
        </aside>
    );
}
