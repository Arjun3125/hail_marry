"use client";

import { FileQuestion, Upload, BookOpen, BarChart3, MessageSquare } from "lucide-react";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
    icon?: LucideIcon;
    title: string;
    description: string;
    eyebrow?: string;
    scopeNote?: string;
    action?: {
        label: string;
        href: string;
    };
    secondaryAction?: {
        label: string;
        href: string;
    };
    className?: string;
}

export default function EmptyState({
    icon: Icon = FileQuestion,
    title,
    description,
    eyebrow = "No records yet",
    scopeNote,
    action,
    secondaryAction,
    className,
}: EmptyStateProps) {
    return (
        <div className={cn("prism-empty-shell", className)}>
            <div className="prism-empty-icon">
                <Icon className="h-7 w-7 text-[var(--text-secondary)]" />
            </div>
            <span className="prism-empty-eyebrow">{eyebrow}</span>
            <h3 className="mt-3 text-lg font-semibold text-[var(--text-primary)]">{title}</h3>
            <p className="mt-2 max-w-md text-sm leading-6 text-[var(--text-muted)]">{description}</p>
            {scopeNote ? <p className="prism-empty-scope mt-3 max-w-lg text-xs leading-5 text-[var(--text-secondary)]">{scopeNote}</p> : null}
            {(action || secondaryAction) ? (
                <div className="prism-empty-actions mt-5">
                    {action ? (
                        <a
                            href={action.href}
                            className="prism-action"
                        >
                            {action.label}
                        </a>
                    ) : null}
                    {secondaryAction ? (
                        <a
                            href={secondaryAction.href}
                            className="prism-action-secondary"
                        >
                            {secondaryAction.label}
                        </a>
                    ) : null}
                </div>
            ) : null}
        </div>
    );
}

/** Preset empty states for common pages */
export const emptyPresets = {
    noDocuments: {
        icon: Upload,
        title: "No documents yet",
        description: "Upload your first study material to begin grounded study and revision.",
        action: { label: "Upload Document", href: "/student/upload" },
    },
    noResults: {
        icon: BarChart3,
        title: "No results available",
        description: "Results will appear here once your exams are graded.",
    },
    noAttendance: {
        icon: BookOpen,
        title: "No attendance records",
        description: "Attendance will be tracked once your classes begin.",
    },
    noComplaints: {
        icon: MessageSquare,
        title: "No complaints filed",
        description: "This is a good sign! Submit a complaint if you need help.",
    },
} as const;
