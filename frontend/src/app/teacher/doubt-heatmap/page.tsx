"use client";

import { useEffect, useState } from "react";
import { Flame, MessageCircleQuestion, Users, TrendingUp } from "lucide-react";

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

    const getHeatGradient = (intensity: number) => {
        if (intensity >= 0.8) return "from-red-500 to-rose-600";
        if (intensity >= 0.6) return "from-orange-400 to-amber-500";
        if (intensity >= 0.4) return "from-amber-300 to-yellow-400";
        if (intensity >= 0.2) return "from-yellow-200 to-amber-200";
        return "from-green-200 to-emerald-300";
    };

    const getHeatText = (intensity: number) => {
        return intensity >= 0.4 ? "text-white" : "text-gray-800";
    };

    return (
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center gap-3 mb-1">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 shadow-lg">
                        <Flame className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                            Doubt Heatmap
                        </h1>
                        <p className="text-xs text-[var(--text-muted)]">
                            Real-time analysis of student AI queries by topic
                        </p>
                    </div>
                </div>
            </div>

            {error ? (
                <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-12 text-center border border-[var(--border)]/50">
                    <div className="w-12 h-12 mx-auto mb-4 rounded-xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center animate-pulse">
                        <Flame className="w-6 h-6 text-white" />
                    </div>
                    <p className="text-sm text-[var(--text-muted)]">Analyzing student queries...</p>
                </div>
            ) : !data || (data.heatmap.length === 0 && data.top_topics.length === 0) ? (
                <div className="bg-[var(--bg-card)] rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-orange-500 to-red-600 flex items-center justify-center shadow-lg opacity-40">
                        <Flame className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">No data yet</h3>
                    <p className="text-sm text-[var(--text-muted)]">
                        Students need to use the AI Assistant first.
                    </p>
                </div>
            ) : (
                <>
                    {/* Stats */}
                    <div className="grid grid-cols-2 gap-3 mb-6">
                        <div className="bg-gradient-to-br from-blue-500 to-indigo-600 rounded-xl p-4 text-white shadow-md flex items-center gap-3">
                            <MessageCircleQuestion className="w-8 h-8 opacity-80" />
                            <div>
                                <p className="text-2xl font-bold">{data.total_queries}</p>
                                <p className="text-[10px] uppercase tracking-wider opacity-70">AI Queries</p>
                            </div>
                        </div>
                        <div className="bg-gradient-to-br from-emerald-500 to-teal-600 rounded-xl p-4 text-white shadow-md flex items-center gap-3">
                            <Users className="w-8 h-8 opacity-80" />
                            <div>
                                <p className="text-2xl font-bold">{data.student_count}</p>
                                <p className="text-[10px] uppercase tracking-wider opacity-70">Students</p>
                            </div>
                        </div>
                    </div>

                    {/* Subject Heatmap */}
                    {data.heatmap.length > 0 ? (
                        <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-5 mb-6 border border-[var(--border)]/50">
                            <h2 className="text-sm font-bold text-[var(--text-primary)] mb-4 uppercase tracking-wider flex items-center gap-2">
                                <TrendingUp className="w-4 h-4 text-orange-500" />
                                Subject Doubt Intensity
                            </h2>
                            <div className="space-y-3">
                                {data.heatmap.map((item) => (
                                    <div key={item.label} className="flex items-center gap-3">
                                        <span className="w-36 text-xs font-medium text-[var(--text-secondary)] truncate text-right">{item.label}</span>
                                        <div className="flex-1 h-9 bg-[var(--bg-page)] rounded-xl overflow-hidden">
                                            <div
                                                className={`h-full rounded-xl bg-gradient-to-r ${getHeatGradient(item.intensity)} ${getHeatText(item.intensity)} transition-all duration-500 flex items-center px-3 shadow-sm`}
                                                style={{ width: `${Math.max(18, item.intensity * 100)}%` }}
                                            >
                                                <span className="text-[10px] font-bold whitespace-nowrap">{item.query_count} queries</span>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                            <div className="flex items-center gap-2 mt-4 text-[9px] text-[var(--text-muted)] uppercase tracking-widest">
                                <span>Low</span>
                                <div className="flex gap-0.5">
                                    <span className="w-5 h-2.5 rounded-sm bg-gradient-to-r from-green-200 to-emerald-300" />
                                    <span className="w-5 h-2.5 rounded-sm bg-gradient-to-r from-yellow-200 to-amber-200" />
                                    <span className="w-5 h-2.5 rounded-sm bg-gradient-to-r from-amber-300 to-yellow-400" />
                                    <span className="w-5 h-2.5 rounded-sm bg-gradient-to-r from-orange-400 to-amber-500" />
                                    <span className="w-5 h-2.5 rounded-sm bg-gradient-to-r from-red-500 to-rose-600" />
                                </div>
                                <span>High</span>
                            </div>
                        </div>
                    ) : null}

                    {/* Top Topics */}
                    {data.top_topics.length > 0 ? (
                        <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-5 border border-[var(--border)]/50">
                            <h2 className="text-sm font-bold text-[var(--text-primary)] mb-4 uppercase tracking-wider flex items-center gap-2">
                                <Flame className="w-4 h-4 text-orange-500" />
                                Most Asked Topics
                            </h2>
                            <div className="space-y-2">
                                {data.top_topics.map((item, idx) => (
                                    <div key={`${item.topic}-${idx}`} className="flex items-center gap-3 p-2.5 rounded-xl bg-[var(--bg-page)] hover:bg-[var(--border)]/30 transition-colors">
                                        <span className={`w-7 h-7 rounded-lg flex items-center justify-center text-xs font-bold text-white shadow-sm ${idx === 0 ? "bg-gradient-to-br from-red-500 to-rose-600" :
                                                idx === 1 ? "bg-gradient-to-br from-orange-400 to-amber-500" :
                                                    idx === 2 ? "bg-gradient-to-br from-amber-400 to-yellow-500" :
                                                        "bg-gradient-to-br from-gray-400 to-gray-500"
                                            }`}>
                                            {idx + 1}
                                        </span>
                                        <span className="flex-1 text-sm text-[var(--text-primary)] truncate">{item.topic}</span>
                                        <span className="text-xs font-bold text-[var(--text-muted)] bg-[var(--bg-card)] px-2.5 py-1 rounded-full shadow-sm">
                                            {item.count}×
                                        </span>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : null}
                </>
            )}
        </div>
    );
}
