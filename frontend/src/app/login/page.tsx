"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { GraduationCap, Loader2, QrCode, Sparkles } from "lucide-react";
import { api, API_BASE, clearDemoSession, setStoredAccessToken } from "@/lib/api";
import { getRoleDashboard } from "@/lib/auth";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";

declare global {
  interface Window {
    google?: {
      accounts: {
        id: {
          initialize: (config: Record<string, unknown>) => void;
          renderButton: (element: HTMLElement, config: Record<string, unknown>) => void;
        };
      };
    };
  }
}

export default function LoginPage() {
  const router = useRouter();
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const demoLoginEnabled = process.env.NEXT_PUBLIC_ENABLE_DEMO_LOGIN === "true";

  const handleGoogleCallback = async (response: { credential: string }) => {
    setLoading(true);
    setError(null);
    try {
      await api.auth.loginGoogle(response.credential);
      const user = await api.auth.me();
      router.push(getRoleDashboard(user.role));
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  const initGoogle = (el: HTMLDivElement | null) => {
    if (!el || !window.google) return;
    const clientId = process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID;
    if (!clientId) return;

    window.google.accounts.id.initialize({
      client_id: clientId,
      callback: handleGoogleCallback,
    });
    window.google.accounts.id.renderButton(el, {
      theme: "outline",
      size: "large",
      width: "320",
      text: "signin_with",
      shape: "pill",
    });
  };

  const runDemoLogin = async (role: "student" | "teacher" | "admin" | "parent", redirectPath: string) => {
    setLoading(true);
    setError(null);
    clearDemoSession();
    try {
      const res = await fetch(`${API_BASE}/api/auth/demo-login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ role }),
      });

      const payload = await res.json().catch(() => ({} as { detail?: string; access_token?: string }));
      if (!res.ok) {
        setError((payload as { detail?: string }).detail || "Demo login failed");
        return;
      }

      if ((payload as { access_token?: string }).access_token) {
        setStoredAccessToken((payload as { access_token: string }).access_token);
      }
      router.push(redirectPath);
    } catch {
      setError("Backend not running");
    } finally {
      setLoading(false);
    }
  };

  return (
    <PrismPage className="flex min-h-screen items-center py-10">
      <PrismSection className="grid w-full items-center gap-8 lg:grid-cols-[0.95fr_1.05fr]">
        <div className="space-y-6">
          <PrismHeroKicker>
            <Sparkles className="h-3.5 w-3.5" />
            Secure Role-Based Access
          </PrismHeroKicker>
          <div className="space-y-4">
            <h1 className="prism-title text-5xl font-black leading-[0.96] text-[var(--text-primary)] md:text-6xl">
              Enter the platform through a <span className="premium-gradient">cleaner, calmer control point</span>
            </h1>
            <p className="max-w-xl text-lg leading-8 text-[var(--text-secondary)]">
              Staff, students, and parents all enter the same product through role-aware authentication. In demo mode, you can also step directly into curated personas.
            </p>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <PrismPanel className="p-5">
              <p className="mb-2 text-sm font-semibold text-[var(--text-primary)]">Production path</p>
              <p className="text-sm leading-6 text-[var(--text-secondary)]">Google and institutional access stay aligned with your real user role and data boundaries.</p>
            </PrismPanel>
            <PrismPanel className="p-5">
              <p className="mb-2 text-sm font-semibold text-[var(--text-primary)]">Demo path</p>
              <p className="text-sm leading-6 text-[var(--text-secondary)]">Step into student, teacher, admin, or parent journeys without breaking the overall product flow.</p>
            </PrismPanel>
          </div>
        </div>

        <PrismPanel className="mx-auto w-full max-w-md p-8">
          <div className="mb-8 text-center">
            <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-[calc(var(--radius)*0.9)] bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(167,139,250,0.92))] shadow-[0_18px_34px_rgba(96,165,250,0.24)]">
              <GraduationCap className="h-8 w-8 text-[#06101e]" />
            </div>
            <h2 className="prism-title text-3xl font-bold text-[var(--text-primary)]">Welcome to VidyaOS</h2>
            <p className="mt-2 text-sm text-[var(--text-secondary)]">Sign in with your school account or enter one of the demo experiences.</p>
          </div>

          {loading ? (
            <div className="flex flex-col items-center py-8">
              <Loader2 className="mb-3 h-8 w-8 animate-spin text-[var(--primary)]" />
              <p className="text-sm text-[var(--text-secondary)]">Signing you in...</p>
            </div>
          ) : (
            <>
              <div className="mb-5 flex justify-center">
                <div ref={initGoogle} />
              </div>

              <div className="mb-5 text-center">
                <a href="/qr-login" className="inline-flex items-center gap-2 text-xs font-semibold text-status-blue hover:underline">
                  <QrCode className="h-3.5 w-3.5" /> Login with QR code
                </a>
              </div>

              {!process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID && (
                <div className="rounded-[var(--radius-sm)] border border-[var(--border)] bg-[rgba(148,163,184,0.05)] p-4 text-center">
                  <p className="mb-4 text-xs text-[var(--text-muted)]">Google Sign-In requires configuration.</p>
                  {demoLoginEnabled ? (
                    <div className="grid gap-3">
                      <button onClick={() => void runDemoLogin("student", "/student/overview")} className="rounded-2xl bg-[linear-gradient(135deg,rgba(96,165,250,0.96),rgba(129,140,248,0.94))] px-4 py-3 text-sm font-semibold text-[#06101e]">
                        Demo: Student
                      </button>
                      <button onClick={() => void runDemoLogin("teacher", "/teacher/dashboard")} className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">
                        Demo: Teacher
                      </button>
                      <button onClick={() => void runDemoLogin("admin", "/admin/dashboard")} className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">
                        Demo: Admin
                      </button>
                      <button onClick={() => void runDemoLogin("parent", "/parent/dashboard")} className="rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.06)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)]">
                        Demo: Parent
                      </button>
                    </div>
                  ) : (
                    <p className="text-xs text-[var(--text-muted)]">
                      Demo login is disabled. Set `NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true` for local demo access.
                    </p>
                  )}
                </div>
              )}

              {error && (
                <div className="mt-4 rounded-[var(--radius-sm)] border border-error-subtle bg-error-subtle px-4 py-3 text-sm text-status-red text-center">
                  {error}
                </div>
              )}

              <p className="mt-6 text-center text-xs text-[var(--text-muted)]">
                Privacy-first by design. Role access and student data stay isolated.
              </p>
            </>
          )}
        </PrismPanel>
      </PrismSection>
    </PrismPage>
  );
}
