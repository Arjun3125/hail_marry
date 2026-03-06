"use client";

import { useState } from "react";
import { useRouter, usePathname } from "next/navigation";
import { Users, RotateCcw, GraduationCap, BookOpen, Shield, Loader2, X } from "lucide-react";
import { API_BASE } from "@/lib/api";
import { useToast } from "./Toast";

const roles = [
    { id: "student", label: "Student", icon: GraduationCap, path: "/student/overview", color: "bg-blue-500" },
    { id: "teacher", label: "Teacher", icon: BookOpen, path: "/teacher/dashboard", color: "bg-emerald-500" },
    { id: "admin", label: "Admin", icon: Shield, path: "/admin/dashboard", color: "bg-violet-500" },
    { id: "parent", label: "Parent", icon: Users, path: "/parent/dashboard", color: "bg-amber-500" },
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
            await fetch(`${API_BASE}/api/auth/demo-login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ role: role.id }),
            });
        } catch {
            document.cookie = `demo_role=${role.id}; path=/; max-age=86400`;
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
            {/* Floating pill button */}
            <button
                onClick={() => setOpen(!open)}
                className="fixed bottom-4 right-4 z-50 flex items-center gap-2 px-3 py-2 sm:px-4 sm:py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 text-white text-[11px] sm:text-xs font-bold rounded-full shadow-xl hover:shadow-2xl hover:scale-105 transition-all safe-bottom"
            >
                <span className={`w-2 h-2 rounded-full ${currentRole.color} animate-pulse`} />
                <span className="hidden sm:inline">DEMO:</span> {currentRole.label}
            </button>

            {/* Panel */}
            {open && (
                <div className="fixed bottom-14 right-4 z-50 w-[calc(100vw-2rem)] sm:w-72 max-w-72 bg-white rounded-2xl shadow-2xl border border-slate-200 overflow-hidden animate-[fadeIn_0.15s_ease-out]">
                    <div className="bg-gradient-to-r from-indigo-600 to-violet-600 px-4 py-3 flex items-center justify-between">
                        <span className="text-xs font-bold text-white">Demo Controls</span>
                        <button onClick={() => setOpen(false)} className="text-white/70 hover:text-white">
                            <X className="w-4 h-4" />
                        </button>
                    </div>
                    <div className="p-3 space-y-2">
                        <p className="text-[10px] font-bold text-slate-400 uppercase tracking-wider">Switch Role</p>
                        {roles.map((role) => (
                            <button
                                key={role.id}
                                onClick={() => void switchRole(role)}
                                disabled={switching !== null}
                                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${currentRole.id === role.id
                                    ? "bg-indigo-50 text-indigo-700 ring-1 ring-indigo-200"
                                    : "text-slate-600 hover:bg-slate-50"
                                    }`}
                            >
                                <role.icon className="w-4 h-4" />
                                {role.label}
                                {switching === role.id && <Loader2 className="w-3 h-3 animate-spin ml-auto" />}
                                {currentRole.id === role.id && <span className="ml-auto text-[9px] text-indigo-400">Active</span>}
                            </button>
                        ))}
                        <hr className="border-slate-100" />
                        <button
                            onClick={() => void resetDemo()}
                            disabled={resetting}
                            className="w-full flex items-center justify-center gap-2 px-3 py-2.5 text-xs font-bold text-red-600 bg-red-50 rounded-xl hover:bg-red-100 transition-all disabled:opacity-50"
                        >
                            {resetting ? <Loader2 className="w-3 h-3 animate-spin" /> : <RotateCcw className="w-3 h-3" />}
                            Reset Demo Data
                        </button>
                    </div>
                </div>
            )}
        </>
    );
}
