"use client";

import { useEffect, useState } from "react";

/**
 * Guided demo tour using pure CSS + JS.
 * No external dependencies - lightweight overlay-based product tour.
 *
 * Usage:
 *   <GuidedTour steps={tourSteps} storageKey="admin-tour" />
 */

export type TourStep = {
    target: string;
    title: string;
    description: string;
    position?: "top" | "bottom" | "left" | "right";
};

/* Role-specific tour configs */

export const adminTourSteps: TourStep[] = [
    { target: "[href='/admin/setup-wizard']", title: "Setup Wizard", description: "Start here. Set up your school in minutes with the guided wizard." },
    { target: "[href='/admin/dashboard']", title: "Dashboard", description: "Monitor your school's KPIs - attendance, AI usage, and complaints at a glance." },
    { target: "[href='/admin/users']", title: "User management", description: "Add, remove, and manage teachers, students, and parents. Link parents to children." },
    { target: "[href='/admin/classes']", title: "Classes and subjects", description: "Create classes, assign subjects, and organize your academic structure." },
    { target: "[href='/admin/ai-usage']", title: "AI analytics", description: "Track how AI is being used - who is asking questions, which subjects are active, and where usage is rising." },
];

export const teacherTourSteps: TourStep[] = [
    { target: "[href='/teacher/dashboard']", title: "Your dashboard", description: "See today's classes, pending assignments, and student activity." },
    { target: "[href='/teacher/attendance']", title: "Attendance", description: "Mark attendance for your classes. Use CSV bulk import for speed." },
    { target: "[href='/teacher/marks']", title: "Marks entry", description: "Enter exam marks individually or upload via CSV." },
    { target: "[href='/teacher/assignments']", title: "Assignments", description: "Create and manage assignments for your classes." },
    { target: "[href='/teacher/doubt-heatmap']", title: "Doubt heatmap", description: "See which topics students struggle with most using classroom and AI signals." },
];

export const studentTourSteps: TourStep[] = [
    { target: "[href='/student/overview']", title: "Your overview", description: "See your attendance, marks, and login streak at a glance." },
    { target: "[href='/student/ai-studio']", title: "AI study studio", description: "Use one grounded learning workspace for chat, quizzes, flashcards, and mind maps." },
    { target: "[href='/student/attendance']", title: "Attendance", description: "Track your daily attendance across all classes." },
    { target: "[href='/student/results']", title: "Results", description: "View your exam results and performance trends." },
];

export const parentTourSteps: TourStep[] = [
    { target: "[href='/parent/dashboard']", title: "Child overview", description: "See your child's attendance, marks, and recent activity." },
    { target: "[href='/parent/attendance']", title: "Attendance", description: "Check your child's attendance history." },
    { target: "[href='/parent/results']", title: "Results", description: "View exam results and download report cards." },
];

/* Tour component */

export default function GuidedTour({
    steps,
    storageKey = "vidyaos-tour",
}: {
    steps: TourStep[];
    storageKey?: string;
}) {
    const [currentStep, setCurrentStep] = useState(-1);
    const [mounted, setMounted] = useState(false);
    const [showButton, setShowButton] = useState(false);

    useEffect(() => {
        queueMicrotask(() => {
            setMounted(true);
            setShowButton(!localStorage.getItem(storageKey));
        });

        const handleStartTour = () => {
            setCurrentStep(0);
            setShowButton(false);
        };

        window.addEventListener("start-guided-tour", handleStartTour);
        return () => window.removeEventListener("start-guided-tour", handleStartTour);
    }, [storageKey]);

    const isActive = currentStep >= 0 && currentStep < steps.length;
    const step = isActive ? steps[currentStep] : null;

    let position = { top: 0, left: 0, width: 0, height: 0 };
    if (step && typeof window !== "undefined") {
        const el = document.querySelector(step.target);
        if (el) {
            const rect = el.getBoundingClientRect();
            position = {
                top: rect.top + window.scrollY,
                left: rect.left + window.scrollX,
                width: rect.width,
                height: rect.height,
            };
        }
    }

    const startTour = () => {
        setCurrentStep(0);
    };

    const nextStep = () => {
        if (currentStep < steps.length - 1) {
            setCurrentStep(currentStep + 1);
        } else {
            endTour();
        }
    };

    const endTour = () => {
        setCurrentStep(-1);
        localStorage.setItem(storageKey, "completed");
    };

    if (!mounted) return null;
    if (!showButton && !isActive) return null;

    return (
        <>
            {!isActive && showButton && (
                <button
                    onClick={startTour}
                    className="fixed right-4 z-40 flex items-center gap-2 rounded-full bg-[var(--primary)] px-4 py-2.5 text-sm font-medium text-white shadow-lg transition-all hover:scale-105 hover:shadow-xl fab-layer-2"
                    style={{ bottom: "var(--fab-offset)" }}
                >
                    Take a Tour
                </button>
            )}

            {isActive && step && (
                <>
                    <div
                        className="fixed inset-0 z-[9998] bg-black/50 transition-opacity"
                        onClick={endTour}
                    />

                    <div
                        className="fixed z-[9999] rounded-lg ring-4 ring-[var(--primary)] ring-offset-2 transition-all duration-300 pointer-events-none"
                        style={{
                            top: position.top - 4,
                            left: position.left - 4,
                            width: position.width + 8,
                            height: position.height + 8,
                        }}
                    />

                    <div
                        className="fixed z-[10000] max-w-xs rounded-xl border border-[var(--border)] bg-[var(--bg-card)] p-5 shadow-2xl transition-all duration-300"
                        style={{
                            top: position.top + position.height + 16,
                            left: Math.max(16, position.left),
                        }}
                    >
                        <div className="mb-2 flex items-center justify-between">
                            <h3 className="text-sm font-bold text-[var(--text-primary)]">{step.title}</h3>
                            <span className="text-[10px] text-[var(--text-muted)]">
                                {currentStep + 1}/{steps.length}
                            </span>
                        </div>
                        <p className="mb-4 text-xs leading-relaxed text-[var(--text-secondary)]">
                            {step.description}
                        </p>
                        <div className="flex items-center justify-between">
                            <button
                                onClick={endTour}
                                className="text-xs text-[var(--text-muted)] transition-colors hover:text-[var(--text-secondary)]"
                            >
                                Skip Tour
                            </button>
                            <button
                                onClick={nextStep}
                                className="rounded-lg bg-[var(--primary)] px-4 py-1.5 text-xs font-medium text-white transition-colors hover:bg-[var(--primary-hover)]"
                            >
                                {currentStep === steps.length - 1 ? "Finish" : "Next ->"}
                            </button>
                        </div>
                    </div>
                </>
            )}
        </>
    );
}
