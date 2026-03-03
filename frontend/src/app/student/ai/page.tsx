"use client";

import { useState } from "react";
import { Bot, Send, Loader2, FileText, Sparkles, HelpCircle, BookOpen } from "lucide-react";
import { API_BASE } from "@/lib/api";

interface AIResponse {
    answer: string;
    citations: Array<{ source: string; page: string }>;
    mode: string;
}

const modes = [
    { id: "qa", label: "Q&A", icon: HelpCircle, desc: "Ask questions about your notes" },
    { id: "study_guide", label: "Study Guide", icon: BookOpen, desc: "Generate a study guide" },
    { id: "quiz", label: "Quiz", icon: Sparkles, desc: "Create a quiz from notes" },
];

export default function AIAssistant() {
    const [query, setQuery] = useState("");
    const [mode, setMode] = useState("qa");
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<Array<{ query: string; response: AIResponse }>>([]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || loading) return;

        setLoading(true);
        try {
            const res = await fetch(`${API_BASE}/api/ai/query`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ query: query.trim(), mode }),
            });

            if (res.ok) {
                const data = await res.json();
                const aiResponse: AIResponse = {
                    answer: data.answer || data.response_text || "No response received.",
                    citations: data.citations || [],
                    mode,
                };
                setHistory((prev) => [...prev, { query: query.trim(), response: aiResponse }]);
            } else {
                setHistory((prev) => [...prev, { query: query.trim(), response: {
                    answer: "Sorry, something went wrong. Please try again.",
                    citations: [],
                    mode,
                } }]);
            }
        } catch {
            setHistory((prev) => [...prev, { query: query.trim(), response: {
                answer: "Cannot connect to AI service. Make sure the backend is running.",
                citations: [],
                mode,
            } }]);
        } finally {
            setLoading(false);
            setQuery("");
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center gap-2 mb-1">
                    <Bot className="w-6 h-6 text-[var(--primary)]" />
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                        AI Study Assistant
                    </h1>
                </div>
                <p className="text-sm text-[var(--text-secondary)]">
                    Ask questions about your uploaded notes. Answers are citation-grounded.
                </p>
            </div>

            {/* Mode Selector */}
            <div className="flex gap-3 mb-6">
                {modes.map((m) => (
                    <button
                        key={m.id}
                        onClick={() => setMode(m.id)}
                        className={`flex items-center gap-2 px-4 py-2.5 rounded-[var(--radius-sm)] text-sm font-medium transition-all ${mode === m.id
                                ? "bg-[var(--primary)] text-white shadow-md"
                                : "bg-white text-[var(--text-secondary)] border border-[var(--border)] hover:border-[var(--primary)] hover:text-[var(--primary)]"
                            }`}
                    >
                        <m.icon className="w-4 h-4" />
                        {m.label}
                    </button>
                ))}
            </div>

            {/* Chat History */}
            <div className="space-y-4 mb-6">
                {history.map((item, i) => (
                    <div key={i} className="space-y-3">
                        {/* User Query */}
                        <div className="flex justify-end">
                            <div className="bg-[var(--primary)] text-white px-4 py-3 rounded-[var(--radius)] rounded-br-sm max-w-[80%]">
                                <p className="text-sm">{item.query}</p>
                            </div>
                        </div>

                        {/* AI Response */}
                        <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <div className="flex items-center gap-2 mb-3">
                                <Bot className="w-4 h-4 text-[var(--primary)]" />
                                <span className="text-xs font-medium text-[var(--primary)] bg-[var(--primary-light)] px-2 py-0.5 rounded-full capitalize">
                                    {item.response.mode}
                                </span>
                            </div>
                            <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap">
                                {item.response.answer}
                            </div>

                            {/* Citations */}
                            {item.response.citations.length > 0 && (
                                <div className="mt-4 pt-3 border-t border-[var(--border)]">
                                    <p className="text-xs font-medium text-[var(--text-muted)] mb-2">
                                        Citations:
                                    </p>
                                    <div className="flex flex-wrap gap-2">
                                        {item.response.citations.map((c, j) => (
                                            <span
                                                key={j}
                                                className="inline-flex items-center gap-1 text-xs bg-[var(--bg-page)] text-[var(--text-secondary)] px-2.5 py-1 rounded-full"
                                            >
                                                <FileText className="w-3 h-3" />
                                                {c.source} p.{c.page}
                                            </span>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {/* Loading */}
                {loading && (
                    <div className="bg-white rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                        <div className="flex items-center gap-3">
                            <Loader2 className="w-5 h-5 text-[var(--primary)] animate-spin" />
                            <p className="text-sm text-[var(--text-muted)]">
                                Searching your notes and generating response...
                            </p>
                        </div>
                    </div>
                )}
            </div>

            {/* Empty State */}
            {history.length === 0 && !loading && (
                <div className="bg-white rounded-[var(--radius)] p-12 shadow-[var(--shadow-card)] text-center mb-6">
                    <Bot className="w-12 h-12 text-[var(--primary-light)] mx-auto mb-4" />
                    <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                        Ask about your notes
                    </h3>
                    <p className="text-sm text-[var(--text-muted)] max-w-md mx-auto">
                        Type a question below. The AI will search your uploaded curriculum
                        materials and respond with citations.
                    </p>
                    <div className="flex flex-wrap justify-center gap-2 mt-6">
                        {[
                            "Explain photosynthesis",
                            "What is a quadratic equation?",
                            "Summarize Chapter 3",
                        ].map((suggestion) => (
                            <button
                                key={suggestion}
                                onClick={() => setQuery(suggestion)}
                                className="px-3 py-1.5 text-xs text-[var(--primary)] bg-[var(--primary-light)] rounded-full hover:bg-[var(--primary)] hover:text-white transition-colors"
                            >
                                {suggestion}
                            </button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <form
                onSubmit={handleSubmit}
                className="sticky bottom-6 bg-white rounded-[var(--radius)] shadow-[var(--shadow-md)] p-3 flex items-center gap-3"
            >
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={
                        mode === "qa"
                            ? "Ask a question about your notes..."
                            : mode === "study_guide"
                                ? "Enter a topic to generate a study guide..."
                                : "Enter a topic to create a quiz..."
                    }
                    className="flex-1 px-4 py-3 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)] focus:border-transparent"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className="px-5 py-3 bg-[var(--primary)] text-white rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <Send className="w-4 h-4" />
                </button>
            </form>
        </div>
    );
}
