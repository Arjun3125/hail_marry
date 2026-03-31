"use client";

import { useEffect, useMemo, useRef, useState } from "react";
import { usePathname, useRouter, useSearchParams } from "next/navigation";

import { APIError, api } from "@/lib/api";

import { MascotPanel } from "./MascotPanel";
import { MascotChatMessage, MascotResponse } from "./types";

function buildSessionId(role: string) {
    return `mascot:${role}:session`;
}

function readActiveNotebookId() {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem("activeNotebookId");
}

function writeActiveNotebookId(notebookId: string | null | undefined) {
    if (typeof window === "undefined" || !notebookId) return;
    window.localStorage.setItem("activeNotebookId", notebookId);
}

function readActiveNotebookLabel() {
    if (typeof window === "undefined") return null;
    return window.localStorage.getItem("activeNotebookLabel");
}

function writeActiveNotebookLabel(notebookLabel: string | null | undefined) {
    if (typeof window === "undefined") return;
    if (!notebookLabel) {
        window.localStorage.removeItem("activeNotebookLabel");
        return;
    }
    window.localStorage.setItem("activeNotebookLabel", notebookLabel);
}

function readMascotPageContext(pathname: string) {
    if (typeof window === "undefined") return null;
    const raw = window.localStorage.getItem("mascotPageContext");
    if (!raw) return null;
    try {
        const parsed = JSON.parse(raw) as {
            route?: string;
            current_page_entity?: string | null;
            current_page_entity_id?: string | null;
            metadata?: Record<string, unknown>;
        };
        if (!parsed || parsed.route !== pathname) return null;
        return parsed;
    } catch {
        return null;
    }
}

function prettifySegment(value: string) {
    return value
        .split(/[-_]/g)
        .filter(Boolean)
        .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
        .join(" ");
}

function buildRouteLabel(pathname: string) {
    const segments = pathname.split("/").filter(Boolean);
    if (segments.length <= 1) return "Workspace";
    return segments
        .slice(1)
        .map(prettifySegment)
        .join(" / ");
}

function buildPageContextLabel(
    pathname: string,
    pageContext: {
        current_page_entity?: string | null;
        metadata?: Record<string, unknown>;
    } | null,
) {
    const entity = typeof pageContext?.current_page_entity === "string" ? pageContext.current_page_entity.trim() : "";
    const metadata = pageContext?.metadata || {};
    const preferredKeys = ["class_name", "classId", "subject", "exam_name", "wizard_step", "setup_step", "topic", "view"];
    const details = preferredKeys
        .map((key) => metadata[key])
        .find((value) => typeof value === "string" && value.trim()) as string | undefined;
    const base = entity ? prettifySegment(entity) : buildRouteLabel(pathname);
    return details ? `${base}: ${details}` : base;
}

function buildPageContextHint(
    pathname: string,
    pageContext: {
        current_page_entity?: string | null;
        metadata?: Record<string, unknown>;
    } | null,
) {
    const entity = pageContext?.current_page_entity;
    if (entity === "attendance_import") return "Ask the mascot to review OCR lines, import attendance, or summarize class attendance patterns.";
    if (entity === "marks_import") return "Ask the mascot to import marks, review OCR rows, or generate an assessment from the current subject.";
    if (entity === "class_roster") return "Ask the mascot to onboard a class roster, review extracted students, or create a quiz for this class.";
    if (entity === "setup_wizard") return "Ask the mascot to review onboarding progress, validate imports, or open the next admin setup step.";
    if (pathname.includes("/upload")) return "Ask the mascot to attach material to a notebook, summarize it, or generate study tools.";
    if (pathname.includes("/assistant")) return "Use natural language to create notebooks, run study tools, and navigate the platform.";
    return "The mascot is using your current page context to suggest the most relevant actions.";
}

function extractNotebookLabel(response: MascotResponse) {
    const created = response.actions.find(
        (action) => action.kind === "notebook_create" || action.kind === "notebook_update",
    );
    const payload = created?.payload || {};
    const name = payload.name;
    if (typeof name === "string" && name.trim()) return name.trim();
    const navigationTarget = response.navigation?.target;
    if (navigationTarget && typeof navigationTarget === "string" && navigationTarget.toLowerCase().includes("notebook")) {
        return response.follow_up_suggestions.find((item) => item.toLowerCase().includes("notebook")) || null;
    }
    return null;
}

function formatFileSize(bytes: number) {
    if (!Number.isFinite(bytes) || bytes <= 0) return "0 KB";
    if (bytes < 1024 * 1024) return `${Math.max(1, Math.round(bytes / 1024))} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function describeAttachment(file: File | null) {
    if (!file) return null;
    const lowerName = file.name.toLowerCase();
    const mime = file.type.toLowerCase();
    let kind = "Document";
    if (mime.startsWith("image/")) kind = "Image";
    else if (lowerName.endsWith(".pdf")) kind = "PDF";
    else if (lowerName.endsWith(".docx")) kind = "DOCX";
    else if (lowerName.endsWith(".pptx")) kind = "PPTX";
    else if (lowerName.endsWith(".xlsx")) kind = "XLSX";
    return {
        name: file.name,
        kind,
        sizeLabel: formatFileSize(file.size),
    };
}

export function MascotShell({
    role,
    fullPage = false,
    onClose,
}: {
    role: string;
    fullPage?: boolean;
    onClose?: () => void;
}) {
    const pathname = usePathname();
    const router = useRouter();
    const searchParams = useSearchParams();
    const [draft, setDraft] = useState("");
    const [messages, setMessages] = useState<MascotChatMessage[]>([
        {
            id: "mascot-welcome",
            role: "assistant",
            text: "I can help you create notebooks, open tools, answer questions, and trigger study workflows with natural language.",
        },
    ]);
    const [loading, setLoading] = useState(false);
    const [confirmingId, setConfirmingId] = useState<string | null>(null);
    const [suggestions, setSuggestions] = useState<string[]>([]);
    const [sessionId, setSessionId] = useState<string | null>(null);
    const [attachment, setAttachment] = useState<File | null>(null);
    const [activeNotebookLabel, setActiveNotebookLabel] = useState<string | null>(null);
    const seededPromptRef = useRef<string | null>(null);

    useEffect(() => {
        if (typeof window === "undefined") return;
        const key = buildSessionId(role);
        const existing = window.sessionStorage.getItem(key) || `mascot-${role}-${Date.now()}`;
        window.sessionStorage.setItem(key, existing);
        setSessionId(existing);
    }, [role]);

    useEffect(() => {
        const prompt = searchParams.get("prompt")?.trim();
        if (!prompt || seededPromptRef.current === prompt) return;
        seededPromptRef.current = prompt;
        setDraft(prompt);
    }, [searchParams]);

    const notebookId = useMemo(() => readActiveNotebookId(), [pathname, messages.length]);
    const pageContext = useMemo(() => readMascotPageContext(pathname), [pathname, messages.length, attachment?.name]);
    const pageContextLabel = useMemo(() => buildPageContextLabel(pathname, pageContext), [pathname, pageContext]);
    const pageContextHint = useMemo(() => buildPageContextHint(pathname, pageContext), [pathname, pageContext]);
    const attachmentMeta = useMemo(() => describeAttachment(attachment), [attachment]);

    useEffect(() => {
        setActiveNotebookLabel(readActiveNotebookLabel());
    }, [pathname, messages.length]);

    useEffect(() => {
        let cancelled = false;
        void api.mascot
            .suggestions({
                current_route: pathname,
                notebook_id: notebookId,
                current_page_entity: pageContext?.current_page_entity || null,
            })
            .then((payload) => {
                if (!cancelled) {
                    setSuggestions(Array.isArray((payload as { suggestions?: string[] }).suggestions) ? (payload as { suggestions: string[] }).suggestions : []);
                }
            })
            .catch(() => {
                if (!cancelled) setSuggestions([]);
            });
        return () => {
            cancelled = true;
        };
    }, [pathname, notebookId]);

    const applyResponse = (response: MascotResponse) => {
        writeActiveNotebookId(response.notebook_id);
        const nextNotebookLabel = extractNotebookLabel(response);
        if (response.notebook_id && nextNotebookLabel) {
            writeActiveNotebookLabel(nextNotebookLabel);
            setActiveNotebookLabel(nextNotebookLabel);
        }
        if (response.follow_up_suggestions.length) {
            setSuggestions(response.follow_up_suggestions);
        }
        if (response.navigation?.href && response.intent === "navigate") {
            if (response.navigation.notebook_id) {
                writeActiveNotebookId(response.navigation.notebook_id);
            }
            router.push(response.navigation.href);
        }
        setMessages((prev) => [
            ...prev,
            {
                id: response.trace_id,
                role: "assistant",
                text: response.reply_text,
                response,
            },
        ]);
    };

    const sendMessage = async (message: string) => {
        const trimmed = message.trim();
        if ((!trimmed && !attachment) || loading) return;
        const userText = attachment ? (trimmed ? `${trimmed}\n\n[Attached: ${attachment.name}]` : `[Attached: ${attachment.name}]`) : trimmed;
        setMessages((prev) => [...prev, { id: `user-${Date.now()}`, role: "user", text: userText }]);
        setDraft("");
        setLoading(true);
        try {
            let response: MascotResponse;
            if (attachment) {
                const formData = new FormData();
                formData.append("file", attachment);
                formData.append("message", trimmed);
                if (notebookId) formData.append("notebook_id", notebookId);
                if (sessionId) formData.append("session_id", sessionId);
                formData.append("current_route", pathname);
                if (pageContext?.current_page_entity) formData.append("current_page_entity", pageContext.current_page_entity);
                if (pageContext?.current_page_entity_id) formData.append("current_page_entity_id", pageContext.current_page_entity_id);
                if (pageContext?.metadata && Object.keys(pageContext.metadata).length > 0) {
                    formData.append("context_metadata", JSON.stringify(pageContext.metadata));
                }
                response = (await api.mascot.upload(formData)) as MascotResponse;
            } else {
                response = (await api.mascot.message({
                    message: trimmed,
                    channel: "web",
                    notebook_id: notebookId,
                    session_id: sessionId,
                    conversation_history: messages.slice(-6).map((item) => ({ role: item.role, content: item.text })),
                    ui_context: {
                        current_route: pathname,
                        selected_notebook_id: notebookId,
                        current_page_entity: pageContext?.current_page_entity || undefined,
                        current_page_entity_id: pageContext?.current_page_entity_id || undefined,
                        metadata: pageContext?.metadata || undefined,
                    },
                })) as MascotResponse;
            }
            applyResponse(response);
            setAttachment(null);
        } catch (error) {
            const detail = error instanceof APIError ? error.message : "Mascot request failed.";
            setMessages((prev) => [...prev, { id: `assistant-error-${Date.now()}`, role: "assistant", text: detail }]);
        } finally {
            setLoading(false);
        }
    };

    const handleConfirm = async (confirmationId: string, approved: boolean) => {
        if (!confirmationId) return;
        setConfirmingId(confirmationId);
        try {
            const response = (await api.mascot.confirm({
                confirmation_id: confirmationId,
                approved,
                channel: "web",
                session_id: sessionId,
            })) as MascotResponse;
            applyResponse(response);
        } catch (error) {
            const detail = error instanceof APIError ? error.message : "Confirmation failed.";
            setMessages((prev) => [...prev, { id: `assistant-confirm-error-${Date.now()}`, role: "assistant", text: detail }]);
        } finally {
            setConfirmingId(null);
        }
    };

    const handleNavigate = (href: string, nextNotebookId?: string | null) => {
        writeActiveNotebookId(nextNotebookId || null);
        router.push(href);
    };

    return (
        <MascotPanel
            title="Vidya Mascot"
            messages={messages}
            suggestions={suggestions}
            draft={draft}
            loading={loading}
            confirmingId={confirmingId}
            fullPage={fullPage}
            attachmentName={attachment?.name || null}
            attachmentKind={attachmentMeta?.kind || null}
            attachmentSizeLabel={attachmentMeta?.sizeLabel || null}
            activeNotebookId={notebookId}
            activeNotebookLabel={activeNotebookLabel}
            pageContextLabel={pageContextLabel}
            pageContextHint={pageContextHint}
            onDraftChange={setDraft}
            onSend={() => void sendMessage(draft)}
            onAttach={setAttachment}
            onClearAttachment={() => setAttachment(null)}
            onSelectSuggestion={(value) => void sendMessage(value)}
            onNavigate={handleNavigate}
            onConfirm={(confirmationId, approved) => void handleConfirm(confirmationId, approved)}
            onClose={onClose}
            onExpand={fullPage ? undefined : () => router.push(`/${role}/assistant`)}
        />
    );
}
