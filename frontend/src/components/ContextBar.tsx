"use client";

import { useVidyaContext } from "@/providers/VidyaContextProvider";
import { Bookmark, ChevronRight, Layers3, Sparkles } from "lucide-react";
import { usePathname, useRouter } from "next/navigation";
import { LowDataToggle } from "./LowDataToggle";

type ContextBarItem = {
    label: string;
    href: string;
};

function titleCase(value: string) {
    return value.charAt(0).toUpperCase() + value.slice(1);
}

const roleRoutes = [
    { id: "student", label: "Student", href: "/student/overview" },
    { id: "teacher", label: "Teacher", href: "/teacher/dashboard" },
    { id: "admin", label: "Admin", href: "/admin/dashboard" },
    { id: "parent", label: "Parent", href: "/parent/dashboard" },
];

export function ContextBar({
    role,
    items,
    schoolName = "VidyaOS",
}: {
    role: string;
    items: ContextBarItem[];
    schoolName?: string;
}) {
    const pathname = usePathname();
    const router = useRouter();
    const { activeSubject, activeClassId, activeClassLabel, lastAITopic, lastRole } = useVidyaContext();
    const currentSection =
        [...items]
            .sort((left, right) => right.href.length - left.href.length)
            .find((item) => pathname === item.href || pathname.startsWith(`${item.href}/`))
            ?.label || "Workspace";
    const showWorkflowSignals = !lastRole || lastRole === role;
    const classLabel = showWorkflowSignals ? activeClassLabel || (activeClassId ? `Class ${activeClassId}` : null) : null;
    const subjectLabel = showWorkflowSignals ? activeSubject : null;
    const aiTopicLabel = showWorkflowSignals ? lastAITopic : null;
    const hasSignals = Boolean(classLabel || subjectLabel || aiTopicLabel);

    return (
        <div className="flex flex-col gap-3 rounded-[1.5rem] border border-[var(--border)] bg-[rgba(8,14,28,0.48)] px-4 py-3 shadow-[0_18px_34px_rgba(2,6,23,0.08)] sm:flex-row sm:items-center sm:justify-between">
            <div className="flex flex-wrap items-center gap-1.5 text-[11px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                <span>{schoolName}</span>
                <ChevronRight className="h-3 w-3 opacity-50" />
                <span>{titleCase(role)}</span>
                <ChevronRight className="h-3 w-3 opacity-50" />
                <span className="text-[var(--text-secondary)]">{currentSection}</span>
                <label className="ml-2 inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-3 py-1.5 normal-case tracking-normal text-[var(--text-secondary)]">
                    <span className="text-[10px] uppercase tracking-[0.14em] text-[var(--text-muted)]">Viewing as</span>
                    <select
                        value={role}
                        onChange={(event) => {
                            const nextRole = roleRoutes.find((item) => item.id === event.target.value);
                            if (nextRole) router.push(nextRole.href);
                        }}
                        className="bg-transparent text-xs font-semibold text-[var(--text-primary)] outline-none"
                    >
                        {roleRoutes.map((item) => (
                            <option key={item.id} value={item.id}>
                                {item.label}
                            </option>
                        ))}
                    </select>
                </label>
            </div>

            <div className="flex flex-wrap items-center gap-2 text-xs text-[var(--text-secondary)]">
                {classLabel ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.08)] px-3 py-1.5">
                        <Layers3 className="h-3.5 w-3.5" />
                        {classLabel}
                    </span>
                ) : null}
                {subjectLabel ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-[rgba(79,142,247,0.22)] bg-[rgba(79,142,247,0.08)] px-3 py-1.5 text-[var(--text-primary)]">
                        <Bookmark className="h-3.5 w-3.5" />
                        {subjectLabel}
                    </span>
                ) : null}
                {aiTopicLabel && aiTopicLabel !== subjectLabel ? (
                    <span className="inline-flex items-center gap-1.5 rounded-full border border-[rgba(251,191,36,0.24)] bg-[rgba(251,191,36,0.09)] px-3 py-1.5 text-[var(--text-primary)]">
                        <Sparkles className="h-3.5 w-3.5" />
                        AI: {aiTopicLabel}
                    </span>
                ) : null}
                {!hasSignals ? (
                    <span className="text-[11px] uppercase tracking-[0.14em] text-[var(--text-muted)]">
                        Context follows your current workflow
                    </span>
                ) : null}
                <LowDataToggle />
            </div>
        </div>
    );
}
