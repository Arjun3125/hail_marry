"use client";

import { useEffect, useState } from "react";
import { CreditCard, Zap, FileText, Users } from "lucide-react";

import { api } from "@/lib/api";

type BillingData = {
    plan: string;
    max_students: number;
    ai_daily_limit: number;
    total_queries: number;
    total_tokens: number;
    total_documents: number;
    estimated_cost: string;
};

export default function AdminBillingPage() {
    const [billing, setBilling] = useState<BillingData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.admin.billing();
                setBilling(payload as BillingData);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load billing");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Billing & Plan</h1>
                <p className="text-sm text-[var(--text-secondary)]">View your plan details and usage</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading billing...</p>
            ) : (
                <>
                    <div className="bg-gradient-to-br from-[var(--primary)] to-blue-700 rounded-[var(--radius)] p-6 text-white mb-6">
                        <div className="flex items-center justify-between">
                            <div>
                                <p className="text-xs opacity-80">Current Plan</p>
                                <h2 className="text-2xl font-bold">{billing?.plan || "basic"}</h2>
                            </div>
                            <CreditCard className="w-10 h-10 opacity-50" />
                        </div>
                        <div className="grid grid-cols-1 gap-3 mt-4 sm:grid-cols-3 sm:gap-4">
                            <div>
                                <p className="text-xs opacity-70">Max Students</p>
                                <p className="text-lg font-semibold">{billing?.max_students ?? 0}</p>
                            </div>
                            <div>
                                <p className="text-xs opacity-70">AI Queries/Day</p>
                                <p className="text-lg font-semibold">{billing?.ai_daily_limit ?? 0}</p>
                            </div>
                            <div>
                                <p className="text-xs opacity-70">Status</p>
                                <p className="text-lg font-semibold">{billing?.estimated_cost || "-"}</p>
                            </div>
                        </div>
                    </div>

                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                            <Zap className="w-5 h-5 text-[var(--primary)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{(billing?.total_queries ?? 0).toLocaleString()}</p>
                            <p className="text-xs text-[var(--text-muted)]">Total AI Queries</p>
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                            <FileText className="w-5 h-5 text-[var(--primary)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{(billing?.total_tokens ?? 0).toLocaleString()}</p>
                            <p className="text-xs text-[var(--text-muted)]">Total Tokens Used</p>
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] p-5">
                            <Users className="w-5 h-5 text-[var(--primary)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{billing?.total_documents ?? 0}</p>
                            <p className="text-xs text-[var(--text-muted)]">Documents Uploaded</p>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
