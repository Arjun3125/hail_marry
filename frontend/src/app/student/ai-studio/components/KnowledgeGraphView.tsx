"use client";

import { useMemo } from "react";
import dagre from "dagre";
import {
    Background,
    Controls,
    Edge,
    MiniMap,
    Node,
    Position,
    ReactFlow,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

type MindNode = {
    id?: string;
    label?: string;
    name?: string;
    children?: MindNode[];
};

type ConceptNode = string | { id?: string; label?: string; name?: string };
type ConceptEdge = [string, string] | { from?: string; to?: string; label?: string };

const nodeWidth = 180;
const nodeHeight = 52;

function layoutElements(nodes: Node[], edges: Edge[]) {
    const graph = new dagre.graphlib.Graph();
    graph.setDefaultEdgeLabel(() => ({}));
    graph.setGraph({ rankdir: "LR", ranksep: 80, nodesep: 30 });

    nodes.forEach((node) => graph.setNode(node.id, { width: nodeWidth, height: nodeHeight }));
    edges.forEach((edge) => graph.setEdge(edge.source, edge.target));
    dagre.layout(graph);

    return {
        nodes: nodes.map((node) => {
            const position = graph.node(node.id);
            return {
                ...node,
                sourcePosition: Position.Right,
                targetPosition: Position.Left,
                position: {
                    x: position.x - nodeWidth / 2,
                    y: position.y - nodeHeight / 2,
                },
            };
        }),
        edges,
    };
}

function buildMindMap(root: MindNode) {
    const nodes: Node[] = [];
    const edges: Edge[] = [];

    const walk = (node: MindNode, parentId?: string, index = 0) => {
        const id = node.id || `${parentId || "root"}-${index}`;
        const label = node.label || node.name || "Untitled";
        nodes.push({
            id,
            data: { label },
            type: "default",
            position: { x: 0, y: 0 },
            style: {
                borderRadius: 18,
                border: "1px solid rgba(99, 102, 241, 0.25)",
                background: "rgba(15, 23, 42, 0.88)",
                color: "white",
                width: nodeWidth,
                padding: 12,
            },
        });

        if (parentId) {
            edges.push({
                id: `${parentId}-${id}`,
                source: parentId,
                target: id,
                animated: false,
                style: { stroke: "rgba(99, 102, 241, 0.45)", strokeWidth: 2 },
            });
        }

        (node.children || []).forEach((child, childIndex) => walk(child, id, childIndex));
    };

    walk(root);
    return layoutElements(nodes, edges);
}

function buildConceptMap(data: { nodes?: ConceptNode[]; edges?: ConceptEdge[] }) {
    const normalizedNodes = (data.nodes || []).map((node, index) => {
        if (typeof node === "string") {
            return { id: `node-${index}`, label: node };
        }
        return {
            id: node.id || `node-${index}`,
            label: node.label || node.name || `Node ${index + 1}`,
        };
    });

    const nodeIdByLabel = new Map(normalizedNodes.map((node) => [node.label, node.id]));

    const nodes: Node[] = normalizedNodes.map((node) => ({
        id: node.id,
        data: { label: node.label },
        type: "default",
        position: { x: 0, y: 0 },
        style: {
            borderRadius: 18,
            border: "1px solid rgba(6, 182, 212, 0.28)",
            background: "rgba(15, 23, 42, 0.88)",
            color: "white",
            width: nodeWidth,
            padding: 12,
        },
    }));

    const edges: Edge[] = (data.edges || []).map((edge, index) => {
        if (Array.isArray(edge)) {
            const source = nodeIdByLabel.get(edge[0]) || edge[0];
            const target = nodeIdByLabel.get(edge[1]) || edge[1];
            return {
                id: `edge-${index}`,
                source,
                target,
                label: "",
                style: { stroke: "rgba(6, 182, 212, 0.45)", strokeWidth: 2 },
            };
        }

        return {
            id: `edge-${index}`,
            source: nodeIdByLabel.get(edge.from || "") || edge.from || "",
            target: nodeIdByLabel.get(edge.to || "") || edge.to || "",
            label: edge.label || "",
            style: { stroke: "rgba(6, 182, 212, 0.45)", strokeWidth: 2 },
        };
    });

    return layoutElements(nodes, edges);
}

export function KnowledgeGraphView({
    kind,
    data,
}: {
    kind: "mindmap" | "concept_map";
    data: MindNode | { nodes?: ConceptNode[]; edges?: ConceptEdge[] };
}) {
    const graph = useMemo(() => {
        if (kind === "mindmap") {
            return buildMindMap(data as MindNode);
        }
        return buildConceptMap(data as { nodes?: ConceptNode[]; edges?: ConceptEdge[] });
    }, [data, kind]);

    return (
        <div className="h-[420px] rounded-2xl border border-[var(--border)] bg-[var(--bg-page)]">
            <ReactFlow
                nodes={graph.nodes}
                edges={graph.edges}
                fitView
                fitViewOptions={{ padding: 0.2 }}
                nodesDraggable
                nodesConnectable={false}
                elementsSelectable
                proOptions={{ hideAttribution: true }}
            >
                <Background color="rgba(148, 163, 184, 0.14)" gap={18} />
                <Controls />
                <MiniMap pannable zoomable />
            </ReactFlow>
        </div>
    );
}
