"use client";

import {
    HelpCircle,
    BookOpen,
    MessageSquare,
    Sparkles,
    Layers,
    Shuffle,
    Swords,
    PenLine,
    Brain,
    GitBranch,
    Network,
    ChevronLeft,
    ChevronRight,
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
        color: "from-indigo-500 to-violet-600",
        bgColor: "bg-indigo-500/10",
        textColor: "text-indigo-600",
        tools: [
            { id: "qa", label: "Q&A", icon: HelpCircle, desc: "Ask anything" },
            { id: "study_guide", label: "Study Guide", icon: BookOpen, desc: "Topic summaries" },
            { id: "socratic", label: "Socratic", icon: MessageSquare, desc: "Guided discovery" },
        ],
    },
    {
        id: "practice",
        label: "Practice",
        color: "from-emerald-500 to-teal-600",
        bgColor: "bg-emerald-500/10",
        textColor: "text-emerald-600",
        tools: [
            { id: "quiz", label: "Quiz", icon: Sparkles, desc: "Test yourself" },
            { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Spaced repetition" },
            { id: "perturbation", label: "Exam Prep", icon: Shuffle, desc: "Question variations" },
        ],
    },
    {
        id: "thinking",
        label: "Thinking",
        color: "from-amber-500 to-orange-600",
        bgColor: "bg-amber-500/10",
        textColor: "text-amber-600",
        tools: [
            { id: "debate", label: "Debate", icon: Swords, desc: "Challenge ideas" },
            { id: "essay_review", label: "Essay Review", icon: PenLine, desc: "Writing feedback" },
        ],
    },
    {
        id: "visual",
        label: "Visual",
        color: "from-cyan-500 to-blue-600",
        bgColor: "bg-cyan-500/10",
        textColor: "text-cyan-600",
        tools: [
            { id: "mindmap", label: "Mind Map", icon: Brain, desc: "Hierarchies" },
            { id: "flowchart", label: "Flowchart", icon: GitBranch, desc: "Processes" },
            { id: "concept_map", label: "Concept Map", icon: Network, desc: "Relationships" },
        ],
    },
];

export function ToolRail({ activeTool, onToolChange, collapsed, onToggleCollapse }: ToolRailProps) {
    return (
        <aside
            className={`tool-rail ${collapsed ? "w-16" : "w-64"} flex flex-col border-r border-[var(--border-light)] bg-[var(--bg-card)]/80 backdrop-blur-md transition-all duration-300 shadow-sm z-10`}
        >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b border-[var(--border)]">
                {!collapsed && (
                    <div className="flex items-center gap-2">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                            <Sparkles className="w-4 h-4 text-white" />
                        </div>
                        <span className="font-semibold text-[var(--text-primary)]">AI Studio</span>
                    </div>
                )}
                <button
                    onClick={onToggleCollapse}
                    className="p-1.5 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                    title={collapsed ? "Expand" : "Collapse"}
                >
                    {collapsed ? <ChevronRight className="w-4 h-4" /> : <ChevronLeft className="w-4 h-4" />}
                </button>
            </div>

            {/* Tool Groups */}
            <div className="flex-1 overflow-y-auto p-2 space-y-1">
                {toolGroups.map((group) => (
                    <div key={group.id} className="mb-4">
                        {!collapsed && (
                            <div className={`flex items-center gap-2 px-3 py-2 text-xs font-medium ${group.textColor} uppercase tracking-wider`}>
                                <div className={`w-2 h-2 rounded-full bg-gradient-to-br ${group.color}`} />
                                {group.label}
                            </div>
                        )}
                        <div className="space-y-0.5">
                            {group.tools.map((tool) => {
                                const isActive = activeTool === tool.id;
                                const Icon = tool.icon;

                                return (
                                    <button
                                        key={tool.id}
                                        onClick={() => onToolChange(tool.id)}
                                        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200 group ${
                                            isActive
                                                ? `${group.bgColor} ${group.textColor} font-medium`
                                                : "hover:bg-[var(--surface-hover)] text-[var(--text-secondary)]"
                                        }`}
                                        title={collapsed ? tool.label : undefined}
                                    >
                                        <Icon className={`w-4 h-4 flex-shrink-0 ${isActive ? "" : "text-[var(--text-muted)] group-hover:text-[var(--text-secondary)]"}`} />
                                        {!collapsed && (
                                            <div className="flex flex-col min-w-0">
                                                <span className="text-sm truncate">{tool.label}</span>
                                                <span className="text-[10px] text-[var(--text-muted)] truncate">{tool.desc}</span>
                                            </div>
                                        )}
                                    </button>
                                );
                            })}
                        </div>
                    </div>
                ))}
            </div>
        </aside>
    );
}
