"use client";

import { AlertCircle, Brain, Sparkles } from "lucide-react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import remarkMath from "remark-math";
import rehypeKatex from "rehype-katex";

import { CitationPopover } from "./CitationPopover";
import { EditableNotesSurface } from "./EditableNotesSurface";
import { FlashcardDeck, type FlashcardState } from "./FlashcardDeck";
import { KnowledgeGraphView } from "./KnowledgeGraphView";
import { MermaidDiagram } from "./MermaidDiagram";
import { QuizView, type QuizState } from "./QuizView";

export type ToolState = QuizState | FlashcardState;

interface AIMessageRendererProps {
    response: AIResponse;
    isLoading?: boolean;
    initialState?: ToolState;
    onStateChange?: (state: ToolState) => void;
}

type Citation = {
    source?: string;
    page?: string | null;
    url?: string | null;
    text?: string;
};

type AIResponse = {
    answer: string;
    citations: Citation[];
    mode: string;
    runtime_mode?: string;
    is_demo_response?: boolean;
    demo_notice?: string | null;
};

type QuizQuestion = {
    question?: string;
    q?: string;
    options?: string[];
    correct?: string;
    answer?: string | number;
    citation?: string | null;
};

type Flashcard = { front: string; back: string; citation?: string | null };

type FlowchartStep = {
    id: string;
    label: string;
    detail: string;
    citation: string;
};

type FlowchartArtifact = {
    mermaid?: string;
    steps?: FlowchartStep[];
};

function parseJson<T>(value: string): T | null {
    try {
        return JSON.parse(value) as T;
    } catch {
        return null;
    }
}

function renderQuiz(
    answer: string,
    isLoading: boolean,
    initialState?: QuizState,
    onStateChange?: (state: QuizState) => void,
) {
    const parsed = parseJson<{ questions?: QuizQuestion[] } | QuizQuestion[]>(answer);
    const questions = Array.isArray(parsed) ? parsed : parsed?.questions || [];
    if (!questions.length) return null;

    return (
        <QuizView
            questions={questions}
            isLoading={isLoading}
            initialState={initialState}
            onStateChange={onStateChange}
        />
    );
}

function renderFlashcards(
    answer: string,
    isLoading: boolean,
    initialState?: FlashcardState,
    onStateChange?: (state: FlashcardState) => void,
) {
    const parsed = parseJson<{ cards?: Flashcard[] } | Flashcard[]>(answer);
    const cards = Array.isArray(parsed) ? parsed : parsed?.cards || [];
    return cards.length ? (
        <FlashcardDeck
            cards={cards}
            isLoading={isLoading}
            initialState={initialState}
            onStateChange={onStateChange}
        />
    ) : null;
}

function renderMindMap(answer: string) {
    const parsed = parseJson<Record<string, unknown>>(answer);
    return parsed ? <KnowledgeGraphView kind="mindmap" data={parsed} /> : null;
}

function renderConceptMap(answer: string) {
    const parsed = parseJson<Record<string, unknown>>(answer);
    return parsed ? <KnowledgeGraphView kind="concept_map" data={parsed} /> : null;
}

function renderFlowchart(answer: string) {
    const parsed = parseJson<FlowchartArtifact>(answer);
    const chart = typeof parsed?.mermaid === "string" ? parsed.mermaid.trim() : answer.trim();
    if (!chart) return null;

    return (
        <div className="space-y-3">
            <MermaidDiagram chart={chart} />
            {(parsed?.steps || []).length ? (
                <div className="grid gap-2">
                    {parsed?.steps?.map((step, index) => (
                        <div key={`${step.id}-${index}`} className="rounded-2xl border border-[var(--border)] bg-[var(--bg-page)] p-4">
                            <p className="text-sm font-semibold text-[var(--text-primary)]">
                                {index + 1}. {step.label}
                            </p>
                            <p className="mt-1 text-xs text-[var(--text-secondary)]">{step.detail}</p>
                            <p className="mt-2 text-[10px] text-[var(--text-muted)]">Citation: {step.citation}</p>
                        </div>
                    ))}
                </div>
            ) : null}
        </div>
    );
}

function renderEditableDoc(mode: string, answer: string) {
    if (mode === "study_guide") {
        return <EditableNotesSurface title="Study guide" content={answer} />;
    }
    if (mode === "essay_review") {
        return <EditableNotesSurface title="Essay review" content={answer} />;
    }
    return null;
}

function renderDefaultText(answer: string) {
    return (
        <div className="prose prose-invert max-w-none text-sm leading-7">
            <ReactMarkdown remarkPlugins={[remarkGfm, remarkMath]} rehypePlugins={[rehypeKatex]}>
                {answer}
            </ReactMarkdown>
        </div>
    );
}

function progressLinesForMode(mode: string) {
    if (mode === "quiz" || mode === "flashcards") {
        return [
            "Reading your latest class notes...",
            "Finding useful recall points for this topic...",
            "Preparing practice that matches your level...",
        ];
    }

    if (mode === "study_guide") {
        return [
            "Reading your uploaded material...",
            "Grouping definitions, examples, and weak areas...",
            "Preparing a study guide you can revise from...",
        ];
    }

    return [
        "Reading your notes and textbook context...",
        "Finding relevant sections for your question...",
        "Preparing a grounded answer with sources...",
    ];
}

export function AIMessageRenderer({
    response,
    isLoading = false,
    initialState,
    onStateChange,
}: AIMessageRendererProps) {
    const structured =
        renderEditableDoc(response.mode, response.answer) ||
        (response.mode === "quiz"
            ? renderQuiz(response.answer, isLoading, initialState as QuizState | undefined, onStateChange as ((state: QuizState) => void) | undefined)
            : null) ||
        (response.mode === "flashcards"
            ? renderFlashcards(response.answer, isLoading, initialState as FlashcardState | undefined, onStateChange as ((state: FlashcardState) => void) | undefined)
            : null) ||
        (response.mode === "mindmap" ? renderMindMap(response.answer) : null) ||
        (response.mode === "concept_map" ? renderConceptMap(response.answer) : null) ||
        (response.mode === "flowchart" ? renderFlowchart(response.answer) : null);
    const showProgressLanguage = isLoading && !response.answer.trim();

    return (
        <div className="space-y-4">
            {response.is_demo_response ? (
                <div className="flex items-start gap-2 rounded-xl border border-amber-400/20 bg-amber-500/10 px-3 py-2 text-xs text-amber-100">
                    <AlertCircle className="mt-0.5 h-3.5 w-3.5 shrink-0 text-amber-300" />
                    <div>
                        <p className="font-medium">Demo runtime</p>
                        <p className="text-amber-100/80">{response.demo_notice || "This response is a demo preview."}</p>
                    </div>
                </div>
            ) : null}

            <div className="flex flex-wrap items-center gap-2">
                <span className="inline-flex items-center gap-1.5 rounded-full bg-indigo-500/12 px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] text-indigo-300">
                    <Sparkles className="h-3 w-3" />
                    {response.mode.replace("_", " ")}
                </span>
                {response.mode === "mindmap" || response.mode === "concept_map" ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full bg-cyan-500/12 px-2.5 py-1 text-[10px] uppercase tracking-[0.2em] text-cyan-300">
                        <Brain className="h-3 w-3" />
                        Interactive map
                    </span>
                ) : null}
            </div>

            {showProgressLanguage ? (
                <div className="rounded-[1.5rem] border border-[rgba(79,142,247,0.22)] bg-[rgba(79,142,247,0.08)] p-4">
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-status-blue">AI is working</p>
                    <div className="mt-3 space-y-2">
                        {progressLinesForMode(response.mode).map((line, index) => (
                            <div key={line} className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
                                <span className={`h-2 w-2 rounded-full ${index === 0 ? "animate-pulse bg-status-blue" : "bg-[var(--border)]"}`} />
                                {line}
                            </div>
                        ))}
                    </div>
                </div>
            ) : (
                structured || renderDefaultText(response.answer)
            )}

            {response.citations.length > 0 ? (
                <div className="space-y-2 border-t border-[var(--border)]/60 pt-4">
                    <p className="text-[10px] font-medium uppercase tracking-[0.24em] text-[var(--text-muted)]">Sources</p>
                    <div className="flex flex-wrap gap-2">
                        {response.citations.map((citation, index) => (
                            <CitationPopover key={`${citation.source || "source"}-${index}`} citation={citation} />
                        ))}
                    </div>
                </div>
            ) : null}
        </div>
    );
}
