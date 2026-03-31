"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
    History,
    Pin,
    Clock,
    ChevronRight,
    Loader2,
    X,
} from "lucide-react";
import { api } from "@/lib/api";

interface AIHistorySidebarProps {
    currentMode?: string;
    onSelectItem?: (item: AIHistoryItem) => void;
    className?: string;
}

interface AIHistoryItem {
    id: string;
    mode: string;
    query_text: string;
    response_text: string;
    title: string | null;
    created_at: string;
    is_pinned: boolean;
}

const modeIcons: Record<string, string> = {
    qa: "❓",
    study_guide: "📚",
    quiz: "❓",
    mindmap: "🧠",
    flowchart: "📊",
    flashcards: "🎴",
    concept_map: "🕸️",
    socratic: "🗣️",
    perturbation: "🔄",
    debate: "⚔️",
    essay_review: "✍️",
    weak_topic: "📉",
};

export default function AIHistorySidebar({
    currentMode,
    onSelectItem,
    className = "",
}: AIHistorySidebarProps) {
    const router = useRouter();
    const [items, setItems] = useState<AIHistoryItem[]>([]);
    const [loading, setLoading] = useState(true);
    const [expanded, setExpanded] = useState(false);
    const [activeTab, setActiveTab] = useState<"recent" | "pinned">("recent");

    const loadHistory = useCallback(async () => {
        try {
            setLoading(true);
            const params: Record<string, string | number | boolean | undefined> = { page: 1, page_size: expanded ? 20 : 5 };
            if (currentMode) {
                params.mode = currentMode;
            }
            if (activeTab === "pinned") {
                params.is_pinned = true;
            }
            const res = await api.aiHistory.list(params);
            setItems(res.items || []);
        } catch (err) {
            console.error("Failed to load AI history:", err);
        } finally {
            setLoading(false);
        }
    }, [currentMode, activeTab, expanded]);

    useEffect(() => {
        loadHistory();
    }, [loadHistory]);;

    const handlePin = async (e: React.MouseEvent, id: string) => {
        e.stopPropagation();
        try {
            await api.aiHistory.togglePin(id);
            loadHistory();
        } catch (err) {
            console.error("Failed to pin item:", err);
        }
    };

    const handleSelect = (item: AIHistoryItem) => {
        if (onSelectItem) {
            onSelectItem(item);
        } else {
            router.push(`/student/ai-studio?history=${item.id}`);
        }
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));

        if (days === 0) return "Today";
        if (days === 1) return "Yesterday";
        if (days < 7) return `${days}d ago`;
        return date.toLocaleDateString(undefined, { month: "short", day: "numeric" });
    };

    const getPreview = (item: AIHistoryItem) => {
        if (item.title) return item.title;
        return item.query_text.slice(0, 50) + (item.query_text.length > 50 ? "..." : "");
    };

    if (!expanded) {
        // Collapsed view - show just recent items in a compact bar
        return (
            <div className={`bg-[var(--surface)] border border-[var(--border)] rounded-lg ${className}`}>
                <div
                    className="flex items-center justify-between px-3 py-2 cursor-pointer hover:bg-[var(--surface-hover)] rounded-t-lg"
                    onClick={() => setExpanded(true)}
                >
                    <div className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                        <History className="w-4 h-4" />
                        <span>Recent History</span>
                    </div>
                    <ChevronRight className="w-4 h-4 text-[var(--text-secondary)]" />
                </div>
                {loading ? (
                    <div className="px-3 py-2">
                        <Loader2 className="w-4 h-4 animate-spin text-[var(--text-secondary)]" />
                    </div>
                ) : items.length > 0 ? (
                    <div className="px-2 pb-2">
                        {items.slice(0, 3).map((item) => (
                            <div
                                key={item.id}
                                onClick={() => handleSelect(item)}
                                className="flex items-center gap-2 px-2 py-1.5 text-sm rounded-md hover:bg-[var(--surface-hover)] cursor-pointer"
                            >
                                <span>{modeIcons[item.mode] || "🤖"}</span>
                                <span className="truncate flex-1 text-[var(--text-primary)]">
                                    {getPreview(item)}
                                </span>
                                <span className="text-xs text-[var(--text-secondary)]">
                                    {formatDate(item.created_at)}
                                </span>
                            </div>
                        ))}
                    </div>
                ) : (
                    <div className="px-3 py-2 text-xs text-[var(--text-secondary)]">
                        No history yet
                    </div>
                )}
            </div>
        );
    }

    // Expanded view
    return (
        <div className={`bg-[var(--surface)] border border-[var(--border)] rounded-lg ${className}`}>
            <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
                <div className="flex items-center gap-2">
                    <History className="w-5 h-5 text-[var(--primary)]" />
                    <h3 className="font-medium text-[var(--text-primary)]">AI History</h3>
                </div>
                <button
                    onClick={() => setExpanded(false)}
                    className="p-1 hover:bg-[var(--surface-hover)] rounded"
                >
                    <X className="w-4 h-4 text-[var(--text-secondary)]" />
                </button>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-[var(--border)]">
                <button
                    onClick={() => setActiveTab("recent")}
                    className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                        activeTab === "recent"
                            ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
                            : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                >
                    Recent
                </button>
                <button
                    onClick={() => setActiveTab("pinned")}
                    className={`flex-1 px-4 py-2 text-sm font-medium transition-colors ${
                        activeTab === "pinned"
                            ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
                            : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                >
                    Pinned
                </button>
            </div>

            {/* List */}
            <div className="max-h-96 overflow-y-auto">
                {loading ? (
                    <div className="flex items-center justify-center py-8">
                        <Loader2 className="w-6 h-6 animate-spin text-[var(--primary)]" />
                    </div>
                ) : items.length === 0 ? (
                    <div className="text-center py-8 text-[var(--text-secondary)]">
                        <History className="w-12 h-12 mx-auto mb-2 opacity-50" />
                        <p className="text-sm">
                            {activeTab === "pinned" ? "No pinned items" : "No history yet"}
                        </p>
                        <p className="text-xs mt-1">
                            {activeTab === "pinned"
                                ? "Pin items to access them quickly"
                                : "Start using AI features to build your history"}
                        </p>
                    </div>
                ) : (
                    <div className="divide-y divide-[var(--border)]">
                        {items.map((item) => (
                            <div
                                key={item.id}
                                onClick={() => handleSelect(item)}
                                className="group flex items-start gap-3 px-4 py-3 hover:bg-[var(--surface-hover)] cursor-pointer transition-colors"
                            >
                                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center bg-[var(--surface-hover)] rounded-lg">
                                    <span className="text-lg">{modeIcons[item.mode] || "🤖"}</span>
                                </div>
                                <div className="flex-1 min-w-0">
                                    <p className="text-sm font-medium text-[var(--text-primary)] truncate">
                                        {getPreview(item)}
                                    </p>
                                    <div className="flex items-center gap-2 mt-1">
                                        <Clock className="w-3 h-3 text-[var(--text-secondary)]" />
                                        <span className="text-xs text-[var(--text-secondary)]">
                                            {formatDate(item.created_at)}
                                        </span>
                                    </div>
                                </div>
                                <button
                                    onClick={(e) => handlePin(e, item.id)}
                                    className={`flex-shrink-0 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity ${
                                        item.is_pinned ? "opacity-100 text-[var(--primary)]" : "hover:bg-[var(--surface-hover)]"
                                    }`}
                                >
                                    <Pin className={`w-4 h-4 ${item.is_pinned ? "fill-current" : ""}`} />
                                </button>
                            </div>
                        ))}
                    </div>
                )}
            </div>

            {/* Footer */}
            <div className="px-4 py-3 border-t border-[var(--border)]">
                <button
                    onClick={() => router.push("/student/ai-library")}
                    className="w-full text-center text-sm text-[var(--primary)] hover:underline"
                >
                    View Full Library →
                </button>
            </div>
        </div>
    );
}
