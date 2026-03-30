"use client";

export function MascotSuggestionChips({
    suggestions,
    onSelect,
}: {
    suggestions: string[];
    onSelect: (value: string) => void;
}) {
    if (!suggestions.length) return null;
    return (
        <div className="flex flex-wrap gap-2">
            {suggestions.map((suggestion) => (
                <button
                    key={suggestion}
                    type="button"
                    onClick={() => onSelect(suggestion)}
                    className="rounded-full border border-[var(--border)] bg-[var(--bg-page)] px-3 py-1.5 text-xs text-[var(--text-secondary)] transition-colors hover:border-[var(--primary)] hover:text-[var(--text-primary)]"
                >
                    {suggestion}
                </button>
            ))}
        </div>
    );
}

