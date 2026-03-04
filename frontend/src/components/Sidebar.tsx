"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { GraduationCap, LogOut } from "lucide-react";
import { LucideIcon } from "lucide-react";
import { API_BASE } from "@/lib/api";

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

    const handleLogout = async () => {
        await fetch(`${API_BASE}/api/auth/logout`, {
            method: "POST",
            credentials: "include",
        });
        window.location.href = "/";
    };

    return (
        <aside className="fixed left-0 top-0 z-40 flex h-screen w-60 flex-col border-r border-slate-200 bg-white">
            {/* Logo */}
            <div className="flex h-16 items-center gap-2.5 border-b border-slate-200 px-5">
                <GraduationCap className="h-6 w-6 text-blue-700" />
                <span className="font-semibold text-slate-900">AIaaS</span>
                <span className="ml-auto rounded-full bg-blue-100 px-2 py-0.5 text-[10px] font-semibold capitalize text-blue-700">
                    {role}
                </span>
            </div>

            {/* Nav Items */}
            <nav className="flex-1 space-y-0.5 overflow-y-auto px-3 py-3">
                {items.map((item) => {
                    const isActive = pathname === item.href;
                    return (
                        <Link
                            key={item.href}
                            href={item.href}
                            className={`flex items-center gap-3 rounded-md px-3 py-2.5 text-sm transition-colors ${
                                isActive
                                    ? "border-l-4 border-blue-700 bg-blue-50 font-semibold text-blue-700"
                                    : "text-slate-700 hover:bg-slate-100 hover:text-slate-900"
                                }`}
                        >
                            <item.icon className="h-[18px] w-[18px]" />
                            {item.label}
                        </Link>
                    );
                })}
            </nav>

            {/* User & Logout */}
            <div className="border-t border-slate-200 p-3">
                {userName && (
                    <p className="mb-2 truncate px-3 text-xs text-slate-500">
                        {userName}
                    </p>
                )}
                <button
                    onClick={handleLogout}
                    className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm text-slate-700 transition-colors hover:bg-red-50 hover:text-red-600"
                >
                    <LogOut className="h-[18px] w-[18px]" />
                    Logout
                </button>
            </div>
        </aside>
    );
}
