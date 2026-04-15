"use client";

import { ExportedMessageRepository } from "@assistant-ui/core";

export type Citation = {
    source?: string;
    page?: string | null;
    url?: string | null;
    text?: string;
};

export interface AIResponse {
    answer: string;
    citations: Citation[];
    mode: string;
    runtime_mode?: string;
    is_demo_response?: boolean;
    demo_notice?: string | null;
    query_id?: string | null;
}

export type PersistedThreadRepository = {
    headId?: string | null;
    messages: Array<{
        message: unknown;
        parentId: string | null;
        runConfig?: unknown;
    }>;
};

export type PersistedAssistantThread = {
    id: string;
    title: string;
    preview: string;
    updatedAt: string;
    repository: PersistedThreadRepository;
};

type PersistedThreadStore = {
    threadsByScope: Record<string, PersistedAssistantThread[]>;
    activeThreadByScope: Record<string, string>;
};

const STORAGE_KEY = "vidyaos_ai_studio_threads_v1";
const MAX_THREADS_PER_SCOPE = 12;

function emptyStore(): PersistedThreadStore {
    return {
        threadsByScope: {},
        activeThreadByScope: {},
    };
}

function readStore(): PersistedThreadStore {
    if (typeof window === "undefined") {
        return emptyStore();
    }

    try {
        const raw = window.localStorage.getItem(STORAGE_KEY);
        if (!raw) return emptyStore();
        const parsed = JSON.parse(raw) as PersistedThreadStore;
        return {
            threadsByScope: parsed.threadsByScope || {},
            activeThreadByScope: parsed.activeThreadByScope || {},
        };
    } catch {
        return emptyStore();
    }
}

function writeStore(store: PersistedThreadStore) {
    if (typeof window === "undefined") return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(store));
}

export function makeThreadScopeKey(scope: string, tool: string, notebookId: string | null) {
    return `${scope}:${tool}:${notebookId || "none"}`;
}

export function listPersistedThreads(scopeKey: string) {
    const store = readStore();
    return (store.threadsByScope[scopeKey] || []).sort(
        (a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime(),
    );
}

export function getActivePersistedThreadId(scopeKey: string) {
    const store = readStore();
    return store.activeThreadByScope[scopeKey] || null;
}

export function setActivePersistedThreadId(scopeKey: string, threadId: string) {
    const store = readStore();
    store.activeThreadByScope[scopeKey] = threadId;
    writeStore(store);
}

function createThreadId() {
    return `thread_${Date.now()}_${Math.random().toString(36).slice(2, 8)}`;
}

export function buildThreadTitle(query: string) {
    const normalized = query.replace(/\s+/g, " ").trim();
    if (!normalized) return "Untitled thread";
    return normalized.length > 48 ? `${normalized.slice(0, 48).trimEnd()}...` : normalized;
}

export function buildThreadPreview(query: string, answer?: string) {
    const source = answer?.trim() || query.trim();
    if (!source) return "No messages yet";
    const normalized = source.replace(/\s+/g, " ").trim();
    return normalized.length > 96 ? `${normalized.slice(0, 96).trimEnd()}...` : normalized;
}

export function createEmptyPersistedThread() {
    return {
        id: createThreadId(),
        title: "New thread",
        preview: "No messages yet",
        updatedAt: new Date().toISOString(),
        repository: ExportedMessageRepository.fromArray([]) as PersistedThreadRepository,
    } satisfies PersistedAssistantThread;
}

export function createPersistedThreadFromExchange(query: string, response: AIResponse) {
    return {
        id: createThreadId(),
        title: buildThreadTitle(query),
        preview: buildThreadPreview(query, response.answer),
        updatedAt: new Date().toISOString(),
        repository: ExportedMessageRepository.fromArray([
            {
                role: "user",
                content: [{ type: "text", text: query }],
                metadata: { custom: {} },
            },
            {
                role: "assistant",
                content: [{ type: "text", text: response.answer }],
                metadata: { custom: { aiResponse: response } },
                status: { type: "complete", reason: "stop" },
            },
        ]) as PersistedThreadRepository,
    } satisfies PersistedAssistantThread;
}

export function upsertPersistedThread(scopeKey: string, thread: PersistedAssistantThread) {
    const store = readStore();
    const current = store.threadsByScope[scopeKey] || [];
    const next = [thread, ...current.filter((item) => item.id !== thread.id)]
        .sort((a, b) => new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime())
        .slice(0, MAX_THREADS_PER_SCOPE);

    store.threadsByScope[scopeKey] = next;
    store.activeThreadByScope[scopeKey] = thread.id;
    writeStore(store);
    return next;
}

export function deletePersistedThread(scopeKey: string, threadId: string) {
    const store = readStore();
    const remaining = (store.threadsByScope[scopeKey] || []).filter((thread) => thread.id !== threadId);
    store.threadsByScope[scopeKey] = remaining;

    if (store.activeThreadByScope[scopeKey] === threadId) {
        if (remaining[0]) {
            store.activeThreadByScope[scopeKey] = remaining[0].id;
        } else {
            delete store.activeThreadByScope[scopeKey];
        }
    }

    writeStore(store);
    return remaining;
}
