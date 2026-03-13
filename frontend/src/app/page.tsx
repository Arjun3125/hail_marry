"use client";

import Link from "next/link";
import {
  BookOpen,
  Brain,
  Shield,
  Users,
  GraduationCap,
  BarChart3,
  FileText,
  ArrowRight,
  School,
  Building,
  Library,
  Network,
  CheckCircle2
} from "lucide-react";

const features = [
  {
    icon: Building,
    title: "1. Core ERP Operations",
    desc: "Complete digital nervous system handling attendance, dynamic scheduling, centralized gradebooks, and digital assignment submittals.",
  },
  {
    icon: Brain,
    title: "2. AI-Powered Student Success",
    desc: "A personalized, 24/7 learning assistant providing curriculum-grounded Q&A, study materials generation (flashcards, concept maps), and interactive Socratic tutoring.",
  },
  {
    icon: BarChart3,
    title: "3. Educator Productivity Tools",
    desc: "Empower teachers with Doubt Heatmaps to see class-wide struggles, automated NCERT-aligned assessment generators, and deep class insights.",
  },
  {
    icon: Users,
    title: "4. Parent Engagement Portal",
    desc: "Bring parents into the loop with transparent performance dashboards, downloadable progress reports, and accessible audio summaries.",
  },
  {
    icon: Shield,
    title: "5. Enterprise Governance & Security",
    desc: "Total control for IT with tenant-scoped data isolation, SAML SSO, complete audit trails, and zero public AI model training.",
  },
];

const audiences = [
  {
    icon: BookOpen,
    title: "Private Tutors & Coaching",
    desc: "Rapid onboarding on our shared cloud for independent educators managing 10 to 150 students. Low friction, instant access.",
  },
  {
    icon: School,
    title: "Standard K-12 Schools",
    desc: "Custom tenant branding and advanced AI analytics designed for standard schools with 200 to 1,000 students seeking to augment existing legacy systems.",
  },
  {
    icon: Library,
    title: "Elite Institutional Chains",
    desc: "Fully white-labeled, physically isolated infrastructure with custom data integrations (Tally, Biometrics) and Active Directory SSO for 1,000+ students.",
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--bg-page)]">
      {/* ───── Navigation ─────────────────── */}
      <nav className="fixed top-0 w-full bg-[var(--bg-page)]/80 backdrop-blur-md border-b border-[var(--border)] z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-7 h-7 text-[var(--primary)]" />
            <div className="flex flex-col justify-center h-full">
              <span className="font-black text-xl tracking-tighter text-[var(--text-primary)] leading-none">VidyaOS</span>
              <span className="text-[10px] font-bold leading-none mt-1">
                By <span className="text-black dark:text-white">Modern</span><span className="text-[#ff3b1f]">Hustlers</span>
              </span>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#solutions" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">
              Who We Serve
            </a>
            <a href="#features" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">
              Capabilities
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">
              How It Works
            </a>
            <Link
              href="/login"
              className="px-5 py-2 border border-[var(--border)] text-[var(--text-primary)] text-sm font-medium rounded-full hover:border-[var(--primary)] transition-colors"
            >
              Login
            </Link>
          </div>
        </div>
      </nav>

      {/* ───── Hero ───────────────────────── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[var(--bg-card)] border border-[var(--border)] text-[var(--text-secondary)] text-sm font-medium mb-6">
            <Network className="w-4 h-4 text-[var(--text-primary)]" />
            VidyaOS: The Digital Nervous System for Education
          </div>
          <h1 className="text-4xl md:text-6xl font-extrabold text-[var(--primary)] tracking-tight leading-[1.1] mb-6">
            AI Infrastructure for
            <span className="text-[var(--text-muted)] block mt-2"> Educational Institutions</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed">
            Bridging the gap between traditional school management and next-generation educational technology. A robust, role-based ERP combined with a deeply integrated, curriculum-grounded AI assistant.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-8 py-3.5 bg-[var(--primary)] text-[var(--bg-page)] font-medium rounded-full hover:bg-[var(--primary-hover)] transition-all shadow-md"
            >
              Access Platform
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#solutions"
              className="inline-flex items-center gap-2 px-8 py-3.5 border border-[var(--border)] text-[var(--text-secondary)] font-medium rounded-full hover:border-[var(--text-primary)] hover:text-[var(--text-primary)] transition-all"
            >
              Explore Solutions
            </a>
          </div>
        </div>
      </section>

      {/* ───── Who We Serve ───────────────────── */}
      <section id="solutions" className="py-20 px-6 bg-[var(--bg-card)] border-y border-[var(--border)]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight mb-4">
              Flexible Deployment Models
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              We offer a hybrid licensing model designed to scale from independent private modern tutors to elite K-12 school chains.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {audiences.map((tier) => (
              <div
                key={tier.title}
                className="glass-panel p-8 rounded-2xl transition-colors hover:border-[var(--text-muted)]"
              >
                <div className="w-12 h-12 bg-[var(--bg-card)] border border-[var(--border)] rounded-xl flex items-center justify-center mb-6">
                  <tier.icon className="w-6 h-6 text-[var(--primary)]" />
                </div>
                <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3 tracking-tight">
                  {tier.title}
                </h3>
                <p className="text-[var(--text-secondary)] leading-relaxed">
                  {tier.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── Features ───────────────────── */}
      <section id="features" className="py-24 px-6 bg-[var(--bg-page)]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight mb-4">
              Key Capabilities
            </h2>
            <p className="text-[var(--text-secondary)] max-w-2xl mx-auto">
              From day-to-day administrative operations to personalized student acceleration, VidyaOS replaces fragmented, disconnected tools with a unified intelligent ecosystem.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f, i) => (
              <div
                key={f.title}
                className={`glass-panel p-8 rounded-2xl transition-all ${i === 4 ? "md:col-span-2 lg:col-span-1" : ""}`}
              >
                <div className="w-10 h-10 bg-[var(--bg-page)] border border-[var(--border)] rounded-lg flex items-center justify-center mb-6">
                  <f.icon className="w-5 h-5 text-[var(--primary)]" />
                </div>
                <h3 className="text-lg font-bold text-[var(--text-primary)] mb-3 tracking-tight">
                  {f.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)] leading-relaxed">
                  {f.desc}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── How It Works ───────────────── */}
      <section id="how-it-works" className="py-24 px-6 bg-[var(--bg-card)] border-t border-[var(--border)]">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-[var(--text-primary)] tracking-tight mb-16">
            The VidyaOS Workflow
          </h2>
          <div className="grid md:grid-cols-4 gap-8">
            {[
              {
                step: "01",
                title: "Setup & Index",
                desc: "Teachers upload syllabus, PDFs, and YouTube links. AI securely indexes the exact curriculum.",
                icon: Shield,
              },
              {
                step: "02",
                title: "Student Learning",
                desc: "Students ask questions and get citation-grounded answers based strictly on teacher materials.",
                icon: Brain,
              },
              {
                step: "03",
                title: "Teacher Feedback",
                desc: "Teachers view Doubt Heatmaps to see struggling areas and generate targeted pop-quizzes.",
                icon: FileText,
              },
              {
                step: "04",
                title: "Parent Transparency",
                desc: "Parents listen to automated audio summaries of progress and track daily attendance.",
                icon: Users,
              },
            ].map((s) => (
              <div key={s.step} className="text-center">
                <div className="w-16 h-16 bg-[var(--bg-page)] border border-[var(--border)] rounded-full flex items-center justify-center mx-auto mb-6">
                  <s.icon className="w-7 h-7 text-[var(--primary)]" />
                </div>
                <div className="text-xs font-black text-[var(--text-muted)] tracking-widest mb-3">
                  STAGE {s.step}
                </div>
                <h3 className="text-lg font-bold text-[var(--text-primary)] mb-3 tracking-tight">
                  {s.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)]">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── Return on Investment ────────────────────── */}
      <section className="py-24 px-6 bg-[var(--bg-page)] border-t border-[var(--border)]">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl font-bold text-[var(--text-primary)] tracking-tight mb-6">
            Why Invest in VidyaOS?
          </h2>
          <div className="grid md:grid-cols-2 gap-8 text-left mt-12">
            <div className="glass-panel p-8 rounded-2xl">
              <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3 flex items-center gap-2 tracking-tight">
                <CheckCircle2 className="w-5 h-5 text-[var(--success)]" />
                Platform Consolidation
              </h3>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                Replaces three or more separate subscriptions. Instead of paying separately for a traditional ERP, a disjointed LMS, and a risky public AI tool, VidyaOS unifies it all under one secure umbrella.
              </p>
            </div>
            <div className="glass-panel p-8 rounded-2xl">
              <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3 flex items-center gap-2 tracking-tight">
                <CheckCircle2 className="w-5 h-5 text-[var(--success)]" />
                Prevent Educator Burnout
              </h3>
              <p className="text-[var(--text-secondary)] leading-relaxed">
                Reduces administrative workload for teachers by an estimated 5-10 hours per week. Automated grading, instantaneous lesson planning tools, and intelligent attendance management keep teachers focused on teaching.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ───── Footer ─────────────────────── */}
      <footer className="py-12 px-6 bg-[var(--bg-card)] border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <GraduationCap className="w-6 h-6 text-[var(--text-primary)]" />
            <div className="flex flex-col justify-center h-full">
              <span className="font-bold text-lg tracking-tight text-[var(--text-primary)] opacity-80 leading-none">VidyaOS</span>
              <span className="text-[10px] font-bold leading-none mt-1 opacity-80">
                By <span className="text-black dark:text-white">Modern</span><span className="text-[#ff3b1f]">Hustlers</span>
              </span>
            </div>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            © 2026 ModernHustlers. AI Infrastructure for Educational Institutions.
          </p>
          <div className="flex gap-6 text-sm font-medium text-[var(--text-secondary)]">
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Privacy</a>
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Terms</a>
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
