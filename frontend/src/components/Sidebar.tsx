"use client";

import { useEffect, useMemo, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
    ChevronDown,
    ChevronLeft,
    GraduationCap,
    LogOut,
    Menu,
    X,
} from "lucide-react";
import { LucideIcon } from "lucide-react";

import { PrismDrawer, PrismOverlay } from "@/components/prism/PrismOverlays";
import { API_BASE, clearStoredAccessToken } from "@/lib/api";
import { LanguageToggle } from "@/i18n/LanguageProvider";
import { ThemeToggle } from "./theme/ThemeToggle";
import { LowDataToggle } from "./LowDataToggle";


export interface NavItem {
    label: string;
    href: string;
    icon: LucideIcon;
    group?: string;
    utility?: boolean;
}

interface SidebarProps {
    items: NavItem[];
    role: string;
    userName?: string;
}

const roleMeta: Record<string, { label: string; accent: string; accentSoft: string; accentBorder: string }> = {
    student: {
        label: "Student",
        accent: "var(--role-student)",
        accentSoft: "rgba(59,130,246,0.14)",
        accentBorder: "rgba(59,130,246,0.2)",
    },
    teacher: {
        label: "Teacher",
        accent: "var(--role-teacher)",
        accentSoft: "rgba(16,185,129,0.14)",
        accentBorder: "rgba(16,185,129,0.2)",
    },
    admin: {
        label: "Admin",
        accent: "var(--role-admin)",
        accentSoft: "rgba(139,92,246,0.14)",
        accentBorder: "rgba(139,92,246,0.22)",
    },
    parent: {
        label: "Parent",
        accent: "var(--role-parent)",
        accentSoft: "rgba(249,115,22,0.14)",
        accentBorder: "rgba(249,115,22,0.2)",
    },
};

export default function Sidebar({ items, role, userName }: SidebarProps) {
    const pathname = usePathname();
    const [mobileOpen, setMobileOpen] = useState(false);
    const [collapsed, setCollapsed] = useState(false);
    const [hoverExpanded, setHoverExpanded] = useState(false);
    const [expandedGroups, setExpandedGroups] = useState<Record<string, boolean>>({});
    const [utilityOpen, setUtilityOpen] = useState(false);
    const roleStyle = roleMeta[role] || roleMeta.student;
    const visuallyCollapsed = collapsed && !hoverExpanded && !mobileOpen;

    const primaryItems = useMemo(() => items.filter((item) => !item.utility).slice(0, 5), [items]);
    const overflowItems = useMemo(() => items.filter((item) => !item.utility).slice(5), [items]);
    const utilityItems = useMemo(() => [...overflowItems, ...items.filter((item) => item.utility)], [items, overflowItems]);

    const groups = useMemo(() => {
        const grouped = new Map<string, NavItem[]>();
        for (const item of primaryItems) {
            const key = item.group || "Navigate";
            const bucket = grouped.get(key) || [];
            bucket.push(item);
            grouped.set(key, bucket);
        }
        return Array.from(grouped.entries()).map(([label, groupItems]) => ({ label, items: groupItems }));
    }, [primaryItems]);

    useEffect(() => {
        const applyResponsiveState = () => {
            if (window.innerWidth >= 1024) {
                setMobileOpen(false);
            }
            setCollapsed(window.innerWidth < 1280);
        };
        applyResponsiveState();
        window.addEventListener("resize", applyResponsiveState);
        return () => window.removeEventListener("resize", applyResponsiveState);
    }, []);

    const handleLogout = async () => {
        await fetch(`${API_BASE}/api/auth/logout`, {
            method: "POST",
            credentials: "include",
        });
        clearStoredAccessToken();
        window.location.href = "/";
    };

    const toggleGroup = (label: string) => {
        setExpandedGroups((prev) => ({ ...prev, [label]: !prev[label] }));
    };

    const renderItem = (item: NavItem) => {
        const isActive = pathname === item.href;
        return (
            <Link
                key={item.href}
                href={item.href}
                onClick={() => setMobileOpen(false)}
                title={visuallyCollapsed ? item.label : undefined}
                className={`flex items-center gap-3 rounded-2xl border px-3 py-3 text-sm transition-all duration-[var(--transition-fast)] ${
                    visuallyCollapsed ? "justify-center" : ""
                } ${
                    isActive
                        ? "font-semibold text-[var(--text-primary)] shadow-[var(--shadow-level-2)]"
                        : "border-transparent text-[var(--text-secondary)] hover:border-[var(--border-light)] hover:bg-[rgba(148,163,184,0.08)] hover:text-[var(--text-primary)]"
                }`}
                style={
                    isActive
                        ? {
                            borderColor: roleStyle.accentBorder,
                            background: `linear-gradient(135deg, ${roleStyle.accentSoft}, rgba(255,255,255,0.03))`,
                            color: roleStyle.accent,
                        }
                        : undefined
                }
            >
                <item.icon className="h-[18px] w-[18px] flex-shrink-0" />
                {!visuallyCollapsed ? <span className="truncate">{item.label}</span> : null}
            </Link>
        );
    };

    const sidebarContent = (
        <>
            <div className={`flex h-20 items-center border-b border-[var(--border)] px-4 ${visuallyCollapsed ? "justify-center" : "gap-3"}`}>
                <div
                    className="flex h-11 w-11 items-center justify-center rounded-3xl shadow-[var(--shadow-level-2)]"
                    style={{ background: `linear-gradient(135deg, ${roleStyle.accent}, rgba(255,255,255,0.92))` }}
                >
                    <GraduationCap className="h-5 w-5 flex-shrink-0 text-[#06101e]" />
                </div>
                {!visuallyCollapsed ? (
                    <div className="min-w-0">
                        <p className="text-lg font-bold tracking-tight text-[var(--text-primary)]">VidyaOS</p>
                        <div className="mt-1 flex items-center gap-2">
                            <span
                                className="rounded-full border px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.18em]"
                                style={{
                                    borderColor: roleStyle.accentBorder,
                                    background: roleStyle.accentSoft,
                                    color: roleStyle.accent,
                                }}
                            >
                                {roleStyle.label}
                            </span>
                            <span className="text-xs text-[var(--text-muted)]">Daily operating surface</span>
                        </div>
                    </div>
                ) : null}
            </div>
            <nav className="flex-1 overflow-y-auto px-3 py-3">
                {visuallyCollapsed ? (
                    <div className="space-y-2">
                        {primaryItems.map(renderItem)}
                    </div>
                ) : (
                    <div className="space-y-3">
                        {groups.map((group) => {
                            const open = expandedGroups[group.label] ?? group.items.some((item) => pathname === item.href);
                            const activeInGroup = group.items.some((item) => pathname === item.href);
                            return (
                                <div key={group.label} className="rounded-[var(--radius-sm)] border border-[var(--border-light)] bg-[rgba(255,255,255,0.02)] p-2">
                                    <button
                                        type="button"
                                        onClick={() => toggleGroup(group.label)}
                                        className="flex w-full items-center justify-between rounded-xl px-2 py-2 text-left transition-colors hover:bg-[rgba(148,163,184,0.08)]"
                                    >
                                        <div className="min-w-0">
                                            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">{group.label}</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                {activeInGroup ? "Current section is inside this group" : `${group.items.length} destinations`}
                                            </p>
                                        </div>
                                        <ChevronDown className={`h-4 w-4 text-[var(--text-muted)] transition-transform ${open ? "rotate-180" : ""}`} />
                                    </button>
                                    {open ? (
                                        <div className="mt-2 space-y-2">
                                            {group.items.map(renderItem)}
                                        </div>
                                    ) : null}
                                </div>
                            );
                        })}
                    </div>
                )}
            </nav>

            <div
                className="border-t border-[var(--border)] bg-[rgba(255,255,255,0.02)] p-3"
                onMouseEnter={() => setUtilityOpen(true)}
            >
                {!visuallyCollapsed ? (
                    <button
                        type="button"
                        onClick={() => setUtilityOpen((prev) => !prev)}
                        className="flex w-full items-center justify-between rounded-xl px-2 py-2 text-left transition-colors hover:bg-[rgba(148,163,184,0.08)]"
                    >
                        <div>
                            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-[var(--text-muted)]">Utility</p>
                            <p className="mt-1 text-xs text-[var(--text-secondary)]">Profile, appearance, language, and account controls</p>
                        </div>
                        <ChevronDown className={`h-4 w-4 text-[var(--text-muted)] transition-transform ${utilityOpen ? "rotate-180" : ""}`} />
                    </button>
                ) : null}

                {(visuallyCollapsed || utilityOpen) && utilityItems.length > 0 ? (
                    <div className={`mt-2 space-y-2 ${visuallyCollapsed ? "" : ""}`}>
                        {utilityItems.map(renderItem)}
                    </div>
                ) : null}

                <div className={`mt-3 ${visuallyCollapsed ? "space-y-2" : "space-y-3"}`}>
                    {!visuallyCollapsed && userName ? (
                        <p className="truncate px-2 text-xs text-[var(--text-muted)]">{userName}</p>
                    ) : null}
                    {!visuallyCollapsed ? (
                        <>
                            <div className="px-2">
                                <LowDataToggle />
                            </div>
                            <div className="flex items-center gap-2 px-2">
                                <LanguageToggle />
                                <ThemeToggle />
                            </div>
                        </>
                    ) : null}
                    <button
                        onClick={handleLogout}
                        title={visuallyCollapsed ? "Switch account" : undefined}
                        className={`flex w-full items-center gap-3 rounded-2xl border border-transparent px-3 py-3 text-sm text-[var(--text-secondary)] transition-colors hover:border-error-subtle hover:bg-error-subtle hover:text-status-red ${
                            visuallyCollapsed ? "justify-center" : ""
                        }`}
                    >
                        <LogOut className="h-[18px] w-[18px] flex-shrink-0" />
                        {!visuallyCollapsed ? "Switch account" : null}
                    </button>
                </div>
            </div>
        </>
    );

    return (
        <>
            <div className="fixed left-0 right-0 top-0 z-50 flex h-16 items-center gap-3 border-b border-[var(--border)] bg-[rgba(8,14,28,0.9)] px-4 backdrop-blur-xl lg:hidden">
                <button
                    onClick={() => setMobileOpen(true)}
                    className="rounded-xl p-2 text-[var(--text-secondary)] hover:bg-[var(--bg-hover)] active:bg-[var(--border)]"
                    aria-label="Open menu"
                >
                    <Menu className="h-5 w-5" />
                </button>
                <div
                    className="flex h-9 w-9 items-center justify-center rounded-2xl shadow-[var(--shadow-level-2)]"
                    style={{ background: `linear-gradient(135deg, ${roleStyle.accent}, rgba(255,255,255,0.92))` }}
                >
                    <GraduationCap className="h-5 w-5 text-[#06101e]" />
                </div>
                <div className="min-w-0">
                    <p className="text-base font-bold tracking-tight text-[var(--text-primary)]">VidyaOS</p>
                    <p className="text-[10px] uppercase tracking-[0.18em]" style={{ color: roleStyle.accent }}>
                        {roleStyle.label}
                    </p>
                </div>
            </div>
            {mobileOpen ? (
                <PrismOverlay
                    className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm lg:hidden"
                    onClick={() => setMobileOpen(false)}
                />
            ) : null}

            <PrismDrawer
                className={`fixed left-0 top-0 z-50 flex flex-col transition-transform duration-300 lg:hidden ${mobileOpen ? "translate-x-0" : "-translate-x-full"}`}
            >
                <div className="flex items-center justify-end p-2">
                    <button
                        onClick={() => setMobileOpen(false)}
                        className="rounded-lg p-2 text-[var(--text-muted)] hover:bg-[var(--bg-hover)] hover:text-[var(--text-secondary)]"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>
                {sidebarContent}
            </PrismDrawer>

            <aside
                data-testid="sidebar"
                onMouseEnter={() => setHoverExpanded(true)}
                onMouseLeave={() => {
                    setHoverExpanded(false);
                    setUtilityOpen(false);
                }}
                className={`fixed left-0 top-0 z-40 hidden h-screen flex-col border-r border-[var(--border)] bg-[rgba(8,14,28,0.82)] backdrop-blur-2xl transition-all duration-[var(--transition-base)] lg:flex ${
                    visuallyCollapsed ? "w-[76px]" : "w-[304px]"
                }`}
            >
                {sidebarContent}
                <button
                    onClick={() => setCollapsed((prev) => !prev)}
                    className="absolute -right-3 top-20 z-50 flex h-7 w-7 items-center justify-center rounded-full border border-[var(--border)] bg-[var(--bg-card)] text-[var(--text-muted)] shadow-[var(--shadow-level-1)] transition-all hover:text-[var(--text-secondary)]"
                    aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    <ChevronLeft className={`h-3.5 w-3.5 transition-transform duration-[var(--transition-fast)] ${collapsed ? "rotate-180" : ""}`} />
                </button>
            </aside>

            <div className={`hidden flex-shrink-0 lg:block ${collapsed ? "w-[76px]" : "w-[304px]"}`} aria-hidden="true" />
        </>
    );
}
