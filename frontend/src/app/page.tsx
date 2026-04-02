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
  CheckCircle2,
  Sparkles
} from "lucide-react";

const features = [
  {
    icon: Building,
    title: "Core ERP Operations",
    desc: "Complete digital nervous system handling attendance, dynamic scheduling, centralized gradebooks, and digital assignment submittals.",
    gradient: "from-blue-500/20 to-indigo-500/20",
  },
  {
    icon: Brain,
    title: "AI-Powered Student Success",
    desc: "A personalized, 24/7 learning assistant providing curriculum-grounded Q&A, study materials generation (flashcards, concept maps), and interactive Socratic tutoring.",
    gradient: "from-purple-500/20 to-pink-500/20",
  },
  {
    icon: BarChart3,
    title: "Educator Productivity Tools",
    desc: "Empower teachers with Doubt Heatmaps to see class-wide struggles, automated NCERT-aligned assessment generators, and deep class insights.",
    gradient: "from-amber-500/20 to-orange-500/20",
  },
  {
    icon: Users,
    title: "Parent Engagement Portal",
    desc: "Bring parents into the loop with transparent performance dashboards, downloadable progress reports, and accessible audio summaries.",
    gradient: "from-emerald-500/20 to-teal-500/20",
  },
  {
    icon: Shield,
    title: "Enterprise Governance & Security",
    desc: "Total control for IT with tenant-scoped data isolation, SAML SSO, complete audit trails, and zero public AI model training.",
    gradient: "from-slate-500/20 to-gray-500/20",
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
    <div className="min-h-screen bg-[var(--bg-page)] relative overflow-hidden">
      
      {/* ───── Background Glowing Gradients ─────────────────── */}
      <div className="absolute top-0 left-0 w-full h-[600px] overflow-hidden -z-10 pointer-events-none">
         <div className="absolute top-[-20%] left-[-10%] w-[50%] h-[80%] rounded-full bg-indigo-600/10 blur-[120px]" />
         <div className="absolute top-[10%] right-[-10%] w-[40%] h-[60%] rounded-full bg-cyan-600/10 blur-[120px]" />
      </div>

      {/* ───── Navigation ─────────────────── */}
      <nav className="fixed top-0 w-full bg-[var(--bg-page)]/70 backdrop-blur-xl border-b border-[var(--border)] z-50 transition-all duration-300">
        <div className="max-w-7xl mx-auto px-6 h-[72px] flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-indigo-500 to-cyan-500 flex items-center justify-center shadow-lg shadow-indigo-500/20">
              <GraduationCap className="w-6 h-6 text-white" />
            </div>
            <div className="flex flex-col justify-center h-full">
              <span className="font-black text-xl tracking-tighter text-[var(--text-primary)] leading-none">VidyaOS</span>
              <span className="text-[10px] font-bold leading-none mt-1 opacity-80">
                By <span className="text-black dark:text-white">Modern</span><span className="text-[#ff3b1f]">Hustlers</span>
              </span>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#solutions" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Who We Serve
            </a>
            <a href="#features" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              Capabilities
            </a>
            <a href="#how-it-works" className="text-sm font-medium text-[var(--text-secondary)] hover:text-[var(--text-primary)] transition-colors">
              How It Works
            </a>
            <Link
              href="/login"
              className="px-6 py-2.5 glass-panel text-[var(--text-primary)] text-sm font-semibold rounded-full hover:border-[var(--primary)] hover:shadow-[0_0_15px_rgba(var(--primary-rgb),0.2)] transition-all flex items-center gap-2"
            >
              Login <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        </div>
      </nav>

      {/* ───── Hero ───────────────────────── */}
      <section className="pt-40 pb-24 px-6 relative">
        <div className="max-w-5xl mx-auto text-center stagger-1">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full glass-panel border-[var(--border)] text-[var(--primary)] shadow-[0_0_20px_rgba(var(--primary-rgb),0.1)] text-sm font-medium mb-8">
            <Sparkles className="w-4 h-4" />
            Vidya Prism UI Now Live
          </div>
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight leading-[1.05] mb-8">
            <span className="text-[var(--text-primary)]">AI Infrastructure for</span>
            <br />
            <span className="premium-gradient">Educational Institutions</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed font-light">
            Bridging the gap between traditional school management and next-generation educational technology. A robust, role-based ERP combined with a deeply integrated, curriculum-grounded AI assistant.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-5">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-8 py-4 bg-[var(--text-primary)] text-[var(--bg-page)] font-semibold rounded-full hover:scale-105 transition-transform shadow-xl"
            >
              Access Platform
              <ArrowRight className="w-5 h-5" />
            </Link>
            <a
              href="#solutions"
              className="inline-flex items-center gap-2 px-8 py-4 glass-panel text-[var(--text-primary)] font-semibold rounded-full hover:border-[var(--border-strong)] transition-all"
            >
              Explore Solutions
            </a>
          </div>
        </div>
      </section>

      {/* ───── Who We Serve ───────────────────── */}
      <section id="solutions" className="py-24 px-6 relative z-10 border-t border-[var(--border)] bg-gradient-to-b from-[var(--bg-page)] to-[var(--bg-card)]">
        <div className="max-w-6xl mx-auto stagger-2">
          <div className="text-center mb-16">
            <h2 className="text-4xl font-bold text-[var(--text-primary)] tracking-tight mb-4">
              Flexible Deployment Models
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto text-lg">
              We offer a hybrid licensing model designed to scale from independent tutors to elite K-12 school chains.
            </p>
          </div>
          <div className="grid md:grid-cols-3 gap-6">
            {audiences.map((tier, idx) => (
              <div
                key={tier.title}
                className="glass-panel p-8 rounded-3xl transition-all duration-300 hover:-translate-y-2 hover:shadow-2xl hover:shadow-[var(--primary)]/5 relative overflow-hidden group"
              >
                <div className="absolute inset-0 bg-gradient-to-br from-[var(--primary)]/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity" />
                <div className="w-14 h-14 glass-panel border-[var(--border)] rounded-2xl flex items-center justify-center mb-6 text-[var(--primary)] group-hover:scale-110 transition-transform">
                  <tier.icon className="w-7 h-7" />
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
      <section id="features" className="py-32 px-6 bg-[var(--bg-page)] relative">
        <div className="max-w-6xl mx-auto stagger-3">
          <div className="text-center mb-20">
            <h2 className="text-4xl font-bold text-[var(--text-primary)] tracking-tight mb-4">
              Key Capabilities
            </h2>
            <p className="text-[var(--text-secondary)] max-w-2xl mx-auto text-lg">
              From day-to-day administrative operations to personalized student acceleration, VidyaOS replaces fragmented, disconnected tools.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {features.map((f, i) => (
              <div
                key={f.title}
                className={`glass-panel p-8 rounded-3xl transition-all duration-300 hover:shadow-xl relative overflow-hidden group ${i === 4 ? "md:col-span-2 lg:col-span-1" : ""}`}
              >
                <div className={`absolute top-0 right-0 w-32 h-32 bg-gradient-to-br ${f.gradient} blur-3xl opacity-50 group-hover:opacity-100 transition-opacity`} />
                <div className="relative z-10">
                   <div className="w-12 h-12 bg-[var(--bg-card)] border border-[var(--border)] rounded-xl flex items-center justify-center mb-6 shadow-inner">
                     <f.icon className="w-6 h-6 text-[var(--text-primary)]" />
                   </div>
                   <h3 className="text-xl font-bold text-[var(--text-primary)] mb-3 tracking-tight">
                     {f.title}
                   </h3>
                   <p className="text-[var(--text-secondary)] leading-relaxed">
                     {f.desc}
                   </p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── How It Works ───────────────── */}
      <section id="how-it-works" className="py-24 px-6 bg-[var(--bg-card)] border-t border-[var(--border)] relative z-10">
        <div className="absolute inset-0 bg-[url('https://www.transparenttextures.com/patterns/cubes.png')] opacity-[0.02]" />
        <div className="max-w-6xl mx-auto relative z-10 stagger-4">
          <h2 className="text-4xl font-bold text-center text-[var(--text-primary)] tracking-tight mb-20">
            The VidyaOS Workflow
          </h2>
          <div className="grid md:grid-cols-4 gap-12 md:gap-8">
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
            ].map((s, idx) => (
              <div key={s.step} className="relative text-center group">
                {idx !== 3 && (
                   <div className="hidden md:block absolute top-10 left-[60%] w-[80%] h-[2px] bg-gradient-to-r from-[var(--border-strong)] to-transparent" />
                )}
                <div className="w-20 h-20 glass-panel border-[var(--border-strong)] rounded-full flex items-center justify-center mx-auto mb-8 relative z-10 group-hover:scale-110 transition-transform shadow-xl shadow-[var(--bg-page)]">
                  <s.icon className="w-8 h-8 text-[var(--primary)]" />
                </div>
                <div className="text-xs font-black premium-text tracking-widest mb-3">
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
      <section className="py-32 px-6 bg-[var(--bg-page)] border-t border-[var(--border)] overflow-hidden">
        <div className="max-w-5xl mx-auto text-center stagger-5 relative">
           <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-primary/5 rounded-full blur-[100px] -z-10" />
           <h2 className="text-4xl md:text-5xl font-bold text-[var(--text-primary)] tracking-tight mb-8">
            Why Invest in VidyaOS?
          </h2>
          <div className="grid md:grid-cols-2 gap-8 text-left mt-16">
            <div className="glass-panel p-10 rounded-3xl border border-[var(--border-strong)] shadow-2xl">
              <div className="w-12 h-12 rounded-full bg-[var(--success)]/10 flex items-center justify-center mb-6">
                 <CheckCircle2 className="w-6 h-6 text-[var(--success)]" />
              </div>
              <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-4 tracking-tight">
                Platform Consolidation
              </h3>
              <p className="text-[var(--text-secondary)] text-lg leading-relaxed">
                Replaces three or more separate subscriptions. Instead of paying separately for a traditional ERP, a disjointed LMS, and a risky public AI tool, VidyaOS unifies it all under one secure umbrella.
              </p>
            </div>
            <div className="glass-panel p-10 rounded-3xl border border-[var(--border-strong)] shadow-2xl">
              <div className="w-12 h-12 rounded-full bg-[var(--success)]/10 flex items-center justify-center mb-6">
                 <CheckCircle2 className="w-6 h-6 text-[var(--success)]" />
              </div>
              <h3 className="text-2xl font-bold text-[var(--text-primary)] mb-4 tracking-tight">
                Prevent Educator Burnout
              </h3>
              <p className="text-[var(--text-secondary)] text-lg leading-relaxed">
                Reduces administrative workload for teachers by an estimated 5-10 hours per week. Automated grading, instantaneous lesson planning tools, and intelligent attendance management keep teachers focused on teaching.
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* ───── Footer ─────────────────────── */}
      <footer className="py-12 px-6 bg-[var(--bg-card)] border-t border-[var(--border)]">
        <div className="max-w-7xl mx-auto flex flex-col md:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
             <div className="w-8 h-8 rounded-lg bg-[var(--text-primary)] flex items-center justify-center">
              <GraduationCap className="w-5 h-5 text-[var(--bg-page)]" />
             </div>
            <div className="flex flex-col justify-center h-full">
              <span className="font-bold text-lg tracking-tight text-[var(--text-primary)] leading-none">VidyaOS</span>
              <span className="text-[10px] font-bold leading-none mt-1 opacity-80 text-[var(--text-secondary)]">
                AI Infrastructure for Education
              </span>
            </div>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            © 2026 ModernHustlers. All rights reserved.
          </p>
          <div className="flex gap-8 text-sm font-medium text-[var(--text-secondary)]">
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Privacy</a>
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Terms</a>
            <a href="#" className="hover:text-[var(--text-primary)] transition-colors">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}

