"use client";

import { type ReactNode } from "react";
import { Skeleton as BoneyardSkeleton } from "boneyard-js/react";

interface SkeletonProps {
    className?: string;
    variant?: "line" | "card" | "circle" | "table-row";
    rows?: number;
}

function renderPrimitive(className: string, variant: SkeletonProps["variant"]): ReactNode {
    const base = "skeleton";

    if (variant === "circle") {
        return <div className={`${base} rounded-full ${className}`} />;
    }

    return <div className={`${base} ${className}`} />;
}

export function Skeleton({ className = "", variant = "line" }: SkeletonProps) {
    const primitive = renderPrimitive(className, variant);

    return (
        <BoneyardSkeleton
            loading
            className={className}
            fallback={primitive}
            fixture={primitive}
        >
            {primitive}
        </BoneyardSkeleton>
    );
}

export function SkeletonCard({ className = "" }: { className?: string } = {}) {
    const fallback = (
        <div className="prism-skeleton-card space-y-3">
            <div className="flex items-center justify-between">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-4 rounded" />
            </div>
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-3 w-16" />
        </div>
    );

    return (
        <BoneyardSkeleton
            loading
            name="prism-skeleton-card"
            className={`prism-skeleton-card ${className}`.trim()}
            fallback={fallback}
            fixture={
                <div className="prism-skeleton-card space-y-3">
                    <div className="flex items-center justify-between text-xs uppercase tracking-widest text-[var(--text-muted)]">
                        <span>Status</span>
                        <span>Live</span>
                    </div>
                    <div className="text-3xl font-semibold text-[var(--text-primary)]">82%</div>
                    <div className="text-sm text-[var(--text-muted)]">Readiness is improving across the last seven days.</div>
                </div>
            }
        >
            {fallback}
        </BoneyardSkeleton>
    );
}

export function SkeletonTable({ rows = 5, cols = 3, className = "" }: { rows?: number; cols?: number; className?: string }) {
    const fallback = (
        <div className="prism-table-shell overflow-hidden">
            <div className="flex gap-4 border-b border-[var(--border)] bg-[rgba(8,17,31,0.72)] px-5 py-3">
                {Array.from({ length: cols }).map((_, i) => (
                    <Skeleton key={i} className="h-3 w-20" />
                ))}
            </div>
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex gap-4 border-b border-[var(--border-light)] px-5 py-3.5">
                    {Array.from({ length: cols }).map((_, j) => (
                        <Skeleton key={j} className={`h-3.5 ${j === 0 ? "w-28" : "w-16"}`} />
                    ))}
                </div>
            ))}
        </div>
    );

    return (
        <BoneyardSkeleton
            loading
            name="prism-skeleton-table"
            className={`prism-table-shell ${className}`.trim()}
            fallback={fallback}
            fixture={
                <div className="prism-table-shell overflow-hidden">
                    <div className="flex gap-4 border-b border-[var(--border)] bg-[rgba(8,17,31,0.72)] px-5 py-3 text-xs uppercase tracking-widest text-[var(--text-muted)]">
                        {Array.from({ length: cols }).map((_, i) => (
                            <div key={i} className={i === 0 ? "w-28" : "w-20"}>
                                {i === 0 ? "Name" : `Col ${i + 1}`}
                            </div>
                        ))}
                    </div>
                    {Array.from({ length: rows }).map((_, i) => (
                        <div key={i} className="flex gap-4 border-b border-[var(--border-light)] px-5 py-3.5 text-sm text-[var(--text-secondary)]">
                            <div className="w-28">Row {i + 1}</div>
                            {Array.from({ length: cols - 1 }).map((_, j) => (
                                <div key={j} className="w-20">
                                    Value
                                </div>
                            ))}
                        </div>
                    ))}
                </div>
            }
        >
            {fallback}
        </BoneyardSkeleton>
    );
}

export function SkeletonList({ items = 3, className = "" }: { items?: number; className?: string }) {
    const fallback = (
        <div className="space-y-3">
            {Array.from({ length: items }).map((_, i) => (
                <div key={i} className="prism-skeleton-row flex items-center gap-4 p-3">
                    <Skeleton className="h-10 w-10 rounded-[var(--radius-sm)]" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-3.5 w-32" />
                        <Skeleton className="h-2.5 w-20" />
                    </div>
                </div>
            ))}
        </div>
    );

    return (
        <BoneyardSkeleton
            loading
            name="prism-skeleton-list"
            className={className}
            fallback={fallback}
            fixture={
                <div className="space-y-3">
                    {Array.from({ length: items }).map((_, i) => (
                        <div key={i} className="prism-skeleton-row flex items-center gap-4 p-3">
                            <div className="h-10 w-10 rounded-[var(--radius-sm)] bg-[rgba(96,165,250,0.12)]" />
                            <div className="flex-1">
                                <div className="text-sm font-medium text-[var(--text-primary)]">Item {i + 1}</div>
                                <div className="text-xs text-[var(--text-muted)]">Loading details</div>
                            </div>
                        </div>
                    ))}
                </div>
            }
        >
            {fallback}
        </BoneyardSkeleton>
    );
}
