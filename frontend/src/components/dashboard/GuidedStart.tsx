"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type ChecklistItem = {
    id: string;
    label: string;
};

type TaskItem = {
    label: string;
    href: string;
    priority?: "high" | "medium" | "low";
};

export default function GuidedStart({
    roleLabel,
    checklist,
    tasks,
    storageKey,
}: {
    roleLabel: string;
    checklist: ChecklistItem[];
    tasks: TaskItem[];
    storageKey: string;
}) {
    const [doneMap, setDoneMap] = useState<Record<string, boolean>>({});

    useEffect(() => {
        const raw = window.localStorage.getItem(storageKey);
        if (!raw) return;
        queueMicrotask(() => {
            try {
                setDoneMap(JSON.parse(raw) as Record<string, boolean>);
            } catch {
                setDoneMap({});
            }
        });
    }, [storageKey]);

    const completed = useMemo(
        () => checklist.filter((item) => doneMap[item.id]).length,
        [checklist, doneMap],
    );

    const toggleItem = (id: string) => {
        setDoneMap((prev) => {
            const next = { ...prev, [id]: !prev[id] };
            window.localStorage.setItem(storageKey, JSON.stringify(next));
            return next;
        });
    };

    return (
        <div className="grid gap-4 lg:grid-cols-2 mb-6">
            <section className="rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                <div className="flex items-center justify-between mb-2">
                    <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)]">Start here · {roleLabel}</p>
                    <span className="text-[10px] text-[var(--text-muted)]">{completed}/{checklist.length} done</span>
                </div>
                <ul className="space-y-2">
                    {checklist.map((item) => (
                        <li key={item.id} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                            <button
                                type="button"
                                onClick={() => toggleItem(item.id)}
                                className={`mt-0.5 inline-flex h-4 w-4 shrink-0 items-center justify-center rounded-full text-[10px] ${doneMap[item.id] ? "bg-success-subtle text-[var(--success)]" : "bg-[var(--bg-page)] text-[var(--text-muted)]"}`}
                                aria-label={`Toggle ${item.label}`}
                            >
                                {doneMap[item.id] ? "✓" : "•"}
                            </button>
                            <span className={`leading-5 ${doneMap[item.id] ? "line-through text-[var(--text-muted)]" : ""}`}>{item.label}</span>
                        </li>
                    ))}
                </ul>
            </section>

            <section className="rounded-[var(--radius)] border border-[var(--border)] bg-[var(--bg-card)] p-4 shadow-[var(--shadow-card)]">
                <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-2">Today&apos;s tasks</p>
                <div className="space-y-2">
                    {tasks.map((task) => (
                        <Link
                            key={task.label}
                            href={task.href}
                            className="flex items-center justify-between rounded-[var(--radius-sm)] border border-[var(--border-light)] px-3 py-2 text-sm hover:bg-[var(--bg-page)]"
                        >
                            <span className="text-[var(--text-primary)]">{task.label}</span>
                            <span className={`text-[10px] uppercase tracking-wider ${task.priority === "high" ? "text-[var(--error)]" : task.priority === "medium" ? "text-[var(--warning)]" : "text-[var(--text-muted)]"}`}>
                                {task.priority || "next"}
                            </span>
                        </Link>
                    ))}
                </div>
            </section>
        </div>
    );
}
