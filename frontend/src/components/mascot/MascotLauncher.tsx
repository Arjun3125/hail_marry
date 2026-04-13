"use client";

import { Suspense, useState } from "react";
import { Bot } from "lucide-react";

import { MascotShell } from "./MascotShell";

export function MascotLauncher({ role, fullPage = false }: { role: string; fullPage?: boolean }) {
    const [open, setOpen] = useState(fullPage);

    if (fullPage) {
        return (
            <Suspense fallback={null}>
                <MascotShell role={role} fullPage />
            </Suspense>
        );
    }

    return (
        <div 
            className="fixed right-5 z-[70] flex flex-col items-end gap-3 bottom-5 lg:bottom-5"
            style={{ bottom: "calc(var(--bottom-nav-height, 0rem) + 1.25rem)" }}
        >
            {open ? (
                <Suspense fallback={null}>
                    <MascotShell role={role} onClose={() => setOpen(false)} />
                </Suspense>
            ) : null}
            <button
                type="button"
                onClick={() => setOpen((value) => !value)}
                className="flex h-14 w-14 items-center justify-center rounded-full bg-gradient-to-br from-orange-500 to-amber-500 text-white shadow-xl"
                aria-label="Open mascot assistant"
            >
                <Bot className="h-6 w-6" />
            </button>
        </div>
    );
}
