"use client";

import { useMemo, useState } from "react";
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
} from "lucide-react";

import { api } from "@/lib/api";

type Tool = "quiz" | "flashcards" | "mindmap" | "flowchart" | "concept_map";

type QuizQ = { question: string; options: string[]; correct: string; citation?: string | null };
type Flashcard = { front: string; back: string };
type MindNode = { label: string; children?: MindNode[] };
type ConceptMap = { nodes: { id: string; label: string }[]; edges: { from: string; to: string; label: string }[] };
type ToolData = QuizQ[] | Flashcard[] | MindNode | ConceptMap | string | null;

const tools: { id: Tool; label: string; icon: typeof Brain; desc: string; color: string }[] = [
    { id: "quiz", label: "Quiz", icon: HelpCircle, desc: "MCQ quiz from your notes", color: "from-violet-500 to-pink-600" },
    { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Revision cards", color: "from-amber-500 to-orange-600" },
    { id: "mindmap", label: "Mind Map", icon: Brain, desc: "Topic hierarchy", color: "from-emerald-500 to-green-600" },
    { id: "flowchart", label: "Flowchart", icon: GitBranch, desc: "Step process flow", color: "from-sky-500 to-blue-600" },
    { id: "concept_map", label: "Concept Map", icon: Network, desc: "Linked concept graph", color: "from-rose-500 to-red-600" },
];

export default function StudyToolsPage() {
    const [activeTool, setActiveTool] = useState<Tool | null>(null);
    const [topic, setTopic] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [result, setResult] = useState<ToolData>(null);
    const [citations, setCitations] = useState<Array<{ source?: string; page?: string }>>([]);

    const selectedTool = useMemo(() => tools.find((tool) => tool.id === activeTool) || null, [activeTool]);

    const generateResult = async () => {
        if (!activeTool || !topic.trim()) return;
        try {
            setLoading(true);
            setError(null);
            setResult(null);
            const payload = (await api.student.generateTool({
                tool: activeTool,
                topic: topic.trim(),
            })) as {
                data: ToolData;
                citations?: Array<{ source?: string; page?: string }>;
            };
            setResult(payload.data || null);
            setCitations(payload.citations || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate study tool");
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Study Tools</h1>
                <p className="text-sm text-[var(--text-secondary)]">Generate quizzes, flashcards, mind maps, flowcharts, and concept maps from your uploaded materials.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            <div className="grid grid-cols-2 md:grid-cols-5 gap-3 mb-6">
                {tools.map((tool) => (
                    <button
                        key={tool.id}
                        onClick={() => {
                            setActiveTool(tool.id);
                            setResult(null);
                            setCitations([]);
                        }}
                        className={`p-4 rounded-[var(--radius)] text-center transition-all ${
                            activeTool === tool.id
                                ? `bg-gradient-to-br ${tool.color} text-white shadow-lg scale-[1.02]`
                                : "bg-white shadow-[var(--shadow-card)] hover:shadow-md text-[var(--text-primary)]"
                        }`}
                    >
                        <tool.icon className={`w-6 h-6 mx-auto mb-2 ${activeTool === tool.id ? "text-white" : "text-[var(--primary)]"}`} />
                        <p className="text-xs font-semibold">{tool.label}</p>
                        <p className={`text-[10px] mt-0.5 ${activeTool === tool.id ? "text-white/80" : "text-[var(--text-muted)]"}`}>{tool.desc}</p>
                    </button>
                ))}
            </div>

            {activeTool ? (
                <>
                    <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4 mb-6">
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
                        <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-12 text-center">
                            <Loader2 className="w-8 h-8 mx-auto text-[var(--primary)] animate-spin mb-3" />
                            <p className="text-sm text-[var(--text-secondary)]">Generating {selectedTool?.label}...</p>
                        </div>
                    ) : null}

                    {!loading && result && activeTool === "quiz" ? <QuizView questions={result as QuizQ[]} /> : null}
                    {!loading && result && activeTool === "flashcards" ? <FlashcardsView cards={result as Flashcard[]} /> : null}
                    {!loading && result && activeTool === "mindmap" ? <MindMapView data={result as MindNode} /> : null}
                    {!loading && result && activeTool === "flowchart" ? <FlowchartView code={result as string} /> : null}
                    {!loading && result && activeTool === "concept_map" ? <ConceptMapView data={result as ConceptMap} /> : null}

                    {!loading && citations.length > 0 ? (
                        <div className="mt-4 bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-4">
                            <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Sources</p>
                            <div className="flex flex-wrap gap-2">
                                {citations.map((citation, idx) => (
                                    <span key={`${citation.source || "src"}-${citation.page || "page"}-${idx}`} className="text-[10px] px-2 py-1 rounded-full bg-[var(--bg-page)] text-[var(--text-secondary)]">
                                        {citation.source || "Document"} p.{citation.page || "?"}
                                    </span>
                                ))}
                            </div>
                        </div>
                    ) : null}
                </>
            ) : null}
        </div>
    );
}

function QuizView({ questions }: { questions: QuizQ[] }) {
    return (
        <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
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
        <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
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
                className="w-full text-left p-5 rounded-[var(--radius-sm)] bg-[var(--primary-light)] hover:bg-blue-100 transition-colors"
            >
                <p className="text-[10px] uppercase tracking-wider text-[var(--text-muted)] mb-2">{flipped ? "Answer" : "Prompt"}</p>
                <p className="text-sm text-[var(--text-primary)]">{flipped ? card.back : card.front}</p>
            </button>
        </div>
    );
}

function MindMapView({ data }: { data: MindNode }) {
    return (
        <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6 overflow-x-auto">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">Mind Map</h3>
            <MindNodeView node={data} depth={0} />
        </div>
    );
}

function MindNodeView({ node, depth }: { node: MindNode; depth: number }) {
    const colors = [
        "bg-[var(--primary)] text-white",
        "bg-blue-100 text-blue-800",
        "bg-green-100 text-green-800",
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
    return (
        <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">Generated Mermaid Flowchart</h3>
            <pre className="text-xs p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)] overflow-x-auto whitespace-pre-wrap">{code}</pre>
        </div>
    );
}

function ConceptMapView({ data }: { data: ConceptMap }) {
    return (
        <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-6">
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-3">Concept Map</h3>
            <div className="grid md:grid-cols-2 gap-4">
                <div>
                    <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Nodes</p>
                    <div className="space-y-1">
                        {data.nodes.map((node) => (
                            <div key={node.id} className="text-xs px-2 py-1 rounded bg-[var(--bg-page)] text-[var(--text-secondary)]">
                                {node.id}: {node.label}
                            </div>
                        ))}
                    </div>
                </div>
                <div>
                    <p className="text-xs font-semibold text-[var(--text-secondary)] mb-2">Edges</p>
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
