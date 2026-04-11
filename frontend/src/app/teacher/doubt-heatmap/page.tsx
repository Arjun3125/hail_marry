"use client";

import { useEffect, useMemo, useState } from "react";
import { Flame, MessageCircleQuestion, TrendingUp } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type HeatmapItem = {
    label: string;
    query_count: number;
    intensity: number;
    sample_topics: string[];
};

type TopTopic = { topic: string; count: number };

type HeatmapData = {
    heatmap: HeatmapItem[];
    top_topics: TopTopic[];
    total_queries: number;
    student_count: number;
};

export default function DoubtHeatmapPage() {
    const [data, setData] = useState<HeatmapData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = (await api.teacher.doubtHeatmap()) as HeatmapData;
                setData(payload);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load doubt heatmap");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const summary = useMemo(() => ({
        totalQueries: data?.total_queries ?? 0,
        studentCount: data?.student_count ?? 0,
        hottestBand: data?.heatmap?.[0]?.label ?? "No active band",
    }), [data]);

    const getHeatGradient = (intensity: number) => {
        if (intensity >= 0.8) return "from-red-500 to-rose-600";
        if (intensity >= 0.6) return "from-orange-400 to-amber-500";
        if (intensity >= 0.4) return "from-amber-300 to-yellow-400";
        if (intensity >= 0.2) return "from-yellow-200 to-amber-200";
        return "from-green-200 to-emerald-300";
    };

    const getHeatText = (intensity: number) => (intensity >= 0.4 ? "text-white" : "text-[var(--text-primary)]");

    return (
        <PrismPage variant="dashboard" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Flame className="h-3.5 w-3.5" />
                            Teacher Doubt Surface
                        </PrismHeroKicker>
                    )}
                    title="Read student doubt pressure before it spreads across the class"
                    description="Use AI query patterns to spot where confusion is building, which topics are being asked repeatedly, and where reteaching should start first."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Start with the hottest subject band, then use the top-topic list to decide whether the next move is revision, examples, or a new assessment.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">AI queries</span>
                        <span className="prism-status-value">{summary.totalQueries}</span>
                        <span className="prism-status-detail">Student questions contributing to the current heatmap.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Students represented</span>
                        <span className="prism-status-value">{summary.studentCount}</span>
                        <span className="prism-status-detail">Unique learners contributing to the current signal set.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Hottest band</span>
                        <span className="prism-status-value">{summary.hottestBand}</span>
                        <span className="prism-status-detail">The current highest-pressure doubt cluster in the loaded dataset.</span>
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="teacher-doubt-heatmap"
                        onRetry={() => window.location.reload()}
                    />
                ) : loading ? (
                    <PrismPanel className="p-10">
                        <div className="flex items-center gap-3 text-sm text-[var(--text-muted)]">
                            <Flame className="h-4 w-4 animate-pulse" />
                            Analyzing student query patterns...
                        </div>
                    </PrismPanel>
                ) : !data || (data.heatmap.length === 0 && data.top_topics.length === 0) ? (
                    <EmptyState
                        icon={Flame}
                        title="No doubt telemetry yet"
                        description="Students need to use the assistant before this page can surface real topic pressure."
                        eyebrow="Awaiting learning signals"
                        scopeNote="The heatmap is built from student AI queries, so this surface becomes useful only after students begin asking grounded questions."
                    />
                ) : (
                    <div className="space-y-6">
                        <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
                            <PrismPanel className="p-5">
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">Subject doubt intensity</h2>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Compare which subjects are attracting the highest question volume and urgency.
                                </p>
                                <div className="mt-4 space-y-3">
                                    {data.heatmap.map((item) => (
                                        <div key={item.label} className="flex items-center gap-3">
                                            <span className="w-36 truncate text-right text-xs font-medium text-[var(--text-secondary)]">{item.label}</span>
                                            <div className="flex-1 rounded-xl bg-[var(--bg-page)]">
                                                <div
                                                    className={`flex h-10 items-center rounded-xl bg-gradient-to-r px-3 ${getHeatGradient(item.intensity)} ${getHeatText(item.intensity)} transition-all duration-500`}
                                                    style={{ width: `${Math.max(18, item.intensity * 100)}%` }}
                                                >
                                                    <span className="text-[11px] font-bold">{item.query_count} queries</span>
                                                </div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                                <div className="mt-4 flex items-center gap-2 text-[9px] uppercase tracking-widest text-[var(--text-muted)]">
                                    <span>Low</span>
                                    <div className="flex gap-0.5">
                                        <span className="h-2.5 w-5 rounded-sm bg-gradient-to-r from-green-200 to-emerald-300" />
                                        <span className="h-2.5 w-5 rounded-sm bg-gradient-to-r from-yellow-200 to-amber-200" />
                                        <span className="h-2.5 w-5 rounded-sm bg-gradient-to-r from-amber-300 to-yellow-400" />
                                        <span className="h-2.5 w-5 rounded-sm bg-gradient-to-r from-orange-400 to-amber-500" />
                                        <span className="h-2.5 w-5 rounded-sm bg-gradient-to-r from-red-500 to-rose-600" />
                                    </div>
                                    <span>High</span>
                                </div>
                            </PrismPanel>

                            <div className="space-y-6">
                                <PrismPanel className="p-5">
                                    <div className="flex items-center gap-2">
                                        <MessageCircleQuestion className="h-4 w-4 text-orange-500" />
                                        <h2 className="text-base font-semibold text-[var(--text-primary)]">Most asked topics</h2>
                                    </div>
                                    <div className="mt-4 space-y-2">
                                        {data.top_topics.map((item, idx) => (
                                            <div key={`${item.topic}-${idx}`} className="flex items-center gap-3 rounded-xl bg-[var(--bg-page)] px-3 py-3">
                                                <span className={`flex h-7 w-7 items-center justify-center rounded-lg text-xs font-bold text-white ${
                                                    idx === 0 ? "bg-gradient-to-br from-red-500 to-rose-600" :
                                                    idx === 1 ? "bg-gradient-to-br from-orange-400 to-amber-500" :
                                                    idx === 2 ? "bg-gradient-to-br from-amber-400 to-yellow-500" :
                                                    "bg-gradient-to-br from-gray-400 to-gray-500"
                                                }`}>
                                                    {idx + 1}
                                                </span>
                                                <span className="flex-1 truncate text-sm text-[var(--text-primary)]">{item.topic}</span>
                                                <span className="rounded-full bg-[var(--bg-card)] px-2.5 py-1 text-xs font-bold text-[var(--text-muted)]">
                                                    {item.count}x
                                                </span>
                                            </div>
                                        ))}
                                    </div>
                                </PrismPanel>

                                <PrismPanel className="p-5">
                                    <div className="flex items-center gap-2">
                                        <TrendingUp className="h-4 w-4 text-[var(--primary)]" />
                                        <h2 className="text-base font-semibold text-[var(--text-primary)]">Teaching guidance</h2>
                                    </div>
                                    <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                        <p>High-heat bands usually need either a quick reteach, a worked-example sheet, or a narrow revision quiz before the next class.</p>
                                        <p>Use this surface to choose intervention order, not to replace class-level judgment about why a topic is spiking.</p>
                                    </div>
                                </PrismPanel>
                            </div>
                        </div>
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}
