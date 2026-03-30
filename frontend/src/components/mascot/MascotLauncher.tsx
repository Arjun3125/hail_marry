"use client";

import { useState } from "react";
import { Bot } from "lucide-react";

import { MascotShell } from "./MascotShell";

export function MascotLauncher({ role, fullPage = false }: { role: string; fullPage?: boolean }) {
    const [open, setOpen] = useState(fullPage);

    if (fullPage) {
        return <MascotShell role={role} fullPage />;
    }

    return (
        <div className="fixed bottom-5 right-5 z-[70] flex flex-col items-end gap-3">
            {open ? <MascotShell role={role} onClose={() => setOpen(false)} /> : null}
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
