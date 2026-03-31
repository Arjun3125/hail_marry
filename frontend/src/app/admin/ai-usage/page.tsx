"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, Users, TrendingUp } from "lucide-react";

import { api } from "@/lib/api";

type AIUsageData = {
    total_week: number;
    by_role: {
        students: number;
        teachers: number;
        admin: number;
    };
    heavy_users: Array<{
        name: string;
        queries: number;
        tokens_today?: number;
    }>;
    tool_usage: Array<{
        metric: string;
        count: number;
        token_total: number;
        cache_hits: number;
    }>;
    token_usage_today: number;
    estimated_cost_units_today: number;
    cache_hits_today: number;
    model_mix: Record<string, number>;
    quota_saturation: Array<{
        metric: string;
        current: number;
        daily_limit: number;
        saturation_pct: number;
    }>;
    guardrails: {
        tenant_requests_per_minute: number;
        tenant_daily_cost_units_threshold: number;
        queued_batch_metrics: string[];
        days_window: number;
    };
};

export default function AIUsagePage() {
    const [data, setData] = useState<AIUsageData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.admin.aiUsage();
                setData(payload as AIUsageData);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load AI usage");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const roleUsage = useMemo(() => {
        return [
            { role: "Students", pct: data?.by_role.students ?? 0, color: "var(--primary)" },
            { role: "Teachers", pct: data?.by_role.teachers ?? 0, color: "var(--success)" },
            { role: "Admin", pct: data?.by_role.admin ?? 0, color: "var(--warning)" },
        ];
    }, [data]);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">AI Usage Analytics</h1>
                <p className="text-sm text-[var(--text-secondary)]">Monitor AI query patterns and resource usage</p>
            </div>

            {error ? (
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] mb-4">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <p className="text-sm text-[var(--text-muted)]">Loading analytics...</p>
            ) : (
                <>
                    <div className="grid grid-cols-1 gap-4 mb-6 sm:grid-cols-2 lg:grid-cols-3">
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <Bot className="w-5 h-5 text-[var(--primary)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data?.total_week ?? 0}</p>
                            <p className="text-xs text-[var(--text-muted)]">Total queries this week</p>
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <TrendingUp className="w-5 h-5 text-[var(--success)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data?.token_usage_today ?? 0}</p>
                            <p className="text-xs text-[var(--text-muted)]">Tokens used today</p>
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <Users className="w-5 h-5 text-[var(--primary)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data?.cache_hits_today ?? 0}</p>
                            <p className="text-xs text-[var(--text-muted)]">Cache hits today</p>
                        </div>
                    </div>

                    <div className="grid gap-6 xl:grid-cols-2">
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Usage by Role</h2>
                            <div className="space-y-4">
                                {roleUsage.map((item) => (
                                    <div key={item.role}>
                                        <div className="flex items-center justify-between mb-1">
                                            <span className="text-sm text-[var(--text-secondary)]">{item.role}</span>
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{item.pct}%</span>
                                        </div>
                                        <div className="h-2.5 bg-[var(--bg-page)] rounded-full">
                                            <div className="h-2.5 rounded-full" style={{ width: `${item.pct}%`, backgroundColor: item.color }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Heavy Users</h2>
                            {data?.heavy_users.length ? (
                                <div className="space-y-3">
                                    {data.heavy_users.map((u) => (
                                        <div key={u.name} className="flex items-center justify-between p-3 rounded-[var(--radius-sm)] bg-[var(--bg-page)]">
                                            <div>
                                                <span className="text-sm font-medium text-[var(--text-primary)]">{u.name}</span>
                                                <p className="text-xs text-[var(--text-muted)]">{u.tokens_today ?? 0} tokens today</p>
                                            </div>
                                            <span className="text-sm text-[var(--text-secondary)]">{u.queries} requests</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-[var(--text-muted)]">No usage data found.</p>
                            )}
                        </div>

                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Top Tool Usage</h2>
                            <div className="space-y-3">
                                {(data?.tool_usage ?? []).slice(0, 6).map((item) => (
                                    <div key={item.metric} className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-3">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{item.metric.replaceAll("_", " ")}</span>
                                            <span className="text-sm text-[var(--text-secondary)]">{item.count}</span>
                                        </div>
                                        <p className="mt-1 text-xs text-[var(--text-muted)]">{item.token_total} tokens • {item.cache_hits} cache hits</p>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Quota Pressure</h2>
                            <div className="space-y-4">
                                {(data?.quota_saturation ?? []).slice(0, 5).map((item) => (
                                    <div key={item.metric}>
                                        <div className="mb-1 flex items-center justify-between">
                                            <span className="text-sm text-[var(--text-secondary)]">{item.metric.replaceAll("_", " ")}</span>
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{item.current}/{item.daily_limit}</span>
                                        </div>
                                        <div className="h-2.5 rounded-full bg-[var(--bg-page)]">
                                            <div
                                                className="h-2.5 rounded-full bg-[var(--warning)]"
                                                style={{ width: `${Math.min(item.saturation_pct, 100)}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Model Mix</h2>
                            <div className="space-y-3">
                                {Object.entries(data?.model_mix ?? {}).length ? Object.entries(data?.model_mix ?? {}).map(([model, count]) => (
                                    <div key={model} className="flex items-center justify-between rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-3">
                                        <span className="text-sm font-medium text-[var(--text-primary)] break-all">{model}</span>
                                        <span className="text-sm text-[var(--text-secondary)]">{count} uses</span>
                                    </div>
                                )) : (
                                    <p className="text-sm text-[var(--text-muted)]">No model routing data yet.</p>
                                )}
                            </div>
                        </div>

                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] xl:col-span-2">
                            <h2 className="text-base font-semibold text-[var(--text-primary)] mb-4">Guardrails</h2>
                            <div className="grid gap-4 md:grid-cols-3">
                                <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-3">
                                    <p className="text-xs text-[var(--text-muted)]">Tenant burst limit</p>
                                    <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{data?.guardrails.tenant_requests_per_minute ?? 0}/min</p>
                                </div>
                                <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-3">
                                    <p className="text-xs text-[var(--text-muted)]">Daily cost guardrail</p>
                                    <p className="mt-1 text-lg font-semibold text-[var(--text-primary)]">{data?.estimated_cost_units_today ?? 0} / {data?.guardrails.tenant_daily_cost_units_threshold ?? 0}</p>
                                </div>
                                <div className="rounded-[var(--radius-sm)] bg-[var(--bg-page)] p-3">
                                    <p className="text-xs text-[var(--text-muted)]">Batch-eligible tools</p>
                                    <p className="mt-1 text-sm text-[var(--text-primary)]">{(data?.guardrails.queued_batch_metrics ?? []).join(", ") || "None"}</p>
                                </div>
                            </div>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
