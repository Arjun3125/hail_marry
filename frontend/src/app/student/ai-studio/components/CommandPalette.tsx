"use client";

import { useEffect, useMemo, useState } from "react";
import {
    BookOpen,
    Brain,
    HelpCircle,
    Layers,
    MessageSquare,
    Search,
    Sparkles,
    Swords,
    X,
    type LucideIcon,
} from "lucide-react";

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
    icon: LucideIcon;
    shortcut?: string;
    action: () => void;
    category: string;
}

export function CommandPalette({
    isOpen,
    onClose,
    onToolSelect,
    activeTool,
}: CommandPaletteProps) {
    const [search, setSearch] = useState("");

    useEffect(() => {
        const handleKeyDown = (event: KeyboardEvent) => {
            if (event.key === "Escape" && isOpen) {
                onClose();
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [isOpen, onClose]);

    const commands = useMemo<CommandItem[]>(
        () => [
            {
                id: "qa",
                title: "Q&A Mode",
                description: "Ask questions about your materials",
                icon: HelpCircle,
                shortcut: "1",
                category: "Learning",
                action: () => {
                    onToolSelect("qa");
                    onClose();
                },
            },
            {
                id: "study_guide",
                title: "Study Guide",
                description: "Generate comprehensive topic summaries",
                icon: BookOpen,
                shortcut: "2",
                category: "Learning",
                action: () => {
                    onToolSelect("study_guide");
                    onClose();
                },
            },
            {
                id: "quiz",
                title: "Quiz",
                description: "Test your knowledge",
                icon: Sparkles,
                shortcut: "3",
                category: "Practice",
                action: () => {
                    onToolSelect("quiz");
                    onClose();
                },
            },
            {
                id: "flashcards",
                title: "Flashcards",
                description: "Spaced repetition learning",
                icon: Layers,
                shortcut: "4",
                category: "Practice",
                action: () => {
                    onToolSelect("flashcards");
                    onClose();
                },
            },
            {
                id: "mindmap",
                title: "Mind Map",
                description: "Visual topic hierarchy",
                icon: Brain,
                shortcut: "5",
                category: "Visual",
                action: () => {
                    onToolSelect("mindmap");
                    onClose();
                },
            },
            {
                id: "debate",
                title: "Debate",
                description: "Challenge your ideas",
                icon: Swords,
                shortcut: "6",
                category: "Thinking",
                action: () => {
                    onToolSelect("debate");
                    onClose();
                },
            },
            {
                id: "socratic",
                title: "Socratic Tutor",
                description: "Guided discovery learning",
                icon: MessageSquare,
                category: "Learning",
                action: () => {
                    onToolSelect("socratic");
                    onClose();
                },
            },
        ],
        [onClose, onToolSelect]
    );

    const filteredCommands = useMemo(() => {
        if (!search) {
            return commands;
        }

        const searchTerm = search.toLowerCase();
        return commands.filter(
            (command) =>
                command.title.toLowerCase().includes(searchTerm) ||
                command.description.toLowerCase().includes(searchTerm) ||
                command.category.toLowerCase().includes(searchTerm)
        );
    }, [commands, search]);

    const groupedCommands = useMemo(() => {
        const groups: Record<string, CommandItem[]> = {};

        filteredCommands.forEach((command) => {
            if (!groups[command.category]) {
                groups[command.category] = [];
            }

            groups[command.category].push(command);
        });

        return groups;
    }, [filteredCommands]);

    if (!isOpen) {
        return null;
    }

    return (
        <div className="animate-in fade-in fixed inset-0 z-50 flex items-start justify-center bg-black/50 pt-[15vh] duration-200">
            <div className="w-full max-w-lg overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] shadow-2xl">
                <div className="flex items-center gap-3 border-b border-[var(--border)] px-4 py-3">
                    <Search className="h-5 w-5 text-[var(--text-muted)]" />
                    <input
                        type="text"
                        value={search}
                        onChange={(event) => setSearch(event.target.value)}
                        placeholder="Search tools, actions..."
                        className="flex-1 border-0 bg-transparent text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)]"
                        autoFocus
                    />
                    <div className="flex items-center gap-1">
                        <kbd className="rounded border border-[var(--border)] bg-[var(--bg-page)] px-2 py-1 text-xs">
                            ESC
                        </kbd>
                        <button
                            onClick={onClose}
                            className="rounded p-1.5 text-[var(--text-muted)] hover:bg-[var(--surface-hover)]"
                        >
                            <X className="h-4 w-4" />
                        </button>
                    </div>
                </div>

                <div className="max-h-[60vh] overflow-y-auto p-2">
                    {Object.keys(groupedCommands).length === 0 ? (
                        <div className="py-8 text-center text-[var(--text-muted)]">
                            <p>No results found</p>
                        </div>
                    ) : (
                        Object.entries(groupedCommands).map(([category, items]) => (
                            <div key={category} className="mb-2">
                                <div className="px-3 py-1.5 text-[10px] font-medium uppercase tracking-wider text-[var(--text-muted)]">
                                    {category}
                                </div>
                                {items.map((item) => {
                                    const Icon = item.icon;

                                    return (
                                        <button
                                            key={item.id}
                                            onClick={item.action}
                                            className={`w-full rounded-lg px-3 py-2.5 text-left transition-colors ${
                                                activeTool === item.id
                                                    ? "bg-[var(--primary-light)] text-[var(--primary)]"
                                                    : "text-[var(--text-primary)] hover:bg-[var(--surface-hover)]"
                                            }`}
                                        >
                                            <div className="flex items-center gap-3">
                                                <Icon className="h-4 w-4 text-[var(--text-muted)]" />
                                                <div className="flex-1">
                                                    <p className="text-sm font-medium">{item.title}</p>
                                                    <p className="text-[10px] text-[var(--text-muted)]">
                                                        {item.description}
                                                    </p>
                                                </div>
                                                {item.shortcut ? (
                                                    <kbd className="rounded border border-[var(--border)] bg-[var(--bg-page)] px-1.5 py-0.5 text-[10px]">
                                                        {item.shortcut}
                                                    </kbd>
                                                ) : null}
                                            </div>
                                        </button>
                                    );
                                })}
                            </div>
                        ))
                    )}
                </div>

                <div className="border-t border-[var(--border)] bg-[var(--surface-hover)] px-4 py-2 text-[10px] text-[var(--text-muted)]">
                    <div className="flex items-center gap-4">
                        <span className="flex items-center gap-1">
                            <kbd className="rounded border border-[var(--border)] bg-[var(--bg-card)] px-1">
                                Up/Down
                            </kbd>
                            Navigate
                        </span>
                        <span className="flex items-center gap-1">
                            <kbd className="rounded border border-[var(--border)] bg-[var(--bg-card)] px-1">
                                Enter
                            </kbd>
                            Select
                        </span>
                    </div>
                </div>
            </div>
        </div>
    );
}
