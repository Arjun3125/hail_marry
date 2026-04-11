"use client";

import { useEffect, useMemo, useState } from "react";
import { Sparkles } from "lucide-react";

import { api } from "@/lib/api";

export function RoleMorningBriefing({
    role,
    facts,
    fallback,
}: {
    role: "student" | "teacher" | "admin" | "parent";
    facts: string[];
    fallback: string[];
}) {
    const [lines, setLines] = useState<string[]>(fallback);
    const factKey = useMemo(() => facts.filter(Boolean).join(" | "), [facts]);

    useEffect(() => {
        let cancelled = false;
        const usefulFacts = facts.filter(Boolean).slice(0, 8);
        if (!usefulFacts.length) {
            queueMicrotask(() => setLines(fallback));
            return;
        }

        api.mascot.message({
            message: [
                `Create exactly 3 short morning briefing lines for a ${role}.`,
                "Use only these real VidyaOS facts. Do not invent numbers.",
                ...usefulFacts.map((fact) => `- ${fact}`),
            ].join("\n"),
            channel: "web",
            ui_context: {
                current_route: `/${role}`,
                current_page_entity: "morning_briefing",
                metadata: { role, facts: usefulFacts },
            },
        }).then((payload) => {
            if (cancelled) return;
            const text = String((payload as { response_text?: string; response?: string }).response_text || (payload as { response?: string }).response || "");
            const parsed = text
                .split(/\n+/)
                .map((line) => line.replace(/^[-*\d.\s]+/, "").trim())
                .filter(Boolean)
                .slice(0, 3);
            setLines(parsed.length ? parsed : fallback);
        }).catch(() => {
            if (!cancelled) setLines(fallback);
        });

        return () => {
            cancelled = true;
        };
    }, [factKey, fallback, facts, role]);

    return (
        <div className="rounded-[1.5rem] border border-[rgba(79,142,247,0.22)] bg-[rgba(79,142,247,0.08)] p-4">
            <p className="flex items-center gap-2 text-xs font-semibold uppercase tracking-[0.22em] text-status-blue">
                <Sparkles className="h-4 w-4" />
                AI morning briefing
            </p>
            <div className="mt-3 space-y-2">
                {lines.map((line) => (
                    <p key={line} className="text-sm leading-6 text-[var(--text-secondary)]">
                        {line}
                    </p>
                ))}
            </div>
        </div>
    );
}
