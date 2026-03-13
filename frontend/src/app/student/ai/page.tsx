"use client";

import { useEffect, useState } from "react";
import { Bot, Send, Loader2, FileText, Sparkles, HelpCircle, BookOpen, MessageSquare, Shuffle, Swords, PenLine, Briefcase, Globe, Settings2 } from "lucide-react";
import { api } from "@/lib/api";

type Citation = {
    source?: string;
    page?: string | null;
    url?: string | null;
    text?: string;
    clickable?: boolean;
};

interface AIResponse {
    answer: string;
    citations: Citation[];
    mode: string;
}

type AIJobStatus = "queued" | "running" | "completed" | "failed";

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

const languages = [
    { id: "english", label: "English", flag: "🇬🇧" },
    { id: "hindi", label: "हिंदी", flag: "🇮🇳" },
    { id: "tamil", label: "தமிழ்", flag: "🇮🇳" },
    { id: "telugu", label: "తెలుగు", flag: "🇮🇳" },
    { id: "kannada", label: "ಕನ್ನಡ", flag: "🇮🇳" },
    { id: "bengali", label: "বাংলা", flag: "🇮🇳" },
    { id: "marathi", label: "मराठी", flag: "🇮🇳" },
    { id: "gujarati", label: "ગુજરાતી", flag: "🇮🇳" },
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
    const [language, setLanguage] = useState("english");
    const [responseLength, setResponseLength] = useState("default");
    const [expertiseLevel, setExpertiseLevel] = useState("standard");
    const [showSettings, setShowSettings] = useState(false);
    const [jobId, setJobId] = useState<string | null>(null);
    const [jobStatus, setJobStatus] = useState<AIJobStatus | null>(null);
    const [pendingQuery, setPendingQuery] = useState<string | null>(null);

    const QUEUED_MODES = new Set(["study_guide", "quiz"]);

    const activeMode = modes.find((m) => m.id === mode) || modes[0];

    useEffect(() => {
        if (!jobId || !pendingQuery) return;

        let cancelled = false;
        let timer: ReturnType<typeof setTimeout> | null = null;

        const poll = async () => {
            try {
                const job = await api.ai.jobStatus(jobId) as {
                    status: AIJobStatus;
                    error?: string;
                    result?: {
                        answer: string;
                        citations?: Citation[];
                        mode: string;
                    };
                    poll_after_ms?: number;
                };

                if (cancelled) return;
                setJobStatus(job.status);

                if (job.status === "completed" && job.result) {
                    const result = job.result;
                    setHistory((prev) => [
                        ...prev,
                        {
                            query: pendingQuery,
                            response: {
                                answer: result.answer || "No response received.",
                                citations: result.citations || [],
                                mode: result.mode || mode,
                            },
                        },
                    ]);
                    setLoading(false);
                    setJobId(null);
                    setPendingQuery(null);
                    return;
                }

                if (job.status === "failed") {
                    setHistory((prev) => [
                        ...prev,
                        {
                            query: pendingQuery,
                            response: {
                                answer: job.error || "Sorry, something went wrong. Please try again.",
                                citations: [],
                                mode,
                            },
                        },
                    ]);
                    setLoading(false);
                    setJobId(null);
                    setPendingQuery(null);
                    return;
                }

                timer = setTimeout(() => {
                    void poll();
                }, job.poll_after_ms ?? 2000);
            } catch {
                if (cancelled) return;
                setHistory((prev) => [
                    ...prev,
                    {
                        query: pendingQuery,
                        response: {
                            answer: "Cannot connect to AI service. Make sure the backend is running.",
                            citations: [],
                            mode,
                        },
                    },
                ]);
                setLoading(false);
                setJobId(null);
                setPendingQuery(null);
            }
        };

        void poll();

        return () => {
            cancelled = true;
            if (timer) clearTimeout(timer);
        };
    }, [jobId, pendingQuery, mode]);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        if (!query.trim() || loading) return;

        const submittedQuery = query.trim();
        setLoading(true);
        try {
            if (QUEUED_MODES.has(mode)) {
                const job = await api.ai.enqueueQueryJob({
                    query: submittedQuery,
                    mode,
                    language,
                    response_length: responseLength,
                    expertise_level: expertiseLevel,
                }) as { job_id: string; status: AIJobStatus };
                setPendingQuery(submittedQuery);
                setJobId(job.job_id);
                setJobStatus(job.status);
            } else {
                const data = await api.ai.query({
                    query: submittedQuery,
                    mode,
                    language,
                    response_length: responseLength,
                    expertise_level: expertiseLevel,
                }) as { answer?: string; response_text?: string; citations?: Citation[] };
                const aiResponse: AIResponse = {
                    answer: data.answer || data.response_text || "No response received.",
                    citations: data.citations || [],
                    mode,
                };
                setHistory((prev) => [...prev, { query: submittedQuery, response: aiResponse }]);
                setLoading(false);
            }
        } catch {
            setHistory((prev) => [...prev, {
                query: submittedQuery, response: {
                    answer: "Cannot connect to AI service. Make sure the backend is running.",
                    citations: [],
                    mode,
                }
            }]);
            setLoading(false);
        }
        setQuery("");
    };

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-4">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                    <div className="flex items-center gap-3">
                        <div className={`p-2 rounded-xl bg-gradient-to-br ${activeMode.gradient} shadow-lg`}>
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Study Assistant</h1>
                            <p className="text-xs text-[var(--text-muted)]">Powered by RAG • Citation-grounded</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-2 self-start sm:self-auto">
                        {/* Language Selector */}
                        <div className="flex items-center gap-1.5 bg-[var(--bg-card)] border border-[var(--border)]/50 rounded-xl px-3 py-2">
                            <Globe className="w-3.5 h-3.5 text-[var(--text-muted)]" />
                            <select
                                value={language}
                                onChange={(e) => setLanguage(e.target.value)}
                                className="text-xs bg-transparent border-0 focus:outline-none text-[var(--text-secondary)] cursor-pointer"
                            >
                                {languages.map((l) => (
                                    <option key={l.id} value={l.id}>{l.flag} {l.label}</option>
                                ))}
                            </select>
                        </div>
                        {/* Settings Toggle */}
                        <button
                            onClick={() => setShowSettings(!showSettings)}
                            className={`p-2 rounded-xl border transition-all ${showSettings ? "bg-[var(--primary)] text-white border-[var(--primary)]" : "bg-[var(--bg-card)] text-[var(--text-muted)] border-[var(--border)]/50 hover:border-[var(--primary)]"}`}
                        >
                            <Settings2 className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>

            {/* Settings Panel */}
            {showSettings && (
                <div className="bg-[var(--bg-card)] rounded-2xl p-4 mb-4 border border-[var(--border)]/50 shadow-sm animate-[fadeIn_0.2s_ease-out]">
                    <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                        <div>
                            <label className="block text-[10px] font-bold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Response Length</label>
                            <div className="flex gap-1.5">
                                {[
                                    { id: "brief", label: "Brief", desc: "~2-3 paragraphs" },
                                    { id: "default", label: "Default", desc: "Standard" },
                                    { id: "detailed", label: "Detailed", desc: "In-depth" },
                                ].map((opt) => (
                                    <button
                                        key={opt.id}
                                        onClick={() => setResponseLength(opt.id)}
                                        className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all ${responseLength === opt.id ? "bg-gradient-to-r from-blue-500 to-indigo-600 text-white shadow-sm" : "bg-[var(--bg-page)] text-[var(--text-secondary)] hover:bg-[var(--border)]/30"}`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                        <div>
                            <label className="block text-[10px] font-bold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Expertise Level</label>
                            <div className="flex gap-1.5">
                                {[
                                    { id: "simple", label: "Simple", desc: "For young students" },
                                    { id: "standard", label: "Standard", desc: "Age-appropriate" },
                                    { id: "advanced", label: "Advanced", desc: "Technical depth" },
                                ].map((opt) => (
                                    <button
                                        key={opt.id}
                                        onClick={() => setExpertiseLevel(opt.id)}
                                        className={`flex-1 px-3 py-2 rounded-lg text-xs font-medium transition-all ${expertiseLevel === opt.id ? "bg-gradient-to-r from-emerald-500 to-teal-600 text-white shadow-sm" : "bg-[var(--bg-page)] text-[var(--text-secondary)] hover:bg-[var(--border)]/30"}`}
                                    >
                                        {opt.label}
                                    </button>
                                ))}
                            </div>
                        </div>
                    </div>
                </div>
            )}

            {/* Mode Selector */}
            <div className="grid grid-cols-2 gap-2 mb-4 sm:grid-cols-4">
                {modes.map((m) => (
                    <button
                        key={m.id}
                        onClick={() => setMode(m.id)}
                        disabled={loading}
                        title={m.desc}
                        className={`group relative flex flex-col items-center gap-1.5 px-3 py-3 rounded-xl text-xs font-medium transition-all duration-200 ${mode === m.id
                                ? `bg-gradient-to-br ${m.gradient} text-white shadow-lg scale-[1.03]`
                                : "bg-[var(--bg-card)] text-[var(--text-secondary)] border border-[var(--border)] hover:shadow-md hover:scale-[1.02]"
                            } ${loading ? "opacity-60 cursor-not-allowed" : ""}`}
                    >
                        <m.icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${mode === m.id ? "text-white" : "text-[var(--primary)]"}`} />
                        <span className="leading-tight">{m.label}</span>
                    </button>
                ))}
            </div>

            {/* Chat History */}
            <div className="space-y-4 mb-6">
                {history.map((item, i) => {
                    const itemMode = modes.find((m) => m.id === item.response.mode) || modes[0];
                    return (
                        <div key={i} className="space-y-3">
                            <div className="flex justify-end">
                                <div className={`bg-gradient-to-br ${itemMode.gradient} text-white px-4 py-3 rounded-2xl rounded-br-md max-w-[90%] sm:max-w-[80%] shadow-md`}>
                                    <p className="text-sm">{item.query}</p>
                                </div>
                            </div>
                            <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50">
                                <div className="flex items-center gap-2 mb-3">
                                    <div className={`p-1 rounded-lg bg-gradient-to-br ${itemMode.gradient}`}>
                                        <Bot className="w-3 h-3 text-white" />
                                    </div>
                                    <span className={`text-[10px] font-semibold uppercase tracking-wider bg-gradient-to-r ${itemMode.gradient} bg-clip-text text-transparent`}>
                                        {item.response.mode.replace("_", " ")}
                                    </span>
                                </div>
                                <div className="text-sm text-[var(--text-primary)] leading-relaxed whitespace-pre-wrap">{item.response.answer}</div>
                                {item.response.citations.length > 0 && (
                                    <div className="mt-4 pt-3 border-t border-[var(--border)]/50">
                                        <p className="text-[10px] font-semibold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Sources</p>
                                        <div className="flex flex-wrap gap-1.5">
                                            {item.response.citations.map((c, j) => {
                                                const label = c.text || `${c.source || "Document"}${c.page ? ` p.${c.page}` : ""}`;
                                                const content = (
                                                    <>
                                                        <FileText className="w-2.5 h-2.5" />
                                                        {label}
                                                    </>
                                                );
                                                if (c.url) {
                                                    return (
                                                        <a
                                                            key={j}
                                                            href={c.url}
                                                            target="_blank"
                                                            rel="noopener noreferrer"
                                                            className="inline-flex items-center gap-1 text-[10px] bg-[var(--bg-page)] text-[var(--text-secondary)] px-2 py-1 rounded-lg border border-[var(--border)]/30 hover:text-[var(--primary)] hover:border-[var(--primary)]/40 transition"
                                                        >
                                                            {content}
                                                        </a>
                                                    );
                                                }
                                                return (
                                                    <span key={j} className="inline-flex items-center gap-1 text-[10px] bg-[var(--bg-page)] text-[var(--text-secondary)] px-2 py-1 rounded-lg border border-[var(--border)]/30">
                                                        {content}
                                                    </span>
                                                );
                                            })}
                                        </div>
                                    </div>
                                )}
                            </div>
                        </div>
                    );
                })}
                {loading && (
                    <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-xl bg-gradient-to-br ${activeMode.gradient} animate-pulse`}>
                                <Bot className="w-4 h-4 text-white" />
                            </div>
                            <div>
                                <p className="text-sm font-medium text-[var(--text-primary)]">
                                    {jobStatus === "queued" ? "Queued..." : "Thinking..."}
                                </p>
                                <p className="text-xs text-[var(--text-muted)]">
                                    {jobStatus === "queued"
                                        ? "Waiting for the AI worker to pick up this request"
                                        : "Searching notes and generating response"}
                                </p>
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
                <div className="bg-[var(--bg-card)] rounded-2xl p-12 shadow-[var(--shadow-card)] text-center mb-6 border border-[var(--border)]/50">
                    <div className={`w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br ${activeMode.gradient} flex items-center justify-center shadow-lg`}>
                        <Bot className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">Ask about your notes</h3>
                    <p className="text-sm text-[var(--text-muted)] max-w-md mx-auto mb-6">
                        Type a question below. The AI will search your uploaded curriculum materials and respond with citations.
                    </p>
                    <div className="flex flex-wrap justify-center gap-2">
                        {["Explain photosynthesis", "What is a quadratic equation?", "Summarize Chapter 3"].map((s) => (
                            <button key={s} onClick={() => setQuery(s)} className="px-4 py-2 text-xs font-medium text-[var(--primary)] bg-[var(--primary-light)] rounded-full hover:bg-[var(--primary)] hover:text-white transition-all duration-200 hover:shadow-md">{s}</button>
                        ))}
                    </div>
                </div>
            )}

            {/* Input */}
            <form onSubmit={handleSubmit} className="sticky bottom-4 bg-[var(--bg-card)] rounded-2xl shadow-xl p-3 flex items-center gap-2 sm:gap-3 border border-[var(--border)]/50">
                <input
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder={placeholders[mode] || "Type your question..."}
                    className="flex-1 min-w-0 px-3 py-3 sm:px-4 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-[var(--primary)]/50"
                    disabled={loading}
                />
                <button
                    type="submit"
                    disabled={loading || !query.trim()}
                    className={`px-4 py-3 sm:px-5 bg-gradient-to-r ${activeMode.gradient} text-white rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-40 disabled:cursor-not-allowed hover:scale-[1.02]`}
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
            </form>
        </div>
    );
}
