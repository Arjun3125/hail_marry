"use client";

import { FileQuestion, Upload, BookOpen, BarChart3, MessageSquare } from "lucide-react";
import { LucideIcon } from "lucide-react";

interface EmptyStateProps {
    icon?: LucideIcon;
    title: string;
    description: string;
    action?: {
        label: string;
        href: string;
    };
}

export default function EmptyState({
    icon: Icon = FileQuestion,
    title,
    description,
    action,
}: EmptyStateProps) {
    return (
        <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
            <div className="w-16 h-16 rounded-2xl bg-[var(--bg-hover)] flex items-center justify-center mb-4">
                <Icon className="w-7 h-7 text-[var(--text-muted)]" />
            </div>
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-1">{title}</h3>
            <p className="text-sm text-[var(--text-muted)] max-w-xs mb-4">{description}</p>
            {action && (
                <a
                    href={action.href}
                    className="inline-flex items-center gap-2 px-4 py-2.5 bg-[var(--primary)] text-white text-sm font-medium rounded-lg hover:bg-[var(--primary-hover)] transition-colors shadow-sm"
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
