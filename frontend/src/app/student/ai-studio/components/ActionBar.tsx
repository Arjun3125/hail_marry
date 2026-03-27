"use client";

import { useRouter } from "next/navigation";
import {
    Sparkles,
    Layers,
    Brain,
    Swords,
    Bookmark,
} from "lucide-react";

interface ActionBarProps {
    response: {
        answer: string;
        mode: string;
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

    const handleSave = () => {
        // TODO: Implement save to library functionality
        console.log("Save to library:", { query, response });
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
                onClick={handleSave}
                className="flex items-center gap-1.5 px-2 py-1 text-[10px] bg-[var(--primary)] text-white rounded-md hover:bg-[var(--primary-hover)] transition-colors"
            >
                <Bookmark className="w-3 h-3" />
                Save
            </button>
        </div>
    );
}
