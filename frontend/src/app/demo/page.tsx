"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import {
    GraduationCap, BookOpen, Users, Shield, BarChart3,
    Headphones, Presentation, Network, Brain, Sparkles,
    ArrowRight, Loader2, Play,
} from "lucide-react";
import { API_BASE } from "@/lib/api";

const roles = [
    {
        id: "student",
        label: "Student",
        icon: GraduationCap,
        desc: "AI assistant, study tools, mind maps, podcasts, video overviews",
        gradient: "from-blue-500 to-indigo-600",
        path: "/student/overview",
        persona: "Arjun Patel — Class 10-A",
    },
    {
        id: "teacher",
        label: "Teacher",
        icon: BookOpen,
        desc: "Assessment generator, doubt heatmap, source discovery, class insights",
        gradient: "from-emerald-500 to-teal-600",
        path: "/teacher/dashboard",
        persona: "Ms. Ananya Sharma — Science Teacher",
    },
    {
        id: "admin",
        label: "Admin",
        icon: Shield,
        desc: "User management, analytics, billing, security, reports",
        gradient: "from-violet-500 to-purple-600",
        path: "/admin/dashboard",
        persona: "Dr. Rajesh Kumar — Principal",
    },
    {
        id: "parent",
        label: "Parent",
        icon: Users,
        desc: "Child dashboard, audio progress report, attendance tracking",
        gradient: "from-amber-500 to-orange-600",
        path: "/parent/dashboard",
        persona: "Mr. Vikram Patel — Parent of Arjun",
    },
];

const highlights = [
    { icon: Brain, label: "13 AI Modes", desc: "Socratic, debate, exam prep & more" },
    { icon: Headphones, label: "Audio Podcast", desc: "2 AI hosts discuss your notes" },
    { icon: Presentation, label: "Video Slides", desc: "Narrated presentations from notes" },
    { icon: Network, label: "Mind Maps", desc: "Interactive visual topic graphs" },
    { icon: Sparkles, label: "Source Discovery", desc: "Web search → knowledge base" },
    { icon: BarChart3, label: "Full ERP", desc: "Attendance, marks, timetable" },
];

export default function DemoPage() {
    const router = useRouter();
    const [loading, setLoading] = useState<string | null>(null);

    const enterAs = async (role: typeof roles[0]) => {
        setLoading(role.id);
        try {
            await fetch(`${API_BASE}/api/demo/switch-role`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ role: role.id }),
            });
            // Also set via demo login for JWT cookie
            await fetch(`${API_BASE}/api/auth/demo-login`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ role: role.id }),
            });
            router.push(role.path);
        } catch {
            // Backend may not need JWT in demo mode, just redirect
            document.cookie = `demo_role=${role.id}; path=/; max-age=86400`;
            router.push(role.path);
        } finally {
            setLoading(null);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
            {/* Hero */}
            <div className="max-w-5xl mx-auto px-6 pt-16 pb-8 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-white/10 rounded-full text-xs font-medium mb-6 backdrop-blur-sm border border-white/10">
                    <Play className="w-3 h-3 text-emerald-400" />
                    Interactive Demo — All features live
                </div>
                <h1 className="text-5xl font-extrabold mb-4 leading-tight">
                    <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-pink-400 bg-clip-text text-transparent">
                        AIaaS — AI Infrastructure for Schools
                    </span>
                </h1>
                <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
                    Privacy-first AI that runs on your school&apos;s own hardware. No data leaves your campus.
                    <br />
                    <span className="text-sm text-slate-400">Choose a role below to explore the full platform.</span>
                </p>
            </div>

            {/* Feature Highlights */}
            <div className="max-w-5xl mx-auto px-6 mb-12">
                <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                    {highlights.map((h, i) => (
                        <div key={i} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-3 text-center hover:bg-white/10 transition-all">
                            <h.icon className="w-5 h-5 mx-auto mb-1.5 text-blue-400" />
                            <p className="text-[10px] font-bold text-white">{h.label}</p>
                            <p className="text-[9px] text-slate-400">{h.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            {/* Role Picker */}
            <div className="max-w-5xl mx-auto px-6 pb-20">
                <h2 className="text-center text-sm font-bold text-slate-400 uppercase tracking-widest mb-6">
                    Explore as
                </h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {roles.map((role) => (
                        <button
                            key={role.id}
                            onClick={() => void enterAs(role)}
                            disabled={loading !== null}
                            className={`group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-left hover:bg-white/10 hover:border-white/20 transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 overflow-hidden`}
                        >
                            {/* Gradient glow */}
                            <div className={`absolute inset-0 bg-gradient-to-br ${role.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500 rounded-2xl`} />

                            <div className="relative flex items-start gap-4">
                                <div className={`p-3 rounded-xl bg-gradient-to-br ${role.gradient} shadow-lg`}>
                                    <role.icon className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className="text-lg font-bold text-white">{role.label}</h3>
                                        {loading === role.id && <Loader2 className="w-4 h-4 animate-spin text-blue-400" />}
                                    </div>
                                    <p className="text-xs text-slate-300 mb-2">{role.persona}</p>
                                    <p className="text-xs text-slate-400">{role.desc}</p>
                                </div>
                                <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all mt-2" />
                            </div>
                        </button>
                    ))}
                </div>

                {/* Bottom info */}
                <div className="mt-12 text-center space-y-2">
                    <p className="text-xs text-slate-500">
                        Demo data auto-generated • No real student information • Reset anytime
                    </p>
                    <p className="text-[10px] text-slate-600">
                        Built with Next.js 16 + FastAPI + Ollama + FAISS • Runs on ₹30K school hardware
                    </p>
                </div>
            </div>
        </div>
    );
}
