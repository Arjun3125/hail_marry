"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, CalendarDays, Gauge, TrendingUp, Users } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import {
    PrismHeroKicker,
    PrismPage,
    PrismPageIntro,
    PrismPanel,
    PrismSection,
    PrismSectionHeader,
} from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type AIUsageData = {
    total_week: number;
    by_role: {
        students: number;
        teachers: number;
        admin: number;
        parents: number;
    };
    heavy_users: Array<{
        id?: string;
        email?: string;
        name: string;
        role?: string;
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
    monthly_trend: Array<{
        month: string;
        label: string;
        requests: number;
        tokens: number;
        cache_hits: number;
        estimated_cost_units: number;
    }>;
    role_monthly: Array<{
        month: string;
        label: string;
        students: number;
        teachers: number;
        admin: number;
        parents: number;
    }>;
    six_month_totals: {
        requests: number;
        tokens: number;
        cache_hits: number;
        estimated_cost_units: number;
    };
    top_workflows_6m: Array<{
        metric: string;
        count: number;
        token_total: number;
        cache_hits: number;
        estimated_cost_units: number;
    }>;
    peak_day?: {
        date: string;
        requests: number;
        tokens: number;
        cache_hits: number;
    } | null;
};

const compactNumber = new Intl.NumberFormat("en-IN", {
    notation: "compact",
    maximumFractionDigits: 1,
});

function formatMetric(metric: string) {
    return metric
        .replaceAll("_", " ")
        .replace(/\bqa\b/gi, "Q&A")
        .replace(/\bllm\b/gi, "LLM")
        .replace(/\bai\b/gi, "AI");
}

function formatDateLabel(value?: string | null) {
    if (!value) return "No peak day";
    const date = new Date(`${value}T00:00:00`);
    if (Number.isNaN(date.getTime())) return value;
    return date.toLocaleDateString("en-IN", { day: "numeric", month: "short" });
}

function formatCount(value: number) {
    return compactNumber.format(value || 0);
}

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

    const roleUsage = useMemo(() => [
        { role: "Students", pct: data?.by_role.students ?? 0, color: "var(--primary)" },
        { role: "Teachers", pct: data?.by_role.teachers ?? 0, color: "var(--success)" },
        { role: "Parents", pct: data?.by_role.parents ?? 0, color: "#60a5fa" },
        { role: "Admin", pct: data?.by_role.admin ?? 0, color: "var(--warning)" },
    ], [data]);

    const requestGrowth = useMemo(() => {
        const trend = data?.monthly_trend ?? [];
        if (trend.length < 2) return 0;
        const first = trend.find((item) => item.requests > 0) ?? trend[0];
        const last = trend[trend.length - 1];
        if (!first?.requests) return 0;
        return Math.round(((last.requests - first.requests) / first.requests) * 100);
    }, [data]);

    const peakDayLabel = data?.peak_day
        ? `${formatDateLabel(data.peak_day.date)} · ${formatCount(data.peak_day.requests)} requests`
        : "No peak day recorded";

    const maxMonthlyRequests = Math.max(...(data?.monthly_trend ?? []).map((item) => item.requests), 1);

    return (
        <PrismPage variant="dashboard" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Gauge className="h-3.5 w-3.5" />
                            AI Usage Oversight
                        </PrismHeroKicker>
                    )}
                    title="Show six months of AI adoption, not just today&apos;s traffic"
                    description="This demo view now tells the longer story: how students, teachers, parents, and administrators use the platform over a sustained six-month cycle, which workflows carry the load, and where guardrails matter during peak weeks."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">6-month requests</span>
                        <strong className="prism-status-value">{formatCount(data?.six_month_totals.requests ?? 0)}</strong>
                        <span className="prism-status-detail">Synthetic request volume across the full demo history</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Growth since month 1</span>
                        <strong className="prism-status-value">{requestGrowth}%</strong>
                        <span className="prism-status-detail">Adoption increase from the first visible month to the latest month</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Peak usage day</span>
                        <strong className="prism-status-value">{data?.peak_day ? formatCount(data.peak_day.requests) : 0}</strong>
                        <span className="prism-status-detail">{peakDayLabel}</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Tokens today</span>
                        <strong className="prism-status-value">{formatCount(data?.token_usage_today ?? 0)}</strong>
                        <span className="prism-status-detail">Current day token footprint with cache and cost guardrails still visible</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation error={error} scope="admin-ai-usage" onRetry={() => window.location.reload()} />
                ) : null}

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">Loading AI usage analytics...</p>
                    </PrismPanel>
                ) : !data ? (
                    <PrismPanel className="p-6">
                        <EmptyState
                            icon={Bot}
                            title="No AI usage snapshot yet"
                            description="Usage metrics will appear here once the institution starts generating enough AI activity to summarize."
                            eyebrow="Analytics unavailable"
                        />
                    </PrismPanel>
                ) : (
                    <div className="grid gap-6 xl:grid-cols-2">
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Usage by role today"
                                description="The daily mix should still be student-heavy, but the demo now shows visible participation from teacher, parent, and admin workflows too."
                            />
                            <div className="mt-4 space-y-4">
                                {roleUsage.map((item) => (
                                    <div key={item.role}>
                                        <div className="mb-1 flex items-center justify-between">
                                            <span className="text-sm text-[var(--text-secondary)]">{item.role}</span>
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{item.pct}%</span>
                                        </div>
                                        <div className="h-2.5 rounded-full bg-[var(--bg-page)]">
                                            <div className="h-2.5 rounded-full" style={{ width: `${item.pct}%`, backgroundColor: item.color }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Six-month adoption trend"
                                description="Each month reflects synthetic but realistic growth, stronger pre-exam usage, and broader platform adoption instead of a flat demo trace."
                            />
                            <div className="mt-4 space-y-3">
                                {(data.monthly_trend ?? []).map((item) => (
                                    <div key={item.month} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                        <div className="flex items-center justify-between gap-4">
                                            <div>
                                                <p className="text-sm font-medium text-[var(--text-primary)]">{item.label}</p>
                                                <p className="text-xs text-[var(--text-muted)]">
                                                    {formatCount(item.tokens)} tokens · {formatCount(item.cache_hits)} cache hits
                                                </p>
                                            </div>
                                            <p className="text-sm text-[var(--text-secondary)]">{formatCount(item.requests)} requests</p>
                                        </div>
                                        <div className="mt-3 h-2.5 rounded-full bg-[var(--bg-page)]">
                                            <div
                                                className="h-2.5 rounded-full bg-[var(--primary)]"
                                                style={{ width: `${Math.max((item.requests / maxMonthlyRequests) * 100, 6)}%` }}
                                            />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Workflow leaders across six months"
                                description="This is the clearest demo proof that the product is being used as a study system, not just as a generic chatbot."
                            />
                            <div className="mt-4 space-y-3">
                                {(data.top_workflows_6m ?? []).slice(0, 6).map((item) => (
                                    <div key={item.metric} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                        <div className="flex items-center justify-between gap-4">
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{formatMetric(item.metric)}</span>
                                            <span className="text-sm text-[var(--text-secondary)]">{formatCount(item.count)}</span>
                                        </div>
                                        <p className="mt-2 text-xs text-[var(--text-muted)]">
                                            {formatCount(item.token_total)} tokens · {formatCount(item.cache_hits)} cache hits · {item.estimated_cost_units.toFixed(1)} cost units
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Today&apos;s workflow mix"
                                description="Keep the current-day view visible so quota checks and adoption patterns are grounded in live-like daily behavior."
                            />
                            <div className="mt-4 space-y-3">
                                {(data.tool_usage ?? []).slice(0, 6).map((item) => (
                                    <div key={item.metric} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                        <div className="flex items-center justify-between">
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{formatMetric(item.metric)}</span>
                                            <span className="text-sm text-[var(--text-secondary)]">{item.count}</span>
                                        </div>
                                        <p className="mt-2 text-xs text-[var(--text-muted)]">
                                            {formatCount(item.token_total)} tokens · {formatCount(item.cache_hits)} cache hits
                                        </p>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Daily heavy users"
                                description="Use this list to explain who is driving the current day volume inside the larger six-month adoption story."
                            />
                            {data.heavy_users.length ? (
                                <div className="mt-4 space-y-3">
                                    {data.heavy_users.map((user, index) => (
                                        <div key={user.id ?? user.email ?? `${user.name}-${user.role ?? "user"}-${index}`} className="flex items-center justify-between rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                            <div>
                                                <p className="text-sm font-medium text-[var(--text-primary)]">{user.name}</p>
                                                <p className="text-xs text-[var(--text-muted)]">
                                                    {(user.role ?? "user").replace(/^./, (char) => char.toUpperCase())} · {formatCount(user.tokens_today ?? 0)} tokens today
                                                </p>
                                            </div>
                                            <span className="text-sm text-[var(--text-secondary)]">{formatCount(user.queries)} requests</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="mt-4">
                                    <EmptyState
                                        icon={Users}
                                        title="No heavy-user outliers"
                                        description="The current activity window does not show any unusual concentration of requests."
                                        eyebrow="Usage balanced"
                                    />
                                </div>
                            )}
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Monthly role rhythm"
                                description="This timeline makes the demo feel lived-in: student demand rises first, teacher usage follows assessment cycles, and parent/admin activity stays lighter but persistent."
                            />
                            <div className="mt-4 space-y-3">
                                {(data.role_monthly ?? []).map((item) => (
                                    <div key={item.month} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
                                        <div className="mb-3 flex items-center justify-between">
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{item.label}</p>
                                            <span className="text-xs text-[var(--text-muted)]">
                                                {formatCount(item.students + item.teachers + item.parents + item.admin)} requests
                                            </span>
                                        </div>
                                        <div className="grid gap-2 text-xs text-[var(--text-secondary)] sm:grid-cols-2">
                                            <span>Students: {formatCount(item.students)}</span>
                                            <span>Teachers: {formatCount(item.teachers)}</span>
                                            <span>Parents: {formatCount(item.parents)}</span>
                                            <span>Admin: {formatCount(item.admin)}</span>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Quota pressure"
                                description="Watch these guardrails so the demo shows healthy volume without implying the platform is operating right at the edge."
                            />
                            <div className="mt-4 space-y-4">
                                {(data.quota_saturation ?? []).slice(0, 5).map((item) => (
                                    <div key={item.metric}>
                                        <div className="mb-1 flex items-center justify-between">
                                            <span className="text-sm text-[var(--text-secondary)]">{formatMetric(item.metric)}</span>
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{item.current}/{item.daily_limit}</span>
                                        </div>
                                        <div className="h-2.5 rounded-full bg-[var(--bg-page)]">
                                            <div className="h-2.5 rounded-full bg-[var(--warning)]" style={{ width: `${Math.min(item.saturation_pct, 100)}%` }} />
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                title="Model mix"
                                description="Review which models are carrying the current workflow mix so the demo reflects routing, cost, and reliability tradeoffs."
                            />
                            <div className="mt-4 space-y-3">
                                {Object.entries(data.model_mix ?? {}).length ? Object.entries(data.model_mix ?? {}).map(([model, count]) => (
                                    <div key={model} className="flex items-center justify-between rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                        <span className="break-all text-sm font-medium text-[var(--text-primary)]">{model}</span>
                                        <span className="text-sm text-[var(--text-secondary)]">{formatCount(count)} uses</span>
                                    </div>
                                )) : (
                                    <EmptyState
                                        icon={Bot}
                                        title="No model routing data yet"
                                        description="Model usage mix will appear here once multiple workflows start recording provider activity."
                                        eyebrow="Routing snapshot"
                                    />
                                )}
                            </div>
                        </PrismPanel>

                        <PrismPanel className="p-5 xl:col-span-2">
                            <PrismSectionHeader
                                title="Guardrails and storyline anchors"
                                description="These anchors make the synthetic dataset easier to narrate in a demo: long-horizon totals, peak usage behavior, and the current operational envelope."
                            />
                            <div className="mt-4 grid gap-4 md:grid-cols-4">
                                <InfoTile
                                    icon={TrendingUp}
                                    label="6-month tokens"
                                    value={formatCount(data.six_month_totals.tokens)}
                                />
                                <InfoTile
                                    icon={CalendarDays}
                                    label="Peak day"
                                    value={peakDayLabel}
                                />
                                <InfoTile
                                    icon={Gauge}
                                    label="Daily cost guardrail"
                                    value={`${data.estimated_cost_units_today} / ${data.guardrails.tenant_daily_cost_units_threshold}`}
                                />
                                <InfoTile
                                    icon={Bot}
                                    label="Batch-eligible tools"
                                    value={(data.guardrails.queued_batch_metrics ?? []).map(formatMetric).join(", ") || "None"}
                                />
                            </div>
                        </PrismPanel>
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function InfoTile({
    icon: Icon,
    label,
    value,
}: {
    icon: typeof Bot;
    label: string;
    value: string;
}) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                <Icon className="h-4 w-4" />
                <p className="text-xs font-semibold uppercase tracking-[0.16em]">{label}</p>
            </div>
            <p className="mt-3 text-sm font-medium leading-6 text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
