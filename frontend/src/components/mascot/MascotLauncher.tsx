"use client";

import { Suspense, useState } from "react";
import Image from "next/image";

import { MascotShell } from "./MascotShell";

export function MascotLauncher({ role, fullPage = false, hasBadge = false }: { role: string; fullPage?: boolean; hasBadge?: boolean }) {
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
                className="flex h-16 w-16 items-center justify-center rounded-full shadow-2xl hover:scale-110 transition-transform duration-200 relative"
                style={{
                    background: "linear-gradient(135deg, rgba(30, 58, 95, 0.95) 0%, rgba(13, 31, 53, 0.95) 100%)",
                    boxShadow: "0 0 30px rgba(0, 212, 255, 0.4), 0 8px 24px rgba(0, 0, 0, 0.4)"
                }}
                aria-label="Open Mascot assistant"
            >
                <Image
                    src="/images/mascot-owl-bg.png"
                    alt="VidyaOS Mascot"
                    width={56}
                    height={56}
                    priority
                    className="drop-shadow-lg object-contain"
                />
                {hasBadge && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 rounded-full bg-cyan-400 animate-pulse" />
                )}
            </button>
        </div>
    );
}
