"use client";

import { useEffect, useState } from "react";
import { BarChart3, AlertTriangle, TrendingUp, Sparkles, BrainCircuit } from "lucide-react";

import { api } from "@/lib/api";
import { SkeletonCard } from "@/components/Skeleton";

type InsightSubject = {
    subject: string;
    avg_pct: number;
    is_weak: boolean;
};

type ClassInsight = {
    class: string;
    subjects: InsightSubject[];
    weak_topics: string[];
    recommendation: string;
};

export default function TeacherInsightsPage() {
    const [insights, setInsights] = useState<ClassInsight[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.teacher.insights();
                setInsights(((payload as { insights?: ClassInsight[] })?.insights || []) as ClassInsight[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load insights");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    return (
        <div className="max-w-5xl mx-auto space-y-6">
            <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 mb-4">
                <div>
                    <h1 className="text-3xl font-black text-[var(--text-primary)] flex items-center gap-2">
                        <BrainCircuit className="w-8 h-8 text-[var(--accent-purple)]" />
                        AI Class Insights
                    </h1>
                    <p className="text-sm text-[var(--text-muted)] mt-1">Algorithmic performance analytics and weak topic detection</p>
                </div>
            </div>

            {error && (
                <div className="rounded-xl border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)] shadow-lg animate-in fade-in">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="grid md:grid-cols-2 gap-6 animate-pulse">
                     {Array.from({ length: 4 }).map((_, i) => <SkeletonCard key={i} />)}
                </div>
            ) : insights.length === 0 ? (
                <div className="flex flex-col items-center justify-center p-20 glass-panel rounded-3xl border border-[var(--border-light)] text-center opacity-70">
                    <BrainCircuit className="w-12 h-12 text-[var(--text-muted)] mb-4" />
                    <p className="text-sm font-medium text-[var(--text-muted)]">Gathering telemetry... Check back later.</p>
                </div>
            ) : (
                <div className="grid gap-8">
                    {insights.map((cls, idx) => (
                        <div key={cls.class} className={`relative overflow-hidden glass-panel rounded-3xl border border-[var(--border-light)] shadow-xl p-8 isolate stagger-${Math.min(idx + 1, 6)}`}>
                            {/* Abstract Glow */}
                            <div className="absolute top-0 right-0 w-64 h-64 bg-purple-500/10 blur-[80px] rounded-full translate-x-1/2 -translate-y-1/2 z-[-1]" />
                            
                            <div className="flex flex-col lg:flex-row gap-8">
                                {/* Left Side: Subjects & Bars */}
                                <div className="flex-1 space-y-6">
                                    <div className="flex items-center justify-between">
                                        <h2 className="text-2xl font-black text-[var(--text-primary)]">{cls.class}</h2>
                                        <div className="px-3 py-1 rounded-full bg-[var(--bg-page)] border border-[var(--border-light)] flex items-center gap-1.5 shadow-sm text-xs font-bold text-purple-500">
                                            <BarChart3 className="w-3.5 h-3.5" /> Performance Graph
                                        </div>
                                    </div>

                                    <div className="space-y-4">
                                        {cls.subjects.map((subject) => {
                                            const isExcellent = subject.avg_pct >= 80;
                                            return (
                                                <div key={subject.subject} className="flex items-center gap-4 group">
                                                    <span className="w-28 text-xs font-bold text-[var(--text-secondary)] tracking-wide">{subject.subject}</span>
                                                    <div className="flex-1 h-4 bg-[var(--bg-page)] rounded-full overflow-hidden shadow-inner border border-[var(--border-light)]">
                                                        <div
                                                            className={`h-full rounded-full transition-all duration-1000 ease-out relative ${
                                                                subject.is_weak ? "bg-gradient-to-r from-red-500 to-rose-400" 
                                                                : isExcellent ? "bg-gradient-to-r from-emerald-500 to-teal-400" 
                                                                : "bg-gradient-to-r from-blue-500 to-indigo-400"
                                                            }`}
                                                            style={{ width: `${subject.avg_pct}%` }}
                                                        >
                                                            {/* Shimmer effect */}
                                                            <div className="absolute top-0 right-0 bottom-0 w-8 bg-gradient-to-r from-transparent to-white/30 skew-x-[-20deg] transform translate-x-full group-hover:-translate-x-[200px] transition-transform duration-1000" />
                                                        </div>
                                                    </div>
                                                    <span className={`text-sm font-black w-12 text-right ${subject.is_weak ? "text-rose-500" : "text-[var(--text-primary)]"}`}>
                                                        {subject.avg_pct}%
                                                    </span>
                                                    <div className="w-6 flex justify-center">
                                                        {subject.is_weak && <AlertTriangle className="w-4 h-4 text-rose-500 animate-pulse" />}
                                                        {isExcellent && <Sparkles className="w-4 h-4 text-emerald-500" />}
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </div>

                                {/* Right Side: Weak Topics & Recommendations */}
                                <div className="lg:w-1/3 space-y-4">
                                    <div className="bg-[var(--bg-card)] rounded-2xl p-5 border border-[var(--border-light)] shadow-md">
                                        <h3 className="text-[10px] uppercase tracking-widest font-bold text-[var(--text-muted)] mb-3 flex items-center gap-2">
                                            <AlertTriangle className="w-3 h-3 text-rose-500" /> Targeted Interventions
                                        </h3>
                                        {cls.weak_topics.length > 0 ? (
                                            <div className="flex flex-wrap gap-2">
                                                {cls.weak_topics.map((topic) => (
                                                    <span key={topic} className="text-[10px] font-bold bg-rose-500/10 border border-rose-500/20 text-rose-600 dark:text-rose-400 px-3 py-1.5 rounded-lg shadow-sm">
                                                        {topic}
                                                    </span>
                                                ))}
                                            </div>
                                        ) : (
                                            <p className="text-xs text-[var(--text-muted)]">No major weak topics identified.</p>
                                        )}
                                    </div>

                                    <div className="bg-gradient-to-br from-indigo-500/5 to-purple-600/10 rounded-2xl p-5 border border-purple-500/20 shadow-md">
                                        <h3 className="text-[10px] uppercase tracking-widest font-bold text-purple-600 dark:text-purple-400 mb-3 flex items-center gap-2">
                                            <TrendingUp className="w-3 h-3" /> Copilot Recommendation
                                        </h3>
                                        <p className="text-sm font-medium text-[var(--text-primary)] leading-relaxed">
                                            {cls.recommendation}
                                        </p>
                                        <button className="mt-4 w-full py-2.5 bg-gradient-to-r from-purple-500 to-indigo-600 text-white text-xs font-bold rounded-xl hover:shadow-lg hover:shadow-purple-500/25 transition-all outline-none focus:ring-2 focus:ring-purple-500/50">
                                            Deploy Action Plan
                                        </button>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
