"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import {
    AssistantRuntimeProvider,
    ComposerPrimitive,
    ThreadPrimitive,
    useAui,
    useAuiState,
    useLocalRuntime,
} from "@assistant-ui/react";
import { APIError, api } from "@/lib/api";
import {
    Bot,
    Bookmark,
    Copy,
    History,
    Loader2,
    MessageSquarePlus,
    MoreHorizontal,
    Send,
    Sparkles,
    ThumbsDown,
    ThumbsUp,
    Trash2,
} from "lucide-react";

import { ActionBar } from "./ActionBar";
import { AIMessageRenderer } from "./AIMessageRenderer";
import {
    AIResponse,
    buildThreadPreview,
    buildThreadTitle,
    createEmptyPersistedThread,
    createPersistedThreadFromExchange,
    deletePersistedThread,
    getActivePersistedThreadId,
    listPersistedThreads,
    makeThreadScopeKey,
    PersistedAssistantThread,
    PersistedThreadRepository,
    setActivePersistedThreadId,
    upsertPersistedThread,
} from "./threadPersistence";

interface LearningWorkspaceProps {
    activeTool: string;
    notebookId: string | null;
    workspaceScope?: string;
    requestOptions?: {
        language?: string;
        responseLength?: string;
        expertiseLevel?: string;
    };
    initialExchange?: {
        query: string;
        response: AIResponse;
    } | null;
    seedPrompt?: string | null;
}

type Citation = {
    source?: string;
    page?: string | null;
    url?: string | null;
    text?: string;
};

const toolConfig: Record<string, { placeholder: string; title: string; desc: string }> = {
    qa: { placeholder: "Ask anything about your materials...", title: "Q&A", desc: "Get answers with citations from your notes" },
    study_guide: { placeholder: "Enter a topic for a comprehensive study guide...", title: "Study Guide", desc: "Generate structured topic summaries" },
    socratic: { placeholder: "What would you like to explore through questioning?", title: "Socratic Tutor", desc: "Learn through guided discovery" },
    quiz: { placeholder: "Enter a topic to create a quiz...", title: "Quiz", desc: "Test your knowledge with MCQs" },
    flashcards: { placeholder: "What topic should we make flashcards for?", title: "Flashcards", desc: "Spaced repetition study cards" },
    perturbation: { placeholder: "Paste a question to generate variations...", title: "Exam Prep", desc: "Practice with question variations" },
    debate: { placeholder: "State your position or thesis...", title: "Debate", desc: "Challenge and refine your arguments" },
    essay_review: { placeholder: "Paste your essay for feedback...", title: "Essay Review", desc: "Get writing improvement suggestions" },
    mindmap: { placeholder: "What topic should we map out?", title: "Mind Map", desc: "Visual topic hierarchy" },
    flowchart: { placeholder: "What process should we diagram?", title: "Flowchart", desc: "Step-by-step visualization" },
    concept_map: { placeholder: "What concepts should we connect?", title: "Concept Map", desc: "Relationship visualization" },
};

function extractTextContent(
    parts: ReadonlyArray<{ type: string; text?: string; data?: unknown }> | undefined,
) {
    if (!parts) return "";
    return parts
        .filter((part) => part.type === "text" && typeof part.text === "string")
        .map((part) => part.text || "")
        .join("\n")
        .trim();
}

type PersonalizedSuggestion = {
    id?: string;
    label?: string;
    description?: string;
    prompt?: string;
};

function buildFallbackPrompts(activeTool: string) {
    const config = toolConfig[activeTool] || toolConfig.qa;
    return [
        `Use ${config.title} to help me understand my current material step by step.`,
        `What is the best next study action for me with ${config.title}?`,
    ];
}

function StarterSuggestions({ activeTool, notebookId }: { activeTool: string; notebookId: string | null }) {
    const aui = useAui();
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        let cancelled = false;
        queueMicrotask(() => {
            if (!cancelled) {
                setLoading(true);
            }
        });
        api.personalization.recommendations({
            active_tool: activeTool,
            notebook_id: notebookId,
            current_surface: "ai_studio",
        }).then((payload) => {
            if (cancelled) return;
            const items = ((payload as { items?: PersonalizedSuggestion[] }).items || [])
                .map((item) => item.prompt?.trim())
                .filter((value): value is string => Boolean(value));
            setSuggestions(items.length > 0 ? items.slice(0, 3) : buildFallbackPrompts(activeTool));
        }).catch(() => {
            if (!cancelled) {
                setSuggestions(buildFallbackPrompts(activeTool));
            }
        }).finally(() => {
            if (!cancelled) {
                setLoading(false);
            }
        });

        return () => {
            cancelled = true;
        };
    }, [activeTool, notebookId]);

    return (
        <div className="flex flex-col items-center justify-center h-full text-center">
            <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-indigo-500/20 to-violet-600/20 flex items-center justify-center mb-4">
                <Sparkles className="w-10 h-10 text-indigo-500" />
            </div>
            <h3 className="text-lg font-medium text-[var(--text-primary)] mb-2">Ready to learn?</h3>
            <p className="text-sm text-[var(--text-muted)] max-w-md mb-6">
                {toolConfig[activeTool]?.desc}. Type your query below to get started.
            </p>
            <div className="flex flex-wrap justify-center gap-2">
                {suggestions.map((suggestion) => (
                    <button
                        key={suggestion}
                        type="button"
                        onClick={() => aui.composer().setText(suggestion)}
                        className="px-4 py-2 text-xs bg-[var(--bg-page)] hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] rounded-full border border-[var(--border)] transition-colors"
                    >
                        {suggestion}
                    </button>
                ))}
            </div>
            {loading ? <p className="mt-3 text-[10px] text-[var(--text-muted)]">Loading personalized recommendations…</p> : null}
        </div>
    );
}

function PromptSeed({ seedPrompt }: { seedPrompt?: string | null }) {
    const aui = useAui();
    const seededRef = useRef<string | null>(null);

    useEffect(() => {
        const normalizedPrompt = seedPrompt?.trim() || "";
        if (!normalizedPrompt || seededRef.current === normalizedPrompt) return;
        seededRef.current = normalizedPrompt;
        aui.composer().setText(normalizedPrompt);
    }, [aui, seedPrompt]);

    return null;
}

function MessageBubble({ activeTool }: { activeTool?: string }) {
    const role = useAuiState((s) => s.message.role);
    const text = useAuiState((s) => extractTextContent(s.message.content as ReadonlyArray<{ type: string; text?: string; data?: unknown }>));
    const createdAt = useAuiState((s) => s.message.createdAt);
    const messageIndex = useAuiState((s) => s.message.index);
    const threadMessages = useAuiState((s) => s.thread.messages);
    const metadata = useAuiState((s) => s.message.metadata.custom as { aiResponse?: AIResponse } | undefined);
    const response = metadata?.aiResponse;
    const previousUserText =
        messageIndex > 0
            ? extractTextContent(
                threadMessages[messageIndex - 1]?.content as ReadonlyArray<{ type: string; text?: string; data?: unknown }>
            )
            : "";

    if (role === "user") {
        return (
            <div className="flex justify-end">
                <div className="max-w-[85%] bg-gradient-to-br from-indigo-500 to-violet-600 text-white px-5 py-3 rounded-2xl rounded-br-md shadow-md">
                    <p className="text-sm">{text}</p>
                </div>
            </div>
        );
    }

    const fallbackResponse: AIResponse = response || {
        answer: text || "No response received.",
        citations: [],
        mode: activeTool || "qa",
    };

    return (
        <div className="bg-[var(--bg-page)] rounded-2xl border border-[var(--border)]/50 overflow-hidden">
            <div className="p-5">
                <div className="flex items-center gap-2 mb-4">
                    <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center">
                        <Bot className="w-4 h-4 text-white" />
                    </div>
                    <span className="text-xs font-medium text-[var(--text-muted)] uppercase tracking-wider">
                        AI Assistant
                    </span>
                    <span className="text-xs text-[var(--text-muted)]">
                        {createdAt ? new Date(createdAt).toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }) : ""}
                    </span>
                </div>

                <AIMessageRenderer response={fallbackResponse} />
            </div>

            <div className="flex items-center gap-1 px-5 py-2 bg-[var(--surface-hover)] border-t border-[var(--border)]/50">
                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Copy">
                    <Copy className="w-3.5 h-3.5" />
                </button>
                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Helpful">
                    <ThumbsUp className="w-3.5 h-3.5" />
                </button>
                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Not helpful">
                    <ThumbsDown className="w-3.5 h-3.5" />
                </button>
                <button className="p-1.5 rounded hover:bg-[var(--bg-page)] text-[var(--text-muted)] transition-colors" title="Save">
                    <Bookmark className="w-3.5 h-3.5" />
                </button>
                <div className="flex-1" />
                <ActionBar response={fallbackResponse} query={previousUserText} />
            </div>
        </div>
    );
}

function ComposerBox({ activeTool }: { activeTool: string }) {
    const isRunning = useAuiState((s) => s.thread.isRunning);
    const config = toolConfig[activeTool] || toolConfig.qa;

    return (
        <div className="border-t border-[var(--border)] p-4">
            <ComposerPrimitive.Root className="relative">
                <div className="flex items-end gap-2 bg-[var(--bg-page)] rounded-xl border border-[var(--border)] p-2 focus-within:ring-2 focus-within:ring-[var(--primary)]/50 focus-within:border-[var(--primary)] transition-all">
                    <ComposerPrimitive.Input
                        placeholder={config.placeholder}
                        rows={1}
                        maxRows={6}
                        className="flex-1 min-h-[44px] px-3 py-2.5 text-sm bg-transparent border-0 resize-none focus:outline-none text-[var(--text-primary)] placeholder:text-[var(--text-muted)]"
                    />
                    <ComposerPrimitive.Send
                        className="p-2.5 rounded-lg bg-gradient-to-r from-indigo-500 to-violet-600 text-white hover:shadow-lg transition-all disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isRunning ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                    </ComposerPrimitive.Send>
                </div>
                <p className="mt-2 text-[10px] text-[var(--text-muted)] text-center">
                    Press Enter to send, Shift+Enter for new line
                </p>
            </ComposerPrimitive.Root>
        </div>
    );
}

function ThreadBootstrap({
    thread,
}: {
    thread: PersistedAssistantThread;
}) {
    const aui = useAui();

    useEffect(() => {
        aui.thread().import(thread.repository as never);
    }, [aui, thread.id, thread.repository]);

    return null;
}

function ThreadPersistenceSync({
    activeTool,
    thread,
    onPersist,
}: {
    activeTool: string;
    thread: PersistedAssistantThread;
    onPersist: (thread: PersistedAssistantThread) => void;
}) {
    const aui = useAui();
    const isRunning = useAuiState((s) => s.thread.isRunning);
    const messages = useAuiState((s) => s.thread.messages);
    const lastSerializedRef = useRef("");

    useEffect(() => {
        if (isRunning) return;

        const repository = aui.thread().export() as PersistedThreadRepository;
        const serialized = JSON.stringify(repository);
        if (serialized === lastSerializedRef.current) return;
        lastSerializedRef.current = serialized;

        const userMessages = messages.filter((message) => message.role === "user");
        const assistantMessages = messages.filter((message) => message.role === "assistant");
        const firstUserText = extractTextContent(
            userMessages[0]?.content as ReadonlyArray<{ type: string; text?: string; data?: unknown }>
        );
        const lastAssistantText = extractTextContent(
            assistantMessages.at(-1)?.content as ReadonlyArray<{ type: string; text?: string; data?: unknown }>
        );

        onPersist({
            ...thread,
            title: userMessages.length ? buildThreadTitle(firstUserText) : thread.title,
            preview: buildThreadPreview(firstUserText, lastAssistantText),
            updatedAt: new Date().toISOString(),
            repository,
        });
    }, [activeTool, aui, isRunning, messages, onPersist, thread]);

    return null;
}

function AssistantStudioThread({
    activeTool,
    notebookId,
    thread,
    onPersistThread,
    requestOptions,
    seedPrompt,
}: {
    activeTool: string;
    notebookId: string | null;
    thread: PersistedAssistantThread;
    onPersistThread: (thread: PersistedAssistantThread) => void;
    requestOptions?: {
        language?: string;
        responseLength?: string;
        expertiseLevel?: string;
    };
    seedPrompt?: string | null;
}) {
    const chatModel = useMemo(
        () => ({
            run: async ({ messages }: { messages: ReadonlyArray<{ role: string; content: ReadonlyArray<{ type: string; text?: string }> }> }) => {
                const latestUser = [...messages].reverse().find((message) => message.role === "user");
                const query = extractTextContent(latestUser?.content as ReadonlyArray<{ type: string; text?: string }>);

                try {
                    const data = await api.ai.query({
                        query,
                        mode: activeTool,
                        notebook_id: notebookId,
                        language: requestOptions?.language,
                        response_length: requestOptions?.responseLength,
                        expertise_level: requestOptions?.expertiseLevel,
                    }) as {
                        answer?: string;
                        response_text?: string;
                        citations?: Citation[];
                        runtime_mode?: string;
                        is_demo_response?: boolean;
                        demo_notice?: string | null;
                    };

                    const aiResponse: AIResponse = {
                        answer: data.answer || data.response_text || "No response received.",
                        citations: data.citations || [],
                        mode: activeTool,
                        runtime_mode: data.runtime_mode,
                        is_demo_response: data.is_demo_response,
                        demo_notice: data.demo_notice,
                    };

                    const sourceParts = (aiResponse.citations || [])
                        .filter((citation) => citation.url)
                        .map((citation, index) => ({
                            type: "source" as const,
                            sourceType: "url" as const,
                            id: `${activeTool}-source-${index}`,
                            url: citation.url || "",
                            title: citation.text || citation.source || `Source ${index + 1}`,
                        }));

                    return {
                        content: [
                            { type: "text" as const, text: aiResponse.answer },
                            ...sourceParts,
                        ],
                        metadata: {
                            custom: {
                                aiResponse,
                            },
                        },
                    };
                } catch (err) {
                    const message = err instanceof APIError ? err.message : "Failed to get response. Please try again.";
                    return {
                        content: [{ type: "text" as const, text: message }],
                        metadata: {
                            custom: {
                                aiResponse: {
                                    answer: message,
                                    citations: [],
                                    mode: activeTool,
                                } satisfies AIResponse,
                            },
                        },
                    };
                }
            },
        }),
        [activeTool, notebookId, requestOptions],
    );

    const runtime = useLocalRuntime(chatModel);

    return (
        <AssistantRuntimeProvider runtime={runtime}>
            <ThreadBootstrap thread={thread} />
            <PromptSeed seedPrompt={seedPrompt} />
            <ThreadPersistenceSync activeTool={activeTool} thread={thread} onPersist={onPersistThread} />
            <div className="flex flex-col h-full">
                <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-violet-600 flex items-center justify-center shadow-lg">
                            <Bot className="w-5 h-5 text-white" />
                        </div>
                        <div>
                            <h2 className="font-semibold text-[var(--text-primary)]">{toolConfig[activeTool]?.title || "AI Studio"}</h2>
                            <p className="text-xs text-[var(--text-muted)]">{toolConfig[activeTool]?.desc || "Learn with AI"}</p>
                        </div>
                    </div>
                </div>

                <ThreadPrimitive.Root className="flex min-h-0 flex-1 flex-col">
                    <ThreadPrimitive.Viewport className="flex-1 overflow-y-auto px-6 py-4">
                        <ThreadPrimitive.Empty>
                            <StarterSuggestions activeTool={activeTool} notebookId={notebookId} />
                        </ThreadPrimitive.Empty>
                        <div className="space-y-6">
                            <ThreadPrimitive.Messages>
                                {() => <MessageBubble activeTool={activeTool} />}
                            </ThreadPrimitive.Messages>
                        </div>
                    </ThreadPrimitive.Viewport>
                    <ThreadPrimitive.ViewportFooter>
                        <ComposerBox activeTool={activeTool} />
                    </ThreadPrimitive.ViewportFooter>
                </ThreadPrimitive.Root>
            </div>
        </AssistantRuntimeProvider>
    );
}

export function LearningWorkspace({ activeTool, notebookId, requestOptions, initialExchange, workspaceScope, seedPrompt }: LearningWorkspaceProps) {
    const [hydrated, setHydrated] = useState(false);
    const [threads, setThreads] = useState<PersistedAssistantThread[]>([]);
    const [activeThreadId, setActiveThreadId] = useState<string | null>(null);
    const consumedInitialExchangeRef = useRef<string | null>(null);
    const workspaceScopeKey = useMemo(
        () => makeThreadScopeKey(workspaceScope || "ai-studio", activeTool, notebookId),
        [activeTool, notebookId, workspaceScope],
    );

    const activeThread = useMemo(
        () => threads.find((thread) => thread.id === activeThreadId) || threads[0] || null,
        [activeThreadId, threads],
    );

    const prevToolRef = useRef(activeTool);

    useEffect(() => {
        let cancelled = false;
        const existing = listPersistedThreads(workspaceScopeKey);
        const preferredId = getActivePersistedThreadId(workspaceScopeKey);
        const selected = existing.find((thread) => thread.id === preferredId) || existing[0] || createEmptyPersistedThread();

        if (existing.length === 0) {
            upsertPersistedThread(workspaceScopeKey, selected);
        }

        queueMicrotask(() => {
            if (cancelled) return;
            setThreads(existing.length === 0 ? [selected] : existing);
            setActiveThreadId(selected.id);
            setHydrated(true);
        });

        return () => {
            cancelled = true;
        };
    }, [workspaceScopeKey]);

    useEffect(() => {
        if (!hydrated) return;
        if (prevToolRef.current !== activeTool) {
            prevToolRef.current = activeTool;
            const fresh = createEmptyPersistedThread();
            const next = upsertPersistedThread(workspaceScopeKey, fresh);
            queueMicrotask(() => {
                setThreads(next);
                setActiveThreadId(fresh.id);
            });
        }
    }, [activeTool, hydrated, workspaceScopeKey]);

    useEffect(() => {
        if (!hydrated || !initialExchange) return;
        let cancelled = false;

        const signature = `${workspaceScopeKey}:${initialExchange.query}:${initialExchange.response.answer}`;
        if (consumedInitialExchangeRef.current === signature) return;
        consumedInitialExchangeRef.current = signature;

        const seededThread = createPersistedThreadFromExchange(initialExchange.query, initialExchange.response);
        const nextThreads = upsertPersistedThread(workspaceScopeKey, seededThread);
        queueMicrotask(() => {
            if (cancelled) return;
            setThreads(nextThreads);
            setActiveThreadId(seededThread.id);
        });

        return () => {
            cancelled = true;
        };
    }, [hydrated, initialExchange, workspaceScopeKey]);

    useEffect(() => {
        if (!activeThreadId) return;
        setActivePersistedThreadId(workspaceScopeKey, activeThreadId);
    }, [activeThreadId, workspaceScopeKey]);

    const persistThread = (thread: PersistedAssistantThread) => {
        const nextThreads = upsertPersistedThread(workspaceScopeKey, thread);
        setThreads(nextThreads);
    };

    const createThread = () => {
        const thread = createEmptyPersistedThread();
        const nextThreads = upsertPersistedThread(workspaceScopeKey, thread);
        setThreads(nextThreads);
        setActiveThreadId(thread.id);
    };

    const removeThread = (threadId: string) => {
        const nextThreads = deletePersistedThread(workspaceScopeKey, threadId);
        if (nextThreads.length === 0) {
            const replacement = createEmptyPersistedThread();
            const seeded = upsertPersistedThread(workspaceScopeKey, replacement);
            setThreads(seeded);
            setActiveThreadId(replacement.id);
            return;
        }
        setThreads(nextThreads);
        setActiveThreadId(nextThreads[0]?.id || null);
    };

    if (!hydrated || !activeThread) {
        return (
            <div className="flex h-full items-center justify-center text-sm text-[var(--text-muted)]">
                Loading workspace...
            </div>
        );
    }

    return (
        <div className="flex h-full min-h-0 flex-col">
            <div className="flex items-center gap-2 overflow-x-auto border-b border-[var(--border)] bg-[var(--bg-page)]/70 px-4 py-3">
                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-[11px] uppercase tracking-[0.2em] text-[var(--text-muted)]">
                    <History className="h-3.5 w-3.5" />
                    Threads
                </div>
                {threads.slice(0, 6).map((thread) => (
                    <div
                        key={thread.id}
                        className={`group flex min-w-0 items-center gap-1 rounded-full border px-3 py-1.5 text-sm transition-colors ${
                            thread.id === activeThreadId
                                ? "border-indigo-500/60 bg-indigo-500/12 text-indigo-100"
                                : "border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-secondary)] hover:border-[var(--primary)]/40 hover:text-[var(--text-primary)]"
                        }`}
                    >
                        <button
                            type="button"
                            onClick={() => setActiveThreadId(thread.id)}
                            className="min-w-0 truncate"
                            title={thread.preview}
                        >
                            {thread.title}
                        </button>
                        {threads.length > 1 ? (
                            <button
                                type="button"
                                onClick={() => removeThread(thread.id)}
                                className="rounded-full p-0.5 text-[var(--text-muted)] opacity-70 transition hover:bg-black/10 hover:text-red-300"
                                title="Delete thread"
                            >
                                <Trash2 className="h-3 w-3" />
                            </button>
                        ) : null}
                    </div>
                ))}
                {threads.length > 6 ? (
                    <div className="inline-flex items-center gap-1 rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-xs text-[var(--text-muted)]">
                        <MoreHorizontal className="h-3.5 w-3.5" />
                        {threads.length - 6} more
                    </div>
                ) : null}
                <div className="ml-auto" />
                <button
                    type="button"
                    onClick={createThread}
                    className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[var(--bg-card)] px-3 py-1.5 text-sm text-[var(--text-secondary)] transition-colors hover:border-[var(--primary)]/50 hover:text-[var(--text-primary)]"
                >
                    <MessageSquarePlus className="h-3.5 w-3.5" />
                    New thread
                </button>
            </div>

            <AssistantStudioThread
                key={`${workspaceScopeKey}-${activeThread.id}`}
                activeTool={activeTool}
                notebookId={notebookId}
                thread={activeThread}
                onPersistThread={persistThread}
                requestOptions={requestOptions}
                seedPrompt={seedPrompt}
            />
        </div>
    );
}

function getSuggestions(tool: string): string[] {
    const suggestions: Record<string, string[]> = {
        qa: ["Explain photosynthesis", "What is mitosis?", "Newton's laws"],
        study_guide: ["Cell biology", "World War II", "Organic chemistry"],
        socratic: ["Why is the sky blue?", "What causes tides?", "How do computers work?"],
        quiz: ["Cell structure", "Ancient civilizations", "Algebra"],
        flashcards: ["Vocabulary: biology", "Math formulas", "Historical dates"],
        perturbation: ["If x² = 4, find x", "Explain gravity", "Describe osmosis"],
        debate: ["Social media benefits society", "Homework should be banned", "AI will replace jobs"],
        essay_review: ["Paste your essay here..."],
        mindmap: ["Ecosystem", "Human body", "Water cycle"],
        flowchart: ["Photosynthesis process", "Decision making", "Algorithm"],
        concept_map: ["Climate change", "Economic systems", "Cell division"],
    };
    return suggestions[tool] || ["Try asking anything..."];
}
