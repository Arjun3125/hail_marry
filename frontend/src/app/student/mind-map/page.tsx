"use client";

import { useRef, useState, useEffect, useCallback } from "react";
import { Network, Loader2, ZoomIn, ZoomOut, Maximize2 } from "lucide-react";
import { api } from "@/lib/api";

type MindNode = { label: string; children?: MindNode[] };
type NodePos = { x: number; y: number; label: string; depth: number; parent?: { x: number; y: number } };

function flattenTree(node: MindNode, x: number, y: number, depth: number, positions: NodePos[], parent?: { x: number; y: number }) {
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

const COLORS = [
    "#6366f1", "#8b5cf6", "#ec4899", "#f43f5e", "#f97316",
    "#eab308", "#22c55e", "#14b8a6", "#06b6d4", "#3b82f6",
];

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

    const generate = async () => {
        if (!topic.trim() || loading) return;
        setLoading(true);
        setError(null);
        setData(null);
        try {
            const result = await api.student.generateTool({ tool: "mindmap", topic: topic.trim() }) as { content?: MindNode; mindmap?: MindNode };
            const tree = result?.content || result?.mindmap || result;
            if (tree && typeof tree === "object" && "label" in tree) {
                setData(tree as MindNode);
            } else {
                setError("Could not parse mind map data");
            }
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to generate mind map");
        } finally {
            setLoading(false);
        }
    };

    const draw = useCallback(() => {
        const canvas = canvasRef.current;
        if (!canvas || !data) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        const dpr = window.devicePixelRatio || 1;
        canvas.width = canvas.offsetWidth * dpr;
        canvas.height = canvas.offsetHeight * dpr;
        ctx.scale(dpr, dpr);

        ctx.clearRect(0, 0, canvas.offsetWidth, canvas.offsetHeight);
        ctx.save();
        ctx.translate(pan.x, pan.y + canvas.offsetHeight / (2 * dpr));
        ctx.scale(zoom, zoom);

        const positions: NodePos[] = [];
        flattenTree(data, 0, 0, 0, positions);

        // Draw edges
        positions.forEach((pos) => {
            if (pos.parent) {
                ctx.beginPath();
                ctx.moveTo(pos.parent.x + 60, pos.parent.y);
                const cpx = pos.parent.x + 155;
                ctx.bezierCurveTo(cpx, pos.parent.y, cpx, pos.y, pos.x - 10, pos.y);
                ctx.strokeStyle = COLORS[pos.depth % COLORS.length] + "40";
                ctx.lineWidth = 2;
                ctx.stroke();
            }
        });

        // Draw nodes
        positions.forEach((pos) => {
            const color = COLORS[pos.depth % COLORS.length];
            const w = Math.min(Math.max(ctx.measureText(pos.label).width + 30, 80), 200);
            const h = 36;
            const rx = 12;

            // Shadow
            ctx.shadowColor = color + "30";
            ctx.shadowBlur = 8;
            ctx.shadowOffsetY = 3;

            // Rounded rect
            ctx.beginPath();
            ctx.roundRect(pos.x - 10, pos.y - h / 2, w, h, rx);
            ctx.fillStyle = pos.depth === 0 ? color : "#ffffff";
            ctx.fill();
            ctx.shadowColor = "transparent";
            ctx.strokeStyle = color;
            ctx.lineWidth = pos.depth === 0 ? 0 : 2;
            if (pos.depth > 0) ctx.stroke();

            // Text
            ctx.fillStyle = pos.depth === 0 ? "#ffffff" : color;
            ctx.font = `${pos.depth === 0 ? "bold " : ""}13px Inter, system-ui, sans-serif`;
            ctx.textAlign = "left";
            ctx.textBaseline = "middle";
            const maxTextW = w - 20;
            let text = pos.label;
            if (ctx.measureText(text).width > maxTextW) {
                while (ctx.measureText(text + "…").width > maxTextW && text.length > 0) text = text.slice(0, -1);
                text += "…";
            }
            ctx.fillText(text, pos.x, pos.y);
        });

        ctx.restore();
    }, [data, zoom, pan]);

    useEffect(() => { draw(); }, [draw]);

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
        <div className="max-w-5xl mx-auto">
            {/* Header */}
            <div className="mb-5">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 shadow-lg">
                        <Network className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Interactive Mind Map</h1>
                        <p className="text-xs text-[var(--text-muted)]">Visualize topic relationships from your study materials</p>
                    </div>
                </div>
            </div>

            {/* Input */}
            {!data && (
                <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 mb-5">
                    <input
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") void generate(); }}
                        placeholder="Enter a topic — e.g. Cell Biology, Newton's Laws..."
                        className="w-full px-4 py-3 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-emerald-500/50 mb-3"
                    />
                    <button
                        onClick={() => void generate()}
                        disabled={loading || !topic.trim()}
                        className="w-full px-5 py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white text-sm font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-40 flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Network className="w-4 h-4" />}
                        Generate Mind Map
                    </button>
                </div>
            )}

            {error && <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">{error}</div>}

            {loading && (
                <div className="bg-[var(--bg-card)] rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-emerald-500 to-teal-600 flex items-center justify-center animate-pulse">
                        <Network className="w-7 h-7 text-white" />
                    </div>
                    <p className="text-sm font-medium">Generating mind map...</p>
                </div>
            )}

            {/* Canvas */}
            {!loading && data && (
                <div className="relative bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] border border-[var(--border)]/50 overflow-hidden">
                    {/* Zoom Controls */}
                    <div className="absolute top-3 right-3 flex gap-1.5 z-10">
                        <button onClick={() => setZoom((z) => Math.min(z + 0.15, 2.5))} className="p-2 bg-white/90 rounded-lg shadow-md hover:bg-[var(--bg-card)] transition-all">
                            <ZoomIn className="w-4 h-4 text-[var(--text-secondary)]" />
                        </button>
                        <button onClick={() => setZoom((z) => Math.max(z - 0.15, 0.3))} className="p-2 bg-white/90 rounded-lg shadow-md hover:bg-[var(--bg-card)] transition-all">
                            <ZoomOut className="w-4 h-4 text-[var(--text-secondary)]" />
                        </button>
                        <button onClick={() => { setZoom(1); setPan({ x: 60, y: 0 }); }} className="p-2 bg-white/90 rounded-lg shadow-md hover:bg-[var(--bg-card)] transition-all">
                            <Maximize2 className="w-4 h-4 text-[var(--text-secondary)]" />
                        </button>
                        <button onClick={() => { setData(null); setTopic(""); }} className="px-3 py-2 text-[10px] font-bold bg-white/90 rounded-lg shadow-md hover:bg-[var(--bg-card)] text-[var(--text-muted)] transition-all">New</button>
                    </div>
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
            )}
        </div>
    );
}
