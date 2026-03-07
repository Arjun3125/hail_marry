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
    }>;
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
                <div className="rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)] mb-4">
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
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{data?.heavy_users.length ?? 0}</p>
                            <p className="text-xs text-[var(--text-muted)]">Heavy users identified</p>
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)]">
                            <Users className="w-5 h-5 text-[var(--primary)] mb-2" />
                            <p className="text-2xl font-bold text-[var(--text-primary)]">{(data?.by_role.students ?? 0) + (data?.by_role.teachers ?? 0) + (data?.by_role.admin ?? 0)}%</p>
                            <p className="text-xs text-[var(--text-muted)]">Role distribution coverage</p>
                        </div>
                    </div>

                    <div className="grid lg:grid-cols-2 gap-6">
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
                                            <span className="text-sm font-medium text-[var(--text-primary)]">{u.name}</span>
                                            <span className="text-sm text-[var(--text-secondary)]">{u.queries} queries</span>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <p className="text-sm text-[var(--text-muted)]">No usage data found.</p>
                            )}
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
