"use client";

import { type ReactNode, useEffect, useState } from "react";
import { Plus, Loader2, Star, CheckCircle, Brain, Zap, Clock3, Sparkles } from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismInput } from "@/components/prism/PrismControls";
import { PrismHeroKicker, PrismPage, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type ReviewItem = {
    id: string;
    topic: string;
    subject_id: string | null;
    next_review_at: string;
    interval_days: number;
    ease_factor: number;
    review_count: number;
    is_due: boolean;
};

type ReviewsData = {
    due: ReviewItem[];
    upcoming: ReviewItem[];
    total: number;
};

const ratingLabels = [
    { value: 1, label: "Again", color: "from-red-500 to-rose-600", desc: "Completely forgot" },
    { value: 2, label: "Hard", color: "from-orange-400 to-amber-500", desc: "Struggled a lot" },
    { value: 3, label: "Good", color: "from-yellow-400 to-amber-400", desc: "Some effort needed" },
    { value: 4, label: "Easy", color: "from-green-400 to-emerald-500", desc: "Recalled well" },
    { value: 5, label: "Perfect", color: "from-emerald-500 to-teal-600", desc: "Effortless recall" },
];

export default function ReviewsPage() {
    const [data, setData] = useState<ReviewsData | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [newTopic, setNewTopic] = useState("");
    const [adding, setAdding] = useState(false);
    const [ratingCard, setRatingCard] = useState<string | null>(null);
    const [submitting, setSubmitting] = useState(false);

    const loadReviews = async () => {
        try {
            setLoading(true);
            setError(null);
            const payload = (await api.student.reviews()) as ReviewsData;
            setData(payload);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load reviews");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void loadReviews();
    }, []);

    const addReview = async () => {
        if (!newTopic.trim()) return;
        try {
            setAdding(true);
            await api.student.createReview({ topic: newTopic.trim() });
            setNewTopic("");
            await loadReviews();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to add review");
        } finally {
            setAdding(false);
        }
    };

    const completeReview = async (id: string, rating: number) => {
        try {
            setSubmitting(true);
            await api.student.completeReview(id, { rating });
            setRatingCard(null);
            await loadReviews();
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to complete review");
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <PrismPage className="space-y-6">
            <PrismSection className="space-y-6">
                <div className="grid gap-6 xl:grid-cols-[1.12fr_0.88fr]">
                    <div className="space-y-4">
                        <PrismHeroKicker>
                            <Sparkles className="h-3.5 w-3.5" />
                            Student retention loop
                        </PrismHeroKicker>
                        <div className="space-y-3">
                            <h1 className="prism-title text-4xl font-black leading-[0.98] text-[var(--text-primary)] md:text-5xl">
                                Keep hard-won concepts alive with a <span className="premium-gradient">clear spaced repetition ledger</span>
                            </h1>
                            <p className="max-w-3xl text-base leading-7 text-[var(--text-secondary)] md:text-lg">
                                This route now separates due reviews, upcoming reviews, and topic creation so you can protect recall without losing flow in the rest of the student workspace.
                            </p>
                        </div>
                    </div>

                    <div className="grid gap-3 sm:grid-cols-3 xl:grid-cols-1">
                        <MetricCard
                            icon={<Zap className="h-5 w-5 text-rose-400" />}
                            label="Due now"
                            value={`${data?.due.length ?? 0}`}
                            detail="Cards and concepts that need recall work right away."
                            bg="bg-[linear-gradient(135deg,rgba(251,113,133,0.18),rgba(239,68,68,0.08))]"
                        />
                        <MetricCard
                            icon={<Clock3 className="h-5 w-5 text-status-emerald" />}
                            label="Upcoming"
                            value={`${data?.upcoming.length ?? 0}`}
                            detail="Topics already scheduled for later recall reinforcement."
                            bg="bg-[linear-gradient(135deg,rgba(52,211,153,0.18),rgba(16,185,129,0.08))]"
                        />
                        <MetricCard
                            icon={<Brain className="h-5 w-5 text-[var(--primary)]" />}
                            label="Total topics"
                            value={`${data?.total ?? 0}`}
                            detail="The long-term memory set currently managed by SM-2."
                            bg="bg-[linear-gradient(135deg,rgba(168,85,247,0.18),rgba(99,102,241,0.08))]"
                        />
                    </div>
                </div>

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="student-reviews"
                        onRetry={() => void loadReviews()}
                        simplifiedModeHref="/student/tools"
                    />
                ) : null}

                <PrismPanel className="p-5">
                    <div className="space-y-1">
                        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Add a topic</p>
                        <h2 className="text-lg font-semibold text-[var(--text-primary)]">Seed a new long-term memory track</h2>
                        <p className="text-sm leading-6 text-[var(--text-secondary)]">
                            Add a concept, chapter, or problem area and let the review engine schedule the next recall checkpoints automatically.
                        </p>
                    </div>
                    <div className="mt-4 flex flex-col gap-3 sm:flex-row">
                        <PrismInput
                            value={newTopic}
                            onChange={(e) => setNewTopic(e.target.value)}
                            onKeyDown={(e) => {
                                if (e.key === "Enter") void addReview();
                            }}
                            placeholder="Add a topic to review, for example Photosynthesis or Newton's Laws"
                            className="flex-1 text-sm"
                        />
                        <button
                            onClick={() => void addReview()}
                            disabled={adding || !newTopic.trim()}
                            className="inline-flex items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(139,92,246,0.96),rgba(99,102,241,0.94))] px-5 py-3 text-sm font-semibold text-white shadow-[0_18px_34px_rgba(99,102,241,0.22)] transition hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-40"
                        >
                            {adding ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                            Add Topic
                        </button>
                    </div>
                </PrismPanel>

                {loading ? (
                    <PrismPanel className="p-12 text-center">
                        <Loader2 className="mx-auto mb-3 h-8 w-8 animate-spin text-[var(--primary)]" />
                        <p className="text-sm text-[var(--text-muted)]">Loading reviews...</p>
                    </PrismPanel>
                ) : !data || data.total === 0 ? (
                    <EmptyState
                        icon={Brain}
                        title="No review topics yet"
                        description="Add topics above to start building long-term recall with scheduled spaced repetition."
                    />
                ) : (
                    <div className="grid gap-6 xl:grid-cols-[1.02fr_0.98fr]">
                        <PrismPanel className="space-y-4 p-5">
                            <div className="flex items-center gap-2">
                                <Zap className="h-4 w-4 text-amber-400" />
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Due for review</p>
                            </div>
                            {data.due.length === 0 ? (
                                <EmptyState
                                    icon={CheckCircle}
                                    title="Nothing due right now"
                                    description="Your urgent reviews are clear. Check the upcoming list to see what is scheduled next."
                                />
                            ) : (
                                <div className="space-y-3">
                                    {data.due.map((review) => (
                                        <div key={review.id} className="rounded-[calc(var(--radius)*0.98)] border border-white/10 bg-black/10 p-4">
                                            <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                                                <div className="space-y-2">
                                                    <p className="text-sm font-semibold text-[var(--text-primary)]">{review.topic}</p>
                                                    <div className="flex flex-wrap items-center gap-2">
                                                        <span className="rounded-full bg-white/5 px-2.5 py-1 text-[10px] text-[var(--text-muted)]">
                                                            {review.review_count}x reviewed
                                                        </span>
                                                        <span className="rounded-full bg-white/5 px-2.5 py-1 text-[10px] text-[var(--text-muted)]">
                                                            {review.interval_days}d interval
                                                        </span>
                                                        <span className="rounded-full bg-white/5 px-2.5 py-1 text-[10px] text-[var(--text-muted)]">
                                                            EF {review.ease_factor}
                                                        </span>
                                                    </div>
                                                </div>
                                                {ratingCard === review.id ? (
                                                    <div className="flex flex-wrap gap-1.5 sm:justify-end">
                                                        {ratingLabels.map((r) => (
                                                            <button
                                                                key={r.value}
                                                                onClick={() => void completeReview(review.id, r.value)}
                                                                disabled={submitting}
                                                                className={`rounded-xl bg-gradient-to-r ${r.color} px-2.5 py-1.5 text-[10px] font-bold text-white transition hover:-translate-y-0.5 hover:shadow-md disabled:opacity-40`}
                                                                title={r.desc}
                                                            >
                                                                {r.label}
                                                            </button>
                                                        ))}
                                                    </div>
                                                ) : (
                                                    <button
                                                        onClick={() => setRatingCard(review.id)}
                                                        className="inline-flex items-center gap-1.5 rounded-2xl bg-[linear-gradient(135deg,rgba(139,92,246,0.96),rgba(99,102,241,0.94))] px-4 py-2 text-xs font-semibold text-white transition hover:-translate-y-0.5"
                                                    >
                                                        <Star className="h-3.5 w-3.5" />
                                                        Review
                                                    </button>
                                                )}
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </PrismPanel>

                        <PrismPanel className="space-y-4 p-5">
                            <div className="flex items-center gap-2">
                                <CheckCircle className="h-4 w-4 text-status-emerald" />
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Upcoming</p>
                            </div>
                            {data.upcoming.length === 0 ? (
                                <EmptyState
                                    icon={Clock3}
                                    title="No upcoming reviews yet"
                                    description="Upcoming scheduled reviews will appear here after you complete your first passes."
                                />
                            ) : (
                                <div className="space-y-2">
                                    {data.upcoming.map((review) => (
                                        <div key={review.id} className="flex items-center justify-between gap-3 rounded-[calc(var(--radius)*0.92)] border border-white/10 bg-black/10 p-4">
                                            <div>
                                                <p className="text-sm font-medium text-[var(--text-primary)]">{review.topic}</p>
                                                <p className="mt-1 text-[11px] text-[var(--text-muted)]">
                                                    Due {new Date(review.next_review_at).toLocaleDateString()} · {review.review_count}x reviewed
                                                </p>
                                            </div>
                                            <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-[10px] font-semibold text-status-emerald">
                                                {review.interval_days}d
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            )}
                        </PrismPanel>
                    </div>
                )}
            </PrismSection>
        </PrismPage>
    );
}

function MetricCard({
    icon,
    label,
    value,
    detail,
    bg,
}: {
    icon: ReactNode;
    label: string;
    value: string;
    detail: string;
    bg: string;
}) {
    return (
        <PrismPanel className="p-4">
            <div className={`mb-3 flex h-11 w-11 items-center justify-center rounded-2xl ${bg}`}>{icon}</div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
            <p className="mt-2 text-2xl font-black text-[var(--text-primary)]">{value}</p>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p>
        </PrismPanel>
    );
}
