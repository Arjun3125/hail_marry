"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
import { motion, useReducedMotion } from "framer-motion";
import {
  ArrowRight,
  BookOpen,
  Brain,
  Building,
  CheckCircle2,
  GraduationCap,
  Library,
  Network,
  School,
  Sparkles,
  Users,
} from "lucide-react";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

const PrismHeroScene = dynamic(
  () => import("@/components/prism/PrismHeroScene").then((mod) => mod.PrismHeroScene),
  {
    ssr: false,
    loading: () => (
      <div className="relative h-[360px] w-full overflow-hidden rounded-[calc(var(--radius)*1.2)] border border-[var(--border)] bg-[linear-gradient(135deg,rgba(96,165,250,0.16),rgba(167,139,250,0.12))] shadow-[var(--shadow-card)]" />
    ),
  },
);

const platformPillars = [
  {
    icon: Building,
    title: "Institutional Command",
    body: "Attendance, scheduling, assessments, complaints, governance, and reporting live in one coherent operating system.",
  },
  {
    icon: Brain,
    title: "Curriculum-Grounded AI",
    body: "Students and staff work with AI that stays tied to school-provided materials and traceable workflows.",
  },
  {
    icon: Network,
    title: "Role-Aware Experience",
    body: "Student, teacher, admin, and parent journeys feel purpose-built instead of squeezed into one generic dashboard shell.",
  },
];

const deploymentModels = [
  {
    icon: BookOpen,
    title: "Tutors & Coaching",
    body: "Fast onboarding, compact operations, and immediate access to AI-assisted teaching surfaces.",
  },
  {
    icon: School,
    title: "K-12 Schools",
    body: "Multi-role workflows, branding, and guided rollout for schools modernizing beyond legacy ERP alone.",
  },
  {
    icon: Library,
    title: "Institutional Chains",
    body: "White-labeled deployment, governance, integrations, and stricter infrastructure control.",
  },
];

const outcomes = [
  "Consolidates ERP, LMS, and AI-assisted learning into one operational layer.",
  "Cuts teacher workflow friction through guided AI actions and structured insights.",
  "Gives parents a narrative, confidence-building view into student progress.",
  "Keeps administrators in control of reliability, policy, and adoption signals.",
];

export default function LandingPage() {
  const reducedMotion = Boolean(useReducedMotion());

  return (
    <PrismPage className="pb-12">
      <nav className="fixed inset-x-0 top-0 z-40 border-b border-[var(--border)] bg-[rgba(8,14,28,0.72)] backdrop-blur-2xl">
        <div className="mx-auto flex h-18 max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(167,139,250,0.92))] shadow-[0_18px_34px_rgba(96,165,250,0.22)]">
              <GraduationCap className="h-6 w-6 text-[#07111f]" />
            </div>
            <div>
              <p className="prism-title text-xl font-bold text-[var(--text-primary)]">VidyaOS</p>
              <p className="text-[10px] font-bold uppercase tracking-[0.3em] text-[var(--text-muted)]">ModernHustlers</p>
            </div>
          </div>
          <div className="hidden items-center gap-8 md:flex">
            <a href="#platform" className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)]">Platform</a>
            <a href="#deployments" className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)]">Deployments</a>
            <a href="#outcomes" className="text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)]">Outcomes</a>
            <Link
              href="/login"
              className="inline-flex items-center gap-2 rounded-full border border-[rgba(191,219,254,0.18)] bg-[linear-gradient(135deg,rgba(96,165,250,0.92),rgba(129,140,248,0.92))] px-5 py-2.5 text-sm font-semibold text-[#06101e] shadow-[0_18px_34px_rgba(96,165,250,0.2)]"
            >
              Access Platform <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </nav>

      <PrismSection className="pt-10">
        <div className="grid items-center gap-8 lg:grid-cols-[1.05fr_0.95fr]">
          <motion.div
            initial={reducedMotion ? false : { opacity: 0, y: 18 }}
            animate={reducedMotion ? undefined : { opacity: 1, y: 0 }}
            transition={reducedMotion ? { duration: 0 } : { duration: 0.45 }}
            className="space-y-7"
          >
            <PrismHeroKicker>
              <Sparkles className="h-3.5 w-3.5" />
              Premium AI Infrastructure For Schools
            </PrismHeroKicker>
            <div className="space-y-5">
              <h1 className="prism-title text-5xl font-black leading-[0.95] text-[var(--text-primary)] md:text-7xl">
                A more immersive operating system for{" "}
                <span className="premium-gradient">teaching, learning, and school control</span>
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-[var(--text-secondary)]">
                VidyaOS brings together school operations, curriculum-grounded AI, and role-aware workflows in one product surface that feels premium enough for demos and practical enough for daily use.
              </p>
            </div>
            <div className="flex flex-col gap-3 sm:flex-row">
              <Link
                href="/demo"
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[rgba(191,219,254,0.18)] bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-6 py-3.5 text-sm font-semibold text-[#06101e] shadow-[0_20px_42px_rgba(96,165,250,0.22)]"
              >
                Explore Guided Demo <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-6 py-3.5 text-sm font-semibold text-[var(--text-primary)]"
              >
                Login To Platform
              </Link>
            </div>
            <div className="grid gap-3 sm:grid-cols-3">
              {platformPillars.map((pillar) => (
                <PrismPanel key={pillar.title} className="p-4">
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.18),rgba(167,139,250,0.14))]">
                    <pillar.icon className="h-5 w-5 text-[var(--text-primary)]" />
                  </div>
                  <h2 className="mb-1 text-sm font-semibold text-[var(--text-primary)]">{pillar.title}</h2>
                  <p className="text-sm leading-6 text-[var(--text-secondary)]">{pillar.body}</p>
                </PrismPanel>
              ))}
            </div>
          </motion.div>

          <motion.div
            initial={reducedMotion ? false : { opacity: 0, scale: 0.98 }}
            animate={reducedMotion ? undefined : { opacity: 1, scale: 1 }}
            transition={reducedMotion ? { duration: 0 } : { duration: 0.55, delay: 0.08 }}
            className="space-y-5"
          >
            <PrismHeroScene />
            <div className="grid gap-4 md:grid-cols-2">
              <PrismPanel className="p-5">
                <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Student Experience</p>
                <p className="text-lg font-semibold text-[var(--text-primary)]">AI Studio, guided learning, weak-topic recovery, and document-grounded responses.</p>
              </PrismPanel>
              <PrismPanel className="p-5">
                <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Institution Control</p>
                <p className="text-lg font-semibold text-[var(--text-primary)]">Queue health, compliance, branding, reports, and multi-role operating surfaces.</p>
              </PrismPanel>
            </div>
          </motion.div>
        </div>
      </PrismSection>

      <PrismSection id="deployments" className="mt-12">
        <div className="mb-6 flex items-end justify-between gap-4">
          <div>
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Flexible Deployment Models</p>
            <h2 className="prism-title text-3xl font-bold text-[var(--text-primary)] md:text-4xl">One product, multiple institutional entry points</h2>
          </div>
        </div>
        <div className="grid gap-5 lg:grid-cols-3">
          {deploymentModels.map((model) => (
            <PrismPanel key={model.title} className="p-6">
              <div className="mb-5 flex h-12 w-12 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.16),rgba(103,232,249,0.12))]">
                <model.icon className="h-6 w-6 text-[var(--text-primary)]" />
              </div>
              <h3 className="mb-2 text-2xl font-semibold text-[var(--text-primary)]">{model.title}</h3>
              <p className="text-sm leading-7 text-[var(--text-secondary)]">{model.body}</p>
            </PrismPanel>
          ))}
        </div>
      </PrismSection>

      <PrismSection id="platform" className="mt-12">
        <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]">
          <PrismPanel className="p-7">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">How VidyaOS Works</p>
            <div className="grid gap-4 md:grid-cols-2">
              {[
                "Teachers upload materials and define the curriculum boundary.",
                "Students get grounded AI help, study tools, and revision workflows.",
                "Teachers act on insight surfaces instead of searching across tools.",
                "Admins and parents get visibility without losing operational clarity.",
              ].map((step, index) => (
                <div key={index} className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-4">
                  <div className="mb-3 flex h-9 w-9 items-center justify-center rounded-full bg-[rgba(96,165,250,0.12)] text-sm font-bold text-status-blue">
                    0{index + 1}
                  </div>
                  <p className="text-sm leading-6 text-[var(--text-secondary)]">{step}</p>
                </div>
              ))}
            </div>
          </PrismPanel>
          <PrismPanel id="outcomes" className="p-7">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Why Institutions Buy In</p>
            <div className="space-y-4">
              {outcomes.map((outcome) => (
                <div key={outcome} className="flex gap-3 rounded-[var(--radius-sm)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-4">
                  <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-[var(--accent-indigo)]" />
                  <p className="text-sm leading-6 text-[var(--text-secondary)]">{outcome}</p>
                </div>
              ))}
            </div>
          </PrismPanel>
        </div>
      </PrismSection>

      <PrismSection className="mt-12">
        <PrismPanel className="flex flex-col items-start justify-between gap-5 p-8 md:flex-row md:items-center">
          <div className="max-w-2xl">
            <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Ready To Experience It</p>
            <h2 className="prism-title text-3xl font-bold text-[var(--text-primary)]">See the role-aware product flow, not just isolated screens.</h2>
          </div>
          <div className="flex gap-3">
            <Link href="/demo" className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-5 py-3 text-sm font-semibold text-[#06101e]">
              Enter Demo <Users className="h-4 w-4" />
            </Link>
            <Link href="/login" className="inline-flex items-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-5 py-3 text-sm font-semibold text-[var(--text-primary)]">
              Open Login
            </Link>
          </div>
        </PrismPanel>
      </PrismSection>
    </PrismPage>
  );
}
