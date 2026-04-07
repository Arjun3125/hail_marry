"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  ArrowRight,
  BookOpen,
  Brain,
  GraduationCap,
  Headphones,
  Loader2,
  Network,
  Play,
  Presentation,
  Shield,
  Sparkles,
  Users,
} from "lucide-react";
import { API_BASE, clearDemoSession, setStoredAccessToken } from "@/lib/api";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

type RoleCard = {
  id: "student" | "teacher" | "admin" | "parent";
  label: string;
  icon: typeof GraduationCap;
  desc: string;
  gradient: string;
  path: string;
  persona: string;
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

const roles: RoleCard[] = [
  {
    id: "student",
    label: "Student",
    icon: GraduationCap,
    desc: "AI assistant, study tools, revision flows, mind maps, audio and video overviews.",
    gradient: "from-sky-400 via-blue-500 to-indigo-500",
    path: "/student/overview",
    persona: "Naren, Class 11 Science",
  },
  {
    id: "teacher",
    label: "Teacher",
    icon: BookOpen,
    desc: "Assessment generation, doubt heatmap, upload intelligence, and class-level action surfaces.",
    gradient: "from-emerald-400 via-teal-500 to-cyan-500",
    path: "/teacher/dashboard",
    persona: "Mr. Sharma, Science Faculty",
  },
  {
    id: "admin",
    label: "Admin",
    icon: Shield,
    desc: "Institution monitoring, rollout control, analytics, governance, and operational reliability.",
    gradient: "from-violet-400 via-purple-500 to-fuchsia-500",
    path: "/admin/dashboard",
    persona: "School Operations Lead",
  },
  {
    id: "parent",
    label: "Parent",
    icon: Users,
    desc: "Progress narrative, attendance clarity, result visibility, and action-oriented family reporting.",
    gradient: "from-amber-300 via-orange-400 to-rose-400",
    path: "/parent/dashboard",
    persona: "Mrs. Sharma, Parent",
  },
];

const highlights = [
  { icon: Brain, label: "13 AI modes", desc: "Socratic tutoring, Q&A, debate, exam prep." },
  { icon: Headphones, label: "Audio summaries", desc: "AI-generated narrative reports and learning recaps." },
  { icon: Presentation, label: "Video overviews", desc: "Slide-led learning generated from source material." },
  { icon: Network, label: "Mind maps", desc: "Spatial topic exploration for revision and retention." },
  { icon: Sparkles, label: "Source discovery", desc: "Find and ground new study material quickly." },
  { icon: Shield, label: "Operational control", desc: "Role-aware dashboards with governance and visibility." },
];

const fallbackPlaybooks: Record<RoleCard["id"], Array<{ step: number; title: string; path: string; outcome: string }>> = {
  student: [
    { step: 1, title: "Open AI Studio", path: "/student/ai-studio", outcome: "Start guided learning with curriculum-grounded AI." },
    { step: 2, title: "Review assignments", path: "/student/assignments", outcome: "See pending work and OCR-assisted submission flows." },
    { step: 3, title: "Check results", path: "/student/results", outcome: "Understand progress trends and next focus areas." },
  ],
  teacher: [
    { step: 1, title: "View dashboard", path: "/teacher/dashboard", outcome: "See classes, workload, and insight surfaces." },
    { step: 2, title: "Mark attendance", path: "/teacher/attendance", outcome: "Run a daily classroom workflow." },
    { step: 3, title: "Generate assessment", path: "/teacher/generate-assessment", outcome: "Create an AI-assisted assessment draft." },
  ],
  admin: [
    { step: 1, title: "Open command dashboard", path: "/admin/dashboard", outcome: "Review institutional KPIs and operations." },
    { step: 2, title: "Use setup wizard", path: "/admin/setup-wizard", outcome: "See the guided onboarding flow." },
    { step: 3, title: "Review queue health", path: "/admin/queue", outcome: "Inspect reliability and AI job flow." },
  ],
  parent: [
    { step: 1, title: "Open child dashboard", path: "/parent/dashboard", outcome: "See attendance, marks, and next class." },
    { step: 2, title: "Check attendance", path: "/parent/attendance", outcome: "Review consistency and risk." },
    { step: 3, title: "Read reports", path: "/parent/reports", outcome: "Open narrative progress reporting." },
  ],
};

export default function DemoPage() {
  const router = useRouter();
  const [loading, setLoading] = useState<string | null>(null);
  const [profiles, setProfiles] = useState<DemoProfile[]>([]);
  const [notes, setNotes] = useState<string[]>([]);
  const [profilesLoading, setProfilesLoading] = useState(true);
  const [resetting, setResetting] = useState(false);

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
          roles.map((role) => ({
            role: role.id,
            persona: role.persona,
            email: null,
            landing_path: role.path,
            feature_showcase: [role.desc],
            walkthrough: fallbackPlaybooks[role.id],
          })),
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
    <PrismPage className="pb-12">
      <PrismSection>
        <div className="grid gap-8 lg:grid-cols-[1.05fr_0.95fr]">
          <div className="space-y-6">
            <PrismHeroKicker>
              <Play className="h-3.5 w-3.5" />
              Interactive Demo Experience
            </PrismHeroKicker>
            <div className="space-y-4">
              <h1 className="prism-title text-5xl font-black leading-[0.96] text-[var(--text-primary)] md:text-6xl">
                Walk the product through four{" "}
                <span className="premium-gradient">role-specific realities</span>
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-[var(--text-secondary)]">
                Explore the product the way an actual institution experiences it: student, teacher, admin, and parent all move through different surfaces with different priorities.
              </p>
            </div>
            <div className="grid gap-3 sm:grid-cols-2">
              {highlights.map((item) => (
                <PrismPanel key={item.label} className="flex gap-3 p-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(167,139,250,0.12))]">
                    <item.icon className="h-5 w-5 text-[var(--text-primary)]" />
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-[var(--text-primary)]">{item.label}</p>
                    <p className="text-xs leading-6 text-[var(--text-secondary)]">{item.desc}</p>
                  </div>
                </PrismPanel>
              ))}
            </div>
          </div>

          <PrismPanel className="p-6">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Experience Portal</p>
            <div className="grid gap-4">
              {roles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => void enterAs(role)}
                  disabled={loading !== null}
                  className="group relative overflow-hidden rounded-[calc(var(--radius)*0.9)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-5 text-left transition-all hover:-translate-y-1 hover:border-[var(--border-strong)]"
                >
                  <div className={`absolute inset-0 bg-gradient-to-br ${role.gradient} opacity-10 transition-opacity group-hover:opacity-20`} />
                  <div className="relative flex items-start gap-4">
                    <div className={`flex h-13 w-13 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${role.gradient} shadow-[0_18px_36px_rgba(2,6,23,0.2)]`}>
                      <role.icon className="h-6 w-6 text-[#06101e]" />
                    </div>
                    <div className="flex-1">
                      <div className="mb-1 flex items-center gap-2">
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">{role.label}</h2>
                        {loading === role.id ? <Loader2 className="h-4 w-4 animate-spin text-status-blue" /> : null}
                      </div>
                      <p className="text-xs font-medium text-[var(--text-muted)]">{role.persona}</p>
                      <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{role.desc}</p>
                    </div>
                    <ArrowRight className="mt-1 h-4 w-4 text-[var(--text-muted)] transition-transform group-hover:translate-x-1 group-hover:text-[var(--text-primary)]" />
                  </div>
                </button>
              ))}
            </div>
          </PrismPanel>
        </div>
      </PrismSection>

      <PrismSection className="mt-10">
        <PrismPanel className="p-6">
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Guided Coverage</p>
              <h2 className="prism-title text-3xl font-bold text-[var(--text-primary)]">What each persona can validate in the demo</h2>
            </div>
            <button
              onClick={() => void resetDemo()}
              disabled={resetting}
              className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-4 py-2.5 text-sm font-semibold text-[var(--text-primary)]"
            >
              {resetting ? "Resetting..." : "Reset demo"}
            </button>
          </div>

          {profilesLoading ? (
            <div className="flex items-center justify-center py-10 text-sm text-[var(--text-secondary)]">
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Loading demo walkthrough...
            </div>
          ) : (
            <div className="grid gap-4 md:grid-cols-2">
              {profiles.map((profile) => {
                const roleMeta = roles.find((r) => r.id === profile.role) || roles[0];
                const walkthrough = profile.walkthrough.length > 0 ? profile.walkthrough : fallbackPlaybooks[profile.role];
                return (
                  <div key={profile.role} className="rounded-[calc(var(--radius)*0.9)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-5">
                    <div className="mb-4 flex items-center gap-3">
                      <div className={`flex h-11 w-11 items-center justify-center rounded-2xl bg-gradient-to-br ${roleMeta.gradient}`}>
                        <roleMeta.icon className="h-5 w-5 text-[#06101e]" />
                      </div>
                      <div>
                        <p className="text-sm font-semibold capitalize text-[var(--text-primary)]">{profile.role}</p>
                        <p className="text-xs text-[var(--text-secondary)]">{profile.persona}</p>
                        {profile.email ? <p className="text-[11px] text-[var(--text-muted)]">{profile.email}</p> : null}
                      </div>
                    </div>

                    <div className="mb-4 flex flex-wrap gap-2">
                      {profile.feature_showcase.map((item) => (
                        <span key={`${profile.role}-${item}`} className="rounded-full bg-[rgba(96,165,250,0.12)] px-2.5 py-1 text-[11px] text-[var(--text-primary)]">
                          {item}
                        </span>
                      ))}
                    </div>

                    <div className="space-y-2">
                      {walkthrough.map((step) => (
                        <div key={`${profile.role}-${step.step}`} className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-3">
                          <div className="mb-1 flex items-center justify-between gap-3">
                            <p className="text-xs font-semibold text-[var(--text-primary)]">
                              {step.step}. {step.title}
                            </p>
                            <a href={step.path} className="text-[10px] font-semibold text-status-blue hover:underline">
                              Open
                            </a>
                          </div>
                          <p className="text-xs leading-6 text-[var(--text-secondary)]">{step.outcome}</p>
                        </div>
                      ))}
                    </div>
                  </div>
                );
              })}
            </div>
          )}

          {notes.length > 0 ? (
            <div className="mt-4 rounded-[var(--radius-sm)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-4">
              <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Demo Notes</p>
              <div className="space-y-1">
                {notes.map((note) => (
                  <p key={note} className="text-sm text-[var(--text-secondary)]">{note}</p>
                ))}
              </div>
            </div>
          ) : null}
        </PrismPanel>
      </PrismSection>
    </PrismPage>
  );
}

