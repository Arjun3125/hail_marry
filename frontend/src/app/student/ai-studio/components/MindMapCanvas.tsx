"use client";

import { useRef, useState, useMemo } from "react";
import { ZoomIn, ZoomOut, RotateCcw, Download, Share2 } from "lucide-react";

interface MindNode {
    id: string;
    label: string;
    children?: MindNode[];
    color?: string;
}

interface NodePosition {
    x: number;
    y: number;
    depth: number;
    color: { bg: string; text: string };
}

interface MindMapCanvasProps {
    data: MindNode;
    title?: string;
    onNodeClick?: (node: MindNode) => void;
    onSave?: () => void;
}

// Color palette for nodes
const colors = [
    { bg: "#6366f1", text: "#ffffff" },
    { bg: "#8b5cf6", text: "#ffffff" },
    { bg: "#ec4899", text: "#ffffff" },
    { bg: "#10b981", text: "#ffffff" },
    { bg: "#f59e0b", text: "#ffffff" },
    { bg: "#06b6d4", text: "#ffffff" },
];

// Calculate node positions - defined outside component for proper recursion
function calculateNodePositions(
    node: MindNode,
    depth: number = 0,
    angle: number = 0,
    parentX: number = 0,
    parentY: number = 0
): Map<string, NodePosition> {
    const positions = new Map<string, NodePosition>();
    const radius = 120 + depth * 40;
    const x = parentX + Math.cos(angle) * radius;
    const y = parentY + Math.sin(angle) * radius;

    positions.set(node.id, {
        x,
        y,
        depth,
        color: colors[depth % colors.length],
    });

    if (node.children) {
        const childCount = node.children.length;
        const angleStep = Math.PI / Math.max(childCount, 2);
        const startAngle = angle - (Math.PI / 2);

        node.children.forEach((child, i) => {
            const childAngle = startAngle + i * angleStep;
            const childPositions = calculateNodePositions(child, depth + 1, childAngle, x, y);
            childPositions.forEach((pos: NodePosition, id: string) => positions.set(id, pos));
        });
    }

    return positions;
}

export function MindMapCanvas({ data, title = "Mind Map", onNodeClick, onSave }: MindMapCanvasProps) {
    const svgRef = useRef<SVGSVGElement>(null);
    const containerRef = useRef<HTMLDivElement>(null);
    const [scale, setScale] = useState(1);
    const [translateX, setTranslateX] = useState(0);
    const [translateY, setTranslateY] = useState(0);
    const [isDragging, setIsDragging] = useState(false);
    const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
    const [selectedNode, setSelectedNode] = useState<string | null>(null);

    // Calculate positions
    const positions = useMemo(() => calculateNodePositions(data, 0, -Math.PI / 2, 0, 0), [data]);

    // Handle zoom
    const handleZoomIn = () => setScale((s) => Math.min(s * 1.2, 3));
    const handleZoomOut = () => setScale((s) => Math.max(s / 1.2, 0.3));
    const handleReset = () => {
        setScale(1);
        setTranslateX(0);
        setTranslateY(0);
    };

    // Handle mouse drag
    const handleMouseDown = (e: React.MouseEvent) => {
        const target = e.target as HTMLElement | SVGElement;
        if (e.target === svgRef.current || (target instanceof HTMLElement && target.tagName === "g")) {
            setIsDragging(true);
            setDragStart({ x: e.clientX - translateX, y: e.clientY - translateY });
        }
    };

    const handleMouseMove = (e: React.MouseEvent) => {
        if (isDragging) {
            setTranslateX(e.clientX - dragStart.x);
            setTranslateY(e.clientY - dragStart.y);
        }
    };

    const handleMouseUp = () => {
        setIsDragging(false);
    };

    // Handle node click
    const handleNodeClick = (node: MindNode) => {
        setSelectedNode(node.id);
        onNodeClick?.(node);
    };

    // Export SVG
    const handleExport = () => {
        if (!svgRef.current) return;
        const svgData = new XMLSerializer().serializeToString(svgRef.current);
        const blob = new Blob([svgData], { type: "image/svg+xml" });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = `${title.toLowerCase().replace(/\s+/g, "-")}.svg`;
        link.click();
        URL.revokeObjectURL(url);
    };

    // Render mind map recursively
    const renderNode = (node: MindNode): React.ReactNode => {
        const pos = positions.get(node.id);
        if (!pos) return null;

        const hasChildren = node.children && node.children.length > 0;

        return (
            <g key={node.id}>
                {/* Connection lines to children */}
                {hasChildren &&
                    node.children!.map((child) => {
                        const childPos = positions.get(child.id);
                        if (!childPos) return null;
                        return (
                            <line
                                key={`line-${node.id}-${child.id}`}
                                x1={pos.x}
                                y1={pos.y}
                                x2={childPos.x}
                                y2={childPos.y}
                                stroke="var(--border)"
                                strokeWidth={2}
                                className="transition-all duration-300"
                            />
                        );
                    })}

                {/* Node circle */}
                <g
                    transform={`translate(${pos.x}, ${pos.y})`}
                    onClick={() => handleNodeClick(node)}
                    className="cursor-pointer transition-transform duration-200 hover:scale-110"
                >
                    <circle
                        r={pos.depth === 0 ? 50 : 35}
                        fill={pos.color.bg}
                        stroke={selectedNode === node.id ? "#ffffff" : "transparent"}
                        strokeWidth={selectedNode === node.id ? 4 : 0}
                        className="drop-shadow-lg"
                        filter="url(#shadow)"
                    />
                    <text
                        y={5}
                        textAnchor="middle"
                        fill={pos.color.text}
                        fontSize={pos.depth === 0 ? 14 : 11}
                        fontWeight={pos.depth === 0 ? "bold" : "normal"}
                        className="pointer-events-none select-none"
                    >
                        {node.label.length > 15 ? node.label.slice(0, 15) + "..." : node.label}
                    </text>
                </g>

                {/* Render children */}
                {hasChildren && node.children!.map((child) => renderNode(child))}
            </g>
        );
    };

    // Get viewBox bounds
    const allPositions = Array.from(positions.values());
    const minX = Math.min(...allPositions.map((p: NodePosition) => p.x)) - 100;
    const maxX = Math.max(...allPositions.map((p: NodePosition) => p.x)) + 100;
    const minY = Math.min(...allPositions.map((p: NodePosition) => p.y)) - 100;
    const maxY = Math.max(...allPositions.map((p: NodePosition) => p.y)) + 100;

    return (
        <div ref={containerRef} className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                <div>
                    <h2 className="font-semibold text-[var(--text-primary)]">{title}</h2>
                    <p className="text-xs text-[var(--text-muted)]">
                        {positions.size} nodes • Click and drag to pan
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={handleZoomOut}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Zoom out"
                    >
                        <ZoomOut className="w-4 h-4" />
                    </button>
                    <span className="text-xs text-[var(--text-muted)] w-12 text-center">{Math.round(scale * 100)}%</span>
                    <button
                        onClick={handleZoomIn}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Zoom in"
                    >
                        <ZoomIn className="w-4 h-4" />
                    </button>
                    <div className="w-px h-6 bg-[var(--border)] mx-2" />
                    <button
                        onClick={handleReset}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Reset view"
                    >
                        <RotateCcw className="w-4 h-4" />
                    </button>
                    <button
                        onClick={handleExport}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Export SVG"
                    >
                        <Download className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => onSave?.()}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Save mind map"
                    >
                        <Share2 className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Canvas */}
            <div className="flex-1 overflow-hidden bg-[var(--bg-page)] relative">
                <svg
                    ref={svgRef}
                    className="w-full h-full"
                    viewBox={`${minX} ${minY} ${maxX - minX} ${maxY - minY}`}
                    preserveAspectRatio="xMidYMid meet"
                    onMouseDown={handleMouseDown}
                    onMouseMove={handleMouseMove}
                    onMouseUp={handleMouseUp}
                    onMouseLeave={handleMouseUp}
                    style={{
                        cursor: isDragging ? "grabbing" : "grab",
                        transform: `translate(${translateX}px, ${translateY}px) scale(${scale})`,
                    }}
                >
                    <defs>
                        <filter id="shadow" x="-50%" y="-50%" width="200%" height="200%">
                            <feDropShadow dx="0" dy="2" stdDeviation="3" floodOpacity="0.3" />
                        </filter>
                    </defs>
                    <g>{renderNode(data)}</g>
                </svg>

                {/* Controls overlay */}
                <div className="absolute bottom-4 left-4 bg-[var(--bg-card)] rounded-xl border border-[var(--border)] p-2 shadow-lg">
                    <p className="text-[10px] text-[var(--text-muted)] px-2 py-1">Mouse: Drag to pan • Click nodes • Scroll to zoom</p>
                </div>
            </div>
        </div>
    );
}

