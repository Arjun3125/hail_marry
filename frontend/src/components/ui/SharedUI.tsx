"use client";

import { useEffect, useRef, useState } from "react";

/* ─── Skeleton Loader ─── */

export function SkeletonCard({ className = "" }: { className?: string }) {
    return (
        <div className={`bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] ${className}`}>
            <div className="skeleton h-4 w-1/3 mb-4" />
            <div className="skeleton h-8 w-1/2 mb-3" />
            <div className="skeleton h-3 w-full mb-2" />
            <div className="skeleton h-3 w-4/5" />
        </div>
    );
}

export function SkeletonTable({ rows = 5 }: { rows?: number }) {
    return (
        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
            <div className="skeleton h-4 w-1/4 mb-6" />
            <div className="space-y-3">
                {Array.from({ length: rows }).map((_, i) => (
                    <div key={i} className="flex gap-4">
                        <div className="skeleton h-4 flex-1" />
                        <div className="skeleton h-4 w-20" />
                        <div className="skeleton h-4 w-16" />
                    </div>
                ))}
            </div>
        </div>
    );
}

export function SkeletonText({ lines = 3 }: { lines?: number }) {
    return (
        <div className="space-y-2">
            {Array.from({ length: lines }).map((_, i) => (
                <div key={i} className={`skeleton h-3 ${i === lines - 1 ? "w-3/4" : "w-full"}`} />
            ))}
        </div>
    );
}

/* ─── Animated Counter ─── */

export function AnimatedCounter({
    value,
    suffix = "",
    prefix = "",
    duration = 1000,
    className = "",
}: {
    value: number;
    suffix?: string;
    prefix?: string;
    duration?: number;
    className?: string;
}) {
    const [display, setDisplay] = useState(0);
    const displayRef = useRef(0);

    useEffect(() => {
        const step = Math.max(1, Math.ceil(value / (duration / 16)));
        let current = displayRef.current;
        
        if (current === value) return;
        
        const timer = setInterval(() => {
            current = current < value 
                ? Math.min(current + step, value)
                : Math.max(current - step, value);
                
            displayRef.current = current;
            setDisplay(current);
            if (current === value) {
                clearInterval(timer);
            }
        }, 16);
        
        return () => clearInterval(timer);
    }, [value, duration]);

    return (
        <span className={`tabular-nums ${className}`}>
            {prefix}{display.toLocaleString()}{suffix}
        </span>
    );
}

/* ─── Progress Ring ─── */

export function ProgressRing({
    value,
    max = 100,
    size = 80,
    strokeWidth = 6,
    color = "var(--primary)",
    bgColor = "var(--border)",
    className = "",
    children,
}: {
    value: number;
    max?: number;
    size?: number;
    strokeWidth?: number;
    color?: string;
    bgColor?: string;
    className?: string;
    children?: React.ReactNode;
}) {
    const radius = (size - strokeWidth) / 2;
    const circumference = 2 * Math.PI * radius;
    const pct = Math.min(value / max, 1);
    const offset = circumference * (1 - pct);

    return (
        <div className={`relative inline-flex items-center justify-center ${className}`} style={{ width: size, height: size }}>
            <svg width={size} height={size} className="absolute">
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={bgColor}
                    strokeWidth={strokeWidth}
                />
                <circle
                    cx={size / 2}
                    cy={size / 2}
                    r={radius}
                    fill="none"
                    stroke={color}
                    strokeWidth={strokeWidth}
                    strokeLinecap="round"
                    strokeDasharray={circumference}
                    strokeDashoffset={offset}
                    className="progress-ring-circle"
                />
            </svg>
            {children && (
                <div className="relative z-10 text-center">
                    {children}
                </div>
            )}
        </div>
    );
}

/* ─── Empty State ─── */

export function EmptyState({
    icon,
    title,
    description,
    action,
}: {
    icon?: "chart" | "users" | "book" | "trophy" | "bell" | "search";
    title: string;
    description?: string;
    action?: React.ReactNode;
}) {
    const svgMap: Record<string, React.ReactNode> = {
        chart: (
            <svg viewBox="0 0 120 120" className="w-24 h-24 mx-auto mb-4">
                <rect x="15" y="60" width="16" height="40" rx="4" fill="var(--primary)" opacity="0.2" />
                <rect x="38" y="40" width="16" height="60" rx="4" fill="var(--primary)" opacity="0.35" />
                <rect x="61" y="25" width="16" height="75" rx="4" fill="var(--primary)" opacity="0.5" />
                <rect x="84" y="45" width="16" height="55" rx="4" fill="var(--primary)" opacity="0.3" />
                <line x1="10" y1="105" x2="110" y2="105" stroke="var(--border)" strokeWidth="2" />
            </svg>
        ),
        users: (
            <svg viewBox="0 0 120 120" className="w-24 h-24 mx-auto mb-4">
                <circle cx="60" cy="40" r="18" fill="var(--primary)" opacity="0.2" />
                <circle cx="35" cy="50" r="12" fill="var(--primary)" opacity="0.15" />
                <circle cx="85" cy="50" r="12" fill="var(--primary)" opacity="0.15" />
                <ellipse cx="60" cy="90" rx="35" ry="18" fill="var(--primary)" opacity="0.1" />
            </svg>
        ),
        book: (
            <svg viewBox="0 0 120 120" className="w-24 h-24 mx-auto mb-4">
                <rect x="25" y="20" width="70" height="85" rx="6" fill="var(--primary)" opacity="0.1" stroke="var(--primary)" strokeWidth="2" strokeOpacity="0.2" />
                <line x1="40" y1="40" x2="80" y2="40" stroke="var(--primary)" strokeWidth="2" opacity="0.3" />
                <line x1="40" y1="52" x2="75" y2="52" stroke="var(--primary)" strokeWidth="2" opacity="0.2" />
                <line x1="40" y1="64" x2="70" y2="64" stroke="var(--primary)" strokeWidth="2" opacity="0.15" />
            </svg>
        ),
        trophy: (
            <svg viewBox="0 0 120 120" className="w-24 h-24 mx-auto mb-4">
                <path d="M45 30h30v40a15 15 0 01-30 0V30z" fill="#f59e0b" opacity="0.2" />
                <rect x="52" y="70" width="16" height="20" rx="3" fill="#f59e0b" opacity="0.15" />
                <rect x="40" y="90" width="40" height="8" rx="4" fill="#f59e0b" opacity="0.1" />
                <path d="M45 35H30a10 10 0 000 20h5" stroke="#f59e0b" strokeWidth="2" fill="none" opacity="0.3" />
                <path d="M75 35h15a10 10 0 010 20h-5" stroke="#f59e0b" strokeWidth="2" fill="none" opacity="0.3" />
            </svg>
        ),
        bell: (
            <svg viewBox="0 0 120 120" className="w-24 h-24 mx-auto mb-4">
                <path d="M60 25a25 25 0 00-25 25v20l-8 12h66l-8-12V50a25 25 0 00-25-25z" fill="var(--primary)" opacity="0.15" />
                <circle cx="60" cy="95" r="8" fill="var(--primary)" opacity="0.2" />
            </svg>
        ),
        search: (
            <svg viewBox="0 0 120 120" className="w-24 h-24 mx-auto mb-4">
                <circle cx="52" cy="52" r="25" fill="none" stroke="var(--primary)" strokeWidth="3" opacity="0.2" />
                <line x1="70" y1="70" x2="95" y2="95" stroke="var(--primary)" strokeWidth="4" strokeLinecap="round" opacity="0.2" />
            </svg>
        ),
    };

    return (
        <div className="py-12 text-center">
            {icon && svgMap[icon]}
            <h3 className="text-base font-semibold text-[var(--text-primary)] mb-1">{title}</h3>
            {description && <p className="text-sm text-[var(--text-muted)] max-w-sm mx-auto mb-4">{description}</p>}
            {action}
        </div>
    );
}

/* ─── Mobile Bottom Nav ─── */

export function MobileBottomNav({
    items,
    currentPath,
}: {
    items: Array<{ href: string; icon: React.ComponentType<{ className?: string }>; label: string }>;
    currentPath: string;
}) {
    return (
        <nav className="mobile-bottom-nav safe-bottom">
            {items.map((item) => {
                const isActive = currentPath === item.href || currentPath.startsWith(item.href + "/");
                return (
                    <a
                        key={item.href}
                        href={item.href}
                        className={`flex flex-col items-center gap-0.5 px-2 py-1 text-[10px] font-medium transition-colors ${
                            isActive
                                ? "text-[var(--primary)]"
                                : "text-[var(--text-muted)] hover:text-[var(--text-secondary)]"
                        }`}
                    >
                        <item.icon className={`w-5 h-5 ${isActive ? "text-[var(--primary)]" : ""}`} />
                        {item.label}
                    </a>
                );
            })}
        </nav>
    );
}
