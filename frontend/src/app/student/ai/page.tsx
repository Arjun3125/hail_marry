"use client";

import { useState } from "react";
import { Bot, Send, Loader2, FileText, Sparkles, HelpCircle, BookOpen, MessageSquare, Shuffle, Swords, PenLine, Briefcase } from "lucide-react";
import { API_BASE } from "@/lib/api";

interface AIResponse {
    answer: string;
    citations: Array<{ source: string; page: string }>;
    mode: string;
}

const modes = [
    { id: "qa", label: "Q&A", icon: HelpCircle, desc: "Ask questions about your notes", gradient: "from-blue-500 to-indigo-600" },
    { id: "study_guide", label: "Study Guide", icon: BookOpen, desc: "Generate a study guide", gradient: "from-emerald-500 to-teal-600" },
    { id: "quiz", label: "Quiz", icon: Sparkles, desc: "Create a quiz from notes", gradient: "from-violet-500 to-purple-600" },
    { id: "socratic", label: "Socratic", icon: MessageSquare, desc: "Guided hints, no answers", gradient: "from-amber-500 to-orange-600" },
    { id: "perturbation", label: "Exam Prep", icon: Shuffle, desc: "Novel question variations", gradient: "from-rose-500 to-pink-600" },
    { id: "debate", label: "Debate", icon: Swords, desc: "Challenge your arguments", gradient: "from-red-500 to-rose-600" },
    { id: "essay_review", label: "Essay Review", icon: PenLine, desc: "Feedback on writing", gradient: "from-cyan-500 to-blue-600" },
    { id: "career_sim", label: "Career Sim", icon: Briefcase, desc: "Explore career scenarios", gradient: "from-fuchsia-500 to-purple-600" },
];

const placeholders: Record<string, string> = {
    qa: "Ask a question about your notes...",
    study_guide: "Enter a topic to generate a study guide...",
    quiz: "Enter a topic to create a quiz...",
    socratic: "Ask a question — I'll guide you with hints...",
    perturbation: "Paste a question to get exam-style variations...",
    debate: "State your thesis or argument to debate...",
    essay_review: "Paste your essay or written response for feedback...",
    career_sim: "Enter a career to explore (e.g. doctor, engineer, lawyer)...",
};

export default function AIAssistant() {
    const [query, setQuery] = useState("");
    const [mode, setMode] = useState("qa");
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState<Array<{ query: string; response: AIResponse }>>([]);

    const activeMode = modes.find((m) => m.id === mode) || modes[0];

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
                setHistory((prev) => [...prev, {
                    query: query.trim(), response: {
                        answer: "Sorry, something went wrong. Please try again.",
                        citations: [],
                        mode,
                    }
                }]);
            }
        } catch {
            setHistory((prev) => [...prev, {
                query: query.trim(), response: {
                    answer: "Cannot connect to AI service. Make sure the backend is running.",
                    citations: [],
                    mode,
                }
            }]);
        } finally {
            setLoading(false);
            setQuery("");
        }
    };

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header with gradient accent */}
            <div className="mb-6">
                <div className="flex items-center gap-3 mb-1">
                    <div className={`p-2 rounded-xl bg-gradient-to-br ${activeMode.gradient} shadow-lg`}>
                        <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                            AI Study Assistant
                        </h1>
                        <p className="text-xs text-[var(--text-muted)]">
                            Powered by RAG • Answers are citation-grounded
                        </p>
                    </div>
                </div>
            </div>

            {/* Mode Selector — pill grid with gradients */}
            <div className="grid grid-cols-4 gap-2 mb-6">
                {modes.map((m) => (
                    <button
                        key={m.id}
                        onClick={() => setMode(m.id)}
                        title={m.desc}
                        className={`group relative flex flex-col items-center gap-1.5 px-3 py-3 rounded-xl text-xs font-medium transition-all duration-200 ${mode === m.id
                                ? `bg-gradient-to-br ${m.gradient} text-white shadow-lg scale-[1.03]`
                                : "bg-white text-[var(--text-secondary)] border border-[var(--border)] hover:shadow-md hover:border-transparent hover:scale-[1.02]"
                            }`}
                    >
                        <m.icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${mode === m.id ? "text-white" : "text-[var(--primary)]"}`} />
                        <span className="leading-tight">{m.label}</span>
                        {mode === m.id && (
                            <div className="absolute -bottom-1 left-1/2 -translate-x-1/2 w-1.5 h-1.5 rounded-full bg-white shadow-sm" />
                        )}
                    </button>
                ))}
            </div>

            {/* Active mode description */}
            <div className={`mb-6 px-4 py-2.5 rounded-lg bg-gradient-to-r ${activeMode.gradient} bg-opacity-10 border border-opacity-20`}
                style={{ background: `linear-gradient(135deg, rgba(59,130,246,0.05), rgba(139,92,246,0.05))` }}>
                <p className="text-xs text-[var(--text-secondary)]">
                    <span className="font-semibold text-[var(--text-primary)]">{activeMode.label}</span> — {activeMode.desc}
                </p>
            </div>

            {/* Chat History */}
            <div className="space-y-4 mb-6">
                {history.map((item, i) => {
                    const itemMode = modes.find((m) => m.id === item.response.mode) || modes[0];
                    return (
                        <div key={i} className="space-y-3 animate-[fadeIn_0.3s_ease-out]">
                            {/* User Query */}
                            <div className="flex justify-end">
                                <div className={`bg-gradient-to-br ${itemMode.gradient} text-white px-4 py-3 rounded-2xl rounded-br-md max-w-[80%] shadow-md`}>
                                    <p className="text-sm">{item.query}</p>
                                </div>
                            </div>

                            {/* AI Response */}
                            <div className="bg-white rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50">
                                <div className="flex items-center gap-2 mb-3">
                                    <div className={`p-1 rounded-lg bg-gradient-to-br ${itemMode.gradient}`}>
                                        <Bot className="w-3 h-3 text-white" />
                                    </div>
                                    <span className={`text-[10px] font-semibold uppercase tracking-wider bg-gradient-to-r ${itemMode.gradient} bg-clip-text text-transparent`}>
                                        {item.response.mode.replace("_", " ")}
                                    </span>
                                </div>
                                <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap">
                                    {item.response.answer}
                                </div>

                                {/* Citations */}
                                {item.response.citations.length > 0 && (
                                    <div className="mt-4 pt-3 border-t border-[var(--border)]/50">
                                        <p className="text-[10px] font-semibold text-[var(--text-muted)] mb-2 uppercase tracking-wider">
                                            Sources
                                        </p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {item.response.citations.map((c, j) => (
                                                <span
                                                    key={j}
                                                    className="inline-flex items-center gap-1 text-[10px] bg-[var(--bg-page)] text-[var(--text-secondary)] px-2 py-1 rounded-lg border border-[var(--border)]/30"
                                                >
                                                    <FileText className="w-2.5 h-2.5" />
                                                    {c.source} p.{c.page}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}

                {/* Loading */}
                {loading && (
                    <div className="bg-white rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-xl bg-gradient-to-br ${activeMode.gradient} animate-pulse`}>
                                <Bot className="w-4 h-4 text-white" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-[var(--text-primary)]">Thinking...</p>
                                <p className="text-xs text-[var(--text-muted)]">Searching notes and generating response</p>
                            </div>
                            <div className="ml-auto flex gap-1">
                                <span className="w-2 h-2 rounded-full bg-[var(--primary)] animate-bounce" style={{ animationDelay: "0ms" }} />
                                <span className="w-2 h-2 rounded-full bg-[var(--primary)] animate-bounce" style={{ animationDelay: "150ms" }} />
                                <span className="w-2 h-2 rounded-full bg-[var(--primary)] animate-bounce" style={{ animationDelay: "300ms" }} />
                            </div>
                        </div>
                    </div>
                )}
            </div>

            {/* Empty State */}
            {history.length === 0 && !loading && (
                <div className="bg-white rounded-2xl p-12 shadow-[var(--shadow-card)] text-center mb-6 border border-[var(--border)]/50">
                    <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${activeMode.gradient} flex items-center justify-center shadow-lg`}>
                        <Bot className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">
                        Ask about your notes
                    </h3>
                    <p className="text-sm text-[var(--text-muted)] max-w-md mx-auto mb-6">
                        Type a question below. The AI will search your uploaded curriculum
                        materials and respond with citations.
                    </p>
                    <div className="flex flex-wrap justify-center gap-2">
                        {[
                            "Explain photosynthesis",
                            "What is a quadratic equation?",
                            "Summarize Chapter 3",
                        ].map((suggestion) => (
                            <button
                                key={suggestion}
                                onClick={() => setQuery(suggestion)}
                                className="px-4 py-2 text-xs font-medium text-[var(--primary)] bg-[var(--primary-light)] rounded-full hover:bg-[var(--primary)] hover:text-white transition-all duration-200 hover:shadow-md"
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
                className="sticky bottom-4 bg-white rounded-2xl shadow-xl p-3 flex items-center gap-3 border border-[var(--border)]/50"
            >
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={placeholders[mode] || "Type your question..."}
                    className="flex-1 px-4 py-3 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/50"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className={`px-5 py-3 bg-gradient-to-r ${activeMode.gradient} text-white rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed hover:scale-[1.02]`}
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
            </form>
        </div>
    );
}
