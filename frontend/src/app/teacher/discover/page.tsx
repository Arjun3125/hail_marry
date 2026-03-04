"use client";

import { useState } from "react";
import { Search, Globe, Plus, Loader2, CheckCircle, ExternalLink, BookOpen } from "lucide-react";
import { API_BASE } from "@/lib/api";

type SearchResult = { title: string; url: string; snippet: string };

export default function DiscoverSourcesPage() {
    const [query, setQuery] = useState("");
    const [loading, setLoading] = useState(false);
    const [results, setResults] = useState<SearchResult[]>([]);
    const [error, setError] = useState<string | null>(null);
    const [ingesting, setIngesting] = useState<Record<number, boolean>>({});
    const [ingested, setIngested] = useState<Record<number, { chunks: number }>>({});

    const search = async () => {
        if (!query.trim() || loading) return;
        setLoading(true);
        setError(null);
        setResults([]);
        setIngested({});
        try {
            const res = await fetch(`${API_BASE}/api/ai/discover-sources`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ query: query.trim() }),
            });
            if (res.ok) {
                const data = await res.json();
                setResults(data.results || []);
            } else {
                const err = await res.json().catch(() => ({ detail: "Search failed" }));
                setError(err.detail || "Failed to search");
            }
        } catch {
            setError("Cannot connect to backend");
        } finally {
            setLoading(false);
        }
    };

    const ingestSource = async (idx: number, result: SearchResult) => {
        setIngesting((prev) => ({ ...prev, [idx]: true }));
        try {
            const res = await fetch(`${API_BASE}/api/ai/ingest-url`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                credentials: "include",
                body: JSON.stringify({ url: result.url, title: result.title }),
            });
            if (res.ok) {
                const data = await res.json();
                setIngested((prev) => ({ ...prev, [idx]: { chunks: data.chunks_created } }));
            } else {
                setError("Failed to ingest source");
            }
        } catch {
            setError("Ingestion failed");
        } finally {
            setIngesting((prev) => ({ ...prev, [idx]: false }));
        }
    };

    return (
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="mb-5">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 shadow-lg">
                        <Globe className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Source Discovery</h1>
                        <p className="text-xs text-[var(--text-muted)]">Search the web and add educational resources to your knowledge base</p>
                    </div>
                </div>
            </div>

            {/* Search */}
            <div className="bg-white rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 mb-5">
                <div className="flex gap-2">
                    <input
                        value={query}
                        onChange={(e) => setQuery(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") void search(); }}
                        placeholder="Search for educational resources — e.g. NCERT Class 10 Photosynthesis..."
                        className="flex-1 px-4 py-3 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-amber-500/50"
                    />
                    <button
                        onClick={() => void search()}
                        disabled={loading || !query.trim()}
                        className="px-5 py-3 bg-gradient-to-r from-amber-500 to-orange-600 text-white text-sm font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-40 flex items-center gap-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Search className="w-4 h-4" />}
                        Search
                    </button>
                </div>
            </div>

            {error && <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">{error}</div>}

            {loading && (
                <div className="bg-white rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center animate-pulse">
                        <Search className="w-7 h-7 text-white" />
                    </div>
                    <p className="text-sm font-medium">Searching the web...</p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">Finding educational resources from trusted sources</p>
                </div>
            )}

            {/* Results */}
            {!loading && results.length > 0 && (
                <div className="space-y-3">
                    <p className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-wider">{results.length} results found</p>
                    {results.map((r, i) => (
                        <div key={i} className="bg-white rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 group hover:shadow-md transition-all">
                            <div className="flex items-start gap-3">
                                <div className="p-2 rounded-lg bg-gradient-to-br from-amber-50 to-orange-50 mt-0.5">
                                    <BookOpen className="w-4 h-4 text-amber-600" />
                                </div>
                                <div className="flex-1 min-w-0">
                                    <h3 className="text-sm font-bold text-[var(--text-primary)] mb-1 line-clamp-1">{r.title}</h3>
                                    <p className="text-xs text-[var(--text-muted)] mb-2 line-clamp-2">{r.snippet}</p>
                                    <a href={r.url} target="_blank" rel="noopener noreferrer" className="text-[10px] text-blue-500 hover:underline truncate block max-w-md">
                                        <ExternalLink className="w-3 h-3 inline mr-1" />{r.url}
                                    </a>
                                </div>
                                <div className="flex-shrink-0">
                                    {ingested[i] ? (
                                        <div className="flex items-center gap-1.5 px-3 py-2 bg-emerald-50 text-emerald-700 rounded-xl text-xs font-medium">
                                            <CheckCircle className="w-4 h-4" /> {ingested[i].chunks} chunks
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => void ingestSource(i, r)}
                                            disabled={ingesting[i]}
                                            className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-amber-500 to-orange-600 text-white text-xs font-bold rounded-xl hover:shadow-md transition-all disabled:opacity-50"
                                        >
                                            {ingesting[i] ? <Loader2 className="w-3 h-3 animate-spin" /> : <Plus className="w-3 h-3" />}
                                            Add
                                        </button>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {!loading && results.length === 0 && query && (
                <div className="bg-white rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-gradient-to-br from-amber-500 to-orange-600 flex items-center justify-center opacity-40">
                        <Globe className="w-8 h-8 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-[var(--text-primary)] mb-2">No results yet</h3>
                    <p className="text-sm text-[var(--text-muted)]">Try a different search query</p>
                </div>
            )}
        </div>
    );
}
