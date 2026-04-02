"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
    GraduationCap,
    BookOpen,
    Users,
    Shield,
    BarChart3,
    Headphones,
    Presentation,
    Network,
    Brain,
    Sparkles,
    ArrowRight,
    Loader2,
    Play,
} from "lucide-react";
import { API_BASE, setStoredAccessToken, clearDemoSession } from "@/lib/api";

type RoleCard = {
    id: "student" | "teacher" | "admin" | "parent";
    label: string;
    icon: typeof GraduationCap;
    desc: string;
    gradient: string;
    path: string;
    persona: string;
};

const roles: RoleCard[] = [
    {
        id: "student",
        label: "Student",
        icon: GraduationCap,
        desc: "AI assistant, study tools, mind maps, podcasts, video overviews",
        gradient: "from-blue-500 to-indigo-600",
        path: "/student/overview",
        persona: "Naren - Class 11 Science",
    },
    {
        id: "teacher",
        label: "Teacher",
        icon: BookOpen,
        desc: "Assessment generator, doubt heatmap, source discovery, class insights",
        gradient: "from-emerald-500 to-teal-600",
        path: "/teacher/dashboard",
        persona: "Ms. Ananya Sharma - Science Teacher",
    },
    {
        id: "admin",
        label: "Admin",
        icon: Shield,
        desc: "User management, analytics, billing, security, reports",
        gradient: "from-violet-500 to-purple-600",
        path: "/admin/dashboard",
        persona: "Dr. Rajesh Kumar - Principal",
    },
    {
        id: "parent",
        label: "Parent",
        icon: Users,
        desc: "Child dashboard, audio progress report, attendance tracking",
        gradient: "from-amber-500 to-orange-600",
        path: "/parent/dashboard",
        persona: "Mrs. Sharma - Parent of Naren",
    },
];

const quickStartChecklist: Record<RoleCard["id"], string[]> = {
    admin: ["Create classes and sections", "Add teachers/students", "Open admin dashboard health panel"],
    teacher: ["Open today's class", "Mark attendance", "Generate first assessment"],
    student: ["Open AI study assistant", "Ask one cited question", "Review weekly learning path"],
    parent: ["Open child dashboard", "Check attendance trend", "Review weekly action recommendation"],
};

const nextBestActions: Record<RoleCard["id"], string> = {
    admin: "Next best action: complete onboarding checklist to unlock compliance status.",
    teacher: "Next best action: assign one assessment to the selected class.",
    student: "Next best action: practice one weak topic suggested by AI insights.",
    parent: "Next best action: review this week's narrative timeline and suggested follow-up.",
};

const highlights = [
    { icon: Brain, label: "13 AI Modes", desc: "Socratic, debate, exam prep and more" },
    { icon: Headphones, label: "Audio Podcast", desc: "2 AI hosts discuss your notes" },
    { icon: Presentation, label: "Video Slides", desc: "Narrated presentations from notes" },
    { icon: Network, label: "Mind Maps", desc: "Interactive visual topic graphs" },
    { icon: Sparkles, label: "Source Discovery", desc: "Web search to knowledge base" },
    { icon: BarChart3, label: "Full ERP", desc: "Attendance, marks, timetable" },
];


type GuidedStep = {
    step: number;
    title: string;
    path: string;
    clickHint: string;
    outcome: string;
};

const guidedPlaybooks: Record<RoleCard["id"], GuidedStep[]> = {
    admin: [
        { step: 1, title: "Set up school basics", path: "/admin/setup-wizard", clickHint: "Click Setup Wizard in sidebar", outcome: "Core school profile and defaults are configured." },
        { step: 2, title: "Create users", path: "/admin/users", clickHint: "Click Users → Add user", outcome: "Teacher/student/parent accounts are ready." },
        { step: 3, title: "Review system health", path: "/admin/queue", clickHint: "Click Queue dashboard", outcome: "You can monitor AI load and fallback readiness." },
    ],
    teacher: [
        { step: 1, title: "Open class attendance", path: "/teacher/attendance", clickHint: "Click Attendance in sidebar", outcome: "You can mark your first class attendance." },
        { step: 2, title: "Assign assessment", path: "/teacher/generate-assessment", clickHint: "Click Generate assessment", outcome: "First AI-assisted assessment draft is generated." },
        { step: 3, title: "Track class insights", path: "/teacher/insights", clickHint: "Click Insights", outcome: "You can identify weak areas and next actions." },
    ],
    student: [
        { step: 1, title: "Ask AI with citations", path: "/student/ai", clickHint: "Click AI Assistant", outcome: "You get grounded answers with source references." },
        { step: 2, title: "Complete one assignment", path: "/student/assignments", clickHint: "Click Assignments", outcome: "You finish one high-value learning task quickly." },
        { step: 3, title: "Review performance", path: "/student/results", clickHint: "Click Results", outcome: "You see trend and next best study focus." },
    ],
    parent: [
        { step: 1, title: "Check attendance", path: "/parent/attendance", clickHint: "Click Attendance", outcome: "You verify consistency and identify risk early." },
        { step: 2, title: "Review marks", path: "/parent/results", clickHint: "Click Results", outcome: "You identify one immediate support area." },
        { step: 3, title: "Open weekly report", path: "/parent/reports", clickHint: "Click Reports", outcome: "You get actionable narrative guidance for the week." },
    ],
};


const featureCoverage: Record<RoleCard["id"], Array<{ feature: string; path: string }>> = {
    admin: [
        { feature: "Dashboard KPIs", path: "/admin/dashboard" },
        { feature: "User Management", path: "/admin/users" },
        { feature: "Classes", path: "/admin/classes" },
        { feature: "Complaints", path: "/admin/complaints" },
        { feature: "AI Usage", path: "/admin/ai-usage" },
        { feature: "Reports", path: "/admin/reports" },
        { feature: "Queue Monitoring", path: "/admin/queue" },
        { feature: "Settings", path: "/admin/settings" },
    ],
    teacher: [
        { feature: "Dashboard", path: "/teacher/dashboard" },
        { feature: "Attendance", path: "/teacher/attendance" },
        { feature: "Marks", path: "/teacher/marks" },
        { feature: "Assignments", path: "/teacher/assignments" },
        { feature: "Generate Assessment", path: "/teacher/generate-assessment" },
        { feature: "Insights", path: "/teacher/insights" },
        { feature: "Doubt Heatmap", path: "/teacher/doubt-heatmap" },
        { feature: "Upload", path: "/teacher/upload" },
    ],
    student: [
        { feature: "Overview", path: "/student/overview" },
        { feature: "AI Assistant", path: "/student/ai" },
        { feature: "Study Tools", path: "/student/tools" },
        { feature: "Assignments", path: "/student/assignments" },
        { feature: "Results", path: "/student/results" },
        { feature: "Mind Map", path: "/student/mind-map" },
        { feature: "Audio Overview", path: "/student/audio-overview" },
        { feature: "Video Overview", path: "/student/video-overview" },
    ],
    parent: [
        { feature: "Dashboard", path: "/parent/dashboard" },
        { feature: "Attendance", path: "/parent/attendance" },
        { feature: "Results", path: "/parent/results" },
        { feature: "Reports", path: "/parent/reports" },
    ],
};

type DemoProfile = {
    role: "student" | "teacher" | "admin" | "parent";
    persona: string;
    email: string | null;
    landing_path: string;
    feature_showcase: string[];
    walkthrough: Array<{
        step: number;
        title: string;
        path: string;
        outcome: string;
    }>;
};

type DemoProfilesResponse = {
    demo_mode: boolean;
    profiles: DemoProfile[];
    notes?: string[];
};

export default function DemoPage() {
    const router = useRouter();
    const [loading, setLoading] = useState<string | null>(null);
    const [profiles, setProfiles] = useState<DemoProfile[]>([]);
    const [notes, setNotes] = useState<string[]>([]);
    const [profilesLoading, setProfilesLoading] = useState(true);

    useEffect(() => {
        const loadProfiles = async () => {
            try {
                setProfilesLoading(true);
                const res = await fetch(`${API_BASE}/api/demo/profiles`, { credentials: "include" });
                if (!res.ok) throw new Error("Failed to load demo profiles");
                const payload = (await res.json()) as DemoProfilesResponse;
                setProfiles(payload.profiles || []);
                setNotes(payload.notes || []);
            } catch {
                setProfiles(
                    roles.map((r) => ({
                        role: r.id,
                        persona: r.persona,
                        email: null,
                        landing_path: r.path,
                        feature_showcase: [r.desc],
                        walkthrough: guidedPlaybooks[r.id].map((step) => ({
                            step: step.step,
                            title: step.title,
                            path: step.path,
                            outcome: step.outcome,
                        })),
                    }))
                );
                setNotes([]);
            } finally {
                setProfilesLoading(false);
            }
        };
        void loadProfiles();
    }, []);

    const enterAs = async (role: RoleCard) => {
        setLoading(role.id);
        clearDemoSession();
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
            router.push(role.path);
        } catch {
            document.cookie = `demo_role=${role.id}; path=/; max-age=86400`;
            router.push(role.path);
        } finally {
            setLoading(null);
        }
    };

    const [resetting, setResetting] = useState(false);
    const resetDemo = async () => {
        setResetting(true);
        try {
            await fetch(`${API_BASE}/api/demo/reset`, { method: "POST", credentials: "include" });
            clearDemoSession();
            window.location.reload();
        } catch {
            alert("Reset failed — backend may not be running.");
        } finally {
            setResetting(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-indigo-950 to-slate-900 text-white">
            <div className="max-w-5xl mx-auto px-6 pt-16 pb-8 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-1.5 bg-[var(--bg-card)]/10 rounded-full text-xs font-medium mb-6 backdrop-blur-sm border border-white/10">
                    <Play className="w-3 h-3 text-emerald-400" />
                    Interactive Demo - Guided core features live
                </div>
                <h1 className="text-5xl font-extrabold mb-4 leading-tight">
                    <span className="bg-gradient-to-r from-blue-400 via-violet-400 to-pink-400 bg-clip-text text-transparent">
                        VidyaOS - AI Infrastructure for Schools
                    </span>
                </h1>
                <p className="text-lg text-slate-300 max-w-2xl mx-auto leading-relaxed">
                    Privacy-first AI that runs on your school&apos;s own hardware. No data leaves your campus.
                    <br />
                    <span className="text-sm text-slate-400">Choose a role below to explore the full platform.</span>
                </p>
            </div>

            <div className="max-w-5xl mx-auto px-6 mb-12">
                <div className="grid grid-cols-3 md:grid-cols-6 gap-3">
                    {highlights.map((h) => (
                        <div key={h.label} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-3 text-center hover:bg-[var(--bg-card)]/10 transition-all">
                            <h.icon className="w-5 h-5 mx-auto mb-1.5 text-blue-400" />
                            <p className="text-[10px] font-bold text-white">{h.label}</p>
                            <p className="text-[9px] text-slate-400">{h.desc}</p>
                        </div>
                    ))}
                </div>
            </div>

            <div className="max-w-5xl mx-auto px-6 pb-20">
                <h2 className="text-center text-sm font-bold text-slate-400 uppercase tracking-widest mb-6">Explore as</h2>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                    {roles.map((role) => (
                        <button
                            key={role.id}
                            onClick={() => void enterAs(role)}
                            disabled={loading !== null}
                            className="group relative bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-6 text-left hover:bg-[var(--bg-card)]/10 hover:border-white/20 transition-all duration-300 hover:scale-[1.02] disabled:opacity-50 overflow-hidden"
                        >
                            <div className={`absolute inset-0 bg-gradient-to-br ${role.gradient} opacity-0 group-hover:opacity-10 transition-opacity duration-500 rounded-2xl`} />

                            <div className="relative flex items-start gap-4">
                                <div className={`p-3 rounded-xl bg-gradient-to-br ${role.gradient} shadow-lg`}>
                                    <role.icon className="w-6 h-6 text-white" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <div className="flex items-center gap-2 mb-1">
                                        <h3 className="text-lg font-bold text-white">{role.label}</h3>
                                        {loading === role.id ? <Loader2 className="w-4 h-4 animate-spin text-blue-400" /> : null}
                                    </div>
                                    <p className="text-xs text-slate-300 mb-2">{role.persona}</p>
                                    <p className="text-xs text-slate-400">{role.desc}</p>
                                </div>
                                <ArrowRight className="w-5 h-5 text-slate-500 group-hover:text-white group-hover:translate-x-1 transition-all mt-2" />
                            </div>
                        </button>
                    ))}
                </div>

                <div className="mt-12 text-center space-y-2">
                    <p className="text-xs text-slate-500">Demo data auto-generated - No real student information - Reset anytime</p>
                    <p className="text-[10px] text-slate-600">Built with Next.js 16 + FastAPI + Ollama + FAISS</p>
                </div>

                <div className="mt-10 grid grid-cols-1 lg:grid-cols-3 gap-4">
                    <div className="bg-white/5 border border-white/10 rounded-2xl p-5 lg:col-span-2">
                        <h3 className="text-sm font-bold text-white mb-3">Start here checklist by role</h3>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                            {roles.map((role) => (
                                <div key={`checklist-${role.id}`} className="rounded-xl border border-white/10 bg-black/10 p-3">
                                    <p className="text-xs font-semibold text-white mb-2">{role.label}</p>
                                    <ul className="space-y-1.5">
                                        {quickStartChecklist[role.id].map((item) => (
                                            <li key={`${role.id}-${item}`} className="text-xs text-slate-300">• {item}</li>
                                        ))}
                                    </ul>
                                </div>
                            ))}
                        </div>
                    </div>

                    <div className="bg-white/5 border border-white/10 rounded-2xl p-5">
                        <h3 className="text-sm font-bold text-white mb-3">Support + Next best action</h3>
                        <p className="text-xs text-slate-300 mb-3">Use this support prompt when something fails in hosted mode:</p>
                        <div className="rounded-lg bg-black/20 border border-white/10 p-3 text-[11px] text-slate-200 leading-relaxed">
                            Error while saving assessment. Trace ID: <span className="font-mono">TRC-DEMO-1024</span> · Ref ID: <span className="font-mono">REF-CLASS-7A</span>.
                        </div>
                        <div className="mt-3 space-y-1.5">
                            {roles.map((role) => (
                                <p key={`nba-${role.id}`} className="text-[11px] text-slate-300"><span className="font-semibold text-white">{role.label}:</span> {nextBestActions[role.id]}</p>
                            ))}
                        </div>
                    </div>
                </div>


                <div className="mt-10 rounded-2xl border border-white/10 bg-white/5 p-5">
                    <h2 className="text-center text-sm font-bold text-slate-300 uppercase tracking-widest mb-4">
                        Feature & Function Coverage (Demo Data)
                    </h2>
                    <p className="text-xs text-slate-300 text-center mb-4">
                        Demo includes guided data for core workflows across all roles. Advanced integrations may need environment-specific configuration.
                    </p>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        {roles.map((role) => (
                            <div key={`coverage-${role.id}`} className="rounded-xl border border-white/10 bg-black/10 p-3">
                                <p className="text-xs font-bold text-white mb-2">{role.label} coverage</p>
                                <div className="space-y-1.5">
                                    {featureCoverage[role.id].map((item) => (
                                        <a
                                            key={`${role.id}-${item.path}`}
                                            href={item.path}
                                            className="flex items-center justify-between text-[11px] text-slate-300 hover:text-white"
                                        >
                                            <span>{item.feature}</span>
                                            <span className="text-slate-400">{item.path}</span>
                                        </a>
                                    ))}
                                </div>
                            </div>
                        ))}
                    </div>
                </div>

                <div className="mt-14">
                    <h2 className="text-center text-sm font-bold text-slate-400 uppercase tracking-widest mb-6">
                        Demo Profiles and How Features Work
                    </h2>

                    {profilesLoading ? (
                        <div className="flex items-center justify-center py-10 text-slate-400 text-sm">
                            <Loader2 className="w-4 h-4 animate-spin mr-2" />
                            Loading demo walkthrough...
                        </div>
                    ) : (
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            {profiles.map((profile) => {
                                const roleMeta = roles.find((r) => r.id === profile.role) || roles[0];
                                return (
                                    <div key={profile.role} className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl p-5">
                                        <div className="flex items-center gap-3 mb-3">
                                            <div className={`p-2.5 rounded-xl bg-gradient-to-br ${roleMeta.gradient}`}>
                                                <roleMeta.icon className="w-5 h-5 text-white" />
                                            </div>
                                            <div>
                                                <p className="text-sm font-bold text-white capitalize">{profile.role}</p>
                                                <p className="text-xs text-slate-300">{profile.persona}</p>
                                                {profile.email ? <p className="text-[11px] text-slate-400">{profile.email}</p> : null}
                                            </div>
                                        </div>

                                        <div className="mb-4">
                                            <p className="text-[11px] font-semibold text-slate-300 mb-2 uppercase tracking-wide">Function Showcase</p>
                                            <div className="flex flex-wrap gap-2">
                                                {profile.feature_showcase.map((item) => (
                                                    <span key={`${profile.role}-${item}`} className="text-[11px] px-2 py-1 rounded-md bg-[var(--bg-card)]/10 text-slate-200">
                                                        {item}
                                                    </span>
                                                ))}
                                            </div>
                                        </div>

                                        {(profile.walkthrough.length > 0 ? profile.walkthrough : guidedPlaybooks[profile.role]).length > 0 ? (
                                            <div>
                                                <p className="text-[11px] font-semibold text-slate-300 mb-2 uppercase tracking-wide">Guided process (where to click)</p>
                                                <div className="space-y-2">
                                                    {(profile.walkthrough.length > 0 ? profile.walkthrough : guidedPlaybooks[profile.role]).map((step) => {
                                                        const playbook = guidedPlaybooks[profile.role].find((p) => p.step === step.step);
                                                        return (
                                                            <div key={`${profile.role}-${step.step}`} className="rounded-lg border border-white/10 p-2.5 bg-black/10">
                                                                <div className="flex items-center justify-between gap-2">
                                                                    <p className="text-xs text-white font-semibold">{step.step}. {step.title}</p>
                                                                    <a href={step.path} className="text-[10px] text-blue-300 hover:text-blue-200 underline">Open {step.path}</a>
                                                                </div>
                                                                <p className="text-[11px] text-slate-300 mt-1">{playbook?.clickHint || "Use sidebar navigation"}.</p>
                                                                <p className="text-[11px] text-slate-400 mt-1">Expected: {step.outcome}</p>
                                                            </div>
                                                        );
                                                    })}
                                                </div>
                                            </div>
                                        ) : null}
                                    </div>
                                );
                            })}
                        </div>
                    )}

                    {notes.length > 0 ? (
                        <div className="mt-4 bg-white/5 border border-white/10 rounded-xl p-4">
                            <p className="text-[11px] font-semibold text-slate-300 uppercase tracking-wide mb-2">Demo Notes</p>
                            <div className="space-y-1">
                                {notes.map((note) => (
                                    <p key={note} className="text-xs text-slate-300">{note}</p>
                                ))}
                            </div>
                        </div>
                    ) : null}

                    {/* Reset Demo Button */}
                    <div className="mt-6 text-center">
                        <button
                            onClick={() => void resetDemo()}
                            disabled={resetting}
                            className="px-6 py-2.5 bg-white/10 hover:bg-white/20 border border-white/20 rounded-lg text-sm font-medium text-white transition-colors disabled:opacity-50"
                        >
                            {resetting ? "Resetting..." : "🔄 Reset Demo Environment"}
                        </button>
                        <p className="text-[11px] text-slate-400 mt-2">Restores all data to its original demo state.</p>
                    </div>
                </div>
            </div>
        </div>
    );
}
