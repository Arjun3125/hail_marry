"use client";

import { FormEvent } from "react";
import Image from "next/image";
import { FileImage, FileText, Maximize2, Paperclip, Send, Sparkles, UploadCloud, X } from "lucide-react";

import { MascotMessageList } from "./MascotMessageList";
import { MascotSuggestionChips } from "./MascotSuggestionChips";
import { MascotChatMessage } from "./types";

export function MascotPanel({
    title,
    messages,
    suggestions,
    draft,
    loading,
    confirmingId,
    fullPage,
    attachmentName,
    attachmentKind,
    attachmentSizeLabel,
    activeNotebookId,
    activeNotebookLabel,
    pageContextLabel,
    pageContextHint,
    onDraftChange,
    onSend,
    onAttach,
    onClearAttachment,
    onSelectSuggestion,
    onNavigate,
    onConfirm,
    onClose,
    onExpand,
}: {
    title: string;
    messages: MascotChatMessage[];
    suggestions: string[];
    draft: string;
    loading?: boolean;
    confirmingId?: string | null;
    fullPage?: boolean;
    attachmentName?: string | null;
    attachmentKind?: string | null;
    attachmentSizeLabel?: string | null;
    activeNotebookId?: string | null;
    activeNotebookLabel?: string | null;
    pageContextLabel?: string | null;
    pageContextHint?: string | null;
    onDraftChange: (value: string) => void;
    onSend: () => void;
    onAttach: (file: File | null) => void;
    onClearAttachment: () => void;
    onSelectSuggestion: (value: string) => void;
    onNavigate: (href: string, notebookId?: string | null) => void;
    onConfirm: (confirmationId: string, approved: boolean) => void;
    onClose?: () => void;
    onExpand?: () => void;
}) {
    const submit = (event: FormEvent) => {
        event.preventDefault();
        onSend();
    };

    const AttachmentIcon = attachmentKind === "Image" ? FileImage : FileText;

    return (
        <section
            className={`flex h-full flex-col overflow-hidden border border-[var(--border)] bg-[var(--bg-card)] shadow-[var(--shadow-card)] ${
                fullPage ? "rounded-3xl" : "h-[min(72vh,720px)] w-[min(420px,calc(100vw-2rem))] rounded-3xl"
            }`}
        >
            <header className="flex items-center gap-3 border-b border-[var(--border)] px-4 py-3 bg-gradient-to-r from-slate-900/50 to-slate-800/50">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-gradient-to-br from-slate-700 to-slate-900 border border-cyan-500/30 shadow-lg shadow-cyan-500/20">
                    <Image
                        src="/images/mascot-owl-bg.png"
                        alt="VidyaOS Mascot"
                        width={40}
                        height={40}
                        priority
                        className="drop-shadow-lg object-contain"
                    />
                </div>
                <div className="min-w-0 flex-1">
                    <p className="text-sm font-semibold text-[var(--text-primary)]">{title}</p>
                    <p className="text-xs text-[var(--text-muted)]">Guide, operator, and feature navigator</p>
                </div>
                {!fullPage && onExpand ? (
                    <button
                        type="button"
                        onClick={onExpand}
                        className="rounded-xl border border-[var(--border)] p-2 text-[var(--text-muted)] transition-colors hover:text-[var(--text-primary)]"
                        aria-label="Open full assistant"
                    >
                        <Maximize2 className="h-4 w-4" />
                    </button>
                ) : null}
                {!fullPage && onClose ? (
                    <button
                        type="button"
                        onClick={onClose}
                        className="rounded-xl border border-[var(--border)] p-2 text-[var(--text-muted)] transition-colors hover:text-[var(--text-primary)]"
                        aria-label="Close assistant"
                    >
                        <X className="h-4 w-4" />
                    </button>
                ) : null}
            </header>

            <div className="border-b border-[var(--border)] px-4 py-3">
                <div className="mb-3 flex flex-wrap gap-2">
                    {activeNotebookId ? (
                        <span className="rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1 text-[11px] font-medium text-[var(--text-secondary)]">
                            Notebook: {activeNotebookLabel || activeNotebookId}
                        </span>
                    ) : null}
                    {pageContextLabel ? (
                        <span className="rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1 text-[11px] font-medium text-[var(--text-secondary)]">
                            Context: {pageContextLabel}
                        </span>
                    ) : null}
                </div>
                {pageContextHint ? (
                    <p className="mb-3 text-xs leading-5 text-[var(--text-secondary)]">{pageContextHint}</p>
                ) : null}
                <div className="mb-3 flex items-center gap-2 text-xs text-[var(--text-muted)]">
                    <Sparkles className="h-3.5 w-3.5 text-[var(--primary)]" />
                    Suggested actions
                </div>
                <MascotSuggestionChips suggestions={suggestions} onSelect={onSelectSuggestion} />
            </div>

            <MascotMessageList
                messages={messages}
                loading={loading}
                onNavigate={onNavigate}
                onConfirm={onConfirm}
                onSelectSuggestion={onSelectSuggestion}
                confirmingId={confirmingId}
            />

            <form onSubmit={submit} className="border-t border-[var(--border)] px-4 py-4">
                {attachmentName ? (
                    <div className="mb-3 flex items-start justify-between gap-3 rounded-3xl border border-[var(--border)] bg-[var(--bg-page)] px-4 py-3">
                        <div className="flex min-w-0 items-start gap-3">
                            <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-[var(--bg-card)] text-[var(--primary)]">
                                <AttachmentIcon className="h-4 w-4" />
                            </div>
                            <div className="min-w-0">
                                <p className="truncate text-sm font-medium text-[var(--text-primary)]">{attachmentName}</p>
                                <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                    {[attachmentKind, attachmentSizeLabel, "Ready to ingest"].filter(Boolean).join(" • ")}
                                </p>
                                <p className="mt-1 text-xs text-[var(--text-muted)]">
                                    Add a prompt to ask something after upload, or send with an empty prompt to index only.
                                </p>
                            </div>
                        </div>
                        <button
                            type="button"
                            onClick={onClearAttachment}
                            className="rounded-lg px-2 py-1 text-xs text-[var(--text-muted)] transition-colors hover:text-[var(--text-primary)]"
                        >
                            Remove
                        </button>
                    </div>
                ) : null}
                <div className="flex items-end gap-2 rounded-2xl border border-[var(--border)] bg-[var(--bg-page)] p-2">
                    <label className="flex cursor-pointer items-center gap-2 rounded-xl border border-[var(--border)] px-3 py-3 text-[var(--text-muted)] transition-colors hover:text-[var(--text-primary)]">
                        <Paperclip className="h-4 w-4" />
                        <span className="hidden text-xs font-medium sm:inline">Attach</span>
                        <input
                            type="file"
                            className="hidden"
                            accept=".pdf,.docx,.pptx,.xlsx,image/*"
                            onChange={(event) => onAttach(event.target.files?.[0] || null)}
                            aria-label="Attach file to mascot"
                        />
                    </label>
                    <textarea
                        value={draft}
                        onChange={(event) => onDraftChange(event.target.value)}
                        placeholder="Tell the mascot what you want to do..."
                        rows={2}
                        className="min-h-[64px] flex-1 resize-none bg-transparent px-3 py-2 text-sm text-[var(--text-primary)] outline-none placeholder:text-[var(--text-muted)]"
                    />
                    <button
                        type="submit"
                        disabled={loading || (!draft.trim() && !attachmentName)}
                        className="rounded-xl bg-[var(--primary)] p-3 text-white disabled:opacity-60"
                    >
                        <Send className="h-4 w-4" />
                    </button>
                </div>
                <div className="mt-2 flex flex-wrap items-center gap-2 text-[11px] text-[var(--text-muted)]">
                    <span className="inline-flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1">
                        <UploadCloud className="h-3.5 w-3.5" />
                        PDF, DOCX, PPTX, XLSX, or image
                    </span>
                    <span className="inline-flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1">
                        Ask after upload or ingest only
                    </span>
                </div>
            </form>
        </section>
    );
}
