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
        } catch (error) {
            console.error("Failed to fetch notebooks:", error);
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
        } catch (error) {
            console.error("Failed to create notebook:", error);
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
        } catch (error) {
            console.error("Failed to rename notebook:", error);
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
        } catch (error) {
            console.error("Failed to delete notebook:", error);
            alert("Failed to delete notebook");
        }
    };

    if (loading) {
        return (
            <div className="border-b border-[var(--border)]/80 px-4 py-4">
                <div className="flex items-center gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-3 py-3 text-[var(--text-muted)]">
                    <Book className="h-4 w-4 animate-pulse" />
                    <span className="text-sm">Loading notebooks...</span>
                </div>
            </div>
        );
    }

    return (
        <div className="border-b border-[var(--border)]/80">
            <button
                onClick={() => setIsOpen((prev) => !prev)}
                className="w-full px-4 py-4 transition-colors hover:bg-[rgba(148,163,184,0.04)]"
            >
                <div className="flex items-center justify-between gap-3">
                    <div className="flex min-w-0 items-center gap-3">
                        <div
                            className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl shadow-[0_14px_24px_rgba(2,6,23,0.18)]"
                            style={{ backgroundColor: activeNotebook?.color || "#6366f1" }}
                        >
                            <Book className="h-5 w-5 text-white" />
                        </div>
                        <div className="min-w-0 text-left">
                            <p className="truncate text-sm font-semibold text-[var(--text-primary)]">
                                {activeNotebook?.name || "Select notebook"}
                            </p>
                            <p className="truncate text-[11px] leading-5 text-[var(--text-muted)]">
                                {activeNotebook?.subject || `${notebooks.length} notebook${notebooks.length !== 1 ? "s" : ""} available`}
                            </p>
                        </div>
                    </div>
                    <ChevronDown
                        className={`h-4 w-4 shrink-0 text-[var(--text-muted)] transition-transform ${
                            isOpen ? "rotate-180" : ""
                        }`}
                    />
                </div>
            </button>

            {isOpen ? (
                <div className="border-t border-[var(--border)]/80 bg-[rgba(148,163,184,0.04)]">
                    <div className="space-y-3 border-b border-[var(--border)]/80 p-3">
                        <div className="relative">
                            <Search className="absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-[var(--text-muted)]" />
                            <input
                                type="text"
                                value={search}
                                onChange={(event) => setSearch(event.target.value)}
                                placeholder="Search notebooks"
                                className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] py-2.5 pl-9 pr-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                            />
                        </div>

                        {showCreateForm ? (
                            <div className="space-y-2 rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.7)] p-3">
                                <input
                                    type="text"
                                    value={createName}
                                    onChange={(event) => setCreateName(event.target.value)}
                                    placeholder="Notebook name"
                                    className="w-full rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                />
                                <div className="flex items-center gap-2">
                                    <input
                                        type="text"
                                        value={createSubject}
                                        onChange={(event) => setCreateSubject(event.target.value)}
                                        placeholder="Subject"
                                        className="flex-1 rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-2 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                    />
                                    <input
                                        type="color"
                                        value={createColor}
                                        onChange={(event) => setCreateColor(event.target.value)}
                                        className="h-10 w-12 rounded-xl border border-[var(--border)] bg-transparent"
                                        aria-label="Notebook color"
                                    />
                                </div>
                                <div className="flex items-center justify-end gap-2 pt-1">
                                    <button
                                        onClick={() => setShowCreateForm(false)}
                                        className="rounded-xl px-3 py-1.5 text-xs font-medium text-[var(--text-muted)] transition hover:text-[var(--text-primary)]"
                                    >
                                        Cancel
                                    </button>
                                    <button
                                        onClick={handleCreate}
                                        disabled={!createName.trim()}
                                        className="rounded-xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.92))] px-3 py-1.5 text-xs font-semibold text-[#06101e] disabled:opacity-50"
                                    >
                                        Create
                                    </button>
                                </div>
                            </div>
                        ) : null}
                    </div>

                    <div className="max-h-64 overflow-y-auto px-2 py-2">
                        {filteredNotebooks.length === 0 ? (
                            <div className="px-3 py-4 text-sm text-[var(--text-muted)]">
                                {notebooks.length === 0 ? "No notebooks yet" : "No notebooks match your search"}
                            </div>
                        ) : (
                            filteredNotebooks.map((notebook) => (
                                <div
                                    key={notebook.id}
                                    className={`group flex cursor-pointer items-center justify-between rounded-2xl px-3 py-2.5 transition ${
                                        activeNotebookId === notebook.id
                                            ? "bg-[rgba(96,165,250,0.12)]"
                                            : "hover:bg-[rgba(148,163,184,0.06)]"
                                    }`}
                                    onClick={() => {
                                        onNotebookChange(notebook.id);
                                        setIsOpen(false);
                                    }}
                                >
                                    {editingNotebook?.id === notebook.id ? (
                                        <div className="flex flex-1 items-center gap-2" onClick={(event) => event.stopPropagation()}>
                                            <input
                                                type="text"
                                                value={editName}
                                                onChange={(event) => setEditName(event.target.value)}
                                                className="flex-1 rounded-xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-2 py-1.5 text-sm text-[var(--text-primary)] outline-none"
                                                autoFocus
                                                onKeyDown={(event) => {
                                                    if (event.key === "Enter") void handleRename(notebook);
                                                    if (event.key === "Escape") setEditingNotebook(null);
                                                }}
                                            />
                                            <button
                                                onClick={() => void handleRename(notebook)}
                                                className="rounded-lg p-1 text-status-emerald transition hover:bg-[rgba(16,185,129,0.12)]"
                                            >
                                                <Check className="h-4 w-4" />
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex min-w-0 flex-1 items-center gap-3">
                                                <div
                                                    className="flex h-8 w-8 shrink-0 items-center justify-center rounded-xl"
                                                    style={{ backgroundColor: notebook.color }}
                                                >
                                                    <Book className="h-3.5 w-3.5 text-white" />
                                                </div>
                                                <div className="min-w-0">
                                                    <div className="flex min-w-0 items-center gap-2">
                                                        <span className="truncate text-sm text-[var(--text-primary)]">{notebook.name}</span>
                                                        {notebook.subject ? (
                                                            <span className="rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.08)] px-2 py-0.5 text-[10px] text-[var(--text-muted)]">
                                                                {notebook.subject}
                                                            </span>
                                                        ) : null}
                                                    </div>
                                                </div>
                                            </div>
                                            <div className="ml-2 flex items-center gap-1">
                                                {activeNotebookId === notebook.id ? (
                                                    <Check className="h-4 w-4 text-[var(--primary)]" />
                                                ) : null}
                                                <div className="flex items-center gap-1 opacity-0 transition group-hover:opacity-100">
                                                    <button
                                                        onClick={(event) => {
                                                            event.stopPropagation();
                                                            setEditingNotebook(notebook);
                                                            setEditName(notebook.name);
                                                        }}
                                                        className="rounded-lg p-1 text-[var(--text-muted)] transition hover:bg-[rgba(148,163,184,0.08)] hover:text-[var(--text-primary)]"
                                                    >
                                                        <Edit2 className="h-3 w-3" />
                                                    </button>
                                                    <button
                                                        onClick={(event) => {
                                                            event.stopPropagation();
                                                            void handleDelete(notebook.id);
                                                        }}
                                                        className="rounded-lg p-1 text-[var(--text-muted)] transition hover:bg-[rgba(239,68,68,0.12)] hover:text-status-red"
                                                    >
                                                        <Trash2 className="h-3 w-3" />
                                                    </button>
                                                </div>
                                            </div>
                                        </>
                                    )}
                                </div>
                            ))
                        )}
                    </div>

                    <div className="border-t border-[var(--border)]/80 p-3">
                        <button
                            onClick={() => {
                                setShowCreateForm((prev) => !prev);
                                setSearch("");
                            }}
                            className="flex w-full items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-2.5 text-sm font-medium text-[var(--text-primary)] transition hover:border-[var(--border-strong)] hover:bg-[rgba(148,163,184,0.08)]"
                        >
                            {showCreateForm ? <X className="h-4 w-4" /> : <Plus className="h-4 w-4" />}
                            {showCreateForm ? "Close composer" : "Create notebook"}
                        </button>
                    </div>
                </div>
            ) : null}
        </div>
    );
}
