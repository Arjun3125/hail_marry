"use client";

import { useEffect, useMemo, useState, useCallback, useRef } from "react";
import {
    Brain,
    ChevronLeft,
    ChevronRight,
    GitBranch,
    HelpCircle,
    Layers,
    Loader2,
    Network,
    Sparkles,
    Library,
    Clock,
    Pin,
} from "lucide-react";

import { api } from "@/lib/api";

type Tool = "quiz" | "flashcards" | "mindmap" | "flowchart" | "concept_map";
type AIJobStatus = "queued" | "running" | "completed" | "failed";

type QuizQ = { question: string; options: string[]; correct: string; citation?: string | null };
type Flashcard = { front: string; back: string };
type MindNode = { label: string; children?: MindNode[] };
type ConceptMap = { nodes: { id: string; label: string }[]; edges: { from: string; to: string; label: string }[] };
type ToolData = QuizQ[] | Flashcard[] | MindNode | ConceptMap | string | null;
type Citation = { source?: string; page?: string | null; url?: string | null; text?: string; clickable?: boolean };
type AIHistoryItem = {
    id: string;
    mode: string;
    query_text: string;
    response_text: string;
    title: string | null;
    created_at: string;
    is_pinned: boolean;
    folder_id: string | null;
};

const tools: { id: Tool; label: string; icon: typeof Brain; desc: string; color: string }[] = [
    { id: "quiz", label: "Quiz", icon: HelpCircle, desc: "MCQ quiz from your notes", color: "from-violet-500 to-pink-600" },
    { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Revision cards", color: "from-amber-500 to-orange-600" },
    { id: "mindmap", label: "Mind Map", icon: Brain, desc: "Topic hierarchy", color: "from-emerald-500 to-green-600" },
    { id: "flowchart", label: "Flowchart", icon: GitBranch, desc: "Step process flow", color: "from-sky-500 to-blue-600" },
    { id: "concept_map", label: "Concept Map", icon: Network, desc: "Linked concept graph", color: "from-rose-500 to-red-600" },
];

export default function StudyToolsPage() {
    const [activeTab, setActiveTab] = useState<"create" | "library">("create");
    const [activeTool, setActiveTool] = useState<Tool | null>(null);
    const [topic, setTopic] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ToolData>(null);
    const [citations, setCitations] = useState<Citation[]>([]);
    const [jobId, setJobId] = useState<string | null>(null);
    const [jobStatus, setJobStatus] = useState<AIJobStatus | null>(null);
    
    // Library state
    const [libraryItems, setLibraryItems] = useState<AIHistoryItem[]>([]);
    const [libraryLoading, setLibraryLoading] = useState(false);

    const selectedTool = useMemo(() => tools.find((tool) => tool.id === activeTool) || null, [activeTool]);
    const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
    
    // Inline history for selected tool
    const [toolHistory, setToolHistory] = useState<AIHistoryItem[]>([]);
    
    useEffect(() => {
        if (activeTool) {
            api.aiHistory.list({ mode: activeTool, page: 1 }).then((res) => {
                setToolHistory((res as { items: AIHistoryItem[] }).items?.slice(0, 3) || []);
            });
        }
    }, [activeTool]);
    
    // Load library items
    const loadLibrary = useCallback(async () => {
        try {
            setLibraryLoading(true);
            const toolModes = ["quiz", "flashcards", "mindmap", "flowchart", "concept_map"];
            const allItems: AIHistoryItem[] = [];
            for (const mode of toolModes) {
                const res = await api.aiHistory.list({ mode, page: 1 }) as { items: AIHistoryItem[] };
                if (res.items) {
                    allItems.push(...res.items);
                }
            }
            // Sort by created_at desc
            allItems.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
            setLibraryItems(allItems);
        } catch (err) {
            console.error("Failed to load library:", err);
        } finally {
            setLibraryLoading(false);
        }
    }, []);
    
    useEffect(() => {
        if (activeTab === "library") {
            void loadLibrary();
        }
    }, [activeTab, loadLibrary]);

    useEffect(() => {
        if (!jobId) return;

        let cancelled = false;
        let timer: ReturnType<typeof setTimeout> | null = null;

        const poll = async () => {
            try {
                const job = await api.ai.jobStatus(jobId) as {
                    status: AIJobStatus;
                    error?: string;
                    result?: {
                        data: ToolData;
                        citations?: Citation[];
                    };
                    poll_after_ms?: number;
                };

                if (cancelled) return;
                setJobStatus(job.status);

                if (job.status === "completed" && job.result) {
                    setResult(job.result.data || null);
                    setCitations(job.result.citations || []);
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                if (job.status === "failed") {
                    setError(job.error || "Failed to generate study tool");
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                timer = setTimeout(() => {
                    void poll();
                }, job.poll_after_ms ?? 2000);
            } catch (err) {
                if (cancelled) return;
                setError(err instanceof Error ? err.message : "Failed to load job status");
                setLoading(false);
                setJobId(null);
            }
        };

        void poll();

        return () => {
            cancelled = true;
            if (timer) clearTimeout(timer);
        };
    }, [jobId]);

    const generateResult = async () => {
        if (!activeTool || !topic.trim()) return;
        try {
            setLoading(true);
            setError(null);
            setResult(null);
            setCitations([]);

            if (isDemoMode) {
                // In demo mode, use synchronous endpoint to bypass Redis job queue
                const data = (await api.student.generateTool({
                    tool: activeTool,
                    topic: topic.trim(),
                })) as { data?: ToolData; citations?: Citation[] };
                setResult(data.data || data as unknown as ToolData);
                setCitations(data.citations || []);
                setLoading(false);
            } else {
                setJobStatus("queued");
                const payload = (await api.student.enqueueToolJob({
                    tool: activeTool,
                    topic: topic.trim(),
                })) as {
                    job_id: string;
                    status: AIJobStatus;
                };
                setJobId(payload.job_id);
                setJobStatus(payload.status);
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate study tool");
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Study Tools</h1>
                <p className="text-sm text-[var(--text-secondary)]">Generate quizzes, flashcards, mind maps, flowcharts, and concept maps from your uploaded materials.</p>
            </div>

            {/* Tabs */}
            <div className="flex border-b border-[var(--border)] mb-6">
                <button
                    onClick={() => setActiveTab("create")}
                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                        activeTab === "create"
                            ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
                            : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                >
                    <Sparkles className="w-4 h-4" />
                    Create New
                </button>
                <button
                    onClick={() => setActiveTab("library")}
                    className={`flex items-center gap-2 px-4 py-3 text-sm font-medium transition-colors ${
                        activeTab === "library"
                            ? "text-[var(--primary)] border-b-2 border-[var(--primary)]"
                            : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
                    }`}
                >
                    <Library className="w-4 h-4" />
                    My Library
                    {libraryItems.length > 0 && (
                        <span className="ml-1 text-xs bg-[var(--primary)] text-white px-2 py-0.5 rounded-full">
                            {libraryItems.length}
                        </span>
                    )}
                </button>
            </div>

            {activeTab === "create" ? (
                <>
                    {error ? (
                        <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                            {error}
                        </div>
                    ) : null}

                    <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                        {tools.map((tool) => (
                            <button
                                key={tool.id}
                                onClick={() => {
                                    if (loading) return;
                                    setActiveTool(tool.id);
                                    setResult(null);
                                    setCitations([]);
                                }}
                                className={`p-4 rounded-[var(--radius)] text-center transition-all ${
                                    activeTool === tool.id
                                        ? `bg-gradient-to-br ${tool.color} text-white shadow-lg scale-[1.02]`
                                        : "bg-[var(--bg-card)] shadow-[var(--shadow-card)] hover:shadow-md text-[var(--text-primary)]"
                                } ${loading ? "opacity-60 cursor-not-allowed" : ""}`}
                            >
                                <tool.icon className={`w-6 h-6 mx-auto mb-2 ${activeTool === tool.id ? "text-white" : "text-[var(--primary)]"}`} />
                                <p className="text-xs font-semibold">{tool.label}</p>
                                <p className={`text-[10px] mt-0.5 ${activeTool === tool.id ? "text-white/80" : "text-[var(--text-muted)]"}`}>{tool.desc}</p>
                            </button>
                        ))}
                    </div>

                    {activeTool ? (
                        <>
                            {/* Recent items for this tool */}
                            {toolHistory.length > 0 && (
                                <div className="mb-4 bg-[var(--bg-card)] rounded-[var(--radius)] border border-[var(--border)]/50 p-3">
                                    <div className="flex items-center gap-2 text-xs text-[var(--text-secondary)] mb-2">
                                        <Clock className="w-3.5 h-3.5" />
                                        <span>Recent {selectedTool?.label} you created</span>
                                    </div>
                                    <div className="space-y-2">
                                        {toolHistory.map((item) => (
                                            <div
                                                key={item.id}
                                                className="flex items-center gap-2 p-2 rounded hover:bg-[var(--surface-hover)] cursor-pointer transition-colors"
                                                onClick={() => setTopic(item.query_text)}
                                            >
                                                {item.is_pinned && <Pin className="w-3 h-3 text-[var(--primary)]" />}
                                                <span className="text-sm text-[var(--text-primary)] truncate flex-1">
                                                    {item.title || item.query_text}
                                                </span>
                                                <span className="text-xs text-[var(--text-muted)]">
                                                    {new Date(item.created_at).toLocaleDateString()}
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}

                            <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 mb-6">
                                <div className="flex gap-3">
                                    <input
                                        value={topic}
                                        onChange={(event) => setTopic(event.target.value)}
                                        onKeyDown={(event) => {
                                            if (event.key === "Enter") {
                                                void generateResult();
                                            }
                                        }}
                                        placeholder={`Enter a topic for your ${selectedTool?.label || "tool"}...`}
                                        className="flex-1 px-4 py-2.5 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                                    />
                                    <button
                                        onClick={() => void generateResult()}
                                        disabled={loading || !topic.trim()}
                                        className="px-5 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] disabled:opacity-50 flex items-center gap-2"
                                    >
                                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Sparkles className="w-4 h-4" />}
                                        Generate
                                    </button>
                                </div>
                            </div>

                            {loading ? (
                                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-12 text-center">
                                    <Loader2 className="w-8 h-8 mx-auto text-[var(--primary)] animate-spin mb-3" />
                                    <p className="text-sm text-[var(--text-secondary)]">
                                        {jobStatus === "queued" ? `Queued ${selectedTool?.label}...` : `Generating ${selectedTool?.label}...`}
                                    </p>
                                </div>
                            ) : null}

                            {!loading && result && activeTool === "quiz" ? <QuizView questions={result as QuizQ[]} /> : null}
                            {!loading && result && activeTool === "flashcards" ? <FlashcardsView cards={result as Flashcard[]} /> : null}
                            {!loading && result && activeTool === "mindmap" ? <MindMapView data={result as MindNode} /> : null}
                            {!loading && result && activeTool === "flowchart" ? <FlowchartView code={result as string} /> : null}
                            {!loading && result && activeTool === "concept_map" ? <ConceptMapView data={result as ConceptMap} /> : null}

                            {!loading && citations.length > 0 ? (
                                <div className="mt-4 bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                                    <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Sources</p>
                                    <div className="flex flex-wrap gap-2">
                                        {citations.map((citation, idx) => {
                                            const label = citation.text || `${citation.source || "Document"}${citation.page ? ` p.${citation.page}` : ""}`;
                                            if (citation.url) {
                                                return (
                                                    <a
                                                        key={`${citation.source || "src"}-${citation.page || "page"}-${idx}`}
                                                        href={citation.url}
                                                        target="_blank"
                                                        rel="noopener noreferrer"
                                                        className="text-[10px] px-2 py-1 rounded-full bg-[var(--bg-page)] text-[var(--text-secondary)] hover:text-[var(--primary)] transition"
                                                    >
                                                        {label}
                                                    </a>
                                                );
                                            }
                                            return (
                                                <span key={`${citation.source || "src"}-${citation.page || "page"}-${idx}`} className="text-[10px] px-2 py-1 rounded-full bg-[var(--bg-page)] text-[var(--text-secondary)]">
                                                    {label}
                                                </span>
                                            );
                                        })}
                                    </div>
                                </div>
                            ) : null}
                        </>
                    ) : null}
                </>
            ) : (
                // Library View
                <div>
                    {libraryLoading ? (
                        <div className="flex items-center justify-center py-12">
                            <Loader2 className="w-8 h-8 animate-spin text-[var(--primary)]" />
                        </div>
                    ) : libraryItems.length === 0 ? (
                        <div className="text-center py-12">
                            <Library className="w-16 h-16 mx-auto mb-4 text-[var(--text-muted)] opacity-50" />
                            <h3 className="text-lg font-medium text-[var(--text-primary)] mb-2">No saved tools yet</h3>
                            <p className="text-sm text-[var(--text-secondary)] mb-4">Generate quizzes, flashcards, and more to build your library</p>
                            <button
                                onClick={() => setActiveTab("create")}
                                className="px-4 py-2 bg-[var(--primary)] text-white rounded-lg text-sm font-medium hover:bg-[var(--primary-hover)] transition-colors"
                            >
                                Create Your First Tool
                            </button>
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                            {libraryItems.map((item) => (
                                <div
                                    key={item.id}
                                    className="group bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 hover:shadow-md transition-all cursor-pointer"
                                    onClick={() => {
                                        setActiveTab("create");
                                        setActiveTool(item.mode as Tool);
                                        setTopic(item.query_text);
                                    }}
                                >
                                    <div className="flex items-start justify-between mb-3">
                                        <div className="flex items-center gap-2">
                                            {item.mode === "quiz" && <HelpCircle className="w-5 h-5 text-violet-500" />}
                                            {item.mode === "flashcards" && <Layers className="w-5 h-5 text-amber-500" />}
                                            {item.mode === "mindmap" && <Brain className="w-5 h-5 text-emerald-500" />}
                                            {item.mode === "flowchart" && <GitBranch className="w-5 h-5 text-sky-500" />}
                                            {item.mode === "concept_map" && <Network className="w-5 h-5 text-rose-500" />}
                                            <span className="text-xs font-medium px-2 py-0.5 bg-[var(--bg-page)] rounded-full text-[var(--text-secondary)] capitalize">
                                                {item.mode.replace("_", " ")}
                                            </span>
                                        </div>
                                        {item.is_pinned && <Pin className="w-4 h-4 text-[var(--primary)]" />}
                                    </div>
                                    <h3 className="font-medium text-[var(--text-primary)] mb-2 line-clamp-2">
                                        {item.title || item.query_text}
                                    </h3>
                                    <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
                                        <Clock className="w-3 h-3" />
                                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}

function QuizView({ questions }: { questions: QuizQ[] }) {
    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-4">Generated Quiz</h3>
            <div className="space-y-4">
                {questions.map((question, idx) => (
                    <div key={`quiz-${idx}`} className="p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]">
                        <p className="text-sm font-medium text-[var(--text-primary)] mb-2">{idx + 1}. {question.question}</p>
                        <ul className="space-y-1">
                            {question.options.map((option, optionIdx) => (
                                <li key={`opt-${idx}-${optionIdx}`} className="text-xs text-[var(--text-secondary)]">{option}</li>
                            ))}
                        </ul>
                        <p className="mt-2 text-xs font-semibold text-[var(--primary)]">Correct: {question.correct}</p>
                        {question.citation ? <p className="text-[10px] text-[var(--text-muted)]">Citation: {question.citation}</p> : null}
                    </div>
                ))}
            </div>
        </div>
    );
}

function FlashcardsView({ cards }: { cards: Flashcard[] }) {
    const [current, setCurrent] = useState(0);
    const [flipped, setFlipped] = useState(false);
    const card = cards[current];

    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
            <div className="flex items-center justify-between mb-4">
                <span className="text-xs text-[var(--text-muted)]">Card {current + 1} of {cards.length}</span>
                <div className="flex gap-2">
                    <button
                        onClick={() => {
                            setCurrent(Math.max(0, current - 1));
                            setFlipped(false);
                        }}
                        disabled={current === 0}
                        className="p-1 rounded border border-[var(--border)] disabled:opacity-30"
                    >
                        <ChevronLeft className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => {
                            setCurrent(Math.min(cards.length - 1, current + 1));
                            setFlipped(false);
                        }}
                        disabled={current === cards.length - 1}
                        className="p-1 rounded border border-[var(--border)] disabled:opacity-30"
                    >
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </div>

            <button
                onClick={() => setFlipped((prev) => !prev)}
                className="w-full text-left p-5 rounded-[var(--radius-sm)] bg-[var(--primary-light)] hover:bg-info-badge transition-colors"
            >
                <p className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] mb-2">{flipped ? "Answer" : "Prompt"}</p>
                <p className="text-sm text-[var(--text-primary)]">{flipped ? card.back : card.front}</p>
            </button>
        </div>
    );
}

function MindMapView({ data }: { data: MindNode }) {
    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6 overflow-x-auto">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">Mind Map</h3>
            <MindNodeView node={data} depth={0} />
        </div>
    );
}

function MindNodeView({ node, depth }: { node: MindNode; depth: number }) {
    const colors = [
        "bg-[var(--primary)] text-white",
        "bg-info-badge text-status-blue",
        "bg-success-badge text-status-green",
        "bg-orange-100 text-orange-800",
    ];
    return (
        <div className={depth > 0 ? "ml-6 mt-2" : ""}>
            <div className={`inline-block px-3 py-1.5 rounded-full text-xs font-medium ${colors[depth % colors.length]}`}>
                {node.label}
            </div>
            {(node.children || []).map((child, idx) => (
                <MindNodeView key={`${depth}-${idx}-${child.label}`} node={child} depth={depth + 1} />
            ))}
        </div>
    );
}

function FlowchartView({ code }: { code: string }) {
    const containerRef = useRef<HTMLDivElement>(null);
    const [svg, setSvg] = useState<string>("");
    const [renderError, setRenderError] = useState(false);

    useEffect(() => {
        let cancelled = false;
        if (!code) return;
        
        // Dynamic import to avoid SSR issues with Mermaid
        import("mermaid").then(async (mod) => {
            const mermaid = mod.default;
            mermaid.initialize({ startOnLoad: false, theme: "neutral" });
            try {
                // Mermaid needs a unique ID per render
                const id = `mermaid-${Math.random().toString(36).substring(2, 9)}`;
                const { svg: rendered } = await mermaid.render(id, code);
                if (!cancelled) {
                    setSvg(rendered);
                    setRenderError(false);
                }
            } catch (err) {
                console.error("Mermaid parsing error:", err);
                if (!cancelled) setRenderError(true);
            }
        });
        
        return () => { cancelled = true; };
    }, [code]);

    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">Generated Flowchart</h3>
            
            <div className="bg-[var(--bg-page)] rounded-[var(--radius-sm)] overflow-hidden">
                {svg ? (
                    <div className="p-4 w-full overflow-x-auto flex justify-center" dangerouslySetInnerHTML={{ __html: svg }} />
                ) : renderError ? (
                    <div className="p-4 text-center text-red-500 text-sm">Failed to render diagram visually. Raw code below.</div>
                ) : (
                    <div className="flex justify-center items-center h-32 text-[var(--text-muted)] gap-2">
                        <Loader2 className="w-5 h-5 animate-spin" /> Rendering Diagram...
                    </div>
                )}
            </div>

            <details className="mt-4 group">
                <summary className="text-xs font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] cursor-pointer select-none">
                    View Raw Syntax
                </summary>
                <div className="mt-2 border border-[var(--border-light)] rounded-[var(--radius-sm)]">
                    <pre className="text-xs p-3 bg-black text-green-400 overflow-x-auto whitespace-pre-wrap">{code}</pre>
                </div>
            </details>
        </div>
    );
}

function ConceptMapView({ data }: { data: ConceptMap }) {
    // Convert ConceptMap JSON to Mermaid Flowchart syntax
    const mermaidCode = useMemo(() => {
        if (!data || !data.nodes || !data.edges) return "";
        try {
            let code = "graph LR\n";
            // Map IDs to labels for valid Mermaid syntax (avoiding special character breaks)
            const escapeLabel = (l: string) => `"${l.replace(/"/g, "'")}"`;
            
            data.nodes.forEach(n => {
                const safeId = n.id.replace(/[^a-zA-Z0-9]/g, "_");
                code += `    ${safeId}[${escapeLabel(n.label)}]\n`;
            });
            
            data.edges.forEach(e => {
                const safeFrom = e.from.replace(/[^a-zA-Z0-9]/g, "_");
                const safeTo = e.to.replace(/[^a-zA-Z0-9]/g, "_");
                if (e.label) {
                    code += `    ${safeFrom} -->|${escapeLabel(e.label)}| ${safeTo}\n`;
                } else {
                    code += `    ${safeFrom} --> ${safeTo}\n`;
                }
            });
            return code;
        } catch {
            return "";
        }
    }, [data]);

    if (mermaidCode) {
        return <FlowchartView code={mermaidCode} />;
    }

    // Fallback to text lists if data structure is corrupted
    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">Concept Map</h3>
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Nodes</p>
                    <div className="space-y-1">
                        {data.nodes.map((node) => (
                            <div key={node.id} className="text-xs px-2 py-1 rounded bg-[var(--bg-page)] text-[var(--text-secondary)]">
                                {node.label}
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Relationships</p>
                    <div className="space-y-1">
                        {data.edges.map((edge, idx) => (
                            <div key={`${edge.from}-${edge.to}-${idx}`} className="text-xs px-2 py-1 rounded bg-[var(--bg-page)] text-[var(--text-secondary)]">
                                {edge.from} {"->"} {edge.to}{edge.label ? ` (${edge.label})` : ""}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
}
