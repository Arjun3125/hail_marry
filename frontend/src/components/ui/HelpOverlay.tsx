"use client";

import { useState } from "react";
import { CircleHelp, X } from "lucide-react";

export default function HelpOverlay({
    title,
    items,
}: {
    title: string;
    items: string[];
}) {
    const [open, setOpen] = useState(false);

    return (
        <>
            <button
                type="button"
                onClick={() => setOpen(true)}
                className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] border border-[var(--border-light)] text-xs font-semibold text-[var(--text-primary)] hover:bg-[var(--bg-page)]"
            >
                <CircleHelp className="w-3.5 h-3.5" /> Help overlay
            </button>
            {open ? (
                <div className="fixed inset-0 z-[70] bg-black/45 backdrop-blur-[1px] p-4 flex items-center justify-center">
                    <div className="w-full max-w-md rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-md)]">
                        <div className="flex items-center justify-between mb-3">
                            <h3 className="text-sm font-bold text-[var(--text-primary)]">{title}</h3>
                            <button type="button" onClick={() => setOpen(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                <X className="w-4 h-4" />
                            </button>
                        </div>
                        <ul className="space-y-2">
                            {items.map((item) => (
                                <li key={item} className="text-sm text-[var(--text-secondary)]">• {item}</li>
                            ))}
                        </ul>
                    </div>
                </div>
            ) : null}
        </>
    );
}
