"use client";

import { type ReactNode, useEffect, useState } from "react";
import {
    PolarAngleAxis,
    PolarGrid,
    PolarRadiusAxis,
    Radar,
    RadarChart,
    ResponsiveContainer,
    Tooltip,
} from "recharts";
import {
    Activity,
    BrainCircuit,
    Flame,
    GraduationCap,
    ShieldAlert,
    Target,
    TrendingUp,
} from "lucide-react";

import { SkeletonCard } from "@/components/Skeleton";
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

type RiskLevel = "low" | "medium" | "high";

type MasterySummary = {
    attendance_pct: number;
    absent_streak: number;
    overall_score_pct: number | null;
    exam_readiness_pct: number | null;
    current_streak_days: number;
    total_reviews_completed: number;
    last_review_at: string | null;
    strongest_subject: string | null;
    weakest_subject: string | null;
    highest_risk: RiskLevel;
    dropout_risk: RiskLevel;
    academic_risk: RiskLevel;
    fee_risk: RiskLevel;
};

type SubjectMastery = {
    subject: string;
    score: number;
    fullMark: number;
};

type ConceptSignal = {
    concept: string;
    mastery_score: number;
    confidence_score: number;
};

type FocusTopic = {
    topic: string;
    subject: string | null;
    mastery_score: number;
    confidence_score: number;
    review_due_at: string | null;
    last_evidence_type: string | null;
    last_evidence_score: number | null;
    updated_at: string | null;
    concepts: ConceptSignal[];
};

type MasteryInsights = {
    tracked_topics: number;
    low_mastery_topics: number;
    due_reviews: number;
    strongest_topic: string | null;
    weakest_topic: string | null;
};

type MasteryResponse = {
    summary: MasterySummary;
    subject_mastery: SubjectMastery[];
    focus_topics: FocusTopic[];
    insights: MasteryInsights;
    recommended_actions: string[];
};

function riskColor(level: RiskLevel) {
    if (level === "high") return "var(--error)";
    if (level === "medium") return "var(--warning)";
    return "var(--success)";
}

function riskLabel(level: RiskLevel) {
    if (level === "high") return "High risk";
    if (level === "medium") return "Needs attention";
    return "On track";
}

function scoreColor(score: number | null | undefined) {
    if (score == null) return "var(--text-secondary)";
    if (score >= 75) return "var(--success)";
    if (score >= 60) return "var(--warning)";
    return "var(--error)";
}

function formatEvidence(value: string | null) {
    if (!value) return "No recent evidence";
    return value.replace(/_/g, " ");
}

function formatShortDate(value: string | null) {
    if (!value) return "No review scheduled";
    const parsed = new Date(value);
    if (Number.isNaN(parsed.getTime())) return "Review timing unavailable";
    return parsed.toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function MetricCard({
    label,
    value,
    detail,
    icon,
    tone,
}: {
    label: string;
    value: ReactNode;
    detail: string;
    icon: ReactNode;
    tone: string;
}) {
    return (
        <PrismPanel className="p-4">
            <div className="mb-3 flex h-11 w-11 items-center justify-center rounded-2xl" style={{ background: tone }}>
                {icon}
            </div>
            <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">{label}</p>
            <div className="mt-2 text-2xl font-black text-[var(--text-primary)]">{value}</div>
            <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">{detail}</p>
        </PrismPanel>
    );
}

export default function PersonalMasteryMap() {
    const [payload, setPayload] = useState<MasteryResponse | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const load = async () => {
        try {
            setLoading(true);
            setError(null);
            const response = await api.student.mastery();
            setPayload((response || null) as MasteryResponse | null);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Failed to load mastery map");
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        void load();
    }, []);

    const summary = payload?.summary;
    const insights = payload?.insights;
    const subjectMastery = payload?.subject_mastery ?? [];
    const focusTopics = payload?.focus_topics ?? [];
    const recommendedActions = payload?.recommended_actions ?? [];
    const readinessScore = summary?.exam_readiness_pct ?? summary?.overall_score_pct ?? 0;

    return (
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    className="grid gap-4 xl:grid-cols-[1.15fr_0.85fr]"
                    kicker={(
                        <PrismHeroKicker>
                            <BrainCircuit className="h-3.5 w-3.5" />
                            Intelligence Layer
                        </PrismHeroKicker>
                    )}
                    title="See your real mastery signal down to the topic level"
                    description="Blend profile data with live topic mastery records so readiness, risk, and weak concepts stay visible without relying on placeholders or guesswork."
                    aside={(
                        <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-2">
                            <MetricCard
                                label="Readiness"
                                value={`${Math.round(readinessScore)}%`}
                                detail={summary?.exam_readiness_pct != null ? "Exam preparedness from the unified profile." : "Using current academic average until readiness is computed."}
                                icon={<Target className="h-5 w-5 text-status-blue" />}
                                tone="linear-gradient(135deg,rgba(96,165,250,0.18),rgba(129,140,248,0.08))"
                            />
                            <MetricCard
                                label="Academic health"
                                value={summary ? riskLabel(summary.academic_risk) : "--"}
                                detail={summary?.weakest_subject ? `${summary.weakest_subject} is currently the weakest subject.` : "Will update as more assessed performance arrives."}
                                icon={<GraduationCap className="h-5 w-5" style={{ color: riskColor(summary?.academic_risk ?? "low") }} />}
                                tone="linear-gradient(135deg,rgba(251,191,36,0.18),rgba(249,115,22,0.08))"
                            />
                            <MetricCard
                                label="Attendance"
                                value={`${Math.round(summary?.attendance_pct ?? 0)}%`}
                                detail={`${summary?.absent_streak ?? 0} consecutive absences in the current record.`}
                                icon={<Activity className="h-5 w-5" style={{ color: riskColor(summary?.dropout_risk ?? "low") }} />}
                                tone="linear-gradient(135deg,rgba(248,113,113,0.18),rgba(239,68,68,0.08))"
                            />
                            <MetricCard
                                label="Momentum"
                                value={summary ? `${summary.current_streak_days} days` : "--"}
                                detail={`${summary?.total_reviews_completed ?? 0} completed review cycles are already reflected here.`}
                                icon={<Flame className="h-5 w-5 text-status-emerald" />}
                                tone="linear-gradient(135deg,rgba(45,212,191,0.18),rgba(16,185,129,0.08))"
                            />
                        </div>
                    )}
                />

                {error ? (
                    <ErrorRemediation
                        error={error}
                        scope="student-mastery"
                        onRetry={() => {
                            void load();
                        }}
                    />
                ) : null}

                {loading ? (
                    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
                        {Array.from({ length: 4 }).map((_, idx) => (
                            <SkeletonCard key={idx} />
                        ))}
                    </div>
                ) : null}

                {!loading ? (
                    <div className="grid gap-6 xl:grid-cols-[1.02fr_0.98fr]">
                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                className="mb-4"
                                kicker="Overview"
                                title={(
                                    <span className="inline-flex items-center gap-2">
                                        <TrendingUp className="h-4 w-4 text-[var(--primary)]" />
                                        Subject Mastery Radar
                                    </span>
                                )}
                                description="Subject-level averages are derived from live topic mastery rows, with profile-level mastery used as fallback coverage."
                            />

                            {subjectMastery.length === 0 ? (
                                <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm leading-6 text-[var(--text-muted)]">
                                    No mastery evidence has been generated yet. Complete quizzes, reviews, or guided study sessions to start seeing subject-level signal here.
                                </div>
                            ) : (
                                <div className="grid gap-4 lg:grid-cols-[0.95fr_1.05fr]">
                                    <div className="h-[320px]">
                                        <ResponsiveContainer width="100%" height="100%">
                                            <RadarChart cx="50%" cy="50%" outerRadius="72%" data={subjectMastery}>
                                                <PolarGrid stroke="var(--border)" />
                                                <PolarAngleAxis dataKey="subject" tick={{ fill: "var(--text-secondary)", fontSize: 12 }} />
                                                <PolarRadiusAxis angle={24} domain={[0, 100]} tick={{ fill: "var(--text-muted)", fontSize: 10 }} />
                                                <Radar
                                                    name="Mastery"
                                                    dataKey="score"
                                                    stroke="var(--primary)"
                                                    fill="var(--primary)"
                                                    fillOpacity={0.28}
                                                />
                                                <Tooltip
                                                    contentStyle={{
                                                        backgroundColor: "var(--bg-card)",
                                                        borderColor: "var(--border)",
                                                        borderRadius: "12px",
                                                    }}
                                                    itemStyle={{ color: "var(--text-primary)" }}
                                                />
                                            </RadarChart>
                                        </ResponsiveContainer>
                                    </div>
                                    <div className="grid gap-3 content-start">
                                        {subjectMastery.map((item) => (
                                            <div
                                                key={item.subject}
                                                className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4"
                                            >
                                                <div className="flex items-center justify-between gap-3">
                                                    <span className="text-sm font-semibold text-[var(--text-primary)]">{item.subject}</span>
                                                    <span className="text-sm font-bold" style={{ color: scoreColor(item.score) }}>
                                                        {Math.round(item.score)}%
                                                    </span>
                                                </div>
                                                <div className="mt-3 h-2 rounded-full bg-[rgba(255,255,255,0.05)]">
                                                    <div
                                                        className="h-2 rounded-full transition-all"
                                                        style={{ width: `${Math.max(4, Math.min(100, item.score))}%`, backgroundColor: scoreColor(item.score) }}
                                                    />
                                                </div>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </PrismPanel>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader
                                className="mb-4"
                                kicker="Actions"
                                title={(
                                    <span className="inline-flex items-center gap-2">
                                        <ShieldAlert className="h-4 w-4 text-[var(--primary)]" />
                                        Priority Signals
                                    </span>
                                )}
                                description="This section converts profile risk, review pressure, and weak-topic evidence into the next actions that matter."
                            />

                            <div className="grid gap-3 sm:grid-cols-2">
                                <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4">
                                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Tracked topics</p>
                                    <p className="mt-2 text-3xl font-black text-[var(--text-primary)]">{insights?.tracked_topics ?? 0}</p>
                                    <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Core topic mastery rows currently contributing to this map.</p>
                                </div>
                                <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4">
                                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Due reviews</p>
                                    <p className="mt-2 text-3xl font-black text-[var(--text-primary)]">{insights?.due_reviews ?? 0}</p>
                                    <p className="mt-1 text-sm leading-6 text-[var(--text-secondary)]">Topics whose review date has already arrived.</p>
                                </div>
                            </div>

                            <div className="mt-4 grid gap-3 sm:grid-cols-3">
                                {summary ? (
                                    <>
                                        <div className="rounded-[1.25rem] border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3">
                                            <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-muted)]">Dropout risk</p>
                                            <p className="mt-2 text-sm font-semibold" style={{ color: riskColor(summary.dropout_risk) }}>{riskLabel(summary.dropout_risk)}</p>
                                        </div>
                                        <div className="rounded-[1.25rem] border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3">
                                            <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-muted)]">Academic risk</p>
                                            <p className="mt-2 text-sm font-semibold" style={{ color: riskColor(summary.academic_risk) }}>{riskLabel(summary.academic_risk)}</p>
                                        </div>
                                        <div className="rounded-[1.25rem] border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-3">
                                            <p className="text-[11px] uppercase tracking-[0.2em] text-[var(--text-muted)]">Fee risk</p>
                                            <p className="mt-2 text-sm font-semibold" style={{ color: riskColor(summary.fee_risk) }}>{riskLabel(summary.fee_risk)}</p>
                                        </div>
                                    </>
                                ) : null}
                            </div>

                            <div className="mt-4 rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Recommended focus</p>
                                {recommendedActions.length === 0 ? (
                                    <p className="mt-3 text-sm leading-6 text-[var(--text-secondary)]">
                                        No urgent low-mastery topics yet. Keep building evidence through quizzes and reviews.
                                    </p>
                                ) : (
                                    <div className="mt-3 flex flex-wrap gap-2">
                                        {recommendedActions.map((topic) => (
                                            <span key={topic} className="prism-chip">
                                                {topic}
                                            </span>
                                        ))}
                                    </div>
                                )}
                                <div className="mt-4 grid gap-2 text-sm text-[var(--text-secondary)]">
                                    <p>Strongest current signal: <span className="font-semibold text-[var(--text-primary)]">{insights?.strongest_topic || summary?.strongest_subject || "--"}</span></p>
                                    <p>Most urgent recovery zone: <span className="font-semibold text-[var(--text-primary)]">{insights?.weakest_topic || summary?.weakest_subject || "--"}</span></p>
                                    <p>Latest review event: <span className="font-semibold text-[var(--text-primary)]">{summary?.last_review_at ? formatShortDate(summary.last_review_at) : "No review history yet"}</span></p>
                                </div>
                            </div>
                        </PrismPanel>
                    </div>
                ) : null}

                {!loading ? (
                    <PrismPanel className="p-5">
                        <PrismSectionHeader
                            className="mb-4"
                            kicker="Detail"
                            title={(
                                <span className="inline-flex items-center gap-2">
                                    <BrainCircuit className="h-4 w-4 text-[var(--primary)]" />
                                    Sub-topic Focus Matrix
                                </span>
                            )}
                            description="Each card below is backed by a live topic mastery row and its concept-level evidence, so you can see exactly where understanding is forming or collapsing."
                        />

                        {focusTopics.length === 0 ? (
                            <div className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-8 text-sm leading-6 text-[var(--text-muted)]">
                                No topic-level mastery rows exist yet. Use AI Studio, complete reviews, or submit quiz results to generate the first concept signal.
                            </div>
                        ) : (
                            <div className="grid gap-4 xl:grid-cols-2">
                                {focusTopics.map((topic) => (
                                    <div
                                        key={topic.topic}
                                        className="rounded-[1.5rem] border border-[var(--border)] bg-[rgba(148,163,184,0.04)] p-4"
                                    >
                                        <div className="flex flex-wrap items-start justify-between gap-3">
                                            <div>
                                                <h3 className="text-base font-semibold text-[var(--text-primary)]">{topic.topic}</h3>
                                                <p className="mt-1 text-sm text-[var(--text-secondary)]">{topic.subject || "General learning signal"}</p>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-xs uppercase tracking-[0.18em] text-[var(--text-muted)]">Mastery</p>
                                                <p className="mt-1 text-xl font-black" style={{ color: scoreColor(topic.mastery_score) }}>
                                                    {Math.round(topic.mastery_score)}%
                                                </p>
                                            </div>
                                        </div>

                                        <div className="mt-4 flex flex-wrap gap-2">
                                            <span className="prism-chip">Confidence {Math.round(topic.confidence_score * 100)}%</span>
                                            <span className="prism-chip">{formatEvidence(topic.last_evidence_type)}</span>
                                            <span className="prism-chip">{formatShortDate(topic.review_due_at)}</span>
                                        </div>

                                        <div className="mt-4 h-2 rounded-full bg-[rgba(255,255,255,0.05)]">
                                            <div
                                                className="h-2 rounded-full transition-all"
                                                style={{
                                                    width: `${Math.max(4, Math.min(100, topic.mastery_score))}%`,
                                                    backgroundColor: scoreColor(topic.mastery_score),
                                                }}
                                            />
                                        </div>

                                        <div className="mt-4 space-y-3">
                                            {topic.concepts.length === 0 ? (
                                                <p className="text-sm leading-6 text-[var(--text-secondary)]">
                                                    No extracted concepts yet. The core topic score is already being tracked.
                                                </p>
                                            ) : (
                                                topic.concepts.map((concept) => (
                                                    <div key={`${topic.topic}-${concept.concept}`}>
                                                        <div className="mb-1 flex items-center justify-between gap-3">
                                                            <span className="text-xs font-medium uppercase tracking-[0.16em] text-[var(--text-muted)]">
                                                                {concept.concept}
                                                            </span>
                                                            <span className="text-xs font-semibold" style={{ color: scoreColor(concept.mastery_score) }}>
                                                                {Math.round(concept.mastery_score)}%
                                                            </span>
                                                        </div>
                                                        <div className="h-2 rounded-full bg-[rgba(255,255,255,0.05)]">
                                                            <div
                                                                className="h-2 rounded-full transition-all"
                                                                style={{
                                                                    width: `${Math.max(4, Math.min(100, concept.mastery_score))}%`,
                                                                    backgroundColor: scoreColor(concept.mastery_score),
                                                                }}
                                                            />
                                                        </div>
                                                        <p className="mt-1 text-[11px] leading-5 text-[var(--text-muted)]">
                                                            Confidence {Math.round(concept.confidence_score * 100)}%
                                                        </p>
                                                    </div>
                                                ))
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        )}
                    </PrismPanel>
                ) : null}
            </PrismSection>
        </PrismPage>
    );
}
