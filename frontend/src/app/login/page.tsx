"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { GraduationCap, Loader2 } from "lucide-react";
import { api, API_BASE } from "@/lib/api";
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

    return (
        <div className="min-h-screen bg-[var(--bg-page)] flex items-center justify-center px-4">
            <div className="w-full max-w-md">
                {/* Logo & Header */}
                <div className="text-center mb-8">
                    <div className="w-16 h-16 bg-[var(--primary-light)] rounded-2xl flex items-center justify-center mx-auto mb-4">
                        <GraduationCap className="w-8 h-8 text-[var(--primary)]" />
                    </div>
                    <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                        Welcome to AIaaS
                    </h1>
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
                                        onClick={async () => {
                                            // Demo mode: login as student directly
                                            setLoading(true);
                                            try {
                                                const res = await fetch(`${API_BASE}/api/auth/demo-login`, {
                                                    method: "POST",
                                                    headers: { "Content-Type": "application/json" },
                                                    credentials: "include",
                                                    body: JSON.stringify({ role: "student" }),
                                                });
                                                if (res.ok) {
                                                    router.push("/student/overview");
                                                }
                                            } catch {
                                                setError("Backend not running");
                                            } finally {
                                                setLoading(false);
                                            }
                                        }}
                                        className="w-full py-3 bg-[var(--primary)] text-white rounded-[var(--radius-sm)] font-medium hover:bg-[var(--primary-hover)] transition-colors mb-3"
                                    >
                                        Demo: Login as Student
                                    </button>
                                    <button
                                        onClick={async () => {
                                            setLoading(true);
                                            try {
                                                const res = await fetch(`${API_BASE}/api/auth/demo-login`, {
                                                    method: "POST",
                                                    headers: { "Content-Type": "application/json" },
                                                    credentials: "include",
                                                    body: JSON.stringify({ role: "teacher" }),
                                                });
                                                if (res.ok) {
                                                    router.push("/teacher/dashboard");
                                                }
                                            } catch {
                                                setError("Backend not running");
                                            } finally {
                                                setLoading(false);
                                            }
                                        }}
                                        className="w-full py-3 border border-[var(--border)] text-[var(--text-secondary)] rounded-[var(--radius-sm)] font-medium hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors mb-3"
                                    >
                                        Demo: Login as Teacher
                                    </button>
                                    <button
                                        onClick={async () => {
                                            setLoading(true);
                                            try {
                                                const res = await fetch(`${API_BASE}/api/auth/demo-login`, {
                                                    method: "POST",
                                                    headers: { "Content-Type": "application/json" },
                                                    credentials: "include",
                                                    body: JSON.stringify({ role: "admin" }),
                                                });
                                                if (res.ok) {
                                                    router.push("/admin/dashboard");
                                                }
                                            } catch {
                                                setError("Backend not running");
                                            } finally {
                                                setLoading(false);
                                            }
                                        }}
                                        className="w-full py-3 border border-[var(--border)] text-[var(--text-secondary)] rounded-[var(--radius-sm)] font-medium hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors"
                                    >
                                        Demo: Login as Admin
                                    </button>
                                    <button
                                        onClick={async () => {
                                            setLoading(true);
                                            try {
                                                const res = await fetch(`${API_BASE}/api/auth/demo-login`, {
                                                    method: "POST",
                                                    headers: { "Content-Type": "application/json" },
                                                    credentials: "include",
                                                    body: JSON.stringify({ role: "parent" }),
                                                });
                                                if (res.ok) {
                                                    router.push("/parent/dashboard");
                                                }
                                            } catch {
                                                setError("Backend not running");
                                            } finally {
                                                setLoading(false);
                                            }
                                        }}
                                        className="w-full py-3 border border-[var(--border)] text-[var(--text-secondary)] rounded-[var(--radius-sm)] font-medium hover:border-[var(--primary)] hover:text-[var(--primary)] transition-colors mt-3"
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
