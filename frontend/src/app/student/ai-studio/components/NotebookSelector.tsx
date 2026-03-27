"use client";

import { useState, useEffect, useCallback } from "react";
import { Book, Plus, Edit2, Trash2, Check, ChevronDown } from "lucide-react";
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

    const fetchNotebooks = useCallback(async () => {
        try {
            setLoading(true);
            const response = await api.notebooks.list();
            setNotebooks(response.items || []);
        } catch (err) {
            console.error("Failed to fetch notebooks:", err);
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        fetchNotebooks();
    }, [fetchNotebooks]);

    const activeNotebook = notebooks.find((n) => n.id === activeNotebookId);

    const handleCreate = async () => {
        const name = prompt("Enter notebook name:");
        if (!name) return;

        try {
            const newNotebook = await api.notebooks.create({ name });
            setNotebooks((prev) => [newNotebook, ...prev]);
            onNotebookChange(newNotebook.id);
            onCreateNotebook?.();
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
            await api.notebooks.update(notebook.id, { name: editName });
            setNotebooks((prev) =>
                prev.map((n) => (n.id === notebook.id ? { ...n, name: editName } : n))
            );
            setEditingNotebook(null);
        } catch (err) {
            console.error("Failed to rename notebook:", err);
            alert("Failed to rename notebook");
        }
    };

    const handleDelete = async (notebookId: string) => {
        if (!confirm("Are you sure you want to delete this notebook?")) return;

        try {
            await api.notebooks.delete(notebookId);
            setNotebooks((prev) => prev.filter((n) => n.id !== notebookId));
            if (activeNotebookId === notebookId) {
                onNotebookChange(null);
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
            {/* Active Notebook Display */}
            <button
                onClick={() => setIsOpen(!isOpen)}
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

            {/* Dropdown */}
            {isOpen && (
                <div className="border-t border-[var(--border)] bg-[var(--bg-page)]">
                    {/* Notebook List */}
                    <div className="max-h-48 overflow-y-auto py-1">
                        {notebooks.length === 0 ? (
                            <div className="px-3 py-2 text-sm text-[var(--text-muted)]">
                                No notebooks yet
                            </div>
                        ) : (
                            notebooks.map((notebook) => (
                                <div
                                    key={notebook.id}
                                    className={`flex items-center justify-between px-3 py-2 hover:bg-[var(--surface-hover)] cursor-pointer ${
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
                                                    if (e.key === "Enter") handleRename(notebook);
                                                    if (e.key === "Escape") setEditingNotebook(null);
                                                }}
                                            />
                                            <button
                                                onClick={() => handleRename(notebook)}
                                                className="p-1 text-emerald-600 hover:bg-emerald-50 rounded"
                                            >
                                                <Check className="w-4 h-4" />
                                            </button>
                                        </div>
                                    ) : (
                                        <>
                                            <div className="flex items-center gap-2 flex-1">
                                                <div
                                                    className="w-6 h-6 rounded flex items-center justify-center"
                                                    style={{ backgroundColor: notebook.color }}
                                                >
                                                    <Book className="w-3 h-3 text-white" />
                                                </div>
                                                <span className="text-sm text-[var(--text-primary)] truncate">
                                                    {notebook.name}
                                                </span>
                                            </div>
                                            {activeNotebookId === notebook.id && (
                                                <Check className="w-4 h-4 text-[var(--primary)]" />
                                            )}
                                        </>
                                    )}

                                    {/* Actions */}
                                    {editingNotebook?.id !== notebook.id && (
                                        <div className="flex items-center gap-1 opacity-0 group-hover:opacity-100">
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
                                                    handleDelete(notebook.id);
                                                }}
                                                className="p-1 text-[var(--text-muted)] hover:text-red-600 hover:bg-red-50 rounded"
                                            >
                                                <Trash2 className="w-3 h-3" />
                                            </button>
                                        </div>
                                    )}
                                </div>
                            ))
                        )}
                    </div>

                    {/* Create Button */}
                    <div className="border-t border-[var(--border)] p-2">
                        <button
                            onClick={handleCreate}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2 text-sm text-[var(--primary)] hover:bg-[var(--primary-light)] rounded-lg transition-colors"
                        >
                            <Plus className="w-4 h-4" />
                            Create Notebook
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
}
