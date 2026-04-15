"use client";

import { Suspense, useEffect, useMemo, useState } from "react";
import { useSearchParams } from "next/navigation";
import dynamic from "next/dynamic";
import { useVidyaContext } from "@/providers/VidyaContextProvider";
import { useLanguage } from "@/i18n/LanguageProvider";
import {
    BookMarked,
    Bot,
    Command,
    PanelsTopLeft,
    Sparkles,
    Target,
} from "lucide-react";

import { ToolRail } from "./components/ToolRail";
import { LearningWorkspace } from "./components/LearningWorkspace";
import { NotebookSelector } from "./components/NotebookSelector";
import { SessionSummaryModal, type SessionSummaryData } from "./components/SessionSummaryModal";
import { useKeyboardShortcuts } from "./hooks/useKeyboardShortcuts";
import { useSessionInactivity } from "./hooks/useSessionInactivity";
import { api } from "@/lib/api";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
} from "@/components/prism/PrismPage";
import "./ai-studio.css";

const ContextPanel = dynamic(
    () => import("./components/ContextPanel").then((mod) => mod.ContextPanel),
    {
        loading: () => <div className="p-4 text-xs text-[var(--text-muted)]">Loading context...</div>,
    },
);

const FocusMode = dynamic(
    () => import("./components/FocusMode").then((mod) => mod.FocusMode),
    {
        loading: () => null,
    },
);

const validTools = new Set([
    "qa",
    "study_guide",
    "socratic",
    "quiz",
    "flashcards",
    "perturbation",
    "debate",
    "essay_review",
    "mindmap",
    "flowchart",
    "concept_map",
]);

// Tool details now reference i18n keys
const toolDetails = {
    qa: { labelKey: "ai_studio.tools.qa.title", summaryKey: "ai_studio.tools.qa.summary" },
    study_guide: { labelKey: "ai_studio.tools.study_guide.title", summaryKey: "ai_studio.tools.study_guide.summary" },
    socratic: { labelKey: "ai_studio.tools.socratic.title", summaryKey: "ai_studio.tools.socratic.summary" },
    quiz: { labelKey: "ai_studio.tools.quiz.title", summaryKey: "ai_studio.tools.quiz.summary" },
    flashcards: { labelKey: "ai_studio.tools.flashcards.title", summaryKey: "ai_studio.tools.flashcards.summary" },
    perturbation: { labelKey: "ai_studio.tools.perturbation.title", summaryKey: "ai_studio.tools.perturbation.summary" },
    debate: { labelKey: "ai_studio.tools.debate.title", summaryKey: "ai_studio.tools.debate.summary" },
    essay_review: { labelKey: "ai_studio.tools.essay_review.title", summaryKey: "ai_studio.tools.essay_review.summary" },
    mindmap: { labelKey: "ai_studio.tools.mindmap.title", summaryKey: "ai_studio.tools.mindmap.summary" },
    flowchart: { labelKey: "ai_studio.tools.flowchart.title", summaryKey: "ai_studio.tools.flowchart.summary" },
    concept_map: { labelKey: "ai_studio.tools.concept_map.title", summaryKey: "ai_studio.tools.concept_map.summary" },
} as const;

// Intent options now with i18n keys
const intentOptionsConfig = [
    {
        id: "understand_topic",
        labelKey: "ai_studio.intents.understand_topic.label",
        descriptionKey: "ai_studio.intents.understand_topic.description",
        tool: "qa",
    },
    {
        id: "practice_test",
        labelKey: "ai_studio.intents.practice_test.label",
        descriptionKey: "ai_studio.intents.practice_test.description",
        tool: "quiz",
    },
    {
        id: "review_weak_areas",
        labelKey: "ai_studio.intents.review_weak_areas.label",
        descriptionKey: "ai_studio.intents.review_weak_areas.description",
        tool: "flashcards",
    },
    {
        id: "homework_help",
        labelKey: "ai_studio.intents.homework_help.label",
        descriptionKey: "ai_studio.intents.homework_help.description",
        tool: "socratic",
    },
] as const;

type IntentId = (typeof intentOptionsConfig)[number]["id"];

function normalizeTool(rawTool: string | null) {
    if (!rawTool) return null;
    return validTools.has(rawTool) ? rawTool : null;
}

function LoadingFallback() {
    const { t } = useLanguage();
    return (
        <PrismPage className="pb-8">
            <PrismSection>
                <PrismPanel className="flex min-h-[60vh] items-center justify-center p-8 text-sm text-[var(--text-muted)]">
                    {t("ai_studio.loading_studio")}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

export default function AIStudioPage() {
    return (
        <Suspense fallback={<LoadingFallback />}>
            <AIStudioContent />
        </Suspense>
    );
}

function AIStudioContent() {
    const { t } = useLanguage();
    const searchParams = useSearchParams();
    const { activeSubject, mergeContext } = useVidyaContext();
    const [activeTool, setActiveTool] = useState("qa");
    const [railCollapsed, setRailCollapsed] = useState(false);
    const [contextCollapsed, setContextCollapsed] = useState(false);
    const [focusMode, setFocusMode] = useState(false);
    const [activeNotebookId, setActiveNotebookId] = useState<string | null>(null);
    const [showIntentSelector, setShowIntentSelector] = useState(false);
    const [selectedIntent, setSelectedIntent] = useState<IntentId | null>(null);
    const [requestOptions, setRequestOptions] = useState<{
        language?: string;
        responseLength?: string;
        expertiseLevel?: string;
    }>({});
    const [initialExchange, setInitialExchange] = useState<{
        query: string;
        response: {
            answer: string;
            citations: Array<{ source?: string; page?: string | null; url?: string | null; text?: string }>;
            mode: string;
        };
    } | null>(null);

    // Session inactivity tracking
    const [showInactivityModal, setShowInactivityModal] = useState(false);
    const [sessionExchangeCount] = useState(0);
    const [nowMs, setNowMs] = useState(0);
    const [sessionStartTimeMs, setSessionStartTimeMs] = useState(0);

    const handleInactivity = () => {
        setShowInactivityModal(true);
    };

    const { resetTimer } = useSessionInactivity(handleInactivity);

    const searchKey = searchParams.toString();
    const requestedTool = useMemo(
        () => normalizeTool(searchParams.get("tool") || searchParams.get("mode")),
        [searchParams]
    );
    const seedPrompt = useMemo(() => searchParams.get("prompt"), [searchParams]);
    const subjectScope = useMemo(() => searchParams.get("subject") || activeSubject, [activeSubject, searchParams]);

    useEffect(() => {
        const startedAt = window.Date.now();
        const initId = window.setTimeout(() => {
            setNowMs(startedAt);
            setSessionStartTimeMs(startedAt);
        }, 0);
        const tick = window.setInterval(() => setNowMs(window.Date.now()), 1000);
        return () => {
            window.clearTimeout(initId);
            window.clearInterval(tick);
        };
    }, []);

    useEffect(() => {
        queueMicrotask(() => {
            const savedNotebook = localStorage.getItem("activeNotebookId");
            if (savedNotebook) {
                setActiveNotebookId(savedNotebook);
            }

            const savedIntent = localStorage.getItem("student-ai-studio-intent") as IntentId | null;
            if (savedIntent && intentOptionsConfig.some((option) => option.id === savedIntent)) {
                setSelectedIntent(savedIntent);
                const matchedIntent = intentOptionsConfig.find((option) => option.id === savedIntent);
                if (!requestedTool && matchedIntent) {
                    setActiveTool(matchedIntent.tool);
                }
            }

            if (!savedIntent && !requestedTool && !seedPrompt && !searchParams.get("history")) {
                setShowIntentSelector(true);
            }
        });
    }, [requestedTool, searchParams, seedPrompt]);

    useEffect(() => {
        if (activeNotebookId) {
            localStorage.setItem("activeNotebookId", activeNotebookId);
        } else {
            localStorage.removeItem("activeNotebookId");
        }
    }, [activeNotebookId]);

    useEffect(() => {
        queueMicrotask(() => {
            if (requestedTool) {
                setActiveTool(requestedTool);
                setShowIntentSelector(false);
            }

            const notebookId = searchParams.get("notebook_id");
            if (notebookId) {
                setActiveNotebookId(notebookId);
            }

            setRequestOptions((prev) => ({
                language: searchParams.get("language") || prev.language,
                responseLength: searchParams.get("response_length") || prev.responseLength,
                expertiseLevel: searchParams.get("expertise_level") || prev.expertiseLevel,
            }));
        });
    }, [requestedTool, searchKey, searchParams]);

    useEffect(() => {
        mergeContext({
            lastRole: "student",
            activeSubject: subjectScope || null,
            lastAITopic: subjectScope || seedPrompt || null,
        });
    }, [mergeContext, seedPrompt, subjectScope]);

    useEffect(() => {
        const historyId = searchParams.get("history");
        if (!historyId) {
            queueMicrotask(() => {
                setInitialExchange(null);
            });
            return;
        }

        let cancelled = false;
        api.aiHistory
            .get(historyId)
            .then((item) => {
                if (cancelled) return;
                const historyItem = item as { mode?: string; query_text?: string; response_text?: string };
                const historyMode = normalizeTool(historyItem.mode || null);
                if (!requestedTool && historyMode) {
                    setActiveTool(historyMode);
                }
                setShowIntentSelector(false);
                setInitialExchange({
                    query: historyItem.query_text || "",
                    response: {
                        answer: historyItem.response_text || "No response received.",
                        citations: [],
                        mode: historyMode || requestedTool || "qa",
                    },
                });
            })
            .catch(() => {
                if (!cancelled) {
                    setInitialExchange(null);
                }
            });

        return () => {
            cancelled = true;
        };
    }, [requestedTool, searchKey, searchParams]);

    useKeyboardShortcuts({
        onToggleFocus: () => setFocusMode((prev) => !prev),
        onToggleRail: () => setRailCollapsed((prev) => !prev),
        onTogglePanel: () => setContextCollapsed((prev) => !prev),
    });

    const chooseIntent = (intentId: IntentId) => {
        const chosenIntent = intentOptionsConfig.find((option) => option.id === intentId);
        if (!chosenIntent) return;
        setSelectedIntent(intentId);
        setActiveTool(chosenIntent.tool);
        setRailCollapsed(true);
        setShowIntentSelector(false);
        localStorage.setItem("student-ai-studio-intent", intentId);
        setSessionStartTimeMs(nowMs || sessionStartTimeMs);
    };

    const handleContinueSession = () => {
        setShowInactivityModal(false);
        resetTimer();
    };

    const handleEndSession = () => {
        setShowInactivityModal(false);
        // Redirect to dashboard or show session ended message
        window.location.href = "/student/overview";
    };

    const sessionData: SessionSummaryData | null = showInactivityModal
        ? {
              duration: Math.floor(((nowMs || sessionStartTimeMs) - sessionStartTimeMs) / 1000),
              toolUsed: activeTool,
              exchangeCount: sessionExchangeCount,
              topicsExplored: selectedIntent ? [selectedIntent.replace(/_/g, " ")] : [],
          }
        : null;

    const activeToolMeta = toolDetails[activeTool as keyof typeof toolDetails] || toolDetails.qa;
    const activeIntentMeta = selectedIntent ? intentOptionsConfig.find((option) => option.id === selectedIntent) : null;
    const notebookStatus = activeNotebookId
        ? `Notebook linked: ${activeNotebookId.slice(0, 8)}`
        : "All notebooks available";

    return (
        <PrismPage variant="workspace" className="space-y-8 pb-8">
            <PrismSection className="space-y-10">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student AI Workspace
                        </PrismHeroKicker>
                    )}
                    title={t("ai_studio.intent_selector_subtitle")}
                    description="AI Studio now uses a mode-selector entry point so first-time students pick the job they need done before the deeper three-panel workspace appears."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Study posture</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Choose the reason for this session first. The workspace then opens with the right tool, a narrower left rail, and less initial noise.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <Target className="h-4 w-4 text-status-blue" />
                            <span className="prism-status-label">Session intent</span>
                        </div>
                        <p className="prism-status-value">{activeIntentMeta ? t(activeIntentMeta.labelKey) : "Choose an intent"}</p>
                        <p className="prism-status-detail">
                            {activeIntentMeta ? t(activeIntentMeta.descriptionKey) : "Advanced users can skip this, but first-session students should start here."}
                        </p>
                    </div>
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <Bot className="h-4 w-4 text-status-blue" />
                            <span className="prism-status-label">Active mode</span>
                        </div>
                        <p className="prism-status-value">{t(activeToolMeta.labelKey)}</p>
                        <p className="prism-status-detail">{t(activeToolMeta.summaryKey)}</p>
                    </div>
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <BookMarked className="h-4 w-4 text-status-emerald" />
                            <span className="prism-status-label">Notebook scope</span>
                        </div>
                        <p className="prism-status-value">{activeNotebookId ? "Notebook scoped" : "Open scope"}</p>
                        <p className="prism-status-detail">{notebookStatus}</p>
                    </div>
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <BookMarked className="h-4 w-4 text-status-amber" />
                            <span className="prism-status-label">Subject focus</span>
                        </div>
                        <p className="prism-status-value">{subjectScope || "No subject locked"}</p>
                        <p className="prism-status-detail">
                            {subjectScope
                                ? "This subject now persists into assignments and lecture review."
                                : "Open scope remains available until a study workflow narrows it."}
                        </p>
                    </div>
                    <div className="prism-status-item">
                        <div className="flex items-center gap-2">
                            <Command className="h-4 w-4 text-status-violet" />
                            <span className="prism-status-label">Flow controls</span>
                        </div>
                        <p className="prism-status-value">Keyboard ready</p>
                        <p className="prism-status-detail">Use shortcuts for focus mode, tool rail, and context rail once the session is underway.</p>
                    </div>
                </div>

                {showIntentSelector ? (
                    <PrismPanel className="p-10 md:p-12">
                        <div className="mx-auto max-w-3xl text-center">
                            <p className="prism-status-label">Entry point</p>
                            <h2 className="mt-3 text-3xl font-black text-[var(--text-primary)]">{t("ai_studio.intent_selector_title")}</h2>
                            <p className="mt-3 text-sm leading-7 text-[var(--text-secondary)]">
                                Pick one intent and AI Studio will open in the right mode with a calmer starting layout.
                            </p>
                        </div>
                        <div className="mx-auto mt-10 grid max-w-4xl gap-8 md:grid-cols-2">
                            {intentOptionsConfig.map((option) => (
                                <button
                                    key={option.id}
                                    type="button"
                                    onClick={() => chooseIntent(option.id)}
                                    className="vidya-command-card text-left transition-transform duration-[var(--transition-fast)] hover:-translate-y-0.5"
                                >
                                    <p className="prism-status-label">Mode selector</p>
                                    <p className="mt-3 text-xl font-bold text-[var(--text-primary)]">{t(option.labelKey)}</p>
                                    <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">{t(option.descriptionKey)}</p>
                                </button>
                            ))}
                        </div>
                        <div className="mt-6 flex justify-center">
                            <button
                                type="button"
                                onClick={() => setShowIntentSelector(false)}
                                className="prism-action-secondary"
                            >
                                Continue in advanced workspace
                            </button>
                        </div>
                    </PrismPanel>
                ) : (
                    <PrismPanel className="overflow-hidden p-0">
                        <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-8 py-6">
                            <div className="flex flex-wrap items-center gap-3">
                                <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.08)] px-3 py-1.5 text-[11px] font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">
                                    <PanelsTopLeft className="h-3.5 w-3.5" />
                                    Deep Work Layout
                                </div>
                                {activeIntentMeta ? (
                                    <div className="inline-flex items-center gap-2 rounded-full border border-[rgba(79,142,247,0.22)] bg-[rgba(79,142,247,0.08)] px-3 py-1.5 text-xs text-[var(--text-primary)]">
                                        Intent: {t(activeIntentMeta.labelKey)}
                                    </div>
                                ) : null}
                            </div>
                            <button
                                type="button"
                                onClick={() => setShowIntentSelector(true)}
                                className="prism-action-secondary"
                            >
                                Change intent
                            </button>
                        </div>

                        <div className="ai-studio-container">
                            <aside className={`tool-rail ${railCollapsed ? "collapsed" : ""}`}>
                                <NotebookSelector
                                    activeNotebookId={activeNotebookId}
                                    onNotebookChange={setActiveNotebookId}
                                />
                                <ToolRail
                                    activeTool={activeTool}
                                    onToolChange={setActiveTool}
                                    collapsed={railCollapsed}
                                    onToggleCollapse={() => setRailCollapsed(!railCollapsed)}
                                />
                            </aside>

                            <main className="learning-workspace">
                                <LearningWorkspace
                                    key={`${activeTool}:${activeNotebookId ?? "none"}`}
                                    activeTool={activeTool}
                                    notebookId={activeNotebookId}
                                    requestOptions={requestOptions}
                                    initialExchange={initialExchange}
                                    seedPrompt={seedPrompt}
                                />
                            </main>

                            <aside className={`context-panel ${contextCollapsed ? "collapsed" : ""}`}>
                                <ContextPanel
                                    collapsed={contextCollapsed}
                                    onToggleCollapse={() => setContextCollapsed(!contextCollapsed)}
                                    notebookId={activeNotebookId}
                                    activeTool={activeTool}
                                />
                            </aside>
                        </div>
                    </PrismPanel>
                )}

                {focusMode ? <FocusMode onExit={() => setFocusMode(false)} activeTool={activeTool} /> : null}

                <SessionSummaryModal
                    isOpen={showInactivityModal}
                    sessionData={sessionData}
                    onContinue={handleContinueSession}
                    onEnd={handleEndSession}
                />
            </PrismSection>
        </PrismPage>
    );
}
