"use client";

import { Sparkles, ArrowRight, Lightbulb, TrendingUp } from "lucide-react";

interface SmartSuggestion {
    id: string;
    type: "quiz" | "flashcards" | "mindmap" | "deep_dive" | "practice";
    title: string;
    description: string;
    confidence: number; // 0-100
}

interface SmartSuggestionsProps {
    lastQuery?: string;
    lastResponse?: string;
    onSuggestionClick: (suggestion: SmartSuggestion) => void;
    sessionStats: {
        questionsAsked: number;
        timeSpent: number; // minutes
        toolsUsed: string[];
    };
}

export function SmartSuggestions({
    lastQuery,
    lastResponse,
    onSuggestionClick,
    sessionStats,
}: SmartSuggestionsProps) {
    // Generate suggestions based on context
    const suggestions: SmartSuggestion[] = generateSuggestions(lastQuery, lastResponse, sessionStats);

    if (suggestions.length === 0) return null;

    return (
        <div className="bg-gradient-to-br from-indigo-500/5 to-violet-600/5 rounded-xl border border-indigo-500/20 p-4">
            <div className="flex items-center gap-2 mb-3">
                <Lightbulb className="w-4 h-4 text-indigo-500" />
                <span className="text-sm font-medium text-[var(--text-primary)]">
                    Suggested next steps
                </span>
                {sessionStats.questionsAsked > 0 && (
                    <span className="text-[10px] text-[var(--text-muted)]">
                        ({sessionStats.questionsAsked} questions this session)
                    </span>
                )}
            </div>

            <div className="space-y-2">
                {suggestions.map((suggestion) => (
                    <button
                        key={suggestion.id}
                        onClick={() => onSuggestionClick(suggestion)}
                        className="w-full flex items-center gap-3 p-3 rounded-lg bg-[var(--bg-card)] hover:bg-[var(--surface-hover)] border border-[var(--border)]/50 hover:border-indigo-500/30 transition-all group"
                    >
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center flex-shrink-0">
                            {suggestion.type === "quiz" && <Sparkles className="w-4 h-4 text-white" />}
                            {suggestion.type === "flashcards" && <Lightbulb className="w-4 h-4 text-white" />}
                            {suggestion.type === "mindmap" && <TrendingUp className="w-4 h-4 text-white" />}
                            {(suggestion.type === "deep_dive" || suggestion.type === "practice") && <ArrowRight className="w-4 h-4 text-white" />}
                        </div>
                        <div className="flex-1 text-left">
                            <p className="text-sm font-medium text-[var(--text-primary)] group-hover:text-indigo-600 transition-colors">
                                {suggestion.title}
                            </p>
                            <p className="text-[10px] text-[var(--text-muted)]">
                                {suggestion.description}
                            </p>
                        </div>
                        <div className="flex items-center gap-1">
                            <div className="w-16 h-1 bg-[var(--border)] rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-indigo-500 to-violet-600 rounded-full"
                                    style={{ width: `${suggestion.confidence}%` }}
                                />
                            </div>
                            <span className="text-[10px] text-[var(--text-muted)]">
                                {suggestion.confidence}%
                            </span>
                        </div>
                    </button>
                ))}
            </div>
        </div>
    );
}

function generateSuggestions(
    query?: string,
    response?: string,
    stats?: { questionsAsked: number; timeSpent: number; toolsUsed: string[] }
): SmartSuggestion[] {
    const suggestions: SmartSuggestion[] = [];

    // Context-aware suggestions
    if (query) {
        // After any learning query, suggest testing knowledge
        if (!stats?.toolsUsed.includes("quiz")) {
            suggestions.push({
                id: "1",
                type: "quiz",
                title: "Test your understanding",
                description: `Create a quiz about "${query.slice(0, 40)}${query.length > 40 ? "..." : ""}"`,
                confidence: 85,
            });
        }

        // Suggest flashcards for factual content
        if (!stats?.toolsUsed.includes("flashcards")) {
            suggestions.push({
                id: "2",
                type: "flashcards",
                title: "Make study cards",
                description: "Extract key facts for spaced repetition",
                confidence: 75,
            });
        }

        // Suggest mind map for complex topics
        if (!stats?.toolsUsed.includes("mindmap") && (response && response.length > 200)) {
            suggestions.push({
                id: "3",
                type: "mindmap",
                title: "Visualize the concepts",
                description: "Create a hierarchical mind map",
                confidence: 70,
            });
        }
    }

    // Session-based suggestions
    if (stats) {
        if (stats.questionsAsked > 3 && stats.timeSpent > 10) {
            suggestions.push({
                id: "4",
                type: "practice",
                title: "Take a break?",
                description: "You've been studying for 10+ minutes",
                confidence: 60,
            });
        }

        // Encourage variety
        if (stats.toolsUsed.length === 1 && stats.questionsAsked > 2) {
            suggestions.push({
                id: "5",
                type: "deep_dive",
                title: "Try a different tool",
                description: "Explore visual or practice modes",
                confidence: 65,
            });
        }
    }

    return suggestions.slice(0, 3); // Max 3 suggestions
}
