"use client";

import { ReactNode, Suspense } from "react";
import {
    SkeletonDashboard,
    SkeletonList,
    SkeletonCardGrid,
    SkeletonQuiz,
    SkeletonTable,
} from "./Skeleton";

interface SkeletonBoundaryProps {
    children: ReactNode;
    variant?: "dashboard" | "list" | "card-grid" | "quiz" | "table" | "default";
    fallback?: ReactNode;
}

export default function SkeletonBoundary({
    children,
    variant = "default",
    fallback,
}: SkeletonBoundaryProps) {
    const defaultFallbacks: Record<string, ReactNode> = {
        dashboard: <SkeletonDashboard />,
        list: <SkeletonList items={5} />,
        "card-grid": <SkeletonCardGrid items={6} />,
        quiz: <SkeletonQuiz />,
        table: <SkeletonTable rows={8} cols={4} />,
        default: <SkeletonList items={3} />,
    };

    const fallbackComponent = fallback || defaultFallbacks[variant];

    return (
        <Suspense fallback={fallbackComponent}>
            {children}
        </Suspense>
    );
}
