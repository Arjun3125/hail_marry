"use client";

import { useEffect, useMemo, useState } from "react";
import {
    BookOpen,
    CheckCircle2,
    ExternalLink,
    Globe,
    Loader2,
    Plus,
    Search,
} from "lucide-react";

import EmptyState from "@/components/EmptyState";
import { PrismHeroKicker, PrismPage, PrismPageIntro, PrismPanel, PrismSection } from "@/components/prism/PrismPage";
import { useNetworkAware } from "@/hooks/useNetworkAware";
import ErrorRemediation from "@/components/ui/ErrorRemediation";
import { api } from "@/lib/api";

type SearchResult = {
    title: string;
    url: string;
    snippet: string;
};

type ResourceHistoryItem = {
    id: string;
    name: string;
    type: "document" | "youtube";
    status: "processing" | "completed" | "failed";
    detail?: string;
    created_at?: string | null;
};

type AIJobStatus = "queued" | "running" | "completed" | "failed";

export default function DiscoverSourcesPage() {
    const { isSlowConnection, saveData } = useNetworkAware();
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<SearchResult[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [ingesting, setIngesting] = useState<Record<number, boolean>>({});
    const [ingested, setIngested] = useState<Record<number, { chunks: number }>>({});
    const [historyItems, setHistoryItems] = useState<ResourceHistoryItem[]>([]);
    const [historyIndexedChunks, setHistoryIndexedChunks] = useState(0);

    const summary = useMemo(() => {
        const activeIngestions = Object.values(ingesting).filter(Boolean).length;
        const completedIngestions = Object.keys(ingested).length;
        const indexedChunks = Object.values(ingested).reduce((sum, item) => sum + item.chunks, 0);

        return {
            activeIngestions,
            completedIngestions,
            indexedChunks,
        };
    }, [ingested, ingesting]);
    const fallbackPollMs = saveData ? 6000 : isSlowConnection ? 4000 : 2000;

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const payload = await api.teacher.resourceHistory() as {
                    summary?: { indexed_chunks?: number };
                    recent_activity?: ResourceHistoryItem[];
                };
                setHistoryItems((payload.recent_activity || []).filter((item) => item.type === "youtube" || item.type === "document").slice(0, 6));
                setHistoryIndexedChunks(payload.summary?.indexed_chunks || 0);
            } catch {
                // Discovery history is additive only.
            }
        };

        void loadHistory();
    }, []);

    const resetSearchState = () => {
        setResults([]);
        setIngested({});
        setIngesting({});
    };

    const search = async () => {
        if (!query.trim() || loading) return;

        setLoading(true);
        setError(null);
        resetSearchState();

        try {
            const data = (await api.ai.discoverSources({ query: query.trim() })) as { results?: SearchResult[] };
            setResults(data.results || []);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Cannot connect to backend");
        } finally {
            setLoading(false);
        }
    };

    const pollIngestJob = async (idx: number, jobId: string) => {
        try {
            const job = (await api.ai.jobStatus(jobId)) as {
                status: AIJobStatus;
                error?: string;
                result?: { chunks_created?: number };
                poll_after_ms?: number;
            };

            if (job.status === "completed") {
                setIngested((prev) => ({ ...prev, [idx]: { chunks: job.result?.chunks_created || 0 } }));
                setIngesting((prev) => ({ ...prev, [idx]: false }));
                return;
            }

            if (job.status === "failed") {
                setError(job.error || "Failed to ingest source");
                setIngesting((prev) => ({ ...prev, [idx]: false }));
                return;
            }

            window.setTimeout(() => {
                void pollIngestJob(idx, jobId);
            }, job.poll_after_ms ?? fallbackPollMs);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ingestion failed");
            setIngesting((prev) => ({ ...prev, [idx]: false }));
        }
    };

    const ingestSource = async (idx: number, result: SearchResult) => {
        setError(null);
        setIngesting((prev) => ({ ...prev, [idx]: true }));

        try {
            const job = (await api.ai.ingestUrl({ url: result.url, title: result.title })) as {
                job_id: string;
                status: AIJobStatus;
            };

            if (job.status === "failed") {
                setError("Failed to ingest source");
                setIngesting((prev) => ({ ...prev, [idx]: false }));
                return;
            }

            void pollIngestJob(idx, job.job_id);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Ingestion failed");
            setIngesting((prev) => ({ ...prev, [idx]: false }));
        }
    };

    return (
        <PrismPage variant="workspace" className="space-y-6 pb-8">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={(
                        <PrismHeroKicker>
                            <Globe className="h-3.5 w-3.5" />
                            Teacher Discovery Surface
                        </PrismHeroKicker>
                    )}
                    title="Find relevant external sources before you add them to class knowledge"
                    description="Search for instructional resources, review relevance before ingestion, and add only the best material into the shared learning base."
                    aside={(
                        <div className="prism-briefing-panel">
                            <p className="prism-status-label">Best use</p>
                            <p className="mt-2 text-sm leading-6 text-[var(--text-secondary)]">
                                Keep queries narrow and curriculum-specific so the results are easier to vet before they become searchable class knowledge.
                            </p>
                        </div>
                    )}
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Results in view</span>
                        <span className="prism-status-value">{results.length}</span>
                        <span className="prism-status-detail">Current candidates returned by the active discovery query.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Sources indexed</span>
                        <span className="prism-status-value">{summary.completedIngestions || historyItems.length}</span>
                        <span className="prism-status-detail">Results already added into the knowledge base for this teacher workspace.</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Indexed chunks</span>
                        <span className="prism-status-value">{summary.completedIngestions ? summary.indexedChunks : historyIndexedChunks}</span>
                        <span className="prism-status-detail">
                            {summary.activeIngestions ? `${summary.activeIngestions} ingestion job running.` : "Ready to ingest selected sources."}
                        </span>
                    </div>
                </div>

                <PrismPanel className="overflow-hidden p-0">
                    <div className="border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                        <div className="flex flex-wrap items-center justify-between gap-3">
                            <div>
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Discovery workspace</p>
                                <p className="mt-1 text-sm text-[var(--text-secondary)]">
                                    Start with a topic query, review the web results, then selectively ingest the best sources.
                                </p>
                            </div>
                            <button
                                onClick={() => void search()}
                                disabled={loading || !query.trim()}
                                className="inline-flex items-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.96),rgba(249,115,22,0.94))] px-4 py-2.5 text-sm font-semibold text-[#261204] shadow-[0_18px_34px_rgba(249,115,22,0.2)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                            >
                                {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
                                Search Sources
                            </button>
                        </div>
                    </div>

                    <div className="grid gap-6 p-5 xl:grid-cols-[1.15fr_0.85fr]">
                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <div className="mb-4">
                                    <p className="text-sm font-semibold text-[var(--text-primary)]">Search brief</p>
                                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                        Use a tight teaching query so the results stay relevant and easier to vet before ingestion.
                                    </p>
                                </div>

                                <div className="flex flex-col gap-3 md:flex-row">
                                    <input
                                        value={query}
                                        onChange={(e) => setQuery(e.target.value)}
                                        onKeyDown={(e) => {
                                            if (e.key === "Enter") void search();
                                        }}
                                        placeholder="e.g. NCERT Class 10 Photosynthesis, algebra practice set, lab guide..."
                                        className="flex-1 rounded-2xl border border-[var(--border)] bg-[rgba(8,15,30,0.72)] px-4 py-3 text-sm text-[var(--text-primary)] outline-none transition focus:border-[var(--primary)]/50"
                                    />
                                    <button
                                        onClick={() => void search()}
                                        disabled={loading || !query.trim()}
                                        className="inline-flex items-center justify-center gap-2 rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm font-semibold text-[var(--text-primary)] transition hover:border-[rgba(251,191,36,0.3)] hover:bg-[rgba(251,191,36,0.08)] disabled:cursor-not-allowed disabled:opacity-60"
                                    >
                                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Globe className="h-4 w-4" />}
                                        Run Query
                                    </button>
                                </div>
                            </PrismPanel>

                            {error ? (
                                <ErrorRemediation
                                    error={error}
                                    scope="teacher-discover"
                                    onRetry={() => {
                                        if (query.trim()) void search();
                                    }}
                                />
                            ) : null}

                            {loading ? (
                                <PrismPanel className="p-8">
                                    <div className="flex flex-col items-center justify-center text-center">
                                        <div className="mb-4 flex h-14 w-14 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.96),rgba(249,115,22,0.94))]">
                                            <Search className="h-6 w-6 animate-pulse text-[#261204]" />
                                        </div>
                                        <p className="text-sm font-semibold text-[var(--text-primary)]">Searching the web...</p>
                                        <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                            Finding educational resources from the current discovery query.
                                        </p>
                                    </div>
                                </PrismPanel>
                            ) : results.length > 0 ? (
                                <PrismPanel className="overflow-hidden p-0">
                                    <div className="flex flex-wrap items-center justify-between gap-3 border-b border-[var(--border)]/80 bg-[rgba(255,255,255,0.02)] px-5 py-4">
                                        <div>
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">Discovery board</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                Review each candidate source, then ingest the ones worth turning into searchable knowledge.
                                            </p>
                                        </div>
                                        <div className="inline-flex items-center gap-2 rounded-full border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-3 py-1.5 text-xs text-[var(--text-secondary)]">
                                            <Search className="h-3.5 w-3.5" />
                                            {results.length} results returned
                                        </div>
                                    </div>

                                    <div className="space-y-3 p-5">
                                        {results.map((result, index) => {
                                            const isIngesting = Boolean(ingesting[index]);
                                            const ingestStatus = ingested[index];

                                            return (
                                                <div
                                                    key={`${result.url}-${index}`}
                                                    className="rounded-[28px] border border-[var(--border)] bg-[rgba(8,15,30,0.58)] p-5 shadow-[0_18px_40px_rgba(2,6,23,0.16)]"
                                                >
                                                    <div className="flex flex-col gap-4 xl:flex-row xl:items-start">
                                                        <div className="flex flex-1 items-start gap-3">
                                                            <div className="mt-0.5 flex h-11 w-11 items-center justify-center rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.18),rgba(249,115,22,0.12))] text-status-amber">
                                                                <BookOpen className="h-5 w-5" />
                                                            </div>
                                                            <div className="min-w-0 flex-1">
                                                                <h2 className="text-base font-semibold text-[var(--text-primary)]">{result.title}</h2>
                                                                <p className="mt-2 text-sm leading-7 text-[var(--text-secondary)]">{result.snippet}</p>
                                                                <a
                                                                    href={result.url}
                                                                    target="_blank"
                                                                    rel="noopener noreferrer"
                                                                    className="mt-3 inline-flex max-w-full items-center gap-2 text-xs font-medium text-status-blue transition hover:text-[var(--text-primary)]"
                                                                >
                                                                    <ExternalLink className="h-3.5 w-3.5 flex-shrink-0" />
                                                                    <span className="truncate">{result.url}</span>
                                                                </a>
                                                            </div>
                                                        </div>

                                                        <div className="xl:w-[220px]">
                                                            {ingestStatus ? (
                                                                <div className="rounded-2xl border border-[rgba(16,185,129,0.22)] bg-[rgba(16,185,129,0.12)] px-4 py-3 text-sm text-status-emerald">
                                                                    <div className="flex items-center gap-2 font-semibold">
                                                                        <CheckCircle2 className="h-4 w-4" />
                                                                        Source indexed
                                                                    </div>
                                                                    <p className="mt-1 text-xs text-[var(--text-secondary)]">
                                                                        {ingestStatus.chunks} chunks added to the knowledge base.
                                                                    </p>
                                                                </div>
                                                            ) : (
                                                                <button
                                                                    onClick={() => void ingestSource(index, result)}
                                                                    disabled={isIngesting}
                                                                    className="inline-flex w-full items-center justify-center gap-2 rounded-2xl bg-[linear-gradient(135deg,rgba(251,191,36,0.96),rgba(249,115,22,0.94))] px-4 py-3 text-sm font-semibold text-[#261204] shadow-[0_18px_34px_rgba(249,115,22,0.2)] transition-all hover:-translate-y-0.5 disabled:cursor-not-allowed disabled:opacity-60"
                                                                >
                                                                    {isIngesting ? <Loader2 className="h-4 w-4 animate-spin" /> : <Plus className="h-4 w-4" />}
                                                                    {isIngesting ? "Ingesting..." : "Add To Knowledge Base"}
                                                                </button>
                                                            )}
                                                        </div>
                                                    </div>
                                                </div>
                                            );
                                        })}
                                    </div>
                                </PrismPanel>
                            ) : query.trim() ? (
                                <EmptyState
                                    icon={Globe}
                                    title="No discovery matches yet"
                                    description="Try a tighter subject, chapter, or curriculum phrase to improve the result set."
                                    eyebrow="No source matches"
                                    scopeNote="Discovery works best when the query names the board, class, chapter, or concept you actually teach."
                                />
                            ) : (
                                <EmptyState
                                    icon={Search}
                                    title="No search started yet"
                                    description="Enter a teaching query to discover external learning resources worth ingesting."
                                    eyebrow="Awaiting discovery query"
                                    scopeNote="Start with one concept or chapter at a time so the search results stay instructional instead of generic."
                                />
                            )}
                        </div>

                        <div className="space-y-4">
                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Discovery summary</p>
                                <div className="mt-4 space-y-4">
                                    <SummaryRow label="Query" value={query.trim() || "No active search"} />
                                    <SummaryRow label="Results returned" value={`${results.length}`} />
                                    <SummaryRow label="Sources indexed" value={`${summary.completedIngestions || historyItems.length}`} />
                                    <SummaryRow label="Indexed chunks" value={`${summary.completedIngestions ? summary.indexedChunks : historyIndexedChunks}`} />
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Recent curated sources</p>
                                <div className="mt-4 space-y-3">
                                    {historyItems.length > 0 ? historyItems.map((item) => (
                                        <div key={item.id} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3">
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">{item.name}</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">{item.type} • {item.created_at ? new Date(item.created_at).toLocaleDateString() : "Saved source"}</p>
                                        </div>
                                    )) : <p className="text-sm text-[var(--text-secondary)]">No discovery history has been saved yet.</p>}
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Workflow notes</p>
                                <div className="mt-4 space-y-3 text-sm leading-6 text-[var(--text-secondary)]">
                                    <p>This screen is for discovery and ingestion only. It preserves the existing backend contract while framing the work as a teacher-facing resource pipeline.</p>
                                    <p>Search results remain reviewable before ingestion, and indexing feedback stays visible in the same workspace instead of being hidden behind a background action.</p>
                                </div>
                            </PrismPanel>

                            <PrismPanel className="p-5">
                                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-[var(--text-muted)]">Good query shape</p>
                                <div className="mt-4 space-y-3">
                                    <GuideRow label="Curriculum-first" description="Lead with board, class, chapter, or subject so result quality stays instructional." />
                                    <GuideRow label="One concept at a time" description="Smaller topical queries are easier to vet and produce cleaner source ingestion." />
                                    <GuideRow label="Review before add" description="Use the title and snippet to judge whether the source belongs in the shared knowledge base." />
                                </div>
                            </PrismPanel>
                        </div>
                    </div>
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}

function SummaryRow({ label, value }: { label: string; value: string }) {
    return (
        <div className="flex items-center justify-between gap-3 rounded-2xl border border-[var(--border)] bg-[rgba(148,163,184,0.05)] px-4 py-3">
            <span className="text-xs font-semibold uppercase tracking-[0.16em] text-[var(--text-muted)]">{label}</span>
            <span className="max-w-[58%] truncate text-right text-sm font-medium text-[var(--text-primary)]">{value}</span>
        </div>
    );
}

function GuideRow({ label, description }: { label: string; description: string }) {
    return (
        <div className="flex items-start gap-3">
            <div className="mt-0.5 flex h-9 w-9 items-center justify-center rounded-xl bg-[linear-gradient(135deg,rgba(251,191,36,0.18),rgba(249,115,22,0.12))] text-status-amber">
                <Search className="h-4 w-4" />
            </div>
            <div>
                <p className="text-sm font-semibold text-[var(--text-primary)]">{label}</p>
                <p className="text-xs leading-5 text-[var(--text-muted)]">{description}</p>
            </div>
        </div>
    );
}
