"use client";

import { Suspense, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import {
    Bot,
    BookOpen,
    Globe,
    HelpCircle,
    Loader2,
    MessageSquare,
    PenLine,
    Settings2,
    Shuffle,
    Sparkles,
    Swords,
} from "lucide-react";

import AIHistorySidebar from "@/components/AIHistorySidebar";
import { api } from "@/lib/api";
import { LearningWorkspace } from "../ai-studio/components/LearningWorkspace";

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
    runtime_mode?: string;
    is_demo_response?: boolean;
    demo_notice?: string | null;
}

const modes = [
    { id: "qa", label: "Q&A", icon: HelpCircle, desc: "Ask questions about your notes", gradient: "from-blue-500 to-indigo-600" },
    { id: "study_guide", label: "Study Guide", icon: BookOpen, desc: "Generate a study guide", gradient: "from-emerald-500 to-teal-600" },
    { id: "quiz", label: "Quiz", icon: Sparkles, desc: "Create a quiz from notes", gradient: "from-violet-500 to-purple-600" },
    { id: "socratic", label: "Socratic", icon: MessageSquare, desc: "Guided hints, no answers", gradient: "from-amber-500 to-orange-600" },
    { id: "perturbation", label: "Exam Prep", icon: Shuffle, desc: "Novel question variations", gradient: "from-rose-500 to-pink-600" },
    { id: "debate", label: "Debate", icon: Swords, desc: "Challenge your arguments", gradient: "from-red-500 to-rose-600" },
    { id: "essay_review", label: "Essay Review", icon: PenLine, desc: "Feedback on writing", gradient: "from-cyan-500 to-blue-600" },
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

interface HistoryItem {
    id: string;
    mode: string;
    query_text: string;
    response_text: string;
}

export default function AIAssistantPage() {
    return (
        <Suspense fallback={<div className="flex items-center justify-center h-64"><Loader2 className="w-8 h-8 animate-spin text-[var(--primary)]" /></div>}>
            <AIAssistantContent />
        </Suspense>
    );
}

function AIAssistantContent() {
    const searchParams = useSearchParams();
    const [mode, setMode] = useState("qa");
    const [language, setLanguage] = useState("english");
    const [responseLength, setResponseLength] = useState("default");
    const [expertiseLevel, setExpertiseLevel] = useState("standard");
    const [showSettings, setShowSettings] = useState(false);
    const [initialExchange, setInitialExchange] = useState<{ query: string; response: AIResponse } | null>(null);

    const activeMode = modes.find((m) => m.id === mode) || modes[0];

    useEffect(() => {
        const historyId = searchParams.get("history");
        if (!historyId) {
            setInitialExchange(null);
            return;
        }

        api.aiHistory.get(historyId).then((item) => {
            const historyItem = item as HistoryItem;
            setMode(historyItem.mode);
            setInitialExchange({
                query: historyItem.query_text,
                response: {
                    answer: historyItem.response_text,
                    citations: [],
                    mode: historyItem.mode,
                },
            });
        }).catch((err) => {
            console.error("Failed to load history item:", err);
        });
    }, [searchParams]);

    return (
        <div className="flex gap-4 max-w-6xl mx-auto">
            <div className="flex-1 max-w-4xl">
                <div className="mb-4">
                    <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                        <div className="flex items-center gap-3">
                            <div className={`p-2 rounded-xl bg-gradient-to-br ${activeMode.gradient} shadow-lg`}>
                                <Bot className="w-5 h-5 text-white" />
                            </div>
                            <div>
                                <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Study Assistant</h1>
                                <p className="text-xs text-[var(--text-muted)]">Unified assistant-ui shell • structured AI modes</p>
                            </div>
                        </div>
                        <div className="flex items-center gap-2 self-start sm:self-auto">
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
                            <button
                                onClick={() => setShowSettings((prev) => !prev)}
                                className={`p-2 rounded-xl border transition-all ${showSettings ? "bg-[var(--primary)] text-white border-[var(--primary)]" : "bg-[var(--bg-card)] text-[var(--text-muted)] border-[var(--border)]/50 hover:border-[var(--primary)]"}`}
                            >
                                <Settings2 className="w-4 h-4" />
                            </button>
                        </div>
                    </div>
                </div>

                {showSettings ? (
                    <div className="bg-[var(--bg-card)] rounded-2xl p-4 mb-4 border border-[var(--border)]/50 shadow-sm">
                        <div className="grid grid-cols-1 gap-4 md:grid-cols-2">
                            <div>
                                <label className="block text-[10px] font-bold text-[var(--text-muted)] mb-2 uppercase tracking-wider">Response Length</label>
                                <div className="flex gap-1.5">
                                    {[
                                        { id: "brief", label: "Brief" },
                                        { id: "default", label: "Default" },
                                        { id: "detailed", label: "Detailed" },
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
                                        { id: "simple", label: "Simple" },
                                        { id: "standard", label: "Standard" },
                                        { id: "advanced", label: "Advanced" },
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
                ) : null}

                <div className="grid grid-cols-2 gap-2 mb-4 sm:grid-cols-4">
                    {modes.map((m) => (
                        <button
                            key={m.id}
                            onClick={() => {
                                setMode(m.id);
                                setInitialExchange(null);
                            }}
                            title={m.desc}
                            className={`group relative flex flex-col items-center gap-1.5 px-3 py-3 rounded-xl text-xs font-medium transition-all duration-200 ${mode === m.id
                                ? `bg-gradient-to-br ${m.gradient} text-white shadow-lg scale-[1.03]`
                                : "bg-[var(--bg-card)] text-[var(--text-secondary)] border border-[var(--border)] hover:shadow-md hover:scale-[1.02]"
                                }`}
                        >
                            <m.icon className={`w-4 h-4 transition-transform group-hover:scale-110 ${mode === m.id ? "text-white" : "text-[var(--primary)]"}`} />
                            <span className="leading-tight">{m.label}</span>
                        </button>
                    ))}
                </div>

                <div className="min-h-[720px] overflow-hidden rounded-2xl border border-[var(--border)] bg-[var(--bg-card)] shadow-[var(--shadow-card)]">
                    <LearningWorkspace
                        activeTool={mode}
                        notebookId={null}
                        requestOptions={{
                            language,
                            responseLength,
                            expertiseLevel,
                        }}
                        initialExchange={initialExchange}
                    />
                </div>
            </div>

            <aside className="hidden lg:block w-80 shrink-0">
                <AIHistorySidebar
                    currentMode={mode}
                    onSelectItem={(item) => {
                        setMode(item.mode);
                        setInitialExchange({
                            query: item.query_text,
                            response: {
                                answer: item.response_text,
                                citations: [],
                                mode: item.mode,
                            },
                        });
                    }}
                />
            </aside>
        </div>
    );
}
