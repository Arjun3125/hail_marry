"use client";

import { useEffect, useState } from "react";
import { useVidyaContext } from "@/providers/VidyaContextProvider";

export function LowDataToggle() {
    const { isOfflineMode } = useVidyaContext();
    const [enabled, setEnabled] = useState(false);

    const toggleLowDataMode = (enabled: boolean) => {
        setEnabled(enabled);
        if (enabled) {
            document.documentElement.classList.add("low-data-mode");
            localStorage.setItem("lowDataMode", "true");
        } else {
            document.documentElement.classList.remove("low-data-mode");
            localStorage.setItem("lowDataMode", "false");
        }
    };

    useEffect(() => {
        queueMicrotask(() => {
            const saved = localStorage.getItem("lowDataMode") === "true";
            const shouldEnable = saved || isOfflineMode;
            setEnabled(shouldEnable);
            if (shouldEnable) {
                document.documentElement.classList.add("low-data-mode");
            } else {
                document.documentElement.classList.remove("low-data-mode");
            }
        });
    }, [isOfflineMode]);

    return (
        <label className="flex cursor-pointer items-center gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-3 py-2">
            <div className="relative">
                <input
                    type="checkbox"
                    className="peer sr-only"
                    onChange={(e) => toggleLowDataMode(e.target.checked)}
                    checked={enabled}
                    disabled={isOfflineMode}
                />
                <div className="block h-5 w-9 rounded-full bg-[var(--border)] transition-colors peer-checked:bg-[var(--role-student)]"></div>
                <div className="absolute left-1 top-1 h-3 w-3 rounded-full bg-white transition-transform peer-checked:translate-x-4"></div>
            </div>
            <div className="min-w-0 flex-1">
                <p className="text-xs font-semibold text-[var(--text-primary)]">Low-data mode</p>
                <p className="text-[10px] text-[var(--text-muted)]">
                    {isOfflineMode ? "Enabled while offline" : "No animations or heavy assets"}
                </p>
            </div>
        </label>
    );
}
