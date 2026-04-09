"use client";

import dynamic from "next/dynamic";
import Link from "next/link";
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
  Users,
} from "lucide-react";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

const PrismHeroScene = dynamic(
  () => import("@/components/prism/PrismHeroScene").then((mod) => mod.PrismHeroScene),
  {
    ssr: false,
    loading: () => (
      <div className="relative h-[320px] w-full overflow-hidden rounded-[calc(var(--radius)*1.2)] border border-[var(--border)] bg-[linear-gradient(135deg,rgba(96,165,250,0.12),rgba(167,139,250,0.08))] shadow-[var(--shadow-card)]" />
    ),
  },
);

const productProof = [
  {
    icon: Building,
    title: "Institution control",
    body: "Attendance, scheduling, complaints, governance, and reports stay inside one operational layer.",
  },
  {
    icon: Brain,
    title: "Grounded AI",
    body: "Responses, study flows, and classroom assistance stay tied to school-provided material and citations.",
  },
  {
    icon: Network,
    title: "Role-aware product",
    body: "Student, teacher, parent, and admin surfaces each serve a different job without fragmenting the system.",
  },
];

const roleViews = [
  {
    icon: GraduationCap,
    title: "Students",
    body: "Ask from notes, revise weak concepts, generate study artifacts, and stay inside a single learning workspace.",
  },
  {
    icon: BookOpen,
    title: "Teachers",
    body: "Upload material, manage attendance, generate assessments, and act on insight surfaces without context switching.",
  },
  {
    icon: Users,
    title: "Parents",
    body: "See attendance, results, and narrative reports in a calmer, action-oriented family view.",
  },
  {
    icon: Building,
    title: "Admins",
    body: "Monitor queue health, rollout quality, branding, policy, and school-level visibility with operational clarity.",
  },
];

const deploymentModels = [
  {
    icon: BookOpen,
    title: "Tutors and coaching",
    body: "Fast onboarding, compact operations, and guided AI study flows from day one.",
  },
  {
    icon: School,
    title: "K-12 schools",
    body: "One system for classroom work, school control, parent visibility, and learning support.",
  },
  {
    icon: Library,
    title: "Institution chains",
    body: "Branding, governance, and deployment control for multi-campus operations.",
  },
];

const outcomes = [
  "One shell for ERP-style operations and AI-assisted learning.",
  "Less teacher workflow friction through guided actions and insight surfaces.",
  "More parent confidence through narrative, source-backed reporting.",
  "Stronger administrative control over reliability, adoption, and policy.",
];

export default function LandingPage() {
  return (
    <PrismPage variant="report" className="pb-12">
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
          <div className="flex items-center gap-3 md:gap-8">
            <a href="#proof" className="hidden text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)] md:inline-flex">Proof</a>
            <a href="#roles" className="hidden text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)] md:inline-flex">Roles</a>
            <a href="#deployments" className="hidden text-sm text-[var(--text-secondary)] transition-colors hover:text-[var(--text-primary)] md:inline-flex">Deployments</a>
            <Link
              href="/login"
              className="prism-action !px-4 !py-2 text-xs md:!px-4 md:!py-2.5 md:text-sm"
            >
              Login To Platform <ArrowRight className="h-4 w-4" />
            </Link>
          </div>
        </div>
      </nav>

      <PrismSection className="pt-10">
        <PrismPageIntro
          kicker={
            <PrismHeroKicker>
              <Building className="h-3.5 w-3.5" />
              School Operating System
            </PrismHeroKicker>
          }
          title={
            <>
              One product for classroom work,
              <span> family visibility, and school control</span>
            </>
          }
          description="VidyaOS combines role-aware operations with curriculum-grounded AI so students, teachers, parents, and administrators work inside one coherent system instead of separate tools."
          aside={
            <div className="prism-briefing-panel">
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Demo contract</p>
              <p className="mt-2 text-base font-semibold text-[var(--text-primary)]">Six months of synthetic school history, guided role entry, and grounded AI workflows.</p>
              <div className="prism-empty-actions mt-4 justify-start">
                <Link href="/demo" className="prism-action">
                  Explore demo <ArrowRight className="h-4 w-4" />
                </Link>
                <Link href="/login" className="prism-action-secondary">
                  Login To Platform
                </Link>
              </div>
            </div>
          }
        />

        <div className="prism-status-strip mt-5">
          <div className="prism-status-item">
            <span className="prism-status-label">Grounding</span>
            <span className="prism-status-value">Notebook and citation aware</span>
            <span className="prism-status-detail">AI responses stay attached to school-provided materials and visible source context.</span>
          </div>
          <div className="prism-status-item">
            <span className="prism-status-label">Demo data</span>
            <span className="prism-status-value">Six months seeded</span>
            <span className="prism-status-detail">Attendance, results, assignments, and role-specific activity are already populated for walkthroughs.</span>
          </div>
          <div className="prism-status-item">
            <span className="prism-status-label">Role surfaces</span>
            <span className="prism-status-value">Student to admin</span>
            <span className="prism-status-detail">Each role enters a surface tuned to daily work rather than a generic dashboard shell.</span>
          </div>
        </div>
      </PrismSection>

      <PrismSection id="proof" className="mt-8">
        <div className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]">
          <PrismPanel className="p-5 md:p-6">
            <PrismHeroScene />
          </PrismPanel>
          <div className="grid gap-4">
            {productProof.map((item) => (
              <PrismPanel key={item.title} className="prism-operational-card p-5">
                <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.16),rgba(167,139,250,0.12))]">
                  <item.icon className="h-5 w-5 text-[var(--text-primary)]" />
                </div>
                <div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                  <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.body}</p>
                </div>
              </PrismPanel>
            ))}
          </div>
        </div>
      </PrismSection>

      <PrismSection id="roles" className="mt-8">
        <div className="mb-4">
          <p className="mb-2 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Role entry</p>
          <h2 className="prism-title text-3xl font-bold text-[var(--text-primary)] md:text-4xl">Each role sees one system through a different operational lens</h2>
        </div>
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          {roleViews.map((item) => (
            <PrismPanel key={item.title} className="prism-operational-card p-5">
              <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.15),rgba(125,211,252,0.11))]">
                <item.icon className="h-5 w-5 text-[var(--text-primary)]" />
              </div>
              <div>
                <p className="text-base font-semibold text-[var(--text-primary)]">{item.title}</p>
                <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.body}</p>
              </div>
            </PrismPanel>
          ))}
        </div>
      </PrismSection>

      <PrismSection id="deployments" className="mt-8">
        <div className="grid gap-5 lg:grid-cols-[1.1fr_0.9fr]">
          <PrismPanel className="p-6">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Deployment fit</p>
            <div className="grid gap-4 md:grid-cols-3">
              {deploymentModels.map((item) => (
                <div key={item.title} className="prism-operational-row">
                  <div className="mb-3 flex h-10 w-10 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.16),rgba(103,232,249,0.12))]">
                    <item.icon className="h-5 w-5 text-[var(--text-primary)]" />
                  </div>
                  <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                  <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">{item.body}</p>
                </div>
              ))}
            </div>
          </PrismPanel>

          <PrismPanel className="p-6">
            <p className="mb-3 text-[11px] font-bold uppercase tracking-[0.26em] text-[var(--text-muted)]">Why schools adopt it</p>
            <div className="space-y-3">
              {outcomes.map((item) => (
                <div key={item} className="prism-operational-row">
                  <div className="flex gap-3">
                    <CheckCircle2 className="mt-0.5 h-4 w-4 flex-shrink-0 text-[var(--accent-indigo)]" />
                    <p className="text-sm leading-6 text-[var(--text-secondary)]">{item}</p>
                  </div>
                </div>
              ))}
            </div>
          </PrismPanel>
        </div>
      </PrismSection>
    </PrismPage>
  );
}
