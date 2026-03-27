"use client";

import { useState, useEffect, useMemo } from "react";
import { Search, X, Sparkles, Layers, Brain, Swords, BookOpen, HelpCircle, MessageSquare } from "lucide-react";

interface CommandPaletteProps {
    isOpen: boolean;
    onClose: () => void;
    onToolSelect: (toolId: string) => void;
    activeTool: string;
}

interface CommandItem {
    id: string;
    title: string;
    description: string;
    icon: React.ElementType;
    shortcut?: string;
    action: () => void;
    category: string;
}

export function CommandPalette({ isOpen, onClose, onToolSelect, activeTool }: CommandPaletteProps) {
    const [search, setSearch] = useState("");

    // Close on Escape
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.key === "Escape" && isOpen) {
                onClose();
            }
        };
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [isOpen, onClose]);

    const commands = useMemo<CommandItem[]>(() => [
        {
            id: "qa",
            title: "Q&A Mode",
            description: "Ask questions about your materials",
            icon: HelpCircle,
            shortcut: "1",
            category: "Learning",
            action: () => { onToolSelect("qa"); onClose(); },
        },
        {
            id: "study_guide",
            title: "Study Guide",
            description: "Generate comprehensive topic summaries",
            icon: BookOpen,
            shortcut: "2",
            category: "Learning",
            action: () => { onToolSelect("study_guide"); onClose(); },
        },
        {
            id: "quiz",
            title: "Quiz",
            description: "Test your knowledge",
            icon: Sparkles,
            shortcut: "3",
            category: "Practice",
            action: () => { onToolSelect("quiz"); onClose(); },
        },
        {
            id: "flashcards",
            title: "Flashcards",
            description: "Spaced repetition learning",
            icon: Layers,
            shortcut: "4",
            category: "Practice",
            action: () => { onToolSelect("flashcards"); onClose(); },
        },
        {
            id: "mindmap",
            title: "Mind Map",
            description: "Visual topic hierarchy",
            icon: Brain,
            shortcut: "5",
            category: "Visual",
            action: () => { onToolSelect("mindmap"); onClose(); },
        },
        {
            id: "debate",
            title: "Debate",
            description: "Challenge your ideas",
            icon: Swords,
            shortcut: "6",
            category: "Thinking",
            action: () => { onToolSelect("debate"); onClose(); },
        },
        {
            id: "socratic",
            title: "Socratic Tutor",
            description: "Guided discovery learning",
            icon: MessageSquare,
            category: "Learning",
            action: () => { onToolSelect("socratic"); onClose(); },
        },
    ], [onToolSelect, onClose]);

    const filteredCommands = useMemo(() => {
        if (!search) return commands;
        const lower = search.toLowerCase();
        return commands.filter(
            (cmd) =>
                cmd.title.toLowerCase().includes(lower) ||
                cmd.description.toLowerCase().includes(lower) ||
                cmd.category.toLowerCase().includes(lower)
        );
    }, [commands, search]);

    const groupedCommands = useMemo(() => {
        const groups: Record<string, CommandItem[]> = {};
        filteredCommands.forEach((cmd) => {
            if (!groups[cmd.category]) groups[cmd.category] = [];
            groups[cmd.category].push(cmd);
        });
        return groups;
    }, [filteredCommands]);

    if (!isOpen) return null;

    return (
        <div className="fixed inset-0 z-50 bg-black/50 flex items-start justify-center pt-[15vh] animate-in fade-in duration-200">
            <div className="w-full max-w-lg bg-[var(--bg-card)] rounded-2xl shadow-2xl border border-[var(--border)] overflow-hidden">
                {/* Header */}
                <div className="flex items-center gap-3 px-4 py-3 border-b border-[var(--border)]">
                    <Search className="w-5 h-5 text-[var(--text-muted)]" />
                    <input
                        type="text"
                        value={search}
                        onChange={(e) => setSearch(e.target.value)}
                        placeholder="Search tools, actions..."
                        className="flex-1 bg-transparent border-0 outline-none text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
                        autoFocus
                    />
                    <div className="flex items-center gap-1">
                        <kbd className="px-2 py-1 text-xs bg-[var(--bg-page)] border border-[var(--border)] rounded">
                            ESC
                        </kbd>
                        <button
                            onClick={onClose}
                            className="p-1.5 rounded hover:bg-[var(--surface-hover)] text-[var(--text-muted)]"
                        >
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Results */}
                <div className="max-h-[60vh] overflow-y-auto p-2">
                    {Object.keys(groupedCommands).length === 0 ? (
                        <div className="py-8 text-center text-[var(--text-muted)]">
                            <p>No results found</p>
                        </div>
                    ) : (
                        Object.entries(groupedCommands).map(([category, items]) => (
                            <div key={category} className="mb-2">
                                <div className="px-3 py-1.5 text-[10px] font-medium text-[var(--text-muted)] uppercase tracking-wider">
                                    {category}
                                </div>
                                {items.map((item) => (
                                    <button
                                        key={item.id}
                                        onClick={item.action}
                                        className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-left transition-colors ${
                                            activeTool === item.id
                                                ? "bg-[var(--primary-light)] text-[var(--primary)]"
                                                : "hover:bg-[var(--surface-hover)] text-[var(--text-primary)]"
                                        }`}
                                    >
                                        <item.icon className="w-4 h-4 text-[var(--text-muted)]" />
                                        <div className="flex-1">
                                            <p className="text-sm font-medium">{item.title}</p>
                                            <p className="text-[10px] text-[var(--text-muted)]">
                                                {item.description}
                                            </p>
                                        </div>
                                        {item.shortcut && (
                                            <kbd className="px-1.5 py-0.5 text-[10px] bg-[var(--bg-page)] border border-[var(--border)] rounded">
                                                {item.shortcut}
                                            </kbd>
                                        )}
                                    </button>
                                ))}
                            </div>
                        ))
                    )}
                </div>

                {/* Footer */}
                <div className="px-4 py-2 border-t border-[var(--border)] bg-[var(--surface-hover)] text-[10px] text-[var(--text-muted)]">
                    <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                            <kbd className="px-1 bg-[var(--bg-card)] border border-[var(--border)] rounded">↑↓</kbd>
                            Navigate
                        </span>
                        <span className="flex items-center gap-1">
                            <kbd className="px-1 bg-[var(--bg-card)] border border-[var(--border)] rounded">Enter</kbd>
                            Select
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
