"use client";

import { useCallback } from "react";

/**
 * Hook to announce messages to screen readers via the aria-live region.
 * Usage: const announce = useScreenReaderAnnounce(); announce("Quiz ready!");
 */
export function useScreenReaderAnnounce() {
    return useCallback((message: string) => {
        const el = document.getElementById("screen-reader-announcer");
        if (el) {
            el.textContent = "";
            // Small delay ensures screen readers pick up the change
            requestAnimationFrame(() => {
                el.textContent = message;
            });
        }
    }, []);
}
