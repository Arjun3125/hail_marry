"use client";

/**
 * Skeleton — shimmer loading placeholder.
 * Usage: <Skeleton className="h-8 w-32" />
 *        <Skeleton variant="card" />
 *        <Skeleton variant="table-row" rows={5} />
 */

interface SkeletonProps {
    className?: string;
    variant?: "line" | "card" | "circle" | "table-row";
    rows?: number;
}

export function Skeleton({ className = "", variant = "line" }: SkeletonProps) {
    const base = "animate-pulse rounded-[var(--radius-sm)] bg-[var(--border)]";

    if (variant === "circle") {
        return <div className={`${base} rounded-full ${className}`} />;
    }

    return <div className={`${base} ${className}`} />;
}

/** Skeleton for a KPI stat card */
export function SkeletonCard() {
    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] space-y-3">
            <div className="flex items-center justify-between">
                <Skeleton className="h-3 w-20" />
                <Skeleton className="h-4 w-4 rounded" />
            </div>
            <Skeleton className="h-8 w-24" />
            <Skeleton className="h-3 w-16" />
        </div>
    );
}

/** Skeleton for a table */
export function SkeletonTable({ rows = 5, cols = 3 }: { rows?: number; cols?: number }) {
    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
            {/* Header */}
            <div className="flex gap-4 px-5 py-3 border-b border-[var(--border)] bg-[var(--bg-page)]">
                {Array.from({ length: cols }).map((_, i) => (
                    <Skeleton key={i} className="h-3 w-20" />
                ))}
            </div>
            {/* Rows */}
            {Array.from({ length: rows }).map((_, i) => (
                <div key={i} className="flex gap-4 px-5 py-3.5 border-b border-[var(--border-light)]">
                    {Array.from({ length: cols }).map((_, j) => (
                        <Skeleton key={j} className={`h-3.5 ${j === 0 ? "w-28" : "w-16"}`} />
                    ))}
                </div>
            ))}
        </div>
    );
}

/** Skeleton for the schedule/list section */
export function SkeletonList({ items = 3 }: { items?: number }) {
    return (
        <div className="space-y-3">
            {Array.from({ length: items }).map((_, i) => (
                <div key={i} className="flex items-center gap-4 p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]">
                    <Skeleton className="h-10 w-10 rounded-[var(--radius-sm)]" />
                    <div className="flex-1 space-y-2">
                        <Skeleton className="h-3.5 w-32" />
                        <Skeleton className="h-2.5 w-20" />
                    </div>
                </div>
            ))}
        </div>
    );
}
