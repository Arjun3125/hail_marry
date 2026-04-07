"use client";

import { FileQuestion, Upload, BookOpen, BarChart3, MessageSquare } from "lucide-react";
import { LucideIcon } from "lucide-react";
import { cn } from "@/lib/utils";

interface EmptyStateProps {
    icon?: LucideIcon;
    title: string;
    description: string;
    eyebrow?: string;
    action?: {
        label: string;
        href: string;
    };
    className?: string;
}

export default function EmptyState({
    icon: Icon = FileQuestion,
    title,
    description,
    eyebrow = "Nothing here yet",
    action,
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
            {action && (
                <a
                    href={action.href}
                    className="prism-action mt-5"
                >
                    {action.label}
                </a>
            )}
        </div>
    );
}

/** Preset empty states for common pages */
export const emptyPresets = {
    noDocuments: {
        icon: Upload,
        title: "No documents yet",
        description: "Upload your first study material to get started with AI-powered learning.",
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
