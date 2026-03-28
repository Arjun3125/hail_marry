"use client";

import { useFloating, offset, flip, shift, autoUpdate, useHover, useInteractions, FloatingPortal } from "@floating-ui/react";
import { BookText } from "lucide-react";
import { useState } from "react";

type Citation = {
    source?: string;
    page?: string | null;
    url?: string | null;
    text?: string;
};

export function CitationPopover({ citation }: { citation: Citation }) {
    const [open, setOpen] = useState(false);
    const { refs, floatingStyles, context } = useFloating({
        open,
        onOpenChange: setOpen,
        middleware: [offset(10), flip(), shift({ padding: 8 })],
        whileElementsMounted: autoUpdate,
    });
    const hover = useHover(context, { move: false });
    const { getReferenceProps, getFloatingProps } = useInteractions([hover]);
    const label = citation.text || `${citation.source || "Document"}${citation.page ? ` p.${citation.page}` : ""}`;

    return (
        <>
            <button
                ref={refs.setReference}
                type="button"
                className="inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-2.5 py-1 text-[10px] text-[var(--text-secondary)] transition hover:border-[var(--primary)]/40 hover:text-[var(--text-primary)]"
                {...getReferenceProps()}
            >
                <BookText className="h-3 w-3" />
                <span>{label}</span>
            </button>
            {open ? (
                <FloatingPortal>
                    <div
                        ref={refs.setFloating}
                        style={floatingStyles}
                        className="z-50 max-w-64 rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-3 text-xs shadow-2xl"
                        {...getFloatingProps()}
                    >
                        <p className="font-medium text-[var(--text-primary)]">{citation.source || "Study source"}</p>
                        {citation.page ? <p className="mt-1 text-[var(--text-secondary)]">Page {citation.page}</p> : null}
                        {citation.url ? (
                            <a
                                href={citation.url}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="mt-2 inline-flex text-[var(--primary)] hover:underline"
                            >
                                Open source
                            </a>
                        ) : (
                            <p className="mt-2 text-[var(--text-muted)]">Source preview unavailable in this response.</p>
                        )}
                    </div>
                </FloatingPortal>
            ) : null}
        </>
    );
}
