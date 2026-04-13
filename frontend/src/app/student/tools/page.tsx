"use client";

import { useEffect, useMemo, useState, useCallback } from "react";
import {
    ArrowRight,
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
    FolderKanban,
    Pin,
    WandSparkles,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import { useNetworkAware } from "@/hooks/useNetworkAware";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";
import { cn } from "@/lib/utils";

type Tool = "quiz" | "flashcards" | "mindmap" | "flowchart" | "concept_map";
type AIJobStatus = "queued" | "running" | "completed" | "failed";

type QuizQ = { question: string; options: string[]; correct: string; citation?: string | null };
type Flashcard = { front: string; back: string; citation?: string | null };
type MindNode = { label: string; citation?: string | null; children?: MindNode[] };
type ConceptMap = { nodes: { id: string; label: string }[]; edges: { from: string; to: string; label: string }[] };
type FlowchartStep = { id: string; label: string; detail: string; citation: string };
type FlowchartData = { mermaid: string; steps: FlowchartStep[] };
type ToolData = QuizQ[] | Flashcard[] | MindNode | ConceptMap | FlowchartData | string | null;
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

/**
 * Type guard to safely check if an object matches ToolData structure
 */
function isToolData(value: unknown): value is ToolData {
    if (value === null || typeof value === "string") return true;
    if (!value || typeof value !== "object") return false;
    
    const obj = value as Record<string, unknown>;
    
    // Check for array types (QuizQ[] or Flashcard[])
    if (Array.isArray(obj)) return true;
    
    // Check for MindNode (has label, possibly children)
    if ("label" in obj && typeof obj.label === "string") return true;
    
    // Check for ConceptMap (has nodes and edges arrays)
    if ("nodes" in obj && Array.isArray(obj.nodes) && "edges" in obj && Array.isArray(obj.edges)) return true;
    
    // Check for FlowchartData (has mermaid string and steps array)
    if ("mermaid" in obj && typeof obj.mermaid === "string" && "steps" in obj && Array.isArray(obj.steps)) return true;
    
    return false;
}

const tools: { id: Tool; label: string; icon: typeof Brain; desc: string; color: string }[] = [
    { id: "quiz", label: "Quiz", icon: HelpCircle, desc: "MCQ quiz from your notes", color: "from-violet-500 to-pink-600" },
    { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Revision cards", color: "from-amber-500 to-orange-600" },
    { id: "mindmap", label: "Mind Map", icon: Brain, desc: "Topic hierarchy", color: "from-emerald-500 to-green-600" },
    { id: "flowchart", label: "Flowchart", icon: GitBranch, desc: "Step process flow", color: "from-sky-500 to-blue-600" },
    { id: "concept_map", label: "Concept Map", icon: Network, desc: "Linked concept graph", color: "from-rose-500 to-red-600" },
];

export default function StudyToolsPage() {
    const { isSlowConnection, saveData } = useNetworkAware();
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
    const pinnedCount = useMemo(() => libraryItems.filter((item) => item.is_pinned).length, [libraryItems]);
    const isDemoMode = process.env.NEXT_PUBLIC_DEMO_MODE === "true";
    const fallbackPollMs = saveData ? 6000 : isSlowConnection ? 4000 : 2000;
    
    // Inline history for selected tool
    const [toolHistory, setToolHistory] = useState<AIHistoryItem[]>([]);
    
    useEffect(() => {
        if (activeTool) {
            api.aiHistory.list({ mode: activeTool, page: 1 }).then((res) => {
                setToolHistory((res as { items: AIHistoryItem[] }).items?.slice(0, 3) || []);
            }).catch(() => {
                setToolHistory([]);
            });
        } else {
            setToolHistory([]);
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
                }, job.poll_after_ms ?? fallbackPollMs);
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
    }, [fallbackPollMs, jobId]);

    const generateResult = async () => {
        if (!activeTool || !topic.trim()) return;
        try {
            setLoading(true);
            setError(null);
            setResult(null);
            setCitations([]);

            if (isDemoMode) {
                // In demo mode, use synchronous endpoint to bypass Redis job queue
                const response = (await api.student.generateTool({
                    tool: activeTool,
                    topic: topic.trim(),
                })) as { data?: ToolData; citations?: Citation[] };
                
                // Type-safe data extraction: prefer data field, fall back to entire response if it matches ToolData
                if (response.data) {
                    setResult(response.data);
                } else if (isToolData(response)) {
                    setResult(response);
                }
                setCitations(response.citations || []);
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
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student tool studio
                        </PrismHeroKicker>
                    )}
                    title="Build revision assets from your learning material"
                    description="Generate quizzes, flashcards, mind maps, flowcharts, and concept maps in a workspace organized around creation, saved assets, and grounded outputs."
                    aside={(
                        <div className="prism-status-strip">
                        <MetricPanel
                            label="Active workspace"
                            value={selectedTool?.label || "Select a tool"}
                            detail={selectedTool ? selectedTool.desc : "Choose a format to shape the next study pass."}
                        />
                        <MetricPanel
                            label="Saved assets"
                            value={libraryItems.length > 0 ? `${libraryItems.length}` : "Library ready"}
                            detail={libraryItems.length > 0 ? `${pinnedCount} pinned study assets saved for reuse.` : "Generated tools collect in one reusable shelf."}
                        />
                        <MetricPanel
                            label="Recent momentum"
                            value={toolHistory.length > 0 ? `${toolHistory.length} recent` : "Fresh start"}
                            detail={toolHistory.length > 0 ? "Jump back into the latest prompts for this tool." : "Pick a tool and start building your first artifact."}
                        />
                        </div>
                    )}
                />

                {error ? <ErrorRemediation error={error} scope="student-tools" onRetry={() => void generateResult()} simplifiedModeHref="/student/upload" /> : null}

                <div className="grid gap-6 xl:grid-cols-[0.98fr_1.02fr]">
                    <PrismPanel className="space-y-5 p-5">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.24em] text-[var(--text-muted)]">Workspace mode</p>
                                <h2 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">Create or revisit study assets</h2>
                            </div>
                            <div className="inline-flex rounded-full border border-white/10 bg-black/10 p-1">
                                <TabButton active={activeTab === "create"} onClick={() => setActiveTab("create")} icon={WandSparkles}>
                                    Create
                                </TabButton>
                                <TabButton active={activeTab === "library"} onClick={() => setActiveTab("library")} icon={Library}>
                                    Library
                                </TabButton>
                            </div>
                        </div>

            {activeTab === "create" ? (
                <>
                    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-1 2xl:grid-cols-2">
                        {tools.map((tool) => (
                            <button
                                key={tool.id}
                                onClick={() => {
                                    if (loading) return;
                                    setActiveTool(tool.id);
                                    setResult(null);
                                    setCitations([]);
                                }}
                                className={cn(
                                    "group relative overflow-hidden rounded-[calc(var(--radius)*1.05)] border p-4 text-left transition-all duration-200",
                                    activeTool === tool.id
                                        ? `border-white/15 bg-gradient-to-br ${tool.color} text-white shadow-[0_22px_60px_rgba(15,23,42,0.34)]`
                                        : "border-white/8 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.03))] hover:-translate-y-0.5 hover:border-white/15 hover:bg-[linear-gradient(180deg,rgba(255,255,255,0.08),rgba(255,255,255,0.04))]",
                                    loading ? "cursor-not-allowed opacity-60" : ""
                                )}
                            >
                                <div className="flex items-start justify-between gap-3">
                                    <div className={cn("rounded-2xl border p-2.5", activeTool === tool.id ? "border-white/20 bg-white/10" : "border-white/10 bg-white/5")}>
                                        <tool.icon className={cn("h-5 w-5", activeTool === tool.id ? "text-white" : "text-[var(--primary)]")} />
                                    </div>
                                    <ArrowRight className={cn("h-4 w-4 transition-transform group-hover:translate-x-0.5", activeTool === tool.id ? "text-white/70" : "text-[var(--text-muted)]")} />
                                </div>
                                <p className="mt-4 text-sm font-semibold">{tool.label}</p>
                                <p className={cn("mt-1 text-xs leading-6", activeTool === tool.id ? "text-white/80" : "text-[var(--text-secondary)]")}>{tool.desc}</p>
                            </button>
                        ))}
                    </div>

                    {toolHistory.length > 0 ? (
                        <div className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-black/10 p-4">
                            <div className="mb-3 flex items-center gap-2 text-xs font-medium text-[var(--text-secondary)]">
                                <Clock className="h-3.5 w-3.5" />
                                Recent {selectedTool?.label || "tool"} prompts
                            </div>
                            <div className="space-y-2">
                                {toolHistory.map((item) => (
                                    <button
                                        key={item.id}
                                        onClick={() => setTopic(item.query_text)}
                                        className="flex w-full items-center gap-3 rounded-2xl border border-white/8 bg-white/[0.03] px-3 py-2.5 text-left transition hover:border-white/12 hover:bg-white/[0.05]"
                                    >
                                        {item.is_pinned ? <Pin className="h-3.5 w-3.5 text-[var(--primary)]" /> : <Clock className="h-3.5 w-3.5 text-[var(--text-muted)]" />}
                                        <div className="min-w-0 flex-1">
                                            <p className="truncate text-sm font-medium text-[var(--text-primary)]">{item.title || item.query_text}</p>
                                            <p className="text-[11px] text-[var(--text-muted)]">{new Date(item.created_at).toLocaleDateString()}</p>
                                        </div>
                                    </button>
                                ))}
                            </div>
                        </div>
                    ) : null}

                    <div className="rounded-[calc(var(--radius)*1.05)] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.06),rgba(255,255,255,0.02))] p-4">
                        <div className="mb-4 space-y-1">
                            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Prompt builder</p>
                            <h3 className="text-base font-semibold text-[var(--text-primary)]">
                                {selectedTool ? `Generate a ${selectedTool.label.toLowerCase()} from your topic` : "Choose a tool, then describe the topic"}
                            </h3>
                            <p className="text-sm text-[var(--text-secondary)]">
                                Keep the topic specific enough to anchor the output to one chapter, unit, or problem area.
                            </p>
                        </div>

                        <div className="space-y-3">
                            <textarea
                                value={topic}
                                onChange={(event) => setTopic(event.target.value)}
                                placeholder={selectedTool ? `Example: ${toolPlaceholder(selectedTool.id)}` : "Pick a tool first, then enter a focused study topic."}
                                className="min-h-[120px] w-full rounded-[calc(var(--radius)*0.9)] border border-white/10 bg-black/15 px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition placeholder:text-[var(--text-muted)] focus:border-[var(--primary)] focus:ring-2 focus:ring-[var(--primary)]/20"
                            />
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div className="flex flex-wrap gap-2 text-[11px] text-[var(--text-muted)]">
                                    <PromptChip label="High-yield revision" onClick={() => setTopic("High-yield revision points from this chapter")} />
                                    <PromptChip label="Exam prep" onClick={() => setTopic("Exam-focused questions and concepts for this unit")} />
                                    <PromptChip label="Concept links" onClick={() => setTopic("Connections between the main concepts in this topic")} />
                                </div>
                                <button
                                    onClick={() => void generateResult()}
                                    disabled={loading || !activeTool || !topic.trim()}
                                    className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-2.5 text-sm font-semibold text-[#07111f] shadow-[0_18px_34px_rgba(96,165,250,0.24)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-50"
                                >
                                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Sparkles className="h-4 w-4" />}
                                    Generate
                                </button>
                            </div>
                        </div>
                    </div>
                </>
            ) : (
                <div className="space-y-4">
                    <div className="rounded-[calc(var(--radius)*1.05)] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.02))] p-4">
                        <div className="flex items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Saved study assets</p>
                                <h3 className="mt-1 text-base font-semibold text-[var(--text-primary)]">Your generated library</h3>
                            </div>
                            <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-[var(--text-secondary)]">
                                {libraryItems.length} items
                            </div>
                        </div>
                    </div>

                    {libraryLoading ? (
                        <PrismPanel className="flex items-center justify-center p-12">
                            <div className="flex items-center gap-3 text-sm text-[var(--text-secondary)]">
                                <Loader2 className="h-5 w-5 animate-spin text-[var(--primary)]" />
                                Loading your study library...
                            </div>
                        </PrismPanel>
                    ) : libraryItems.length === 0 ? (
                        <EmptyState
                            icon={Library}
                            title="No saved study tools yet"
                            description="Generate your first quiz, flashcards, or map to build a reusable revision shelf."
                            action={{ label: "Switch to create", href: "#student-tools-create" }}
                        />
                    ) : (
                        <div className="grid gap-3">
                            {libraryItems.map((item) => (
                                <button
                                    key={item.id}
                                    onClick={() => {
                                        setActiveTab("create");
                                        setActiveTool(item.mode as Tool);
                                        setTopic(item.query_text);
                                    }}
                                    className="group rounded-[calc(var(--radius)*1.02)] border border-white/10 bg-[linear-gradient(180deg,rgba(255,255,255,0.05),rgba(255,255,255,0.03))] p-4 text-left transition hover:-translate-y-0.5 hover:border-white/15"
                                >
                                    <div className="flex items-start justify-between gap-3">
                                        <div className="flex items-center gap-3">
                                            <div className="rounded-2xl border border-white/10 bg-white/5 p-2.5">
                                                <LibraryIcon mode={item.mode} />
                                            </div>
                                            <div>
                                                <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title || item.query_text}</p>
                                                <p className="text-xs text-[var(--text-secondary)]">{formatToolMode(item.mode)} study asset</p>
                                            </div>
                                        </div>
                                        {item.is_pinned ? <Pin className="h-4 w-4 text-[var(--primary)]" /> : null}
                                    </div>
                                    <div className="mt-3 flex items-center justify-between gap-3 text-[11px] text-[var(--text-muted)]">
                                        <span>{new Date(item.created_at).toLocaleDateString()}</span>
                                        <span className="inline-flex items-center gap-1 text-[var(--text-secondary)] group-hover:text-[var(--text-primary)]">
                                            Open in create mode
                                            <ArrowRight className="h-3.5 w-3.5" />
                                        </span>
                                    </div>
                                </button>
                            ))}
                        </div>
                    )}
                </div>
            )}
                    </PrismPanel>

                    <div className="space-y-6" id="student-tools-create">
                        <PrismPanel className="overflow-hidden p-0">
                            <div className="border-b border-white/8 px-5 py-4">
                                <div className="flex flex-wrap items-start justify-between gap-3">
                                    <div>
                                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Output studio</p>
                                        <h2 className="mt-1 text-lg font-semibold text-[var(--text-primary)]">
                                            {selectedTool ? `${selectedTool.label} workspace` : "Study output preview"}
                                        </h2>
                                        <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                            {loading
                                                ? jobStatus === "queued"
                                                    ? "Your request is queued and will appear here as soon as the job starts."
                                                    : "The generated study artifact will stream into this panel when it is ready."
                                                : selectedTool
                                                  ? "Generated outputs stay grounded to your prompt and can be reused from the library."
                                                  : "Pick a tool on the left to start a focused revision workflow."}
                                        </p>
                                    </div>
                                    <div className="rounded-full border border-white/10 bg-white/5 px-3 py-1 text-xs text-[var(--text-secondary)]">
                                        {selectedTool ? selectedTool.label : "No tool selected"}
                                    </div>
                                </div>
                            </div>
                            <div className="p-5">
                                {loading ? (
                                    <div className="flex min-h-[360px] flex-col items-center justify-center gap-3 rounded-[calc(var(--radius)*0.95)] border border-dashed border-white/10 bg-black/10 px-6 py-10 text-center">
                                        <Loader2 className="h-8 w-8 animate-spin text-[var(--primary)]" />
                                        <div>
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">
                                                {jobStatus === "queued" ? `Queued ${selectedTool?.label || "study tool"}` : `Generating ${selectedTool?.label || "study tool"}`}
                                            </p>
                                            <p className="mt-1 text-sm text-[var(--text-secondary)]">We&apos;re shaping the output around your topic and available study material.</p>
                                        </div>
                                    </div>
                                ) : !selectedTool ? (
                                    <EmptyState
                                        icon={WandSparkles}
                                        title="Choose a study format"
                                        description="Select quiz, flashcards, mind map, flowchart, or concept map to open the creation workspace."
                                        action={{ label: "Go to uploads", href: "/student/upload" }}
                                    />
                                ) : !result ? (
                                    <ToolPreview selectedTool={selectedTool} topic={topic} recentCount={toolHistory.length} />
                                ) : (
                                    <div className="space-y-4">
                                        {activeTool === "quiz" ? <QuizView questions={result as QuizQ[]} /> : null}
                                        {activeTool === "flashcards" ? <FlashcardsView cards={result as Flashcard[]} /> : null}
                                        {activeTool === "mindmap" ? <MindMapView data={result as MindNode} /> : null}
                                        {activeTool === "flowchart" ? <FlowchartView data={result as FlowchartData | string} /> : null}
                                        {activeTool === "concept_map" ? <ConceptMapView data={result as ConceptMap} /> : null}
                                        {citations.length > 0 ? <SourceStrip citations={citations} /> : null}
                                    </div>
                                )}
                            </div>
                        </PrismPanel>
                        <div className="grid gap-4 md:grid-cols-2">
                            <PrismPanel className="p-4">
                                <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
                                    <FolderKanban className="h-3.5 w-3.5" />
                                    Flow
                                </div>
                                <h3 className="text-sm font-semibold text-[var(--text-primary)]">Create, save, return</h3>
                                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                    This route now separates creation from the library so repeated revision feels organized rather than disposable.
                                </p>
                            </PrismPanel>
                            <PrismPanel className="p-4">
                                <div className="mb-2 flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
                                    <Brain className="h-3.5 w-3.5" />
                                    Guidance
                                </div>
                                <h3 className="text-sm font-semibold text-[var(--text-primary)]">Better prompts, better outputs</h3>
                                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                    Use a chapter, lesson, or concept cluster instead of a broad subject name to keep generated material sharper and easier to trust.
                                </p>
                            </PrismPanel>
                        </div>
                    </div>
                </div>
            </PrismSection>
        </PrismPage>
    );
}

function TabButton({
    active,
    onClick,
    icon: Icon,
    children,
}: {
    active: boolean;
    onClick: () => void;
    icon: typeof Library;
    children: React.ReactNode;
}) {
    return (
        <button
            onClick={onClick}
            className={cn(
                "inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-medium transition",
                active ? "bg-white/12 text-[var(--text-primary)] shadow-[inset_0_1px_0_rgba(255,255,255,0.08)]" : "text-[var(--text-secondary)] hover:text-[var(--text-primary)]"
            )}
        >
            <Icon className="h-4 w-4" />
            {children}
        </button>
    );
}

function MetricPanel({ label, value, detail }: { label: string; value: string; detail: string }) {
    return (
        <PrismPanel className="p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-lg font-semibold text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p>
        </PrismPanel>
    );
}

function PromptChip({ label, onClick }: { label: string; onClick: () => void }) {
    return (
        <button onClick={onClick} className="rounded-full border border-white/10 bg-white/5 px-3 py-1.5 transition hover:border-white/15 hover:bg-white/8">
            {label}
        </button>
    );
}

function ToolPreview({
    selectedTool,
    topic,
    recentCount,
}: {
    selectedTool: (typeof tools)[number];
    topic: string;
    recentCount: number;
}) {
    return (
        <div className={cn("rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-gradient-to-br p-5", selectedTool.color)}>
            <div className="flex items-start justify-between gap-4">
                <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/65">Ready to generate</p>
                    <h3 className="mt-2 text-xl font-semibold text-white">{selectedTool.label}</h3>
                    <p className="mt-2 max-w-xl text-sm leading-7 text-white/80">{selectedTool.desc}</p>
                </div>
                <div className="rounded-2xl border border-white/15 bg-white/10 p-3">
                    <selectedTool.icon className="h-5 w-5 text-white" />
                </div>
            </div>

            <div className="mt-6 grid gap-3 md:grid-cols-3">
                <PreviewStat label="Prompt state" value={topic.trim() ? "Ready" : "Waiting"} />
                <PreviewStat label="Recent prompts" value={recentCount > 0 ? `${recentCount}` : "0"} />
                <PreviewStat label="Output style" value={selectedTool.label} />
            </div>

            <div className="mt-6 rounded-[calc(var(--radius)*0.9)] border border-white/15 bg-black/15 p-4">
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-white/65">Next step</p>
                <p className="mt-2 text-sm leading-6 text-white/80">
                    {topic.trim()
                        ? `Generate now to turn "${topic}" into a structured ${selectedTool.label.toLowerCase()} study asset.`
                        : `Add a focused topic on the left and generate a ${selectedTool.label.toLowerCase()} you can revisit later from the library.`}
                </p>
            </div>
        </div>
    );
}

function PreviewStat({ label, value }: { label: string; value: string }) {
    return (
        <div className="rounded-2xl border border-white/15 bg-black/15 p-3">
            <p className="text-[11px] uppercase tracking-[0.18em] text-white/60">{label}</p>
            <p className="mt-2 text-sm font-semibold text-white">{value}</p>
        </div>
    );
}

function SourceStrip({ citations }: { citations: Citation[] }) {
    return (
        <div className="rounded-[calc(var(--radius)*0.95)] border border-white/10 bg-black/10 p-4">
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Sources</p>
            <div className="mt-3 flex flex-wrap gap-2">
                {citations.map((citation, idx) => {
                    const label = citation.text || `${citation.source || "Document"}${citation.page ? ` p.${citation.page}` : ""}`;
                    const key = `${citation.source || "src"}-${citation.page || "page"}-${idx}`;
                    const classes = "rounded-full border border-white/10 bg-white/5 px-3 py-1.5 text-[11px] text-[var(--text-secondary)] transition hover:text-[var(--text-primary)]";
                    if (citation.url) {
                        return <a key={key} href={citation.url} target="_blank" rel="noopener noreferrer" className={classes}>{label}</a>;
                    }
                    return <span key={key} className={classes}>{label}</span>;
                })}
            </div>
        </div>
    );
}

function LibraryIcon({ mode }: { mode: string }) {
    if (mode === "quiz") return <HelpCircle className="h-5 w-5 text-violet-400" />;
    if (mode === "flashcards") return <Layers className="h-5 w-5 text-amber-400" />;
    if (mode === "mindmap") return <Brain className="h-5 w-5 text-emerald-400" />;
    if (mode === "flowchart") return <GitBranch className="h-5 w-5 text-sky-400" />;
    return <Network className="h-5 w-5 text-rose-400" />;
}

function formatToolMode(mode: string) {
    return mode.replace("_", " ");
}

function toolPlaceholder(tool: Tool) {
    if (tool === "quiz") return "Thermodynamics laws and heat engine questions";
    if (tool === "flashcards") return "French Revolution dates, causes, and outcomes";
    if (tool === "mindmap") return "Cell biology structure and major functions";
    if (tool === "flowchart") return "Steps in solving quadratic equations";
    return "How photosynthesis concepts relate to each other";
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
            <div className="inline-flex flex-col gap-1">
                <div className={`inline-block px-3 py-1.5 rounded-full text-xs font-medium ${colors[depth % colors.length]}`}>
                    {node.label}
                </div>
                {node.citation ? (
                    <p className="ml-1 text-[10px] text-[var(--text-muted)]">Citation: {node.citation}</p>
                ) : null}
            </div>
            {(node.children || []).map((child, idx) => (
                <MindNodeView key={`${depth}-${idx}-${child.label}`} node={child} depth={depth + 1} />
            ))}
        </div>
    );
}

function FlowchartView({ data }: { data: FlowchartData | string }) {
    const code = typeof data === "string" ? data : data?.mermaid || "";
    const steps = typeof data === "string" ? [] : data?.steps || [];
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

            {steps.length > 0 ? (
                <div className="mt-4 space-y-2">
                    <p className="text-xs font-semibold text-[var(--text-secondary)]">Grounded Steps</p>
                    {steps.map((step, idx) => (
                        <div key={`${step.id}-${idx}`} className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-3">
                            <p className="text-sm font-medium text-[var(--text-primary)]">{idx + 1}. {step.label}</p>
                            <p className="mt-1 text-xs text-[var(--text-secondary)]">{step.detail}</p>
                            <p className="mt-2 text-[10px] text-[var(--text-muted)]">Citation: {step.citation}</p>
                        </div>
                    ))}
                </div>
            ) : null}

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
        return <FlowchartView data={mermaidCode} />;
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
