"use client";

import { useEffect, useCallback } from "react";

interface KeyboardShortcutsProps {
    onToggleFocus?: () => void;
    onClearConversation?: () => void;
    onSubmit?: () => void;
    onToggleRail?: () => void;
    onTogglePanel?: () => void;
    onToggleContext?: () => void;
}

export function useKeyboardShortcuts({
    onToggleFocus,
    onClearConversation,
    onSubmit,
    onToggleRail,
    onTogglePanel,
    onToggleContext,
}: KeyboardShortcutsProps) {
    const handleKeyDown = useCallback(
        (event: KeyboardEvent) => {
            // Cmd/Ctrl + K - Command palette (placeholder for now)
            if ((event.metaKey || event.ctrlKey) && event.key === "k") {
                event.preventDefault();
                // TODO: Open command palette
            }

            // F - Focus mode
            if (event.key === "f" && !event.metaKey && !event.ctrlKey && !event.altKey) {
                // Only trigger if not typing in an input
                if (event.target instanceof HTMLInputElement || event.target instanceof HTMLTextAreaElement) {
                    return;
                }
                event.preventDefault();
                onToggleFocus?.();
            }

            // Esc - Exit focus mode or close panels
            if (event.key === "Escape") {
                onToggleFocus?.(); // Toggle off if in focus mode
            }

            // Cmd/Ctrl + Enter - Submit
            if ((event.metaKey || event.ctrlKey) && event.key === "Enter") {
                event.preventDefault();
                onSubmit?.();
            }

            // Cmd/Ctrl + L - Toggle library/context panel
            if ((event.metaKey || event.ctrlKey) && event.key === "l") {
                event.preventDefault();
                if (onTogglePanel) {
                    onTogglePanel();
                } else if (onToggleContext) {
                    onToggleContext();
                }
            }

            // Cmd/Ctrl + B - Toggle tool rail
            if ((event.metaKey || event.ctrlKey) && event.key === "b") {
                event.preventDefault();
                onToggleRail?.();
            }

            // Cmd/Ctrl + Shift + Delete - Clear conversation
            if ((event.metaKey || event.ctrlKey) && event.shiftKey && event.key === "Delete") {
                event.preventDefault();
                onClearConversation?.();
            }
        },
        [onToggleFocus, onClearConversation, onSubmit, onToggleRail, onTogglePanel, onToggleContext]
    );

    useEffect(() => {
        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [handleKeyDown]);
}

// Shortcut help modal content
export const keyboardShortcuts = [
    { key: "F", description: "Toggle focus mode" },
    { key: "Esc", description: "Exit focus mode" },
    { key: "Cmd/Ctrl + Enter", description: "Submit query" },
    { key: "Cmd/Ctrl + K", description: "Open command palette" },
    { key: "Cmd/Ctrl + L", description: "Toggle context panel" },
    { key: "Cmd/Ctrl + B", description: "Toggle tool rail" },
    { key: "Cmd/Ctrl + Shift + Del", description: "Clear conversation" },
    { key: "?", description: "Show keyboard shortcuts" },
];
