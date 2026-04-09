"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { Loader2, Maximize2, Network, Sparkles, ZoomIn, ZoomOut } from "lucide-react";

import { api } from "@/lib/api";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";

type MindNode = { label: string; children?: MindNode[] };
type NodePos = { x: number; y: number; label: string; depth: number; parent?: { x: number; y: number } };
type MindMapHistoryItem = {
    id: string;
    title: string;
    created_at: string | null;
    content: MindNode;
};

function flattenTree(
    node: MindNode,
    x: number,
    y: number,
    depth: number,
    positions: NodePos[],
    parent?: { x: number; y: number }
) {
    positions.push({ x, y, label: node.label, depth, parent });
    if (node.children) {
        const total = node.children.length;
        const spacing = Math.max(80, 200 / (depth + 1));
        const startY = y - ((total - 1) * spacing) / 2;
        node.children.forEach((child, i) => {
            flattenTree(child, x + 250, startY + i * spacing, depth + 1, positions, { x, y });
        });
    }
}

const COLORS = ["#6366f1", "#8b5cf6", "#ec4899", "#f43f5e", "#f97316", "#eab308", "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6"];
const EXAMPLES = ["Cell Biology", "Newton's Laws", "The Water Cycle", "Photosynthesis", "World War II"];

export default function InteractiveMindMapPage() {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const [topic, setTopic] = useState("");
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [data, setData] = useState<MindNode | null>(null);
    const [zoom, setZoom] = useState(1);
    const [pan, setPan] = useState({ x: 60, y: 0 });
    const [dragging, setDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [history, setHistory] = useState<MindMapHistoryItem[]>([]);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const payload = await api.student.studyToolHistory("mindmap", 6) as { items?: MindMapHistoryItem[] };
                const items = payload.items || [];
                setHistory(items);
                if (items.length > 0) {
                    setData(items[0].content);
                    setTopic(items[0].title);
                }
            } catch {
                // History is optional outside demo mode.
            }
        };

        void loadHistory();
    }, []);

    const generate = async () => {
        if (!topic.trim() || loading) return;
        setLoading(true);
        setError(null);
        setData(null);
        try {
            const result = await api.student.generateTool({ tool: "mindmap", topic: topic.trim() });
            const rawResult = result as unknown as Record<string, unknown> | null;
            const tree = rawResult?.data || rawResult?.content || rawResult?.mindmap || rawResult;

            if (tree && typeof tree === "object" && "label" in tree) {
                setData(tree as MindNode);
            } else {
                setError(`Could not parse mind map data. Keys: ${rawResult ? Object.keys(rawResult).join(",") : "null"}`);
            }
        } catch (err: unknown) {
            const message = err instanceof Error ? err.message : String(err);
            setError(`Error: ${message}`);
        } finally {
            setLoading(false);
        }
    };

    const draw = useCallback(() => {
        try {
            const canvas = canvasRef.current;
            if (!canvas || !data) return;
            const ctx = canvas.getContext("2d");
            if (!ctx) return;

            const dpr = window.devicePixelRatio || 1;
            const width = canvas.offsetWidth;
            const height = canvas.offsetHeight;
            if (!width || !height || width < 1 || height < 1) return;

            canvas.width = width * dpr;
            canvas.height = height * dpr;
            ctx.scale(dpr, dpr);

            ctx.clearRect(0, 0, width, height);
            ctx.save();
            ctx.translate(pan.x, pan.y + height / (2 * dpr));
            ctx.scale(zoom, zoom);

            const positions: NodePos[] = [];
            flattenTree(data, 0, 0, 0, positions);

            positions.forEach((pos) => {
                if (pos.parent) {
                    ctx.beginPath();
                    ctx.moveTo(pos.parent.x + 60, pos.parent.y);
                    const cpx = pos.parent.x + 155;
                    ctx.bezierCurveTo(cpx, pos.parent.y, cpx, pos.y, pos.x - 10, pos.y);
                    ctx.strokeStyle = `${COLORS[pos.depth % COLORS.length]}40`;
                    ctx.lineWidth = 2;
                    ctx.stroke();
                }
            });

            positions.forEach((pos) => {
                const color = COLORS[pos.depth % COLORS.length];
                const width = Math.min(Math.max(ctx.measureText(pos.label).width + 30, 80), 200);
                const height = 36;
                const radius = 12;

                ctx.shadowColor = `${color}30`;
                ctx.shadowBlur = 8;
                ctx.shadowOffsetY = 3;

                ctx.beginPath();
                if (ctx.roundRect) {
                    ctx.roundRect(pos.x - 10, pos.y - height / 2, width, height, radius);
                } else {
                    const x = pos.x - 10;
                    const y = pos.y - height / 2;
                    ctx.moveTo(x + radius, y);
                    ctx.lineTo(x + width - radius, y);
                    ctx.quadraticCurveTo(x + width, y, x + width, y + radius);
                    ctx.lineTo(x + width, y + height - radius);
                    ctx.quadraticCurveTo(x + width, y + height, x + width - radius, y + height);
                    ctx.lineTo(x + radius, y + height);
                    ctx.quadraticCurveTo(x, y + height, x, y + height - radius);
                    ctx.lineTo(x, y + radius);
                    ctx.quadraticCurveTo(x, y, x + radius, y);
                    ctx.closePath();
                }

                ctx.fillStyle = pos.depth === 0 ? color : "#ffffff";
                ctx.fill();
                ctx.shadowColor = "transparent";
                ctx.strokeStyle = color;
                ctx.lineWidth = pos.depth === 0 ? 0 : 2;
                if (pos.depth > 0) ctx.stroke();

                ctx.fillStyle = pos.depth === 0 ? "#ffffff" : color;
                ctx.font = `${pos.depth === 0 ? "bold " : ""}13px "Segoe UI", Tahoma, Verdana, sans-serif`;
                ctx.textAlign = "left";
                ctx.textBaseline = "middle";
                const maxTextWidth = width - 20;
                let text = pos.label;
                if (ctx.measureText(text).width > maxTextWidth) {
                    while (ctx.measureText(`${text}...`).width > maxTextWidth && text.length > 0) {
                        text = text.slice(0, -1);
                    }
                    text += "...";
                }
                ctx.fillText(text, pos.x, pos.y);
            });

            ctx.restore();
        } catch (err) {
            console.warn("[MindMap] Canvas draw error:", err);
        }
    }, [data, zoom, pan]);

    useEffect(() => {
        draw();
    }, [draw]);

    useEffect(() => {
        const handleResize = () => draw();
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, [draw]);

    const handleMouseDown = (e: React.MouseEvent) => {
        setDragging(true);
        setDragStart({ x: e.clientX - pan.x, y: e.clientY - pan.y });
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (!dragging) return;
        setPan({ x: e.clientX - dragStart.x, y: e.clientY - dragStart.y });
    };

    const handleMouseUp = () => setDragging(false);

    return (
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Spatial Learning Tool
                        </PrismHeroKicker>
                    )}
                    title="Turn a topic into a visual concept structure"
                    description="Use the mind-map workspace to see branches, dependencies, and supporting ideas before you switch into quizzes, notes, or deeper AI study."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with one chapter or process. Narrower topics produce cleaner branches and more useful revision planning.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Mode</span>
                        <span className="prism-status-value">Hierarchical map</span>
                        <span className="prism-status-detail">Best for topic structure, branches, and conceptual dependencies.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Interaction</span>
                        <span className="prism-status-value">Pan and zoom</span>
                        <span className="prism-status-detail">Move across the canvas, inspect branches, then reset when the structure expands.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Use case</span>
                        <span className="prism-status-value">Revision planning</span>
                        <span className="prism-status-detail">See where a concept sits before moving into details, recall practice, or exam prep.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Saved maps</span>
                        <span className="prism-status-value">{history.length}</span>
                        <span className="prism-status-detail">Seeded mind maps already available in the student demo workspace.</span>
                    </div>
                </div>

                {!data ? (
                    <PrismPanel className="p-5">
                        <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
                            <div className="space-y-3">
                                <p className="text-sm font-semibold text-[var(--text-primary)]">Generate a new map</p>
                                <p className="text-sm leading-6 text-[var(--text-secondary)]">
                                    Start with a chapter, a concept family, or a process. The map will lay out the main branches and supporting ideas in a form you can scan faster than plain notes.
                                </p>
                                <input
                                    value={topic}
                                    onChange={(e) => setTopic(e.target.value)}
                                    onKeyDown={(e) => {
                                        if (e.key === "Enter") void generate();
                                    }}
                                    placeholder="Enter a topic, for example Cell Biology or Newton's Laws"
                                    className="w-full rounded-[1.35rem] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                />
                                <button
                                    onClick={() => void generate()}
                                    disabled={loading || !topic.trim()}
                                    className="inline-flex items-center gap-2 rounded-[1.35rem] bg-[linear-gradient(135deg,rgba(45,212,191,0.96),rgba(20,184,166,0.9))] px-5 py-3 text-sm font-bold text-[#041315] transition hover:shadow-[0_18px_32px_rgba(20,184,166,0.22)] disabled:opacity-40"
                                >
                                    {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Network className="h-4 w-4" />}
                                    Generate mind map
                                </button>
                            </div>

                            <div className="prism-support-panel rounded-[1.5rem] p-4">
                                <p className="mb-3 text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Good prompts</p>
                                <div className="flex flex-wrap gap-2">
                                    {EXAMPLES.map((example) => (
                                        <button
                                            key={example}
                                            onClick={() => setTopic(example)}
                                            className="rounded-full border border-[var(--border)] bg-[rgba(255,255,255,0.04)] px-3 py-1.5 text-xs text-[var(--text-secondary)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                                        >
                                            {example}
                                        </button>
                                    ))}
                                </div>
                            </div>
                        </div>
                    </PrismPanel>
                ) : null}

                {error ? <ErrorRemediation error={error} scope="student-mind-map" onRetry={() => void generate()} /> : null}

                {loading ? (
                    <PrismPanel className="p-12 text-center">
                        <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(45,212,191,0.96),rgba(20,184,166,0.9))] animate-pulse">
                            <Network className="h-7 w-7 text-[#041315]" />
                        </div>
                        <p className="text-sm font-medium text-[var(--text-primary)]">Generating mind map...</p>
                    </PrismPanel>
                ) : null}

                {!loading && data ? (
                    <div className="space-y-5">
                        <PrismPanel className="overflow-hidden p-0">
                            <div className="flex flex-wrap items-center gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.08)] px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
                                    <Network className="h-3.5 w-3.5" />
                                    Canvas mode
                                </div>
                                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.04)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                    Topic: {topic}
                                </div>
                                <div className="ml-auto flex gap-2">
                                    <button
                                        onClick={() => setZoom((z) => Math.min(z + 0.15, 2.5))}
                                        className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-2 text-[var(--text-secondary)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                                    >
                                        <ZoomIn className="h-4 w-4" />
                                    </button>
                                    <button
                                        onClick={() => setZoom((z) => Math.max(z - 0.15, 0.3))}
                                        className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-2 text-[var(--text-secondary)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                                    >
                                        <ZoomOut className="h-4 w-4" />
                                    </button>
                                    <button
                                        onClick={() => {
                                            setZoom(1);
                                            setPan({ x: 60, y: 0 });
                                        }}
                                        className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-2 text-[var(--text-secondary)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                                    >
                                        <Maximize2 className="h-4 w-4" />
                                    </button>
                                    <button
                                        onClick={() => {
                                            setData(null);
                                            setTopic("");
                                        }}
                                        className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-2 text-[11px] font-semibold uppercase tracking-[0.18em] text-[var(--text-secondary)] transition hover:border-[var(--border-strong)] hover:text-[var(--text-primary)]"
                                    >
                                        New
                                    </button>
                                </div>
                            </div>

                            <div className="bg-[linear-gradient(180deg,rgba(8,15,30,0.88),rgba(5,10,20,0.92))]">
                                <canvas
                                    ref={canvasRef}
                                    className="w-full cursor-grab active:cursor-grabbing"
                                    style={{ height: "550px" }}
                                    onMouseDown={handleMouseDown}
                                    onMouseMove={handleMouseMove}
                                    onMouseUp={handleMouseUp}
                                    onMouseLeave={handleMouseUp}
                                />
                            </div>
                        </PrismPanel>
                        {history.length > 1 ? (
                            <PrismPanel className="p-5">
                                <div className="mb-4">
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Recent saved maps</p>
                                    <p className="mt-1 text-xs text-[var(--text-secondary)]">Load one of the seeded concept structures to show how this tool has been used over the last six months.</p>
                                </div>
                                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                                    {history.map((item) => (
                                        <button
                                            key={item.id}
                                            type="button"
                                            onClick={() => {
                                                setData(item.content);
                                                setTopic(item.title);
                                                setZoom(1);
                                                setPan({ x: 60, y: 0 });
                                            }}
                                            className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4 text-left transition hover:border-[var(--primary)] hover:bg-[rgba(96,165,250,0.08)]"
                                        >
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "Saved map"}</p>
                                        </button>
                                    ))}
                                </div>
                            </PrismPanel>
                        ) : null}
                    </div>
                ) : null}
            </PrismSection>
        </PrismPage>
    );
}
