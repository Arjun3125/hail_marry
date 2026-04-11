"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import {
    ArrowLeft,
    ArrowRight,
    BookOpen,
    CheckCircle2,
    ClipboardList,
    Database,
    School,
    Sparkles,
    Users,
} from "lucide-react";

import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

const STEPS = [
    {
        id: "identity",
        label: "School Identity",
        icon: School,
        summary: "Name the institution and set the curriculum context.",
    },
    {
        id: "structure",
        label: "Grade + Section Structure",
        icon: BookOpen,
        summary: "Define the grade and section shape before adding people.",
    },
    {
        id: "assignments",
        label: "Subject + Teacher Assignment",
        icon: Users,
        summary: "Map subjects to accountable teachers for daily workflows.",
    },
    {
        id: "start-mode",
        label: "Demo Data or Fresh Start",
        icon: Database,
        summary: "Choose whether this environment starts as a sales demo or a real school.",
    },
    {
        id: "first-action",
        label: "First Action",
        icon: ClipboardList,
        summary: "Pick the first operational task after setup.",
    },
] as const;

type SetupDraft = {
    schoolName?: string;
    board?: string;
    structure?: string;
    subjectMap?: string;
    startMode?: "demo" | "fresh";
    firstAction?: string;
};

const DEFAULT_SETUP = {
    schoolName: "Vidya Public School",
    board: "CBSE",
    structure: "Class 8A, Class 9A, Class 10A",
    subjectMap: "Science -> Mr. Sharma\nMaths -> Ms. Iyer",
    startMode: "demo" as const,
    firstAction: "/admin/dashboard",
};

function readSetupDraft(): SetupDraft | null {
    if (typeof window === "undefined") return null;
    const saved = window.localStorage.getItem("vidyaos-admin-setup-draft");
    if (!saved) return null;
    try {
        return JSON.parse(saved) as SetupDraft;
    } catch {
        return null;
    }
}

export default function SetupWizard() {
    const [initialDraft] = useState<SetupDraft | null>(() => readSetupDraft());
    const hasSavedDraft = Boolean(initialDraft && (
        initialDraft.schoolName !== DEFAULT_SETUP.schoolName || initialDraft.board !== DEFAULT_SETUP.board
    ));
    const [step, setStep] = useState(0);
    const [schoolName, setSchoolName] = useState(initialDraft?.schoolName || DEFAULT_SETUP.schoolName);
    const [board, setBoard] = useState(initialDraft?.board || DEFAULT_SETUP.board);
    const [structure, setStructure] = useState(initialDraft?.structure || DEFAULT_SETUP.structure);
    const [subjectMap, setSubjectMap] = useState(initialDraft?.subjectMap || DEFAULT_SETUP.subjectMap);
    const [startMode, setStartMode] = useState<"demo" | "fresh">(initialDraft?.startMode || DEFAULT_SETUP.startMode);
    const [firstAction, setFirstAction] = useState(initialDraft?.firstAction || DEFAULT_SETUP.firstAction);
    const [showResumePrompt, setShowResumePrompt] = useState(hasSavedDraft);
    const [hasDraft, setHasDraft] = useState(hasSavedDraft);
    const currentStep = STEPS[step];
    const progressPercent = Math.round(((step + 1) / STEPS.length) * 100);

    const setupSnapshot = useMemo(
        () => ({
            schoolName,
            board,
            structure,
            subjectMap,
            startMode,
            firstAction,
            completedAt: step === STEPS.length - 1 ? new Date().toISOString() : null,
        }),
        [board, firstAction, schoolName, startMode, step, structure, subjectMap],
    );

    useEffect(() => {
        if (typeof window === "undefined") return;
        window.localStorage.setItem("vidyaos-admin-setup-draft", JSON.stringify(setupSnapshot));
        window.localStorage.setItem(
            "mascotPageContext",
            JSON.stringify({
                route: "/admin/setup-wizard",
                current_page_entity: "setup_step",
                current_page_entity_id: currentStep.id,
                metadata: {
                    setup_step: currentStep.id,
                    setup_progress: progressPercent,
                    start_mode: startMode,
                },
            }),
        );
    }, [currentStep.id, progressPercent, setupSnapshot, startMode]);

    const goNext = () => setStep((value) => Math.min(STEPS.length - 1, value + 1));
    const goBack = () => setStep((value) => Math.max(0, value - 1));
    const resetDraft = () => {
        if (typeof window === "undefined") return;
        window.localStorage.removeItem("vidyaos-admin-setup-draft");
        setStep(0);
        setSchoolName(DEFAULT_SETUP.schoolName);
        setBoard(DEFAULT_SETUP.board);
        setStructure(DEFAULT_SETUP.structure);
        setSubjectMap(DEFAULT_SETUP.subjectMap);
        setStartMode(DEFAULT_SETUP.startMode);
        setFirstAction(DEFAULT_SETUP.firstAction);
        setHasDraft(false);
        setShowResumePrompt(false);
    };

    return (
        <PrismPage variant="workspace" className="mx-auto max-w-7xl space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Admin first-run setup
                        </PrismHeroKicker>
                    )}
                    title="Set up the institution in five focused steps"
                    description="This follows the transformation plan exactly: identity, class structure, subject ownership, demo or fresh start, and the first action."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Time target</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Each step is designed to take under 2 minutes. Detailed imports still live in Users, Classes, and Timetable after this first-run path.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Current step</span>
                        <span className="prism-status-value">{step + 1} / {STEPS.length}</span>
                        <span className="prism-status-detail">{currentStep.label}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Start mode</span>
                        <span className="prism-status-value">{startMode === "demo" ? "Demo" : "Fresh"}</span>
                        <span className="prism-status-detail">{startMode === "demo" ? "Seeded demo story for sales." : "Blank operational workspace."}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Progress</span>
                        <span className="prism-status-value">{progressPercent}%</span>
                        <span className="prism-status-detail">Draft saved locally for this setup session.</span>
                    </div>
                </div>
            </PrismSection>

            <PrismPanel className="p-5">
                <div className="relative h-2 overflow-hidden rounded-full bg-[rgba(148,163,184,0.12)]">
                    <div
                        className="absolute inset-y-0 left-0 rounded-full bg-[linear-gradient(90deg,rgba(139,92,246,0.96),rgba(96,165,250,0.94))]"
                        style={{ width: `${progressPercent}%` }}
                    />
                </div>
                <div className="mt-5 grid gap-3 md:grid-cols-5">
                    {STEPS.map((item, index) => {
                        const Icon = item.icon;
                        const isActive = index === step;
                        const isPast = index < step;
                        return (
                            <button
                                key={item.id}
                                type="button"
                                onClick={() => setStep(index)}
                                className={`rounded-2xl border px-3 py-3 text-left transition ${
                                    isActive
                                        ? "border-[rgba(139,92,246,0.42)] bg-[rgba(139,92,246,0.12)]"
                                        : isPast
                                          ? "border-[rgba(16,185,129,0.24)] bg-[rgba(16,185,129,0.08)]"
                                          : "border-[var(--border)] bg-[rgba(148,163,184,0.04)]"
                                }`}
                            >
                                <div className="flex items-center gap-3">
                                    <div className={`flex h-9 w-9 items-center justify-center rounded-xl ${isPast ? "bg-success-subtle text-status-emerald" : "bg-[rgba(148,163,184,0.08)] text-[var(--text-secondary)]"}`}>
                                        {isPast ? <CheckCircle2 className="h-4 w-4" /> : <Icon className="h-4 w-4" />}
                                    </div>
                                    <div className="min-w-0">
                                        <p className="text-[10px] font-semibold uppercase tracking-[0.18em] text-[var(--text-muted)]">Step {index + 1}</p>
                                        <p className="truncate text-sm font-semibold text-[var(--text-primary)]">{item.label}</p>
                                    </div>
                                </div>
                            </button>
                        );
                    })}
                </div>
            </PrismPanel>

            <PrismPanel className="min-h-[28rem] p-6 sm:p-8">
                <div className="mb-6">
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{currentStep.label}</p>
                    <h2 className="mt-2 text-3xl font-black text-[var(--text-primary)]">{currentStep.summary}</h2>
                </div>

                {currentStep.id === "identity" ? (
                    <SetupFields>
                        <label className="space-y-2">
                            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Institution name</span>
                            <input value={schoolName} onChange={(event) => setSchoolName(event.target.value)} className="prism-input w-full" />
                        </label>
                        <label className="space-y-2">
                            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Curriculum board</span>
                            <select value={board} onChange={(event) => setBoard(event.target.value)} className="prism-select w-full">
                                <option>CBSE</option>
                                <option>ICSE</option>
                                <option>State Board</option>
                                <option>IB</option>
                            </select>
                        </label>
                    </SetupFields>
                ) : null}

                {currentStep.id === "structure" ? (
                    <SetupFields>
                        <label className="space-y-2 md:col-span-2">
                            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Grades and sections</span>
                            <textarea value={structure} onChange={(event) => setStructure(event.target.value)} className="prism-input min-h-32 w-full" />
                        </label>
                        <Link href="/admin/classes" className="prism-action-secondary md:col-span-2">Open detailed class manager</Link>
                    </SetupFields>
                ) : null}

                {currentStep.id === "assignments" ? (
                    <SetupFields>
                        <label className="space-y-2 md:col-span-2">
                            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Subject to teacher map</span>
                            <textarea value={subjectMap} onChange={(event) => setSubjectMap(event.target.value)} className="prism-input min-h-40 w-full font-mono" />
                        </label>
                        <Link href="/admin/users" className="prism-action-secondary">Import teachers</Link>
                        <Link href="/admin/timetable" className="prism-action-secondary">Map timetable</Link>
                    </SetupFields>
                ) : null}

                {currentStep.id === "start-mode" ? (
                    <div className="grid gap-4 md:grid-cols-2">
                        <ModeCard
                            title="Use demo data"
                            detail="Best for sales walkthroughs with seeded students, parents, AI activity, and operational risk."
                            active={startMode === "demo"}
                            onClick={() => setStartMode("demo")}
                        />
                        <ModeCard
                            title="Fresh start"
                            detail="Best for a real school rollout where admins will import live rosters and configure operations."
                            active={startMode === "fresh"}
                            onClick={() => setStartMode("fresh")}
                        />
                    </div>
                ) : null}

                {currentStep.id === "first-action" ? (
                    <div className="space-y-5">
                        <div className="grid gap-3 md:grid-cols-3">
                            <ActionChoice label="View school health" href="/admin/dashboard" active={firstAction === "/admin/dashboard"} onClick={() => setFirstAction("/admin/dashboard")} />
                            <ActionChoice label="Import users" href="/admin/users" active={firstAction === "/admin/users"} onClick={() => setFirstAction("/admin/users")} />
                            <ActionChoice label="Create timetable" href="/admin/timetable" active={firstAction === "/admin/timetable"} onClick={() => setFirstAction("/admin/timetable")} />
                        </div>
                        <div className="rounded-[1.5rem] border border-[var(--success)]/25 bg-success-subtle p-5">
                            <p className="flex items-center gap-2 text-sm font-semibold text-[var(--success)]">
                                <CheckCircle2 className="h-4 w-4" />
                                Setup path ready for {schoolName || "this institution"}
                            </p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Mode: {startMode === "demo" ? "demo data" : "fresh start"} • Board: {board} • First action is selected below.
                            </p>
                            <Link href={firstAction} className="mt-4 inline-flex items-center gap-2 rounded-2xl bg-[var(--success)] px-5 py-3 text-sm font-bold text-[#06101e]">
                                Continue to first action
                                <ArrowRight className="h-4 w-4" />
                            </Link>
                        </div>
                    </div>
                ) : null}
            </PrismPanel>

            <div className="flex justify-between gap-3">
                <div className="flex gap-2">
                    <button
                        type="button"
                        onClick={goBack}
                        disabled={step === 0}
                        className="inline-flex items-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-5 py-3 text-sm font-semibold text-[var(--text-secondary)] transition disabled:pointer-events-none disabled:opacity-30"
                    >
                        <ArrowLeft className="h-4 w-4" />
                        Back
                    </button>
                    {hasDraft && (
                        <button
                            type="button"
                            onClick={resetDraft}
                            className="inline-flex items-center gap-2 rounded-2xl border border-amber-500/20 bg-amber-500/6 px-5 py-3 text-sm font-semibold text-status-amber transition hover:bg-amber-500/10"
                        >
                            Start fresh
                        </button>
                    )}
                </div>
                <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
                    <CheckCircle2 className="h-3.5 w-3.5 text-status-emerald" />
                    <span>Auto-saving progress</span>
                </div>
                {step < STEPS.length - 1 ? (
                    <button
                        type="button"
                        onClick={goNext}
                        className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(139,92,246,0.96),rgba(96,165,250,0.94))] px-5 py-3 text-sm font-semibold text-white transition hover:-translate-y-0.5"
                    >
                        Next step
                        <ArrowRight className="h-4 w-4" />
                    </button>
                ) : null}
            </div>

            {/* Resume prompt modal */}
            {showResumePrompt && (
                <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm">
                    <div className="w-full max-w-md rounded-3xl border border-[var(--border)] bg-[primary-surface] shadow-[0_20px_60px_rgba(0,0,0,0.3)]">
                        <div className="space-y-5 p-6">
                            <div>
                                <p className="text-sm font-semibold text-[var(--text-muted)]">Welcome back!</p>
                                <h3 className="mt-2 text-xl font-bold text-[var(--text-primary)]">
                                    Continue setup for <span className="text-[var(--primary)]">{schoolName}</span>?
                                </h3>
                            </div>

                            <div className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--text-muted)]">Your progress</p>
                                <p className="mt-2 flex items-baseline gap-2">
                                    <span className="text-3xl font-black text-[var(--text-primary)]">{progressPercent}%</span>
                                    <span className="text-sm text-[var(--text-secondary)]">complete</span>
                                </p>
                                <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
                                    You were on &quot;<span className="font-semibold">{currentStep.label}</span>&quot; ({step + 1} of {STEPS.length} steps).
                                </p>
                            </div>

                            <div className="flex gap-3">
                                <button
                                    onClick={() => setShowResumePrompt(false)}
                                    className="flex-1 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.07)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)] transition hover:bg-[rgba(148,163,184,0.12)]"
                                >
                                    Continue
                                </button>
                                <button
                                    onClick={resetDraft}
                                    className="flex-1 rounded-2xl border border-amber-500/20 bg-amber-500/6 px-4 py-3 text-sm font-semibold text-status-amber transition hover:bg-amber-500/10"
                                >
                                    Start fresh
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            )}
        </PrismPage>
    );
}

function SetupFields({ children }: { children: React.ReactNode }) {
    return <div className="grid gap-5 md:grid-cols-2">{children}</div>;
}

function ModeCard({ title, detail, active, onClick }: { title: string; detail: string; active: boolean; onClick: () => void }) {
    return (
        <button
            type="button"
            onClick={onClick}
            className={`rounded-[1.5rem] border p-5 text-left transition ${
                active ? "border-[rgba(139,92,246,0.48)] bg-[rgba(139,92,246,0.14)]" : "border-[var(--border)] bg-[rgba(148,163,184,0.05)]"
            }`}
        >
            <p className="text-lg font-bold text-[var(--text-primary)]">{title}</p>
            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p>
        </button>
    );
}

function ActionChoice({ label, href, active, onClick }: { label: string; href: string; active: boolean; onClick: () => void }) {
    return (
        <button
            type="button"
            onClick={onClick}
            className={`rounded-[1.25rem] border px-4 py-3 text-left text-sm font-semibold transition ${
                active ? "border-[var(--success)]/40 bg-success-subtle text-[var(--success)]" : "border-[var(--border)] bg-[rgba(148,163,184,0.05)] text-[var(--text-primary)]"
            }`}
        >
            {label}
            <span className="mt-1 block text-[10px] font-medium text-[var(--text-muted)]">{href}</span>
        </button>
    );
}
