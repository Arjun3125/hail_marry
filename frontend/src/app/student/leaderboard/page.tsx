"use client";

import { useEffect, useState } from "react";
import { CheckCircle2, Clock, Crown, Medal, Trophy, TrendingUp } from "lucide-react";

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
import { useNetworkAware } from "@/hooks/useNetworkAware";
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
    const { isSlowConnection, saveData } = useNetworkAware();
    const reducedVisualMode = isSlowConnection || saveData;
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
                setError(null);
                const data = await api.student.testSeries();
                setSeriesList((data || []) as TestSeries[]);
                if (Array.isArray(data) && data.length > 0) setSelectedId(data[0].id);
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
                const [lb, rank] = await Promise.all([api.student.leaderboard(selectedId), api.student.myRank(selectedId)]);
                setLeaderboard(lb as LeaderboardData);
                setMyRank(rank as { rank: number | null; percentile: number | null; pct: number });
            } catch {
                setLeaderboard(null);
                setMyRank(null);
            }
        };
        void load();
    }, [selectedId]);

    const topIcon = (rank: number) => {
        if (rank === 1) return <Crown className="h-4 w-4 text-amber-500" />;
        if (rank === 2) return <Medal className="h-4 w-4 text-slate-400" />;
        if (rank === 3) return <Medal className="h-4 w-4 text-orange-500" />;
        return null;
    };

    return (
        <PrismPage variant="report" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Trophy className="h-3.5 w-3.5" />Rankings</PrismHeroKicker>}
                    title="Use rankings as feedback, not just competition"
                    description="This page shows how you are performing inside a test series so you can understand your standing, percentile, and where more revision may help."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Active series</span>
                        <strong className="prism-status-value">{seriesList.length}</strong>
                        <span className="prism-status-detail">Test series currently available for ranking</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">My rank</span>
                        <strong className="prism-status-value">{myRank?.rank ?? "—"}</strong>
                        <span className="prism-status-detail">Current standing in the selected series</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">My percentile</span>
                        <strong className="prism-status-value">{myRank?.percentile ?? "—"}{myRank?.percentile !== null && myRank?.percentile !== undefined ? "%" : ""}</strong>
                        <span className="prism-status-detail">Relative performance against the current cohort</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-leaderboard" onRetry={() => window.location.reload()} /> : null}

                {loading ? (
                    <PrismPanel className="p-8"><p className="text-sm text-[var(--text-secondary)]">Loading rankings...</p></PrismPanel>
                ) : seriesList.length === 0 ? (
                    <PrismPanel className="p-6">
                        <EmptyState icon={Trophy} title="No active test series" description="Rankings will appear here once you are enrolled in a competitive test series." eyebrow="No challenges yet" />
                    </PrismPanel>
                ) : (
                    <div className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
                        <div className="space-y-6">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title="Series selector" description="Switch between test series to compare your position across different assessments." />
                                <select value={selectedId || ""} onChange={(e) => setSelectedId(e.target.value)} className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3 text-sm text-[var(--text-primary)]">
                                    {seriesList.map((series) => <option key={series.id} value={series.id}>{series.name}</option>)}
                                </select>
                            </PrismPanel>

                            {myRank?.rank ? (
                                <PrismPanel className="space-y-4 p-5">
                                    <PrismSectionHeader title="My standing" description="Treat this as feedback for revision planning rather than a scorecard by itself." />
                                    <InfoTile icon={Trophy} label="Current rank" value={`#${myRank.rank}`} />
                                    <InfoTile icon={TrendingUp} label="Percentile" value={`${myRank.percentile ?? "—"}%`} />
                                    <InfoTile icon={CheckCircle2} label="Average score" value={`${myRank.pct}%`} />
                                </PrismPanel>
                            ) : null}
                        </div>

                        <PrismPanel className="space-y-5 p-5">
                            <PrismSectionHeader title={leaderboard?.series_name || "Leaderboard"} description={leaderboard ? `${leaderboard.total_attempts} competitors • ${leaderboard.total_marks} total marks` : "Series standings"} />
                            {leaderboard && leaderboard.leaderboard.length > 0 ? (
                                <div className="overflow-x-auto">
                                    <table className="w-full min-w-[520px]">
                                        <thead>
                                            <tr className="border-b border-[var(--border)]">
                                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Rank</th>
                                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Student</th>
                                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Score</th>
                                                <th className="px-4 py-3 text-left text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">Percentile</th>
                                            </tr>
                                        </thead>
                                        <tbody>
                                            {leaderboard.leaderboard.map((entry) => (
                                                <tr key={entry.student_id} className={`border-b border-[var(--border-light)] ${entry.rank <= 3 && !reducedVisualMode ? "bg-[rgba(255,255,255,0.02)]" : ""}`}>
                                                    <td className="px-4 py-3">
                                                        <div className="flex items-center gap-2 text-sm font-semibold text-[var(--text-primary)]">
                                                            {topIcon(entry.rank)}
                                                            #{entry.rank}
                                                        </div>
                                                    </td>
                                                    <td className="px-4 py-3">
                                                        <p className="text-sm font-medium text-[var(--text-primary)]">{entry.student_name}</p>
                                                        {entry.time_taken ? <p className="mt-1 text-xs text-[var(--text-muted)]"><Clock className="mr-1 inline h-3 w-3" />{entry.time_taken} min</p> : null}
                                                    </td>
                                                    <td className="px-4 py-3 text-sm text-[var(--text-primary)]">{entry.marks_obtained} / {entry.total_marks} <span className="text-xs text-[var(--text-muted)]">({entry.pct}%)</span></td>
                                                    <td className="px-4 py-3 text-sm font-medium text-[var(--text-primary)]">{entry.percentile} P</td>
                                                </tr>
                                            ))}
                                        </tbody>
                                    </table>
                                </div>
                            ) : (
                                <EmptyState icon={Trophy} title="No leaderboard data yet" description="Standings will appear here once this series has recorded enough attempts to rank students." eyebrow="No standings yet" />
                            )}
                        </PrismPanel>
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function InfoTile({ icon: Icon, label, value }: { icon: typeof Trophy; label: string; value: string }) {
    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4">
            <div className="flex items-center gap-2 text-[var(--text-secondary)]">
                <Icon className="h-4 w-4" />
                <p className="text-xs font-semibold uppercase tracking-[0.16em]">{label}</p>
            </div>
            <p className="mt-3 text-2xl font-semibold text-[var(--text-primary)]">{value}</p>
        </div>
    );
}
