"use client";

import { useState, useEffect } from "react";

/**
 * Guided demo tour using pure CSS + JS.
 * No external dependencies — lightweight overlay-based product tour.
 *
 * Usage:
 *   <GuidedTour steps={tourSteps} storageKey="admin-tour" />
 */

export type TourStep = {
    target: string; // CSS selector
    title: string;
    description: string;
    position?: "top" | "bottom" | "left" | "right";
};

/* ─── Role-specific tour configs ─── */

export const adminTourSteps: TourStep[] = [
    { target: "[href='/admin/setup-wizard']", title: "Setup Wizard", description: "Start here! Set up your school in minutes with the guided wizard." },
    { target: "[href='/admin/dashboard']", title: "Dashboard", description: "Monitor your school's KPIs — attendance, AI usage, and complaints at a glance." },
    { target: "[href='/admin/users']", title: "User Management", description: "Add, remove, and manage teachers, students, and parents. Link parents to children." },
    { target: "[href='/admin/classes']", title: "Classes & Subjects", description: "Create classes, assign subjects, and organize your academic structure." },
    { target: "[href='/admin/ai-usage']", title: "AI Analytics", description: "Track how AI is being used — who's asking questions, which subjects, and usage patterns." },
];

export const teacherTourSteps: TourStep[] = [
    { target: "[href='/teacher/dashboard']", title: "Your Dashboard", description: "See today's classes, pending assignments, and student activity." },
    { target: "[href='/teacher/attendance']", title: "Attendance", description: "Mark attendance for your classes. Use CSV bulk import for speed." },
    { target: "[href='/teacher/marks']", title: "Marks Entry", description: "Enter exam marks individually or upload via CSV." },
    { target: "[href='/teacher/assignments']", title: "Assignments", description: "Create and manage assignments for your classes." },
    { target: "[href='/teacher/doubts']", title: "Doubt Heatmap", description: "See which topics students struggle with most — powered by AI analysis." },
];

export const studentTourSteps: TourStep[] = [
    { target: "[href='/student/overview']", title: "Your Overview", description: "See your attendance, marks, and login streak at a glance." },
    { target: "[href='/student/ai']", title: "AI Study Assistant", description: "Ask questions about your subjects — get grounded answers with citations." },
    { target: "[href='/student/attendance']", title: "Attendance", description: "Track your daily attendance across all classes." },
    { target: "[href='/student/results']", title: "Results", description: "View your exam results and performance trends." },
];

export const parentTourSteps: TourStep[] = [
    { target: "[href='/parent/dashboard']", title: "Child Overview", description: "See your child's attendance, marks, and recent activity." },
    { target: "[href='/parent/attendance']", title: "Attendance", description: "Check your child's attendance history." },
    { target: "[href='/parent/results']", title: "Results", description: "View exam results and download report cards." },
];

/* ─── Tour component ─── */

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

    // Only read localStorage after mounting on client to avoid hydration mismatch
    useEffect(() => {
        setMounted(true);
        setShowButton(!localStorage.getItem(storageKey));
    }, [storageKey]);

    const isActive = currentStep >= 0 && currentStep < steps.length;
    const step = isActive ? steps[currentStep] : null;

    // Calculate position synchronously during render (no setState in effect)
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

    // Don't render anything until mounted on client
    if (!mounted) return null;
    if (!showButton && !isActive) return null;

    return (
        <>
            {/* Start Tour button */}
            {!isActive && showButton && (
                <button
                    onClick={startTour}
                    className="fixed right-4 z-40 flex items-center gap-2 px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-full shadow-lg hover:shadow-xl transition-all hover:scale-105"
                    style={{ bottom: "calc(var(--bottom-nav-height, 4.5rem) + 4rem)" }}
                >
                    ✨ Take a Tour
                </button>
            )}

            {/* Tour overlay */}
            {isActive && step && (
                <>
                    {/* Backdrop */}
                    <div
                        className="fixed inset-0 z-[9998] bg-black/50 transition-opacity"
                        onClick={endTour}
                    />

                    {/* Spotlight */}
                    <div
                        className="fixed z-[9999] rounded-lg ring-4 ring-[var(--primary)] ring-offset-2 transition-all duration-300 pointer-events-none"
                        style={{
                            top: position.top - 4,
                            left: position.left - 4,
                            width: position.width + 8,
                            height: position.height + 8,
                        }}
                    />

                    {/* Tooltip */}
                    <div
                        className="fixed z-[10000] bg-[var(--bg-card)] rounded-xl shadow-2xl border border-[var(--border)] p-5 max-w-xs transition-all duration-300"
                        style={{
                            top: position.top + position.height + 16,
                            left: Math.max(16, position.left),
                        }}
                    >
                        <div className="flex items-center justify-between mb-2">
                            <h3 className="text-sm font-bold text-[var(--text-primary)]">{step.title}</h3>
                            <span className="text-[10px] text-[var(--text-muted)]">
                                {currentStep + 1}/{steps.length}
                            </span>
                        </div>
                        <p className="text-xs text-[var(--text-secondary)] mb-4 leading-relaxed">
                            {step.description}
                        </p>
                        <div className="flex items-center justify-between">
                            <button
                                onClick={endTour}
                                className="text-xs text-[var(--text-muted)] hover:text-[var(--text-secondary)] transition-colors"
                            >
                                Skip Tour
                            </button>
                            <button
                                onClick={nextStep}
                                className="px-4 py-1.5 bg-[var(--primary)] text-white text-xs font-medium rounded-lg hover:bg-[var(--primary-hover)] transition-colors"
                            >
                                {currentStep === steps.length - 1 ? "Finish" : "Next →"}
                            </button>
                        </div>
                    </div>
                </>
            )}
        </>
    );
}
