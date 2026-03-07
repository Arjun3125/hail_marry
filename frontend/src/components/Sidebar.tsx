"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { GraduationCap, LogOut, Menu, X, ChevronLeft } from "lucide-react";
import { LucideIcon } from "lucide-react";
import { API_BASE, clearStoredAccessToken } from "@/lib/api";

interface NavItem {
    label: string;
    href: string;
    icon: LucideIcon;
}

interface SidebarProps {
    items: NavItem[];
    role: string;
    userName?: string;
}

export default function Sidebar({ items, role, userName }: SidebarProps) {
    const pathname = usePathname();
    const [mobileOpen, setMobileOpen] = useState(false);
    const [collapsed, setCollapsed] = useState(false);

    // Close mobile drawer on resize to desktop
    useEffect(() => {
        const handleResize = () => {
            if (window.innerWidth >= 1024) setMobileOpen(false);
        };
        window.addEventListener("resize", handleResize);
        return () => window.removeEventListener("resize", handleResize);
    }, []);

    const handleLogout = async () => {
        await fetch(`${API_BASE}/api/auth/logout`, {
            method: "POST",
            credentials: "include",
        });
        clearStoredAccessToken();
        window.location.href = "/";
    };

    const sidebarWidth = collapsed ? "w-[68px]" : "w-60";

    const sidebarContent = (
        <>
            {/* Logo */}
            <div className={`flex h-14 items-center border-b border-slate-200 px-4 ${collapsed ? "justify-center" : "gap-2.5"}`}>
                <GraduationCap className="h-6 w-6 flex-shrink-0 text-blue-700" />
                {!collapsed && (
                    <div className="flex flex-col justify-center">
                        <div className="flex items-center gap-2">
                            <span className="font-bold tracking-tight text-slate-900">ModernHustlers</span>
                            <span className="rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold capitalize text-blue-700">
                                {role}
                            </span>
                        </div>
                        <div className="flex items-center gap-1 mt-0.5">
                            <img src="/brand/logo-mark.png" alt="ModernHustlers" className="h-3 object-contain" />
                        </div>
                    </div>
                )}
            </div>

            {/* Nav Items */}
            <nav className="flex-1 space-y-0.5 overflow-y-auto px-2 py-2">
                {items.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            onClick={() => setMobileOpen(false)}
                            title={collapsed ? item.label : undefined}
                            className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm transition-all duration-150 ${collapsed ? "justify-center" : ""
                                } ${isActive
                                    ? "bg-blue-50 font-semibold text-blue-700 shadow-sm"
                                    : "text-slate-600 hover:bg-slate-50 hover:text-slate-900"
                                }`}
                        >
                            <item.icon className="h-[18px] w-[18px] flex-shrink-0" />
                            {!collapsed && <span className="truncate">{item.label}</span>}
                        </Link>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="border-t border-slate-200 p-2">
                {userName && !collapsed && (
                    <p className="mb-1 truncate px-3 text-xs text-slate-400">
                        {userName}
                    </p>
                )}
                <button
                    onClick={handleLogout}
                    title={collapsed ? "Logout" : undefined}
                    className={`flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-sm text-slate-600 transition-colors hover:bg-red-50 hover:text-red-600 ${collapsed ? "justify-center" : ""
                        }`}
                >
                    <LogOut className="h-[18px] w-[18px] flex-shrink-0" />
                    {!collapsed && "Logout"}
                </button>
            </div>
        </>
    );

    return (
        <>
            {/* ── Mobile top bar ── */}
            <div className="fixed left-0 right-0 top-0 z-50 flex h-14 items-center gap-3 border-b border-slate-200 bg-white px-4 lg:hidden">
                <button
                    onClick={() => setMobileOpen(true)}
                    className="rounded-lg p-2 text-slate-600 hover:bg-slate-100 active:bg-slate-200"
                    aria-label="Open menu"
                >
                    <Menu className="h-5 w-5" />
                </button>
                <GraduationCap className="h-5 w-5 text-blue-700" />
                <div className="flex flex-col justify-center leading-none">
                    <span className="font-bold text-slate-900 text-sm tracking-tight">ModernHustlers</span>
                    <div className="flex items-center gap-1 mt-0.5">
                        <img src="/brand/logo-mark.png" alt="ModernHustlers" className="h-[10px] object-contain" />
                    </div>
                </div>
                <span className="ml-auto rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold capitalize text-blue-700">
                    {role}
                </span>
            </div>

            {/* ── Mobile overlay ── */}
            {mobileOpen && (
                <div
                    className="fixed inset-0 z-50 bg-black/40 backdrop-blur-sm lg:hidden"
                    onClick={() => setMobileOpen(false)}
                />
            )}

            {/* ── Mobile drawer ── */}
            <aside
                className={`fixed left-0 top-0 z-50 flex h-screen w-72 flex-col bg-white shadow-2xl transition-transform duration-300 lg:hidden ${mobileOpen ? "translate-x-0" : "-translate-x-full"
                    }`}
            >
                <div className="flex items-center justify-end p-2">
                    <button
                        onClick={() => setMobileOpen(false)}
                        className="rounded-lg p-2 text-slate-400 hover:bg-slate-100 hover:text-slate-600"
                    >
                        <X className="h-5 w-5" />
                    </button>
                </div>
                {sidebarContent}
            </aside>

            {/* ── Desktop sidebar ── */}
            <aside
                className={`fixed left-0 top-0 z-40 hidden h-screen flex-col border-r border-slate-200 bg-white transition-all duration-200 lg:flex ${sidebarWidth}`}
            >
                {sidebarContent}
                {/* Collapse toggle */}
                <button
                    onClick={() => setCollapsed(!collapsed)}
                    className="absolute -right-3 top-20 z-50 flex h-6 w-6 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-400 shadow-sm hover:text-slate-600 hover:shadow-md transition-all"
                    aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
                >
                    <ChevronLeft className={`h-3 w-3 transition-transform duration-200 ${collapsed ? "rotate-180" : ""}`} />
                </button>
            </aside>

            {/* ── Spacer for content offset ── */}
            <div className={`hidden lg:block flex-shrink-0 transition-all duration-200 ${sidebarWidth}`} />
        </>
    );
}
