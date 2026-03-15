"use client";

import { useEffect, useState } from "react";
import { Gauge, Zap } from "lucide-react";

export default function AIFallbackNotice({
    queueDepth,
    processingDepth,
    scope,
}: {
    queueDepth: number;
    processingDepth: number;
    scope: string;
}) {
    const [lightMode, setLightMode] = useState(false);
    const estimateMin = processingDepth > 0 ? Math.ceil(queueDepth / processingDepth) : queueDepth > 0 ? queueDepth : 0;
    const highLoad = queueDepth >= 8;

    useEffect(() => {
        const value = window.localStorage.getItem(`lite-mode:${scope}`);
        setLightMode(value === "true");
    }, [scope]);

    const toggle = () => {
        setLightMode((prev) => {
            const next = !prev;
            window.localStorage.setItem(`lite-mode:${scope}`, String(next));
            return next;
        });
    };

    return (
        <div className={`mb-6 rounded-[var(--radius)] border p-4 ${highLoad ? "border-[var(--warning)]/40 bg-warning-subtle" : "border-[var(--border)] bg-[var(--bg-card)]"}`}>
            <div className="flex items-start justify-between gap-3">
                <div>
                    <p className="text-xs uppercase tracking-widest text-[var(--text-muted)] mb-1">AI fallback status</p>
                    <p className="text-sm font-semibold text-[var(--text-primary)] inline-flex items-center gap-1.5">
                        <Gauge className="w-4 h-4" /> {highLoad ? "High load detected" : "AI load is stable"}
                    </p>
                    <p className="text-xs text-[var(--text-secondary)] mt-1">
                        Queue: {queueDepth} pending • Processing: {processingDepth} • Est wait: ~{estimateMin} min
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">
                        {highLoad
                            ? "You can switch to lightweight response mode for faster replies."
                            : "Standard response mode is active."}
                    </p>
                </div>
                <button
                    type="button"
                    onClick={toggle}
                    className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-[var(--radius-sm)] text-xs font-semibold ${lightMode ? "bg-[var(--success)] text-white" : "bg-[var(--primary)] text-white"}`}
                >
                    <Zap className="w-3.5 h-3.5" /> {lightMode ? "Light mode on" : "Enable light mode"}
                </button>
            </div>
        </div>
    );
}
