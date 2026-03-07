"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { GraduationCap, Loader2 } from "lucide-react";
import { api, API_BASE, setStoredAccessToken } from "@/lib/api";
import { getRoleDashboard } from "@/lib/auth";

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

    // Initialize Google Sign In
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
            shape: "rectangular",
        });
    };

    const runDemoLogin = async (role: "student" | "teacher" | "admin" | "parent", redirectPath: string) => {
        setLoading(true);
        setError(null);
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
        <div className="min-h-screen bg-[var(--bg-page)] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                {/* Logo & Header */}
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-[var(--primary-light)] rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <GraduationCap className="w-8 h-8 text-[var(--primary)]" />
                    </div>
                    <div className="flex items-center justify-center mt-4">
                        <img src="/brand/logo-mark.png" alt="ModernHustlers" className="h-7 object-contain" />
                    </div>
                    <p className="text-sm text-[var(--text-secondary)] mt-2">
                        Sign in with your school Google account
                    </p>
                </div>

                {/* Login Card */}
                <div className="bg-white rounded-[var(--radius)] shadow-[var(--shadow-card)] p-8">
                    {loading ? (
                        <div className="flex flex-col items-center py-8">
                            <Loader2 className="w-8 h-8 text-[var(--primary)] animate-spin mb-3" />
                            <p className="text-sm text-[var(--text-secondary)]">Signing you in...</p>
                        </div>
                    ) : (
                        <>
                            {/* Google Sign In Button */}
                            <div className="flex justify-center mb-6">
                                <div ref={initGoogle} />
                            </div>

                            {/* Fallback for when Google client ID is not set */}
                            {!process.env.NEXT_PUBLIC_GOOGLE_CLIENT_ID && (
                                <div className="text-center">
                                    <p className="text-xs text-[var(--text-muted)] mb-4">
                                        Google Sign-In requires configuration.
                                    </p>
                                    {demoLoginEnabled ? (
                                        <>
                                            <button
                                                onClick={() => void runDemoLogin("student", "/student/overview")}
                                                className="w-full py-3 bg-[var(--primary)] text-white rounded-[var(--radius-sm)] font-medium hover:bg-[var(--primary-hover)] transition-colors mb-3"
                                            >
                                                Demo: Login as Student
                                            </button>
                                            <button
                                                onClick={() => void runDemoLogin("teacher", "/teacher/dashboard")}
                                                className="w-full py-3 border border-[var(--border)] text-[var(--text-secondary)] rounded-[var(--radius-sm)] font-medium hover:border-[var(--primary)] hover:text-[var(--primary)] hover:bg-slate-50 transition-colors mb-3"
                                            >
                                                Demo: Login as Teacher
                                            </button>
                                            <button
                                                onClick={() => void runDemoLogin("admin", "/admin/dashboard")}
                                                className="w-full py-3 border border-[var(--border)] text-[var(--text-secondary)] rounded-[var(--radius-sm)] font-medium hover:border-[var(--primary)] hover:text-[var(--primary)] hover:bg-slate-50 transition-colors"
                                            >
                                                Demo: Login as Admin
                                            </button>
                                            <button
                                                onClick={() => void runDemoLogin("parent", "/parent/dashboard")}
                                                className="w-full py-3 border border-[var(--border)] text-[var(--text-secondary)] rounded-[var(--radius-sm)] font-medium hover:border-[var(--primary)] hover:text-[var(--primary)] hover:bg-slate-50 transition-colors mt-3"
                                            >
                                                Demo: Login as Parent
                                            </button>
                                        </>
                                    ) : (
                                        <p className="text-xs text-[var(--text-muted)]">
                                            Demo login is disabled. Set `NEXT_PUBLIC_ENABLE_DEMO_LOGIN=true` for local demo access.
                                        </p>
                                    )}
                                </div>
                            )}

                            {error && (
                                <div className="mt-4 p-3 bg-red-50 text-[var(--error)] text-sm rounded-[var(--radius-sm)] text-center">
                                    {error}
                                </div>
                            )}
                        </>
                    )}
                </div>

                {/* Footer */}
                <p className="text-center text-xs text-[var(--text-muted)] mt-6">
                    Your school&apos;s data is isolated and secure. Privacy-first by design.
                </p>
            </div>
        </div>
    );
}
