"use client";

import { useState, useEffect, useRef } from "react";
import {
    Bot,
    Send,
    Loader2,
    Sparkles,
    BookText,
    Copy,
    ThumbsUp,
    ThumbsDown,
    Bookmark,
} from "lucide-react";
import { api, APIError } from "@/lib/api";
import { ActionBar } from "./ActionBar";

interface LearningWorkspaceProps {
    activeTool: string;
    notebookId: string | null;
}

type Citation = {
    source?: string;
    page?: string | null;
    url?: string | null;
    text?: string;
};

interface AIResponse {
    answer: string;
    citations: Citation[];
    mode: string;
}

interface ConversationItem {
    id: string;
    query: string;
    response: AIResponse;
    timestamp: Date;
}

const toolConfig: Record<string, { placeholder: string; title: string; desc: string }> = {
    qa: { placeholder: "Ask anything about your materials...", title: "Q&A", desc: "Get answers with citations from your notes" },
    study_guide: { placeholder: "Enter a topic for a comprehensive study guide...", title: "Study Guide", desc: "Generate structured topic summaries" },
    socratic: { placeholder: "What would you like to explore through questioning?", title: "Socratic Tutor", desc: "Learn through guided discovery" },
    quiz: { placeholder: "Enter a topic to create a quiz...", title: "Quiz", desc: "Test your knowledge with MCQs" },
    flashcards: { placeholder: "What topic should we make flashcards for?", title: "Flashcards", desc: "Spaced repetition study cards" },
    perturbation: { placeholder: "Paste a question to generate variations...", title: "Exam Prep", desc: "Practice with question variations" },
    debate: { placeholder: "State your position or thesis...", title: "Debate", desc: "Challenge and refine your arguments" },
    essay_review: { placeholder: "Paste your essay for feedback...", title: "Essay Review", desc: "Get writing improvement suggestions" },
    mindmap: { placeholder: "What topic should we map out?", title: "Mind Map", desc: "Visual topic hierarchy" },
    flowchart: { placeholder: "What process should we diagram?", title: "Flowchart", desc: "Step-by-step visualization" },
    concept_map: { placeholder: "What concepts should we connect?", title: "Concept Map", desc: "Relationship visualization" },
    career_sim: { placeholder: "Enter a career to explore (doctor, engineer, etc.)...", title: "Career Simulation", desc: "Role-play professional scenarios" },
};

export function LearningWorkspace({ activeTool, notebookId }: LearningWorkspaceProps) {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [conversation, setConversation] = useState<ConversationItem[]>([]);
    const [currentResponse, setCurrentResponse] = useState<AIResponse | null>(null);
    const messagesEndRef = useRef<HTMLDivElement>(null);

    const config = toolConfig[activeTool] || toolConfig.qa;

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [conversation, currentResponse]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || loading) return;

        const submittedQuery = query.trim();
        setLoading(true);
        setQuery("");

        try {
            const data = await api.ai.query({
                query: submittedQuery,
                mode: activeTool,
                notebook_id: notebookId,
            }) as { answer?: string; response_text?: string; citations?: Citation[] };

            const response: AIResponse = {
                answer: data.answer || data.response_text || "No response received.",
                citations: data.citations || [],
                mode: activeTool,
            };

            const newItem: ConversationItem = {
                id: Date.now().toString(),
                query: submittedQuery,
                response,
                timestamp: new Date(),
            };

            setConversation((prev) => [...prev, newItem]);
            setCurrentResponse(response);
        } catch (err) {
            const errorResponse: AIResponse = {
                answer: err instanceof APIError ? err.message : "Failed to get response. Please try again.",
                citations: [],
                mode: activeTool,
            };

            const newItem: ConversationItem = {
                id: Date.now().toString(),
                query: submittedQuery,
                response: errorResponse,
                timestamp: new Date(),
            };

            setConversation((prev) => [...prev, newItem]);
            setCurrentResponse(errorResponse);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="flex flex-col h-full">
            {/* Tool Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                <div className="flex items-center gap-3">
                    <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg">
                        <Bot className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h2 className="font-semibold text-[var(--text-primary)]">{config.title}</h2>
                        <p className="text-xs text-[var(--text-muted)]">{config.desc}</p>
                    </div>
                </div>
                <div className="flex items-center gap-2">
                    {conversation.length > 0 && (
                        <button
                            onClick={() => {
                                setConversation([]);
                                setCurrentResponse(null);
                            }}
                            className="px-3 py-1.5 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-colors"
                        >
                            Clear
                        </button>
                    )}
                </div>
            </div>

            {/* Conversation Area */}
            <div className="flex-1 overflow-y-auto px-6 py-4 space-y-6">
                {conversation.length === 0 && !loading && (
                    <div className="flex flex-col items-center justify-center h-full text-center">
                        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-600/20 flex items-center justify-center mb-4">
                            <Sparkles className="w-10 h-10 text-indigo-500" />
                        </div>
                        <h3 className="text-lg font-medium text-[var(--text-primary)] mb-2">
                            Ready to learn?
                        </h3>
                        <p className="text-sm text-[var(--text-muted)] max-w-md mb-6">
                            {config.desc}. Type your query below to get started.
                        </p>
                        <div className="flex flex-wrap justify-center gap-2">
                            {getSuggestions(activeTool).map((suggestion) => (
                                <button
                                    key={suggestion}
                                    onClick={() => setQuery(suggestion)}
                                    className="px-4 py-2 text-xs bg-[var(--bg-page)] hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] rounded-full border border-[var(--border)] transition-colors"
                                >
                                    {suggestion}
                                </button>
                            ))}
                        </div>
                    </div>
                )}

                {conversation.map((item) => (
                    <div key={item.id} className="space-y-4">
                        {/* User Query */}
                        <div className="flex justify-end">
                            <div className="max-w-[85%] bg-gradient-to-br from-indigo-500 to-violet-600 text-white px-5 py-3 rounded-2xl rounded-br-md shadow-md">
                                <p className="text-sm">{item.query}</p>
                            </div>
                        </div>

                        {/* AI Response */}
                        <div className="bg-[var(--bg-page)] rounded-2xl border border-[var(--border)]/50 overflow-hidden">
                            <div className="p-5">
                                <div className="flex items-center gap-2 mb-4">
                                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                                        <Bot className="w-4 h-4 text-white" />
                                    </div>
                                    <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                                        AI Assistant
                                    </span>
                                    <span className="text-xs text-[var(--text-muted)]">
                                        {item.timestamp.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })}
                                    </span>
                                </div>

                                <div className="prose prose-sm max-w-none text-[var(--text-primary)] leading-relaxed">
                                    {item.response.answer}
                                </div>

                                {item.response.citations.length > 0 && (
                                    <div className="mt-4 pt-4 border-t border-[var(--border)]/50">
                                        <p className="text-[10px] font-medium text-[var(--text-muted)] uppercase tracking-wider mb-2">
                                            Sources
                                        </p>
                                        <div className="flex flex-wrap gap-2">
                                            {item.response.citations.map((citation, idx) => (
                                                <span
                                                    key={idx}
                                                    className="inline-flex items-center gap-1.5 px-2 py-1 text-[10px] bg-[var(--bg-card)] text-[var(--text-secondary)] rounded-md border border-[var(--border)]/50"
                                                >
                                                    <BookText className="w-3 h-3" />
                                                    {citation.text || `${citation.source}${citation.page ? ` p.${citation.page}` : ""}`}
                                                </span>
                                            ))}
                                        </div>
                                    </div>
                                )}
                            </div>

                            {/* Response Actions */}
                            <div className="flex items-center gap-1 px-5 py-2 bg-[var(--surface-hover)] border-t border-[var(--border)]/50">
                                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Copy">
                                    <Copy className="w-3.5 h-3.5" />
                                </button>
                                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Helpful">
                                    <ThumbsUp className="w-3.5 h-3.5" />
                                </button>
                                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Not helpful">
                                    <ThumbsDown className="w-3.5 h-3.5" />
                                </button>
                                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Save">
                                    <Bookmark className="w-3.5 h-3.5" />
                                </button>
                                <div className="flex-1" />
                                <ActionBar response={item.response} query={item.query} />
                            </div>
                        </div>
                    </div>
                ))}

                {loading && (
                    <div className="flex items-start gap-3">
                        <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center animate-pulse">
                            <Bot className="w-4 h-4 text-white" />
                        </div>
                        <div className="flex items-center gap-2 py-2">
                            <span className="w-2 h-2 rounded-full bg-[var(--primary)] animate-bounce" style={{ animationDelay: "0ms" }} />
                            <span className="w-2 h-2 rounded-full bg-[var(--primary)] animate-bounce" style={{ animationDelay: "150ms" }} />
                            <span className="w-2 h-2 rounded-full bg-[var(--primary)] animate-bounce" style={{ animationDelay: "300ms" }} />
                            <span className="ml-2 text-sm text-[var(--text-muted)]">Thinking...</span>
                        </div>
                    </div>
                )}

                <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <div className="border-t border-[var(--border)] p-4">
                <form onSubmit={handleSubmit} className="relative">
                    <div className="flex items-end gap-2 bg-[var(--bg-page)] rounded-xl border border-[var(--border)] p-2 focus-within:ring-2 focus-within:ring-[var(--primary)]/50 focus-within:border-[var(--primary)] transition-all">
                        <textarea
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter" && !e.shiftKey) {
                                    e.preventDefault();
                                    handleSubmit(e);
                                }
                            }}
                            placeholder={config.placeholder}
                            rows={1}
                            className="flex-1 min-h-[44px] max-h-[120px] px-3 py-2.5 text-sm bg-transparent border-0 resize-none focus:outline-none text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
                            style={{ height: "auto" }}
                            onInput={(e) => {
                                const target = e.target as HTMLTextAreaElement;
                                target.style.height = "auto";
                                target.style.height = `${Math.min(target.scrollHeight, 120)}px`;
                            }}
                        />
                        <button
                            type="submit"
                            disabled={loading || !query.trim()}
                            className="p-2.5 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-600 text-white hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                        </button>
                    </div>
                    <p className="mt-2 text-[10px] text-[var(--text-muted)] text-center">
                        Press Enter to send, Shift+Enter for new line
                    </p>
                </form>
            </div>
        </div>
    );
}

function getSuggestions(tool: string): string[] {
    const suggestions: Record<string, string[]> = {
        qa: ["Explain photosynthesis", "What is mitosis?", "Newton's laws"],
        study_guide: ["Cell biology", "World War II", "Organic chemistry"],
        socratic: ["Why is the sky blue?", "What causes tides?", "How do computers work?"],
        quiz: ["Cell structure", "Ancient civilizations", "Algebra"],
        flashcards: ["Vocabulary: biology", "Math formulas", "Historical dates"],
        perturbation: ["If x² = 4, find x", "Explain gravity", "Describe osmosis"],
        debate: ["Social media benefits society", "Homework should be banned", "AI will replace jobs"],
        essay_review: ["Paste your essay here..."],
        mindmap: ["Ecosystem", "Human body", "Water cycle"],
        flowchart: ["Photosynthesis process", "Decision making", "Algorithm"],
        concept_map: ["Climate change", "Economic systems", "Cell division"],
        career_sim: ["Doctor", "Software engineer", "Teacher", "Lawyer"],
    };
    return suggestions[tool] || ["Try asking anything..."];
}
