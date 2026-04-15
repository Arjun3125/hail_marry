"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
    Sparkles,
    Layers,
    Brain,
    Swords,
    Bookmark,
} from "lucide-react";
import { api } from "@/lib/api";

interface ActionBarProps {
    response: {
        answer: string;
        mode: string;
        query_id?: string | null;
    };
    query: string;
}

const actions = [
    { id: "quiz", label: "Quiz", icon: Sparkles, desc: "Test knowledge" },
    { id: "flashcards", label: "Flashcards", icon: Layers, desc: "Study cards" },
    { id: "mindmap", label: "Mind Map", icon: Brain, desc: "Visual map" },
    { id: "debate", label: "Debate", icon: Swords, desc: "Challenge ideas" },
];

export function ActionBar({ response, query }: ActionBarProps) {
    const router = useRouter();
    const [saved, setSaved] = useState(false);

    const handleAction = (actionId: string) => {
        // Store context in sessionStorage for the target tool to access
        const timestamp = new Date().toISOString();
        sessionStorage.setItem(`ai_studio_context_${actionId}`, JSON.stringify({
            sourceQuery: query,
            sourceResponse: response.answer,
            sourceMode: response.mode,
            timestamp,
        }));

        // Navigate to AI Studio with the target tool pre-selected
        router.push(`/student/ai-studio?tool=${actionId}`);
    };

    const handleSave = async () => {
        const queryId = response.query_id;
        if (queryId) {
            try {
                await api.aiHistory.togglePin(queryId);
                setSaved(true);
            } catch {
                router.push("/student/ai-library");
            }
        } else {
            router.push("/student/ai-library");
        }
    };

    return (
        <div className="flex items-center gap-2">
            <span className="text-[10px] text-[var(--text-muted)] hidden sm:inline">Continue:</span>
            {actions.map((action) => (
                <button
                    key={action.id}
                    onClick={() => handleAction(action.id)}
                    className="flex items-center gap-1.5 px-2 py-1 text-[10px] bg-[var(--bg-page)] hover:bg-[var(--primary-light)] text-[var(--text-secondary)] hover:text-[var(--primary)] rounded-md border border-[var(--border)] transition-colors"
                    title={action.desc}
                >
                    <action.icon className="w-3 h-3" />
                    <span className="hidden sm:inline">{action.label}</span>
                </button>
            ))}
            <div className="w-px h-4 bg-[var(--border)] mx-1" />
            <button
                onClick={() => void handleSave()}
                disabled={saved}
                className={`flex items-center gap-1.5 px-2 py-1 text-[10px] rounded-md transition-colors ${
                    saved
                        ? "bg-[var(--success)] text-white cursor-default"
                        : "bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]"
                }`}
            >
                <Bookmark className="w-3 h-3" />
                {saved ? "Saved" : "Save"}
            </button>
        </div>
    );
}
