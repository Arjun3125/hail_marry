"use client";

import { useEffect, useState } from "react";
import { Trophy, Medal, Clock, TrendingUp, ChevronDown, CheckCircle2, ChevronRight, Crown } from "lucide-react";
import { api } from "@/lib/api";

type TestSeries = {
    id: string;
    name: string;
    description: string;
    total_marks: number;
    duration_minutes: number;
    attempts: number;
};

type LeaderboardEntry = {
    rank: number;
    student_name: string;
    student_id: string;
    marks_obtained: number;
    total_marks: number;
    pct: number;
    percentile: number;
    time_taken: number | null;
};

type LeaderboardData = {
    series_name: string;
    total_marks: number;
    total_attempts: number;
    leaderboard: LeaderboardEntry[];
};

export default function LeaderboardPage() {
    const [seriesList, setSeriesList] = useState<TestSeries[]>([]);
    const [selectedId, setSelectedId] = useState<string | null>(null);
    const [leaderboard, setLeaderboard] = useState<LeaderboardData | null>(null);
    const [myRank, setMyRank] = useState<{ rank: number | null; percentile: number | null; pct: number } | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                const data = await api.student.testSeries();
                setSeriesList((data || []) as TestSeries[]);
                if (Array.isArray(data) && data.length > 0) {
                    setSelectedId(data[0].id);
                }
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load test series");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    useEffect(() => {
        if (!selectedId) return;
        const load = async () => {
            try {
                const [lb, rank] = await Promise.all([
                    api.student.leaderboard(selectedId),
                    api.student.myRank(selectedId),
                ]);
                setLeaderboard(lb as LeaderboardData);
                setMyRank(rank as { rank: number | null; percentile: number | null; pct: number });
            } catch {
                // leaderboard might not exist yet
            }
        };
        void load();
    }, [selectedId]);

    const getRankStyle = (rank: number) => {
        if (rank === 1) return { color: "text-amber-500", bg: "bg-amber-500/10", border: "border-amber-500/50", icon: <Crown className="w-6 h-6 text-amber-500 drop-shadow-md" /> };
        if (rank === 2) return { color: "text-slate-300", bg: "bg-slate-300/10", border: "border-slate-400/50", icon: <Medal className="w-5 h-5 text-slate-300 drop-shadow-md" /> };
        if (rank === 3) return { color: "text-orange-400", bg: "bg-orange-400/10", border: "border-orange-500/50", icon: <Medal className="w-5 h-5 text-orange-400 drop-shadow-md" /> };
        return { color: "text-[var(--text-primary)]", bg: "bg-[var(--bg-card)]", border: "border-transparent", icon: null };
    };

    return (
        <div className="max-w-5xl mx-auto space-y-6 animate-in slide-in-from-bottom-4 duration-500 fade-in pb-12">
            
            {/* Header Area */}
            <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4 mb-8">
                <div>
                    <h1 className="text-3xl font-black text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 via-amber-500 to-orange-500 flex items-center gap-3 drop-shadow-sm">
                        <Trophy className="w-8 h-8 text-yellow-500" />
                        Global Rankings
                    </h1>
                    <p className="text-sm font-medium text-[var(--text-muted)] mt-1.5 ml-1">
                        Track your academic standing and compete with peers worldwide.
                    </p>
                </div>

                {/* Series Selector - Glassmorphic Dropdown */}
                {seriesList.length > 0 && (
                    <div className="relative group">
                        <select
                            value={selectedId || ""}
                            onChange={(e) => setSelectedId(e.target.value)}
                            className="appearance-none pl-5 pr-12 py-3 text-sm font-bold border border-[var(--border-light)] rounded-2xl bg-[var(--bg-card)]/80 backdrop-blur-md text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-amber-500/50 shadow-sm cursor-pointer hover:bg-[var(--bg-card)] transition-colors w-full md:w-auto min-w-[200px]"
                        >
                            {seriesList.map((s) => (
                                <option key={s.id} value={s.id}>
                                    {s.name}
                                </option>
                            ))}
                        </select>
                        <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none w-6 h-6 rounded-md bg-[var(--bg-page)] flex items-center justify-center">
                            <ChevronDown className="w-3.5 h-3.5 text-[var(--text-secondary)]" />
                        </div>
                    </div>
                )}
            </div>

            {error && (
                <div className="rounded-xl border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-500 shadow-md flex items-center gap-2">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="flex flex-col items-center justify-center p-20 glass-panel border border-[var(--border-light)] rounded-3xl opacity-70">
                    <Trophy className="w-12 h-12 text-[var(--text-muted)] mb-4 animate-bounce" />
                    <p className="text-sm font-medium text-[var(--text-muted)]">Calculating percentiles...</p>
                </div>
            ) : seriesList.length === 0 ? (
                <div className="glass-panel border border-[var(--border-light)] rounded-3xl p-12 text-center flex flex-col items-center justify-center">
                    <div className="w-20 h-20 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-900 rounded-full flex items-center justify-center mb-6 shadow-inner">
                        <Trophy className="w-10 h-10 text-[var(--text-muted)] opacity-50" />
                    </div>
                    <h3 className="text-xl font-bold text-[var(--text-primary)] mb-2">No Challenges Active</h3>
                    <p className="text-sm text-[var(--text-secondary)] max-w-sm">
                        You're currently not enrolled in any competitive test series. New challenges will appear here.
                    </p>
                </div>
            ) : (
                <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
                    
                    {/* Left Column - My Stats */}
                    {myRank && myRank.rank && (
                        <div className="lg:col-span-4 space-y-4">
                            <h2 className="text-sm font-bold uppercase tracking-widest text-[var(--text-muted)] mb-3 flex items-center gap-2">
                                <TrendingUp className="w-4 h-4" /> My Performance
                            </h2>
                            
                            {/* Primary Rank Card */}
                            <div className="relative overflow-hidden bg-gradient-to-br from-amber-500/20 via-orange-500/10 to-transparent dark:from-amber-900/30 border border-amber-500/30 rounded-3xl p-6 shadow-lg shadow-amber-500/5 group hover:shadow-amber-500/10 transition-all duration-300">
                                <div className="absolute -right-6 -top-6 w-32 h-32 bg-gradient-to-br from-amber-400 to-orange-500 rounded-full blur-[60px] opacity-20 pointer-events-none group-hover:scale-110 transition-transform"></div>
                                
                                <div className="flex items-center justify-between mb-4">
                                    <div className="flex bg-amber-500/20 rounded-full p-2 items-center justify-center">
                                        <Trophy className="w-5 h-5 text-amber-600 dark:text-amber-400" />
                                    </div>
                                    <span className="text-xs font-bold text-amber-600 dark:text-amber-400 uppercase tracking-wider bg-amber-500/10 px-2.5 py-1 rounded-full">Current Rank</span>
                                </div>
                                
                                <div className="mt-2 flex items-baseline gap-1">
                                    <span className="text-5xl font-black text-amber-600 dark:text-amber-400 drop-shadow-sm">#{myRank.rank}</span>
                                </div>
                                <p className="text-xs font-medium text-amber-700/70 dark:text-amber-400/70 mt-2">
                                    Out of {leaderboard?.total_attempts || 0} competitors
                                </p>
                            </div>

                            {/* Secondary Stats Grid */}
                            <div className="grid grid-cols-2 gap-4">
                                <div className="glass-panel border border-[var(--border-light)] rounded-2xl p-5 shadow-sm hover:border-blue-500/30 transition-colors group">
                                    <div className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider mb-2 group-hover:text-blue-500 transition-colors">Percentile</div>
                                    <div className="text-2xl font-black text-[var(--text-primary)]">
                                        {myRank.percentile}<span className="text-sm font-bold text-[var(--text-muted)] ml-0.5">%</span>
                                    </div>
                                </div>
                                <div className="glass-panel border border-[var(--border-light)] rounded-2xl p-5 shadow-sm hover:border-emerald-500/30 transition-colors group">
                                    <div className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider mb-2 group-hover:text-emerald-500 transition-colors">Avg Score</div>
                                    <div className="text-2xl font-black text-[var(--text-primary)]">
                                        {myRank.pct}<span className="text-sm font-bold text-[var(--text-muted)] ml-0.5">%</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Right Column - Leaderboard Table */}
                    {leaderboard && leaderboard.leaderboard.length > 0 && (
                        <div className="lg:col-span-8 glass-panel border border-[var(--border-light)] rounded-3xl shadow-lg relative overflow-hidden flex flex-col">
                            
                            {/* Subtle background glow */}
                            <div className="absolute top-0 right-0 w-64 h-64 bg-indigo-500/5 rounded-full blur-[80px] pointer-events-none -z-10"></div>

                            {/* Table Header */}
                            <div className="px-6 py-5 border-b border-[var(--border-light)] bg-gradient-to-r from-[var(--bg-card)]/50 to-transparent">
                                <h2 className="text-lg font-bold text-[var(--text-primary)] flex items-center gap-2">
                                    <CheckCircle2 className="w-5 h-5 text-indigo-500" />
                                    {leaderboard.series_name} Standings
                                </h2>
                                <p className="text-xs font-medium text-[var(--text-muted)] mt-1 ml-7">
                                    Max Scale: {leaderboard.total_marks} Points Formats
                                </p>
                            </div>

                            {/* Table Content */}
                            <div className="overflow-x-auto">
                                <table className="w-full min-w-[500px] border-collapse">
                                    <thead>
                                        <tr className="bg-[var(--bg-page)]/50 text-[10px] uppercase tracking-widest text-[var(--text-muted)] font-black border-b border-[var(--border-light)]">
                                            <th className="px-6 py-4 text-center w-20">Pos</th>
                                            <th className="px-6 py-4 text-left">Challenger</th>
                                            <th className="px-6 py-4 text-center">Score</th>
                                            <th className="px-6 py-4 text-center hidden sm:table-cell">Tile</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {leaderboard.leaderboard.map((entry, idx) => {
                                            const style = getRankStyle(entry.rank);
                                            const isTop3 = entry.rank <= 3;
                                            
                                            return (
                                                <tr
                                                    key={entry.student_id}
                                                    className={`group transition-all duration-300 hover:bg-[var(--bg-page)]/80 border-b border-[var(--border-neutral)] last:border-0 relative ${
                                                        isTop3 ? style.bg : ""
                                                    }`}
                                                >
                                                    {/* Left indicator bar for top 3 */}
                                                    {isTop3 && (
                                                        <td className="absolute left-0 top-0 bottom-0 w-1 bg-gradient-to-b from-transparent via-current to-transparent opacity-50" style={{ color: style.color.replace('text-', 'bg-') }}></td>
                                                    )}

                                                    <td className="px-6 py-4 text-center">
                                                        <span className={`inline-flex items-center justify-center w-8 h-8 rounded-full font-black text-sm shadow-sm ${
                                                            isTop3 
                                                                ? `${style.bg} ${style.color} border border-current/20` 
                                                                : "bg-[var(--bg-card)] border border-[var(--border-light)] text-[var(--text-secondary)] group-hover:scale-110 transition-transform"
                                                        }`}>
                                                            {entry.rank}
                                                        </span>
                                                    </td>
                                                    <td className="px-6 py-4">
                                                        <div className="flex items-center gap-3">
                                                            {isTop3 && style.icon}
                                                            <div>
                                                                <p className={`text-sm font-bold ${isTop3 ? style.color : "text-[var(--text-primary)]"} transition-colors`}>
                                                                    {entry.student_name}
                                                                </p>
                                                                {entry.time_taken && (
                                                                    <p className="text-[10px] text-[var(--text-muted)] flex items-center gap-1 mt-0.5">
                                                                        <Clock className="w-3 h-3" /> {entry.time_taken}m completed
                                                                    </p>
                                                                )}
                                                            </div>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 text-center">
                                                        <div className="flex flex-col items-center">
                                                            <span className="text-base font-black text-[var(--text-primary)] tracking-tight">
                                                                {entry.marks_obtained}
                                                            </span>
                                                            <span className="text-[10px] font-bold text-[var(--text-muted)]">
                                                                {entry.pct}%
                                                            </span>
                                                        </div>
                                                    </td>
                                                    <td className="px-6 py-4 text-center hidden sm:table-cell">
                                                        <div className="flex items-center justify-center">
                                                            <span className={`text-xs font-black px-2.5 py-1 rounded-md border ${
                                                                entry.percentile >= 95 ? "bg-emerald-500/10 text-emerald-600 border-emerald-500/20 dark:text-emerald-400"
                                                                : entry.percentile >= 80 ? "bg-blue-500/10 text-blue-600 border-blue-500/20 dark:text-blue-400"
                                                                : entry.percentile >= 50 ? "bg-amber-500/10 text-amber-600 border-amber-500/20 dark:text-amber-400"
                                                                : "bg-[var(--bg-page)] text-[var(--text-muted)] border-[var(--border-light)]"
                                                            }`}>
                                                                {entry.percentile} P
                                                            </span>
                                                        </div>
                                                    </td>
                                                </tr>
                                            );
                                        })}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
}
