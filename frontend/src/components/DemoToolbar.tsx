"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Users, RotateCcw, GraduationCap, BookOpen, Shield, Loader2, X, Sparkles } from "lucide-react";
import { API_BASE, clearDemoSession, setStoredAccessToken } from "@/lib/api";
import { useToast } from "./Toast";

const roles = [
    { id: "student", label: "Student", icon: GraduationCap, path: "/student/overview", color: "bg-sky-500" },
    { id: "teacher", label: "Teacher", icon: BookOpen, path: "/teacher/dashboard", color: "bg-emerald-500" },
    { id: "admin", label: "Admin", icon: Shield, path: "/admin/dashboard", color: "bg-violet-500" },
    { id: "parent", label: "Parent", icon: Users, path: "/parent/dashboard", color: "bg-orange-500" },
];
const salesBeats = [
    "Pain recognition: show the chaos of running a school with separate tools.",
    "Single system: show School Health and live operations.",
    "Depth proof: open AI Studio with citations.",
    "Parent trust: show the WhatsApp-style parent summary.",
    "Call to action: reset or switch roles for the next prospect question.",
];

export default function DemoToolbar() {
    const router = useRouter();
    const pathname = usePathname();
    const [open, setOpen] = useState(false);
    const [resetting, setResetting] = useState(false);
    const [switching, setSwitching] = useState<string | null>(null);
    const { toast } = useToast();

    // Only show on portal pages, not on /demo or /login
    if (!pathname || pathname === "/" || pathname === "/demo" || pathname === "/login") return null;

    const currentRole = roles.find((r) => pathname.startsWith(`/${r.id}`)) || roles[0];

    const switchRole = async (role: typeof roles[0]) => {
        setSwitching(role.id);
        try {
            await fetch(`${API_BASE}/api/demo/switch-role`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ role: role.id }),
            });
            const loginRes = await fetch(`${API_BASE}/api/auth/demo-login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ role: role.id }),
            });
            const payload = await loginRes.json().catch(() => ({} as { access_token?: string }));
            if ((payload as { access_token?: string }).access_token) {
                setStoredAccessToken((payload as { access_token: string }).access_token);
            }
        } catch {
            // Best effort: continue routing even if backend calls fail.
        }
        router.push(role.path);
        toast(`Switched to ${role.label} view`, "success");
        setSwitching(null);
        setOpen(false);
    };

    const resetDemo = async () => {
        setResetting(true);
        try {
            await fetch(`${API_BASE}/api/demo/reset`, {
                method: "POST",
                credentials: "include",
            });
        } catch {
            /* best effort */
        }
        setResetting(false);
        toast("Demo data reset successfully", "success");
        router.push("/demo");
    };

    return (
        <>
            <button
                onClick={() => setOpen(!open)}
                className="fixed right-4 z-50 flex items-center gap-2 rounded-full bg-gradient-to-r from-indigo-600 to-violet-600 px-3 py-2 text-[11px] font-bold text-white shadow-xl transition-all hover:scale-105 hover:shadow-2xl sm:px-4 sm:py-2.5 sm:text-xs"
                style={{ bottom: "calc(var(--bottom-nav-height, 4.5rem) + 1rem)" }}
            >
                <span className={`w-2 h-2 rounded-full ${currentRole.color} animate-pulse`} />
                <span className="hidden sm:inline">DEMO MODE | Viewing as:</span> {currentRole.label}
            </button>

            {open && (
                <div 
                    className="fixed right-4 z-50 w-[calc(100vw-2rem)] sm:w-72 max-w-72 bg-[var(--bg-card)] rounded-2xl shadow-2xl border border-[var(--border)] overflow-hidden animate-[fadeIn_0.15s_ease-out]"
                    style={{ bottom: "calc(var(--bottom-nav-height, 4.5rem) + 3.5rem)" }}
                >
                    <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-3 flex items-center justify-between">
                        <span className="text-xs font-bold text-white">DEMO MODE | Viewing as: {currentRole.label}</span>
                        <button onClick={() => setOpen(false)} className="text-white/70 hover:text-white">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                    <div className="p-3 space-y-2">
                        <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Switch Role</p>
                        {roles.map((role) => (
                            <button
                                key={role.id}
                                onClick={() => void switchRole(role)}
                                disabled={switching !== null}
                                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${currentRole.id === role.id
                                    ? "bg-indigo-badge text-status-indigo ring-1 ring-[var(--primary)]/30"
                                    : "text-[var(--text-secondary)] hover:bg-[var(--bg-page)]"
                                    }`}
                            >
                                <role.icon className="w-4 h-4" />
                                {role.label}
                                {switching === role.id && <Loader2 className="w-3 h-3 animate-spin ml-auto" />}
                                {currentRole.id === role.id && <span className="ml-auto text-[9px] text-status-indigo">Active</span>}
                            </button>
                        ))}
                        <hr className="border-[var(--border)]" />
                        <div className="rounded-xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-3">
                            <p className="text-[10px] font-bold uppercase tracking-wider text-[var(--text-muted)]">5-beat demo script</p>
                            <div className="mt-2 space-y-1.5">
                                {salesBeats.map((beat, index) => (
                                    <p key={beat} className="text-[10px] leading-4 text-[var(--text-secondary)]">
                                        {index + 1}. {beat}
                                    </p>
                                ))}
                            </div>
                        </div>
                        <button
                            onClick={() => {
                                window.dispatchEvent(new Event("start-guided-tour"));
                                setOpen(false);
                            }}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 text-xs font-bold text-status-indigo bg-indigo-500 rounded-xl hover:bg-indigo-badge transition-all"
                        >
                            <Sparkles className="h-3.5 w-3.5" />
                            Highlight Features
                        </button>
                        <button
                            onClick={() => void resetDemo()}
                            disabled={resetting}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 text-xs font-bold text-status-red bg-error-subtle rounded-xl hover:bg-error-badge transition-all disabled:opacity-50"
                        >
                            {resetting ? <Loader2 className="w-3 h-3 animate-spin" /> : <RotateCcw className="w-3 h-3" />}
                            Reset Demo Data
                        </button>
                        <button
                            onClick={() => {
                                clearDemoSession();
                                router.push("/login");
                                setOpen(false);
                            }}
                            className="w-full flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] px-3 py-2.5 text-xs font-bold text-[var(--text-secondary)] transition-all hover:bg-[var(--bg-page)]"
                        >
                            End Demo
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
