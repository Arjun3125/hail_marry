"use client";

import { useCallback, useEffect, useState } from "react";
import { Book, Check, ChevronDown, Edit2, Plus, Search, Trash2, X } from "lucide-react";

import { api } from "@/lib/api";

interface Notebook {
    id: string;
    name: string;
    description?: string;
    subject?: string;
    color: string;
    icon: string;
    created_at: string;
    updated_at: string;
    is_active: boolean;
}

interface NotebookSelectorProps {
    activeNotebookId: string | null;
    onNotebookChange: (notebookId: string | null) => void;
    onCreateNotebook?: () => void;
}

export function NotebookSelector({ activeNotebookId, onNotebookChange, onCreateNotebook }: NotebookSelectorProps) {
    const [notebooks, setNotebooks] = useState<Notebook[]>([]);
    const [loading, setLoading] = useState(true);
    const [isOpen, setIsOpen] = useState(false);
    const [editingNotebook, setEditingNotebook] = useState<Notebook | null>(null);
    const [editName, setEditName] = useState("");
    const [search, setSearch] = useState("");
    const [showCreateForm, setShowCreateForm] = useState(false);
    const [createName, setCreateName] = useState("");
    const [createSubject, setCreateSubject] = useState("");
    const [createColor, setCreateColor] = useState("#6366f1");

    const fetchNotebooks = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.notebooks.list();
            const items = response.items || [];
            setNotebooks(items);
            if (!activeNotebookId && items.length > 0) {
                onNotebookChange(items[0].id);
            }
        } catch (err) {
            console.error("Failed to fetch notebooks:", err);
        } finally {
            setLoading(false);
        }
    }, [activeNotebookId, onNotebookChange]);

    useEffect(() => {
        void fetchNotebooks();
    }, [fetchNotebooks]);

    const activeNotebook = notebooks.find((notebook) => notebook.id === activeNotebookId);
    const filteredNotebooks = notebooks.filter((notebook) => {
        const haystack = `${notebook.name} ${notebook.subject || ""}`.toLowerCase();
        return haystack.includes(search.toLowerCase());
    });

    const handleCreate = async () => {
        if (!createName.trim()) return;

        try {
            const newNotebook = await api.notebooks.create({
                name: createName.trim(),
                subject: createSubject.trim() || undefined,
                color: createColor,
            });
            setNotebooks((prev) => [newNotebook, ...prev]);
            onNotebookChange(newNotebook.id);
            onCreateNotebook?.();
            setCreateName("");
            setCreateSubject("");
            setCreateColor("#6366f1");
            setShowCreateForm(false);
            setSearch("");
        } catch (err) {
            console.error("Failed to create notebook:", err);
            alert("Failed to create notebook");
        }
    };

    const handleRename = async (notebook: Notebook) => {
        if (!editName.trim() || editName === notebook.name) {
            setEditingNotebook(null);
            return;
        }

        try {
            await api.notebooks.update(notebook.id, { name: editName.trim() });
            setNotebooks((prev) =>
                prev.map((item) => (item.id === notebook.id ? { ...item, name: editName.trim() } : item))
            );
            setEditingNotebook(null);
        } catch (err) {
            console.error("Failed to rename notebook:", err);
            alert("Failed to rename notebook");
        }
    };

    const handleDelete = async (notebookId: string) => {
        if (!confirm("Are you sure you want to archive this notebook?")) return;

        try {
            await api.notebooks.delete(notebookId);
            setNotebooks((prev) => prev.filter((item) => item.id !== notebookId));
            if (activeNotebookId === notebookId) {
                const nextNotebook = notebooks.find((item) => item.id !== notebookId);
                onNotebookChange(nextNotebook?.id || null);
            }
        } catch (err) {
            console.error("Failed to delete notebook:", err);
            alert("Failed to delete notebook");
        }
    };

    if (loading) {
        return (
            <div className="p-3 border-b border-[var(--border)]">
                <div className="flex items-center gap-2 text-[var(--text-muted)]">
                    <Book className="w-4 h-4 animate-pulse" />
                    <span className="text-sm">Loading notebooks...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="border-b border-[var(--border)]">
            <button
                onClick={() => setIsOpen((prev) => !prev)}
                className="w-full flex items-center justify-between p-3 hover:bg-[var(--surface-hover)] transition-colors"
            >
                <div className="flex items-center gap-2">
                    <div
                        className="w-8 h-8 rounded-lg flex items-center justify-center"
                        style={{ backgroundColor: activeNotebook?.color || "#6366f1" }}
                    >
                        <Book className="w-4 h-4 text-white" />
                    </div>
                    <div className="text-left">
                        <p className="text-sm font-medium text-[var(--text-primary)]">
                            {activeNotebook?.name || "Select Notebook"}
                        </p>
                        <p className="text-xs text-[var(--text-muted)]">
                            {notebooks.length} notebook{notebooks.length !== 1 ? "s" : ""}
                        </p>
                    </div>
                </div>
                <ChevronDown className={`w-4 h-4 text-[var(--text-muted)] transition-transform ${isOpen ? "rotate-180" : ""}`} />
            </button>

            {isOpen ? (
                <div className="border-t border-[var(--border)] bg-[var(--bg-page)]">
                    <div className="p-2 border-b border-[var(--border)] space-y-2">
                        <div className="relative">
                            <Search className="w-3.5 h-3.5 text-[var(--text-muted)] absolute left-3 top-1/2 -translate-y-1/2" />
                            <input
                                type="text"
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                placeholder="Search notebooks"
                                className="w-full pl-9 pr-3 py-2 text-sm bg-[var(--bg-card)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
                            />
                        </div>

                        {showCreateForm ? (
                            <div className="rounded-lg border border-[var(--border)] bg-[var(--bg-card)] p-2 space-y-2">
                                <input
                                    type="text"
                                    value={createName}
                                    onChange={(e) => setCreateName(e.target.value)}
                                    placeholder="Notebook name"
                                    className="w-full px-3 py-2 text-sm bg-[var(--bg-page)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
                                />
                                <div className="flex items-center gap-2">
                                    <input
                                        type="text"
                                        value={createSubject}
                                        onChange={(e) => setCreateSubject(e.target.value)}
                                        placeholder="Subject"
                                        className="flex-1 px-3 py-2 text-sm bg-[var(--bg-page)] border border-[var(--border)] rounded-lg text-[var(--text-primary)]"
                                    />
                                    <input
                                        type="color"
                                        value={createColor}
                                        onChange={(e) => setCreateColor(e.target.value)}
                                        className="h-10 w-12 rounded border border-[var(--border)] bg-transparent"
                                        aria-label="Notebook color"
                                    />
                                </div>
                                <div className="flex items-center justify-end gap-2">
                                    <button
                                        onClick={() => setShowCreateForm(false)}
                                        className="px-3 py-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleCreate}
                                        disabled={!createName.trim()}
                                        className="px-3 py-1.5 text-xs rounded-md bg-[var(--primary)] text-white disabled:opacity-50"
                                    >
                                        Save
                                    </button>
                                </div>
                            </div>
                        ) : null}
                    </div>

                    <div className="max-h-56 overflow-y-auto py-1">
                        {filteredNotebooks.length === 0 ? (
                            <div className="px-3 py-2 text-sm text-[var(--text-muted)]">
                                {notebooks.length === 0 ? "No notebooks yet" : "No notebooks match your search"}
                            </div>
                        ) : (
                            filteredNotebooks.map((notebook) => (
                                <div
                                    key={notebook.id}
                                    className={`group flex items-center justify-between px-3 py-2 hover:bg-[var(--surface-hover)] cursor-pointer ${
                                        activeNotebookId === notebook.id ? "bg-[var(--primary-light)]" : ""
                                    }`}
                                    onClick={() => {
                                        onNotebookChange(notebook.id);
                                        setIsOpen(false);
                                    }}
                                >
                                    {editingNotebook?.id === notebook.id ? (
                                        <div className="flex-1 flex items-center gap-2" onClick={(e) => e.stopPropagation()}>
                                            <input
                                                type="text"
                                                value={editName}
                                                onChange={(e) => setEditName(e.target.value)}
                                                className="flex-1 px-2 py-1 text-sm bg-[var(--bg-card)] border border-[var(--border)] rounded"
                                                autoFocus
                                                onKeyDown={(e) => {
                                                    if (e.key === "Enter") void handleRename(notebook);
                                                    if (e.key === "Escape") setEditingNotebook(null);
                                                }}
                                            />
                                            <button
                                                onClick={() => void handleRename(notebook)}
                                                className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                                            >
                                                <Check className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex items-center gap-2 flex-1 min-w-0">
                                                <div
                                                    className="w-6 h-6 rounded flex items-center justify-center"
                                                    style={{ backgroundColor: notebook.color }}
                                                >
                                                    <Book className="w-3 h-3 text-white" />
                                                </div>
                                                <span className="text-sm text-[var(--text-primary)] truncate">
                                                    {notebook.name}
                                                </span>
                                                {notebook.subject ? (
                                                    <span className="text-[10px] px-1.5 py-0.5 rounded bg-[var(--bg-card)] text-[var(--text-muted)] border border-[var(--border)]">
                                                        {notebook.subject}
                                                    </span>
                                                ) : null}
                                            </div>
                                            {activeNotebookId === notebook.id ? (
                                                <Check className="w-4 h-4 text-[var(--primary)]" />
                                            ) : null}
                                        </>
                                    )}

                                    {editingNotebook?.id !== notebook.id ? (
                                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    setEditingNotebook(notebook);
                                                    setEditName(notebook.name);
                                                }}
                                                className="p-1 text-[var(--text-muted)] hover:text-[var(--text-primary)] hover:bg-[var(--surface-hover)] rounded"
                                            >
                                                <Edit2 className="w-3 h-3" />
                                            </button>
                                            <button
                                                onClick={(e) => {
                                                    e.stopPropagation();
                                                    void handleDelete(notebook.id);
                                                }}
                                                className="p-1 text-[var(--text-muted)] hover:text-red-600 hover:bg-red-50 rounded"
                                            >
                                                <Trash2 className="w-3 h-3" />
                                            </button>
                                        </div>
                                    ) : null}
                                </div>
                            ))
                        )}
                    </div>

                    <div className="border-t border-[var(--border)] p-2">
                        <button
                            onClick={() => {
                                setShowCreateForm((prev) => !prev);
                                setSearch("");
                            }}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-[var(--primary)] hover:bg-[var(--primary-light)] rounded-lg transition-colors"
                        >
                            {showCreateForm ? <X className="w-4 h-4" /> : <Plus className="w-4 h-4" />}
                            {showCreateForm ? "Close" : "Create Notebook"}
                        </button>
                    </div>
                </div>
            ) : null}
        </div>
    );
}
