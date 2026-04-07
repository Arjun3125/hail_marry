"use client";

import { useState } from "react";
import { CircleHelp, X } from "lucide-react";

import { PrismDialog, PrismDialogHeader, PrismOverlay } from "@/components/prism/PrismOverlays";

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
                <CircleHelp className="h-3.5 w-3.5" /> Help overlay
            </button>
            {open ? (
                <PrismOverlay className="z-[70]">
                    <PrismDialog className="w-full max-w-md p-4">
                        <PrismDialogHeader className="mb-3 border-b-0 px-0 py-0">
                            <h3 className="text-sm font-bold text-[var(--text-primary)]">{title}</h3>
                            <button type="button" onClick={() => setOpen(false)} className="text-[var(--text-muted)] hover:text-[var(--text-primary)]">
                                <X className="h-4 w-4" />
                            </button>
                        </PrismDialogHeader>
                        <ul className="space-y-2">
                            {items.map((item) => (
                                <li key={item} className="text-sm text-[var(--text-secondary)]">
                                    • {item}
                                </li>
                            ))}
                        </ul>
                    </PrismDialog>
                </PrismOverlay>
            ) : null}
        </>
    );
}
