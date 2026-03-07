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
  Sparkles,
  ArrowRight,
  CheckCircle2,
} from "lucide-react";

const features = [
  {
    icon: Brain,
    title: "AI-Powered Q&A",
    desc: "Students ask questions about uploaded notes. AI answers with citations from source material.",
  },
  {
    icon: FileText,
    title: "Study Guide Generator",
    desc: "Automatically generate structured study guides from curriculum documents.",
  },
  {
    icon: Sparkles,
    title: "Smart Quiz Builder",
    desc: "AI creates quizzes from your notes with answer keys and explanations.",
  },
  {
    icon: BarChart3,
    title: "Performance Analytics",
    desc: "Track student performance, identify weak topics, and generate targeted remediation.",
  },
  {
    icon: Shield,
    title: "Privacy-First",
    desc: "Your school's data stays isolated. Multi-tenant architecture with strict security.",
  },
  {
    icon: Users,
    title: "Multi-Tenant ERP",
    desc: "Attendance, marks, assignments, timetable, complaints — all in one platform.",
  },
];

const pricingTiers = [
  {
    name: "Basic",
    price: "₹5,000",
    period: "/month",
    features: ["Attendance tracking", "Marks & results", "Timetable", "Complaint portal"],
    popular: false,
  },
  {
    name: "Pro",
    price: "₹12,000",
    period: "/month",
    features: [
      "Everything in Basic",
      "AI Q&A (50 queries/day)",
      "Study Guide generation",
      "Quiz builder",
      "Document upload",
    ],
    popular: true,
  },
  {
    name: "Advanced",
    price: "₹25,000",
    period: "/month",
    features: [
      "Everything in Pro",
      "Weak topic intelligence",
      "Concept maps",
      "AI usage analytics",
      "Custom AI credits",
    ],
    popular: false,
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-white">
      {/* ───── Navigation ─────────────────── */}
      <nav className="fixed top-0 w-full bg-white/80 backdrop-blur-md border-b border-[var(--border)] z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-7 h-7 text-[var(--primary)]" />
            <div className="flex flex-col justify-center leading-none">
              <span className="text-xl font-semibold text-[var(--text-primary)]">
                VidyaOS
              </span>
              <span className="text-[10px] font-bold text-orange-600 tracking-wider uppercase mt-0.5">
                By ModernHustlers
              </span>
            </div>
          </div>
          <div className="hidden md:flex items-center gap-8">
            <a href="#features" className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">
              Features
            </a>
            <a href="#pricing" className="text-sm text-[var(--text-secondary)] hover:text-[var(--primary)] transition-colors">
              Pricing
            </a>
            <Link
              href="/login"
              className="px-5 py-2 bg-[var(--primary)] text-white text-sm font-medium rounded-[var(--radius-sm)] hover:bg-[var(--primary-hover)] transition-colors"
            >
              Login
            </Link>
          </div>
        </div>
      </nav>

      {/* ───── Hero ───────────────────────── */}
      <section className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto text-center">
          <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-[var(--primary-light)] text-[var(--primary)] text-sm font-medium mb-6">
            <Sparkles className="w-4 h-4" />
            AI-Powered Educational Intelligence
          </div>
          <h1 className="text-4xl md:text-6xl font-bold text-[var(--text-primary)] leading-tight mb-6">
            Your School&apos;s
            <span className="text-[var(--primary)]"> AI Study Partner</span>
          </h1>
          <p className="text-lg md:text-xl text-[var(--text-secondary)] max-w-2xl mx-auto mb-10 leading-relaxed">
            Upload your notes. Ask questions. Get citation-grounded answers.
            Built for Indian schools with complete ERP, privacy-first AI, and
            intelligent performance tracking.
          </p>
          <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
            <Link
              href="/login"
              className="inline-flex items-center gap-2 px-8 py-3.5 bg-[var(--primary)] text-white font-medium rounded-[var(--radius)] hover:bg-[var(--primary-hover)] transition-all shadow-md hover:shadow-lg"
            >
              Get Started
              <ArrowRight className="w-4 h-4" />
            </Link>
            <a
              href="#features"
              className="inline-flex items-center gap-2 px-8 py-3.5 border border-[var(--border)] text-[var(--text-secondary)] font-medium rounded-[var(--radius)] hover:border-[var(--primary)] hover:text-[var(--primary)] transition-all"
            >
              See Features
            </a>
          </div>
        </div>
      </section>

      {/* ───── Features ───────────────────── */}
      <section id="features" className="py-20 px-6 bg-[var(--bg-page)]">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-3xl font-bold text-[var(--text-primary)] mb-4">
              Everything Your School Needs
            </h2>
            <p className="text-[var(--text-secondary)] max-w-xl mx-auto">
              From day-to-day ERP operations to AI-powered learning — one platform for everything.
            </p>
          </div>
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((f) => (
              <div
                key={f.title}
                className="bg-white p-6 rounded-[var(--radius)] shadow-[var(--shadow-card)] hover:shadow-[var(--shadow-md)] transition-shadow"
              >
                <div className="w-10 h-10 bg-[var(--primary-light)] rounded-[var(--radius-sm)] flex items-center justify-center mb-4">
                  <f.icon className="w-5 h-5 text-[var(--primary)]" />
                </div>
                <h3 className="text-base font-semibold text-[var(--text-primary)] mb-2">
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
      <section className="py-20 px-6 bg-white">
        <div className="max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-[var(--text-primary)] mb-16">
            How It Works
          </h2>
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                step: "01",
                title: "Upload Notes",
                desc: "Teachers upload PDF notes, DOCX files, or paste YouTube lecture links.",
                icon: BookOpen,
              },
              {
                step: "02",
                title: "AI Processes",
                desc: "Documents are chunked, embedded, and indexed in your school's private vector DB.",
                icon: Brain,
              },
              {
                step: "03",
                title: "Students Learn",
                desc: "Students ask questions and get citation-grounded answers from their own materials.",
                icon: GraduationCap,
              },
            ].map((s) => (
              <div key={s.step} className="text-center">
                <div className="w-14 h-14 bg-[var(--primary-light)] rounded-full flex items-center justify-center mx-auto mb-4">
                  <s.icon className="w-6 h-6 text-[var(--primary)]" />
                </div>
                <div className="text-xs font-bold text-[var(--primary)] tracking-widest mb-2">
                  STEP {s.step}
                </div>
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                  {s.title}
                </h3>
                <p className="text-sm text-[var(--text-secondary)]">{s.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── Pricing ────────────────────── */}
      <section id="pricing" className="py-20 px-6 bg-[var(--bg-page)]">
        <div className="max-w-5xl mx-auto">
          <h2 className="text-3xl font-bold text-center text-[var(--text-primary)] mb-4">
            Simple, Transparent Pricing
          </h2>
          <p className="text-center text-[var(--text-secondary)] mb-16">
            Per school, per month. No hidden fees.
          </p>
          <div className="grid md:grid-cols-3 gap-6">
            {pricingTiers.map((tier) => (
              <div
                key={tier.name}
                className={`bg-white rounded-[var(--radius)] p-8 shadow-[var(--shadow-card)] relative ${tier.popular ? "ring-2 ring-[var(--primary)]" : ""
                  }`}
              >
                {tier.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 bg-[var(--primary)] text-white text-xs font-medium rounded-full">
                    Most Popular
                  </div>
                )}
                <h3 className="text-lg font-semibold text-[var(--text-primary)] mb-2">
                  {tier.name}
                </h3>
                <div className="flex items-baseline gap-1 mb-6">
                  <span className="text-3xl font-bold text-[var(--text-primary)]">
                    {tier.price}
                  </span>
                  <span className="text-sm text-[var(--text-secondary)]">
                    {tier.period}
                  </span>
                </div>
                <ul className="space-y-3 mb-8">
                  {tier.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-[var(--text-secondary)]">
                      <CheckCircle2 className="w-4 h-4 text-[var(--success)] mt-0.5 shrink-0" />
                      {f}
                    </li>
                  ))}
                </ul>
                <Link
                  href="/login"
                  className={`block text-center py-2.5 rounded-[var(--radius-sm)] text-sm font-medium transition-colors ${tier.popular
                    ? "bg-[var(--primary)] text-white hover:bg-[var(--primary-hover)]"
                    : "border border-[var(--border)] text-[var(--text-secondary)] hover:border-[var(--primary)] hover:text-[var(--primary)]"
                    }`}
                >
                  Get Started
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ───── Footer ─────────────────────── */}
      <footer className="py-12 px-6 bg-white border-t border-[var(--border)]">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row items-center justify-between gap-4">
          <div className="flex items-center gap-2">
            <GraduationCap className="w-5 h-5 text-[var(--primary)]" />
            <div className="flex flex-col justify-center leading-none">
              <span className="font-semibold text-[var(--text-primary)]">VidyaOS</span>
              <span className="text-[10px] font-bold text-orange-600 tracking-wider uppercase mt-1">By ModernHustlers</span>
            </div>
          </div>
          <p className="text-sm text-[var(--text-muted)]">
            © 2026 VidyaOS by ModernHustlers. AI Infrastructure for Educational Institutions.
          </p>
          <div className="flex gap-6 text-sm text-[var(--text-secondary)]">
            <a href="#" className="hover:text-[var(--primary)]">Privacy</a>
            <a href="#" className="hover:text-[var(--primary)]">Terms</a>
            <a href="#" className="hover:text-[var(--primary)]">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
