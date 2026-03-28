"use client";

import { useEffect, useState, useCallback } from "react";
import { useRouter } from "next/navigation";
import {
    Library,
    Search,
    Pin,
    Trash2,
    Plus,
    Grid,
    List,
    Clock,
    Loader2,
    FolderOpen,
} from "lucide-react";
import { api } from "@/lib/api";

interface AIHistoryItem {
    id: string;
    mode: string;
    query_text: string;
    response_text: string;
    title: string | null;
    created_at: string;
    token_usage: number | null;
    citation_count: number;
    is_pinned: boolean;
    folder_id: string | null;
    folder_name: string | null;
}

interface AIFolder {
    id: string;
    name: string;
    color: string;
    item_count: number;
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

const modeLabels: Record<string, string> = {
    qa: "Q&A",
    study_guide: "Study Guide",
    quiz: "Quiz",
    mindmap: "Mind Map",
    flowchart: "Flowchart",
    flashcards: "Flashcards",
    concept_map: "Concept Map",
    socratic: "Socratic",
    perturbation: "Exam Prep",
    debate: "Debate",
    essay_review: "Essay Review",
    weak_topic: "Weak Topics",
};

const folderColors: Record<string, string> = {
    blue: "bg-blue-500",
    green: "bg-green-500",
    purple: "bg-purple-500",
    orange: "bg-orange-500",
    pink: "bg-pink-500",
    red: "bg-red-500",
    yellow: "bg-yellow-500",
};

export default function AILibraryPage() {
    const router = useRouter();
    const [items, setItems] = useState<AIHistoryItem[]>([]);
    const [folders, setFolders] = useState<AIFolder[]>([]);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<"grid" | "list">("grid");
    const [searchQuery, setSearchQuery] = useState("");
    const [selectedFolder, setSelectedFolder] = useState<string | null>(null);
    const [selectedMode, setSelectedMode] = useState<string | null>(null);
    const [showPinnedOnly, setShowPinnedOnly] = useState(false);
    const [page, setPage] = useState(1);
    const [hasMore, setHasMore] = useState(true);
    const [stats, setStats] = useState({ total_queries: 0, queries_this_week: 0, queries_this_month: 0 });

    const loadData = useCallback(async () => {
        try {
            setLoading(true);
            const [historyRes, foldersRes, statsRes] = await Promise.all([
                api.aiHistory.list({
                    page,
                    folder_id: selectedFolder || undefined,
                    mode: selectedMode || undefined,
                    is_pinned: showPinnedOnly || undefined,
                    search: searchQuery || undefined,
                }),
                api.aiHistory.folders.list(),
                api.aiHistory.stats(),
            ]);
            setItems(historyRes.items || []);
            setFolders(foldersRes.folders || []);
            setHasMore(historyRes.has_more);
            setStats(statsRes);
        } catch (err) {
            console.error("Failed to load AI library:", err);
        } finally {
            setLoading(false);
        }
    }, [page, selectedFolder, selectedMode, showPinnedOnly, searchQuery]);

    useEffect(() => {
        loadData();
    }, [loadData]);

    const handlePin = async (id: string) => {
        try {
            await api.aiHistory.togglePin(id);
            loadData();
        } catch (err) {
            console.error("Failed to pin item:", err);
        }
    };

    const handleDelete = async (id: string) => {
        if (!confirm("Delete this item?")) return;
        try {
            await api.aiHistory.delete(id);
            loadData();
        } catch (err) {
            console.error("Failed to delete item:", err);
        }
    };

    const handleCreateFolder = async () => {
        const name = prompt("Folder name:");
        if (!name) return;
        try {
            await api.aiHistory.folders.create(name);
            loadData();
        } catch (err) {
            console.error("Failed to create folder:", err);
        }
    };

    const formatDate = (dateStr: string) => {
        const date = new Date(dateStr);
        const now = new Date();
        const diff = now.getTime() - date.getTime();
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (days === 0) return "Today";
        if (days === 1) return "Yesterday";
        if (days < 7) return `${days} days ago`;
        return date.toLocaleDateString();
    };

    const getPreview = (item: AIHistoryItem) => {
        if (item.title) return item.title;
        return item.query_text.slice(0, 60) + (item.query_text.length > 60 ? "..." : "");
    };

    return (
        <div className="flex h-[calc(100vh-4rem)]">
            {/* Sidebar */}
            <div className="w-64 border-r border-[var(--border)] bg-[var(--surface)] p-4 overflow-y-auto">
                <div className="flex items-center gap-2 mb-6">
                    <Library className="w-5 h-5 text-[var(--primary)]" />
                    <h2 className="font-semibold text-[var(--text-primary)]">AI Library</h2>
                </div>

                {/* Stats */}
                <div className="mb-6 p-3 bg-[var(--surface-hover)] rounded-lg">
                    <div className="text-2xl font-bold text-[var(--primary)]">{stats.total_queries}</div>
                    <div className="text-xs text-[var(--text-secondary)]">Total AI queries</div>
                    <div className="mt-2 flex gap-4 text-xs text-[var(--text-secondary)]">
                        <span>{stats.queries_this_week} this week</span>
                        <span>{stats.queries_this_month} this month</span>
                    </div>
                </div>

                {/* Filters */}
                <div className="space-y-2 mb-6">
                    <button
                        onClick={() => { setSelectedFolder(null); setSelectedMode(null); setShowPinnedOnly(false); }}
                        className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                            !selectedFolder && !selectedMode && !showPinnedOnly
                                ? "bg-[var(--primary)] text-white"
                                : "hover:bg-[var(--surface-hover)] text-[var(--text-primary)]"
                        }`}
                    >
                        <FolderOpen className="w-4 h-4" />
                        All Items
                    </button>
                    <button
                        onClick={() => setShowPinnedOnly(!showPinnedOnly)}
                        className={`w-full flex items-center gap-2 px-3 py-2 rounded-lg text-sm transition-colors ${
                            showPinnedOnly
                                ? "bg-[var(--primary)] text-white"
                                : "hover:bg-[var(--surface-hover)] text-[var(--text-primary)]"
                        }`}
                    >
                        <Pin className="w-4 h-4" />
                        Pinned
                    </button>
                </div>

                {/* Mode Filters */}
                <div className="mb-4">
                    <h3 className="text-xs font-medium text-[var(--text-secondary)] uppercase mb-2">By Type</h3>
                    <div className="space-y-1">
                        {Object.entries(modeLabels).map(([mode, label]) => (
                            <button
                                key={mode}
                                onClick={() => setSelectedMode(selectedMode === mode ? null : mode)}
                                className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                                    selectedMode === mode
                                        ? "bg-[var(--primary-subtle)] text-[var(--primary)]"
                                        : "hover:bg-[var(--surface-hover)] text-[var(--text-secondary)]"
                                }`}
                            >
                                <span>{modeIcons[mode]}</span>
                                <span className="truncate">{label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Folders */}
                <div>
                    <div className="flex items-center justify-between mb-2">
                        <h3 className="text-xs font-medium text-[var(--text-secondary)] uppercase">Folders</h3>
                        <button
                            onClick={handleCreateFolder}
                            className="p-1 hover:bg-[var(--surface-hover)] rounded"
                        >
                            <Plus className="w-4 h-4 text-[var(--text-secondary)]" />
                        </button>
                    </div>
                    <div className="space-y-1">
                        {folders.map((folder) => (
                            <button
                                key={folder.id}
                                onClick={() => setSelectedFolder(selectedFolder === folder.id ? null : folder.id)}
                                className={`w-full flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm transition-colors ${
                                    selectedFolder === folder.id
                                        ? "bg-[var(--primary-subtle)] text-[var(--primary)]"
                                        : "hover:bg-[var(--surface-hover)] text-[var(--text-secondary)]"
                                }`}
                            >
                                <div className={`w-3 h-3 rounded-full ${folderColors[folder.color] || "bg-gray-400"}`} />
                                <span className="truncate flex-1 text-left">{folder.name}</span>
                                <span className="text-xs opacity-60">{folder.item_count}</span>
                            </button>
                        ))}
                    </div>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1 flex flex-col overflow-hidden">
                {/* Header */}
                <div className="p-4 border-b border-[var(--border)] flex items-center gap-4">
                    <div className="flex-1 relative">
                        <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-secondary)]" />
                        <input
                            type="text"
                            placeholder="Search your AI history..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-10 pr-4 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                        />
                    </div>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={() => setViewMode("grid")}
                            className={`p-2 rounded-lg transition-colors ${
                                viewMode === "grid" ? "bg-[var(--primary-subtle)] text-[var(--primary)]" : "hover:bg-[var(--surface-hover)]"
                            }`}
                        >
                            <Grid className="w-4 h-4" />
                        </button>
                        <button
                            onClick={() => setViewMode("list")}
                            className={`p-2 rounded-lg transition-colors ${
                                viewMode === "list" ? "bg-[var(--primary-subtle)] text-[var(--primary)]" : "hover:bg-[var(--surface-hover)]"
                            }`}
                        >
                            <List className="w-4 h-4" />
                        </button>
                    </div>
                </div>

                {/* Items Grid/List */}
                <div className="flex-1 overflow-y-auto p-4">
                    {loading && items.length === 0 ? (
                        <div className="flex items-center justify-center h-full">
                            <Loader2 className="w-8 h-8 animate-spin text-[var(--primary)]" />
                        </div>
                    ) : items.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-full text-[var(--text-secondary)]">
                            <Library className="w-16 h-16 mb-4 opacity-50" />
                            <p>No AI history yet</p>
                            <p className="text-sm mt-1">Start using AI features to build your library</p>
                        </div>
                    ) : viewMode === "grid" ? (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {items.map((item) => (
                                <div
                                    key={item.id}
                                    className="group bg-[var(--surface)] border border-[var(--border)] rounded-lg p-4 hover:border-[var(--primary)] hover:shadow-md transition-all cursor-pointer"
                                    onClick={() => router.push(`/student/ai?history=${item.id}`)}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            <span className="text-lg">{modeIcons[item.mode]}</span>
                                            <span className="text-xs font-medium px-2 py-0.5 bg-[var(--surface-hover)] rounded-full text-[var(--text-secondary)]">
                                                {modeLabels[item.mode]}
                                            </span>
                                        </div>
                                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={(e) => { e.stopPropagation(); handlePin(item.id); }}
                                                className={`p-1.5 rounded ${item.is_pinned ? "text-[var(--primary)]" : "hover:bg-[var(--surface-hover)]"}`}
                                            >
                                                <Pin className={`w-4 h-4 ${item.is_pinned ? "fill-current" : ""}`} />
                                            </button>
                                            <button
                                                onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                                                className="p-1.5 hover:bg-red-100 text-red-500 rounded"
                                            >
                                                <Trash2 className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                    <h3 className="font-medium text-[var(--text-primary)] mb-2 line-clamp-2">
                                        {getPreview(item)}
                                    </h3>
                                    <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)]">
                                        <Clock className="w-3 h-3" />
                                        <span>{formatDate(item.created_at)}</span>
                                        {item.citation_count > 0 && (
                                            <span className="ml-auto">📚 {item.citation_count} sources</span>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    ) : (
                        <div className="space-y-2">
                            {items.map((item) => (
                                <div
                                    key={item.id}
                                    className="group flex items-center gap-4 p-3 bg-[var(--surface)] border border-[var(--border)] rounded-lg hover:border-[var(--primary)] cursor-pointer"
                                    onClick={() => router.push(`/student/ai?history=${item.id}`)}
                                >
                                    <span className="text-xl">{modeIcons[item.mode]}</span>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-medium text-[var(--text-primary)] truncate">
                                            {getPreview(item)}
                                        </h3>
                                        <div className="flex items-center gap-3 text-xs text-[var(--text-secondary)] mt-1">
                                            <span className="px-2 py-0.5 bg-[var(--surface-hover)] rounded-full">
                                                {modeLabels[item.mode]}
                                            </span>
                                            <span>{formatDate(item.created_at)}</span>
                                            {item.citation_count > 0 && (
                                                <span>📚 {item.citation_count} sources</span>
                                            )}
                                        </div>
                                    </div>
                                    <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                        <button
                                            onClick={(e) => { e.stopPropagation(); handlePin(item.id); }}
                                            className={`p-1.5 rounded ${item.is_pinned ? "text-[var(--primary)]" : "hover:bg-[var(--surface-hover)]"}`}
                                        >
                                            <Pin className={`w-4 h-4 ${item.is_pinned ? "fill-current" : ""}`} />
                                        </button>
                                        <button
                                            onClick={(e) => { e.stopPropagation(); handleDelete(item.id); }}
                                            className="p-1.5 hover:bg-red-100 text-red-500 rounded"
                                        >
                                            <Trash2 className="w-4 h-4" />
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}

                    {hasMore && !loading && (
                        <div className="flex justify-center mt-6">
                            <button
                                onClick={() => setPage(page + 1)}
                                className="px-4 py-2 bg-[var(--surface)] border border-[var(--border)] rounded-lg text-sm hover:bg-[var(--surface-hover)] transition-colors"
                            >
                                Load More
                            </button>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
