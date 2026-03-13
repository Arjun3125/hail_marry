"use client";

import { useEffect, useState } from "react";
import { Plus, Loader2, Star, CheckCircle, Brain, Zap } from "lucide-react";

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
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="mb-6">
                <div className="flex items-center gap-3 mb-1">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg">
                        <Brain className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">
                            Spaced Repetition
                        </h1>
                        <p className="text-xs text-[var(--text-muted)]">
                            SM-2 Algorithm • Long-term memory builder
                        </p>
                    </div>
                </div>
            </div>

            {error ? (
                <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {/* Add new review card */}
            <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-4 mb-6 border border-[var(--border)]/50">
                <div className="flex flex-col gap-3 sm:flex-row">
                    <input
                        value={newTopic}
                        onChange={(e) => setNewTopic(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") void addReview(); }}
                        placeholder="Add a topic to review (e.g. Photosynthesis, Newton's Laws)..."
                        className="flex-1 px-4 py-2.5 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50"
                    />
                    <button
                        onClick={() => void addReview()}
                        disabled={adding || !newTopic.trim()}
                        className="w-full sm:w-auto px-5 py-2.5 bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-medium rounded-xl hover:shadow-lg transition-all duration-200 disabled:opacity-40 flex items-center justify-center gap-2 hover:scale-[1.02]"
                    >
                        {adding ? <Loader2 className="w-4 h-4 animate-spin" /> : <Plus className="w-4 h-4" />}
                        Add Topic
                    </button>
                </div>
            </div>

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-12 text-center border border-[var(--border)]/50">
                    <Loader2 className="w-8 h-8 mx-auto text-violet-500 animate-spin mb-3" />
                    <p className="text-sm text-[var(--text-muted)]">Loading reviews...</p>
                </div>
            ) : !data || data.total === 0 ? (
                <div className="bg-[var(--bg-card)] rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center shadow-lg">
                        <Brain className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">No review topics yet</h3>
                    <p className="text-sm text-[var(--text-muted)] max-w-md mx-auto">
                        Add topics above to start building your long-term memory with scientifically-proven spaced repetition!
                    </p>
                </div>
            ) : (
                <>
                    {/* Stats strip */}
                    <div className="grid grid-cols-1 gap-3 mb-6 sm:grid-cols-3">
                        <div className="bg-gradient-to-br from-rose-500 to-red-600 rounded-xl p-3 text-center text-white shadow-md">
                            <p className="text-2xl font-bold">{data.due.length}</p>
                            <p className="text-[10px] uppercase tracking-wider opacity-80">Due Now</p>
                        </div>
                        <div className="bg-gradient-to-br from-emerald-500 to-green-600 rounded-xl p-3 text-center text-white shadow-md">
                            <p className="text-2xl font-bold">{data.upcoming.length}</p>
                            <p className="text-[10px] uppercase tracking-wider opacity-80">Upcoming</p>
                        </div>
                        <div className="bg-gradient-to-br from-violet-500 to-purple-600 rounded-xl p-3 text-center text-white shadow-md">
                            <p className="text-2xl font-bold">{data.total}</p>
                            <p className="text-[10px] uppercase tracking-wider opacity-80">Total Topics</p>
                        </div>
                    </div>

                    {/* Due Reviews */}
                    {data.due.length > 0 ? (
                        <div className="mb-6">
                            <h2 className="text-sm font-bold text-[var(--text-primary)] mb-3 flex items-center gap-2 uppercase tracking-wider">
                                <Zap className="w-4 h-4 text-amber-500" />
                                Due for Review
                            </h2>
                            <div className="space-y-3">
                                {data.due.map((review) => (
                                    <div key={review.id} className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-4 border-l-4 border-rose-500 border border-[var(--border)]/50 transition-all duration-200 hover:shadow-md">
                                        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
                                            <div>
                                                <p className="text-sm font-bold text-[var(--text-primary)]">{review.topic}</p>
                                                <div className="flex flex-wrap items-center gap-2 mt-1">
                                                    <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-page)] px-2 py-0.5 rounded-full">
                                                        {review.review_count}× reviewed
                                                    </span>
                                                    <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-page)] px-2 py-0.5 rounded-full">
                                                        {review.interval_days}d interval
                                                    </span>
                                                    <span className="text-[10px] text-[var(--text-muted)] bg-[var(--bg-page)] px-2 py-0.5 rounded-full">
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
                                                            className={`px-2.5 py-1.5 rounded-lg text-white text-[10px] font-bold bg-gradient-to-r ${r.color} hover:shadow-md transition-all duration-200 hover:scale-105 disabled:opacity-40`}
                                                            title={r.desc}
                                                        >
                                                            {r.label}
                                                        </button>
                                                    ))}
                                                </div>
                                            ) : (
                                                <button
                                                    onClick={() => setRatingCard(review.id)}
                                                    className="px-4 py-2 bg-gradient-to-r from-violet-500 to-purple-600 text-white text-xs font-bold rounded-xl hover:shadow-lg transition-all duration-200 flex items-center gap-1.5 hover:scale-[1.02]"
                                                >
                                                    <Star className="w-3.5 h-3.5" />
                                                    Review
                                                </button>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    ) : null}

                    {/* Upcoming Reviews */}
                    {data.upcoming.length > 0 ? (
                        <div>
                            <h2 className="text-sm font-bold text-[var(--text-primary)] mb-3 flex items-center gap-2 uppercase tracking-wider">
                                <CheckCircle className="w-4 h-4 text-emerald-500" />
                                Upcoming
                            </h2>
                            <div className="space-y-2">
                                {data.upcoming.map((review) => (
                                    <div key={review.id} className="bg-[var(--bg-card)] rounded-xl shadow-sm p-3 flex items-center justify-between border border-[var(--border)]/50 hover:shadow-md transition-all duration-200">
                                        <div>
                                            <p className="text-sm font-medium text-[var(--text-primary)]">{review.topic}</p>
                                            <p className="text-[10px] text-[var(--text-muted)] mt-0.5">
                                                Due {new Date(review.next_review_at).toLocaleDateString()} · {review.review_count}× reviewed
                                            </p>
                                        </div>
                                        <span className="text-[10px] font-semibold text-status-emerald bg-emerald-subtle px-2.5 py-1 rounded-full">
                                            {review.interval_days}d
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
