"use client";

import { MascotActionResultCard } from "./MascotActionResultCard";
import { MascotConfirmationCard } from "./MascotConfirmationCard";
import { MascotChatMessage } from "./types";

export function MascotMessageList({
    messages,
    loading,
    onNavigate,
    onConfirm,
    onSelectSuggestion,
    confirmingId,
}: {
    messages: MascotChatMessage[];
    loading?: boolean;
    onNavigate?: (href: string, notebookId?: string | null) => void;
    onConfirm: (confirmationId: string, approved: boolean) => void;
    onSelectSuggestion?: (value: string) => void;
    confirmingId?: string | null;
}) {
    return (
        <div className="flex flex-1 flex-col gap-3 overflow-y-auto px-4 py-4">
            {messages.map((message) => (
                <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}>
                    <div
                        className={`max-w-[88%] rounded-3xl px-4 py-3 text-sm ${
                            message.role === "user"
                                ? "bg-[var(--primary)] text-white"
                                : "border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-primary)]"
                        }`}
                    >
                        <p className="whitespace-pre-wrap">{message.text}</p>
                        {message.role === "assistant" && message.response ? (
                            <>
                                <MascotActionResultCard response={message.response} onNavigate={onNavigate} onSelectSuggestion={onSelectSuggestion} />
                                <MascotConfirmationCard
                                    response={message.response}
                                    loading={confirmingId === message.response.confirmation_id}
                                    onDecision={(approved) => onConfirm(message.response?.confirmation_id || "", approved)}
                                />
                            </>
                        ) : null}
                    </div>
                </div>
            ))}
            {loading ? <p className="text-xs text-[var(--text-muted)]">Mascot is thinking…</p> : null}
        </div>
    );
}
