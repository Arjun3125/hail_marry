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
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

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
    desc: "AI assistant, study tools, revision flows, mind maps, and source-grounded learning workspaces.",
    gradient: "from-sky-400 via-blue-500 to-indigo-500",
    path: "/student/overview",
    persona: "Naren, Class 11 Science",
  },
  {
    id: "teacher",
    label: "Teacher",
    icon: BookOpen,
    desc: "Assessment generation, attendance, material upload, and class-level action surfaces.",
    gradient: "from-emerald-400 via-teal-500 to-cyan-500",
    path: "/teacher/dashboard",
    persona: "Mr. Sharma, Science Faculty",
  },
  {
    id: "admin",
    label: "Admin",
    icon: Shield,
    desc: "Institution monitoring, rollout control, analytics, and operational reliability views.",
    gradient: "from-violet-400 via-purple-500 to-fuchsia-500",
    path: "/admin/dashboard",
    persona: "School Operations Lead",
  },
  {
    id: "parent",
    label: "Parent",
    icon: Users,
    desc: "Progress narrative, attendance visibility, result review, and family-facing action summaries.",
    gradient: "from-amber-300 via-orange-400 to-rose-400",
    path: "/parent/dashboard",
    persona: "Mrs. Sharma, Parent",
  },
];

const highlights = [
  { icon: Brain, label: "Grounded AI", desc: "Q&A, tutoring, revision, and assessment support anchored to school materials." },
  { icon: Headphones, label: "Narrative reporting", desc: "Audio and written summaries for learning and parent communication." },
  { icon: Presentation, label: "Study artifacts", desc: "Video overviews, quizzes, and revision assets generated from source content." },
  { icon: Network, label: "Visual learning", desc: "Mind maps and concept scaffolds for deeper recall and topic exploration." },
  { icon: Sparkles, label: "Role demos", desc: "Each role enters a purpose-built flow instead of a generic preview shell." },
  { icon: Shield, label: "Operations visibility", desc: "Queue, governance, and rollout surfaces remain visible in the same system." },
];

const fallbackPlaybooks: Record<RoleCard["id"], Array<{ step: number; title: string; path: string; outcome: string }>> = {
  student: [
    { step: 1, title: "Open AI Studio", path: "/student/ai-studio", outcome: "Start guided learning with curriculum-grounded AI." },
    { step: 2, title: "Review assignments", path: "/student/assignments", outcome: "See pending work and OCR-assisted submission flows." },
    { step: 3, title: "Check results", path: "/student/results", outcome: "Understand progress trends and next focus areas." },
  ],
  teacher: [
    { step: 1, title: "View dashboard", path: "/teacher/dashboard", outcome: "See classes, workload, and intervention surfaces." },
    { step: 2, title: "Mark attendance", path: "/teacher/attendance", outcome: "Run a daily classroom workflow." },
    { step: 3, title: "Generate assessment", path: "/teacher/generate-assessment", outcome: "Create an AI-assisted assessment draft." },
  ],
  admin: [
    { step: 1, title: "Open command dashboard", path: "/admin/dashboard", outcome: "Review institutional KPIs and operations." },
    { step: 2, title: "Use setup wizard", path: "/admin/setup-wizard", outcome: "See the guided onboarding flow." },
    { step: 3, title: "Review queue health", path: "/admin/queue", outcome: "Inspect reliability and AI job flow." },
  ],
  parent: [
    { step: 1, title: "Open child dashboard", path: "/parent/dashboard", outcome: "See attendance, marks, and next action points." },
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
      alert("Reset failed - backend may not be running.");
    } finally {
      setResetting(false);
    }
  };

  return (
    <PrismPage variant="dashboard" className="pb-12">
      <PrismSection>
        <PrismPageIntro
          kicker={
            <PrismHeroKicker>
              <Play className="h-3.5 w-3.5" />
              Guided Demo
            </PrismHeroKicker>
          }
          title={
            <>
              Enter the product as a real
              <span> student, teacher, admin, or parent</span>
            </>
          }
          description="The demo is seeded with six months of synthetic school activity so each role can validate the actual product flow instead of isolated showcase screens."
          aside={
            <div className="prism-briefing-panel">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">How to use it</p>
              <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">Choose a role, land inside its working surface, and use the guided coverage below to verify the main flows.</p>
              <button
                onClick={() => void resetDemo()}
                disabled={resetting}
                className="prism-action-secondary mt-4"
              >
                {resetting ? "Resetting..." : "Reset demo state"}
              </button>
            </div>
          }
        />

        <div className="prism-status-strip mt-5">
          <div className="prism-status-item">
            <span className="prism-status-label">Coverage</span>
            <span className="prism-status-value">Four role paths</span>
            <span className="prism-status-detail">Student, teacher, admin, and parent each enter a role-aware surface with different priorities.</span>
          </div>
          <div className="prism-status-item">
            <span className="prism-status-label">Data</span>
            <span className="prism-status-value">Seeded history</span>
            <span className="prism-status-detail">Attendance, assignments, results, and reporting are already populated for walkthrough review.</span>
          </div>
          <div className="prism-status-item">
            <span className="prism-status-label">Validation</span>
            <span className="prism-status-value">Task-first</span>
            <span className="prism-status-detail">Every role can validate actual actions, not just static cards or promotional screens.</span>
          </div>
        </div>
      </PrismSection>

      <PrismSection className="mt-8">
        <div className="grid gap-5 lg:grid-cols-[0.92fr_1.08fr]">
          <PrismPanel className="p-5">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">What the demo proves</p>
            <div className="grid gap-3 sm:grid-cols-2">
              {highlights.map((item) => (
                <div key={item.label} className="prism-operational-row">
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.16),rgba(167,139,250,0.12))]">
                    <item.icon className="h-5 w-5 text-[var(--text-primary)]" />
                  </div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">{item.label}</p>
                  <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.desc}</p>
                </div>
              ))}
            </div>
          </PrismPanel>

          <PrismPanel className="p-5">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Choose a role</p>
            <div className="grid gap-3">
              {roles.map((role) => (
                <button
                  key={role.id}
                  onClick={() => void enterAs(role)}
                  disabled={loading !== null}
                  className="group prism-operational-row text-left transition-colors hover:border-[var(--border-strong)]"
                >
                  <div className="flex items-start gap-4">
                    <div className={`flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${role.gradient} shadow-[0_14px_28px_rgba(2,6,23,0.16)]`}>
                      <role.icon className="h-5 w-5 text-[#06101e]" />
                    </div>
                    <div className="flex-1">
                      <div className="mb-1 flex items-center gap-2">
                        <h2 className="text-base font-semibold text-[var(--text-primary)]">{role.label}</h2>
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

      <PrismSection className="mt-8">
        <PrismPanel className="p-6">
          <div className="mb-5 flex items-center justify-between gap-4">
            <div>
              <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Guided coverage</p>
              <h2 className="prism-title text-3xl font-bold text-[var(--text-primary)]">What each persona can validate in the demo</h2>
            </div>
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
                  <div key={profile.role} className="prism-support-panel rounded-[calc(var(--radius)*0.9)] p-5">
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
                        <div key={`${profile.role}-${step.step}`} className="prism-operational-row">
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
            <div className="prism-support-panel mt-4 rounded-[var(--radius-sm)] p-4">
              <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Demo notes</p>
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
