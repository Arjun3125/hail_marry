"use client";

import { useEffect, useState } from "react";
import { Trophy, Medal, Clock, TrendingUp, ChevronDown } from "lucide-react";
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
                setError(err instanceof Error ? err.message : "Failed to load");
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

    const getRankEmoji = (rank: number) => {
        if (rank === 1) return "🥇";
        if (rank === 2) return "🥈";
        if (rank === 3) return "🥉";
        return `#${rank}`;
    };

    const getRankColor = (rank: number) => {
        if (rank === 1) return "text-yellow-500";
        if (rank === 2) return "text-gray-400";
        if (rank === 3) return "text-status-amber";
        return "text-[var(--text-primary)]";
    };

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)] flex items-center gap-2">
                    <Trophy className="w-6 h-6 text-yellow-500" />
                    Leaderboard & Rankings
                </h1>
                <p className="text-sm text-[var(--text-secondary)]">
                    See how you rank against other students in mock tests
                </p>
            </div>

            {error && (
                <div className="mb-4 rounded-lg border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="text-sm text-[var(--text-muted)]">Loading test series...</div>
            ) : seriesList.length === 0 ? (
                <div className="bg-[var(--bg-card)] rounded-xl p-8 shadow-[var(--shadow-card)] text-center">
                    <Trophy className="w-12 h-12 mx-auto text-[var(--text-muted)] mb-3" />
                    <p className="text-[var(--text-secondary)]">No test series available yet.</p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">Ask your teacher to create a mock test series.</p>
                </div>
            ) : (
                <>
                    {/* Series selector */}
                    <div className="mb-6">
                        <div className="relative inline-block">
                            <select
                                value={selectedId || ""}
                                onChange={(e) => setSelectedId(e.target.value)}
                                className="appearance-none pl-4 pr-10 py-2.5 text-sm font-medium border border-[var(--border)] rounded-lg bg-[var(--bg-card)] text-[var(--text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--primary)]"
                            >
                                {seriesList.map((s) => (
                                    <option key={s.id} value={s.id}>
                                        {s.name} ({s.attempts} attempts)
                                    </option>
                                ))}
                            </select>
                            <ChevronDown className="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-[var(--text-muted)] pointer-events-none" />
                        </div>
                    </div>

                    {/* My Rank Card */}
                    {myRank && myRank.rank && (
                        <div className="grid grid-cols-3 gap-4 mb-6">
                            <div className="bg-gradient-to-br from-yellow-50 to-amber-50 dark:from-yellow-900/20 dark:to-amber-900/20 rounded-xl p-5 shadow-sm border border-yellow-200/50">
                                <div className="flex items-center gap-2 mb-2">
                                    <Medal className="w-5 h-5 text-yellow-600" />
                                    <span className="text-xs font-medium text-yellow-700 dark:text-yellow-400">Your Rank</span>
                                </div>
                                <p className="text-3xl font-bold text-yellow-600">
                                    {getRankEmoji(myRank.rank)}
                                </p>
                            </div>
                            <div className="bg-[var(--bg-card)] rounded-xl p-5 shadow-[var(--shadow-card)]">
                                <div className="flex items-center gap-2 mb-2">
                                    <TrendingUp className="w-5 h-5 text-[var(--primary)]" />
                                    <span className="text-xs font-medium text-[var(--text-muted)]">Percentile</span>
                                </div>
                                <p className="text-3xl font-bold text-[var(--primary)]">
                                    {myRank.percentile}%
                                </p>
                            </div>
                            <div className="bg-[var(--bg-card)] rounded-xl p-5 shadow-[var(--shadow-card)]">
                                <div className="flex items-center gap-2 mb-2">
                                    <Trophy className="w-5 h-5 text-green-600" />
                                    <span className="text-xs font-medium text-[var(--text-muted)]">Score</span>
                                </div>
                                <p className="text-3xl font-bold text-[var(--text-primary)]">
                                    {myRank.pct}%
                                </p>
                            </div>
                        </div>
                    )}

                    {/* Leaderboard Table */}
                    {leaderboard && leaderboard.leaderboard.length > 0 && (
                        <div className="bg-[var(--bg-card)] rounded-xl shadow-[var(--shadow-card)] overflow-hidden">
                            <div className="px-5 py-4 border-b border-[var(--border)]">
                                <h2 className="text-base font-semibold text-[var(--text-primary)]">
                                    {leaderboard.series_name}
                                </h2>
                                <p className="text-xs text-[var(--text-muted)]">
                                    {leaderboard.total_attempts} students attempted • Max: {leaderboard.total_marks} marks
                                </p>
                            </div>
                            <div className="overflow-x-auto">
                                <table className="w-full min-w-[600px]">
                                    <thead>
                                        <tr className="border-b border-[var(--border)]">
                                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase w-16">Rank</th>
                                            <th className="px-5 py-3 text-left text-xs font-medium text-[var(--text-muted)] uppercase">Student</th>
                                            <th className="px-5 py-3 text-center text-xs font-medium text-[var(--text-muted)] uppercase">Score</th>
                                            <th className="px-5 py-3 text-center text-xs font-medium text-[var(--text-muted)] uppercase">Percentile</th>
                                            <th className="px-5 py-3 text-center text-xs font-medium text-[var(--text-muted)] uppercase">Time</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {leaderboard.leaderboard.map((entry) => (
                                            <tr
                                                key={entry.student_id}
                                                className={`border-b border-[var(--border-light)] hover:bg-[var(--bg-page)] transition-colors ${entry.rank <= 3 ? "bg-warning-subtle/30 dark:bg-yellow-900/5" : ""}`}
                                            >
                                                <td className="px-5 py-3">
                                                    <span className={`text-lg font-bold ${getRankColor(entry.rank)}`}>
                                                        {getRankEmoji(entry.rank)}
                                                    </span>
                                                </td>
                                                <td className="px-5 py-3">
                                                    <p className="text-sm font-medium text-[var(--text-primary)]">{entry.student_name}</p>
                                                </td>
                                                <td className="px-5 py-3 text-center">
                                                    <span className="text-sm font-bold text-[var(--text-primary)]">
                                                        {entry.marks_obtained}/{entry.total_marks}
                                                    </span>
                                                    <span className="text-xs text-[var(--text-muted)] ml-1">({entry.pct}%)</span>
                                                </td>
                                                <td className="px-5 py-3 text-center">
                                                    <span className={`text-sm font-medium ${entry.percentile >= 90 ? "text-green-600" : entry.percentile >= 70 ? "text-[var(--primary)]" : "text-[var(--text-secondary)]"}`}>
                                                        {entry.percentile}%
                                                    </span>
                                                </td>
                                                <td className="px-5 py-3 text-center">
                                                    <span className="text-xs text-[var(--text-muted)] flex items-center justify-center gap-1">
                                                        <Clock className="w-3 h-3" />
                                                        {entry.time_taken ? `${entry.time_taken}m` : "-"}
                                                    </span>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    )}
                </>
            )}
        </div>
    );
}
