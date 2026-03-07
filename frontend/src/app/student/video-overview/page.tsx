"use client";

import { useEffect, useState } from "react";
import { Presentation, ChevronLeft, ChevronRight, PlayCircle, PauseCircle, Loader2, Volume2 } from "lucide-react";
import { api } from "@/lib/api";

type Slide = { title: string; bullets: string[]; narration: string };
type VideoData = { slides: Slide[]; presentation_title: string; total_slides: number };
type AIJobStatus = "queued" | "running" | "completed" | "failed";

export default function VideoOverviewPage() {
    const [topic, setTopic] = useState("");
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<VideoData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [current, setCurrent] = useState(0);
    const [autoPlaying, setAutoPlaying] = useState(false);
    const [speakingSlide, setSpeakingSlide] = useState(-1);
    const [jobId, setJobId] = useState<string | null>(null);
    const [jobStatus, setJobStatus] = useState<AIJobStatus | null>(null);

    useEffect(() => {
        if (!jobId) return;

        let cancelled = false;
        let timer: ReturnType<typeof setTimeout> | null = null;

        const poll = async () => {
            try {
                const job = await api.ai.jobStatus(jobId) as {
                    status: AIJobStatus;
                    error?: string;
                    result?: VideoData;
                    poll_after_ms?: number;
                };

                if (cancelled) return;
                setJobStatus(job.status);

                if (job.status === "completed" && job.result) {
                    setData(job.result);
                    setCurrent(0);
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                if (job.status === "failed") {
                    setError(job.error || "Failed to generate video overview");
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                timer = setTimeout(() => {
                    void poll();
                }, job.poll_after_ms ?? 2000);
            } catch (err) {
                if (cancelled) return;
                setError(err instanceof Error ? err.message : "Failed to load job status");
                setLoading(false);
                setJobId(null);
            }
        };

        void poll();

        return () => {
            cancelled = true;
            if (timer) clearTimeout(timer);
        };
    }, [jobId]);

    const generate = async () => {
        if (!topic.trim() || loading) return;
        setLoading(true);
        setError(null);
        setData(null);
        setJobStatus("queued");
        try {
            const job = await api.ai.enqueueVideoOverviewJob({
                topic: topic.trim(),
                num_slides: 6,
            }) as { job_id: string; status: AIJobStatus };
            setJobId(job.job_id);
            setJobStatus(job.status);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Cannot connect to backend");
            setLoading(false);
        }
    };

    const speakSlide = (idx: number) => {
        if (!data || idx >= data.slides.length) return;
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(data.slides[idx].narration);
        utt.rate = 0.95;
        setSpeakingSlide(idx);
        utt.onend = () => setSpeakingSlide(-1);
        utt.onerror = () => setSpeakingSlide(-1);
        window.speechSynthesis.speak(utt);
    };

    const autoPlay = () => {
        if (!data || autoPlaying) return;
        window.speechSynthesis.cancel();
        setAutoPlaying(true);
        setCurrent(0);

        let i = 0;
        const playNext = () => {
            if (i >= data.slides.length) {
                setAutoPlaying(false);
                setSpeakingSlide(-1);
                return;
            }
            setCurrent(i);
            setSpeakingSlide(i);
            const utt = new SpeechSynthesisUtterance(data.slides[i].narration);
            utt.rate = 0.93;
            utt.onend = () => { i++; setTimeout(playNext, 500); };
            utt.onerror = () => { i++; setTimeout(playNext, 500); };
            window.speechSynthesis.speak(utt);
        };
        playNext();
    };

    const stopAutoPlay = () => {
        window.speechSynthesis.cancel();
        setAutoPlaying(false);
        setSpeakingSlide(-1);
    };

    const colors = [
        "from-blue-600 to-indigo-700",
        "from-emerald-600 to-teal-700",
        "from-violet-600 to-purple-700",
        "from-amber-600 to-orange-700",
        "from-rose-600 to-pink-700",
        "from-cyan-600 to-blue-700",
        "from-fuchsia-600 to-purple-700",
        "from-lime-600 to-green-700",
        "from-red-600 to-rose-700",
        "from-sky-600 to-indigo-700",
        "from-teal-600 to-emerald-700",
        "from-orange-600 to-red-700",
    ];

    return (
        <div className="max-w-4xl mx-auto">
            {/* Header */}
            <div className="mb-5">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 shadow-lg">
                        <Presentation className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Video Overview</h1>
                        <p className="text-xs text-[var(--text-muted)]">AI-narrated slide presentation from your notes</p>
                    </div>
                </div>
            </div>

            {/* Input */}
            {!data && (
                <div className="bg-white rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 mb-5">
                    <input
                        value={topic}
                        onChange={(e) => setTopic(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") void generate(); }}
                        placeholder="Enter a topic — e.g. Water Cycle, Indian Independence..."
                        className="w-full px-4 py-3 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-cyan-500/50 mb-3"
                    />
                    <button
                        onClick={() => void generate()}
                        disabled={loading || !topic.trim()}
                        className="w-full px-5 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-sm font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-40 flex items-center justify-center gap-2"
                    >
                        {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Presentation className="w-4 h-4" />}
                        Generate Presentation
                    </button>
                </div>
            )}

            {error && <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">{error}</div>}

            {loading && (
                <div className="bg-white rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center animate-pulse">
                        <Presentation className="w-7 h-7 text-white" />
                    </div>
                    <p className="text-sm font-medium">
                        {jobStatus === "queued" ? "Queued for presentation generation..." : "Generating slides..."}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">
                        {jobStatus === "queued"
                            ? "Waiting for the AI worker to start this job"
                            : "Creating narrated presentation from your materials"}
                    </p>
                </div>
            )}

            {/* Presentation Viewer */}
            {!loading && data && data.slides.length > 0 && (
                <div className="space-y-4">
                    {/* Controls */}
                    <div className="flex items-center justify-between bg-white rounded-2xl p-3 shadow-[var(--shadow-card)] border border-[var(--border)]/50">
                        <h2 className="text-sm font-bold text-[var(--text-primary)] truncate px-2">{data.presentation_title}</h2>
                        <div className="flex items-center gap-2">
                            {!autoPlaying ? (
                                <button onClick={autoPlay} className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-600 text-white text-xs font-bold rounded-xl hover:shadow-md transition-all">
                                    <PlayCircle className="w-4 h-4" /> Auto-Play
                                </button>
                            ) : (
                                <button onClick={stopAutoPlay} className="flex items-center gap-1.5 px-4 py-2 bg-gradient-to-r from-red-500 to-rose-600 text-white text-xs font-bold rounded-xl hover:shadow-md transition-all">
                                    <PauseCircle className="w-4 h-4" /> Stop
                                </button>
                            )}
                            <button onClick={() => { setData(null); setTopic(""); }} className="px-3 py-2 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)] transition-all">New</button>
                        </div>
                    </div>

                    {/* Slide Card */}
                    <div className={`bg-gradient-to-br ${colors[current % colors.length]} rounded-2xl p-8 text-white shadow-xl min-h-[350px] flex flex-col justify-between transition-all duration-500`}>
                        <div>
                            <p className="text-[10px] uppercase tracking-widest opacity-60 mb-2">Slide {current + 1} of {data.slides.length}</p>
                            <h3 className="text-2xl font-extrabold mb-6 leading-tight">{data.slides[current].title}</h3>
                            <ul className="space-y-3">
                                {data.slides[current].bullets.map((b, j) => (
                                    <li key={j} className="flex items-start gap-3">
                                        <span className="w-2 h-2 rounded-full bg-white/60 mt-1.5 flex-shrink-0" />
                                        <span className="text-sm opacity-95 leading-relaxed">{b}</span>
                                    </li>
                                ))}
                            </ul>
                        </div>
                        <div className="flex items-center justify-between mt-6 pt-4 border-t border-white/20">
                            <button
                                onClick={() => setCurrent(Math.max(0, current - 1))}
                                disabled={current === 0}
                                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-30 transition-all"
                            >
                                <ChevronLeft className="w-5 h-5" />
                            </button>
                            <button
                                onClick={() => speakSlide(current)}
                                disabled={speakingSlide === current}
                                className="flex items-center gap-2 px-4 py-2 bg-white/20 hover:bg-white/30 rounded-xl text-xs font-bold transition-all"
                            >
                                <Volume2 className={`w-4 h-4 ${speakingSlide === current ? "animate-pulse" : ""}`} />
                                {speakingSlide === current ? "Speaking..." : "Narrate"}
                            </button>
                            <button
                                onClick={() => setCurrent(Math.min(data.slides.length - 1, current + 1))}
                                disabled={current === data.slides.length - 1}
                                className="p-2 rounded-lg bg-white/10 hover:bg-white/20 disabled:opacity-30 transition-all"
                            >
                                <ChevronRight className="w-5 h-5" />
                            </button>
                        </div>
                    </div>

                    {/* Slide Thumbnails */}
                    <div className="flex gap-2 overflow-x-auto pb-2">
                        {data.slides.map((s, i) => (
                            <button
                                key={i}
                                onClick={() => { setCurrent(i); if (!autoPlaying) speakSlide(i); }}
                                className={`flex-shrink-0 w-28 p-3 rounded-xl text-left transition-all ${i === current
                                        ? `bg-gradient-to-br ${colors[i % colors.length]} text-white shadow-md scale-105`
                                        : "bg-white text-[var(--text-secondary)] border border-[var(--border)]/50 hover:shadow-md"
                                    }`}
                            >
                                <p className="text-[9px] font-bold opacity-60">{i + 1}</p>
                                <p className={`text-[10px] font-medium truncate ${i === current ? "text-white" : ""}`}>{s.title}</p>
                            </button>
                        ))}
                    </div>

                    {/* Narration Text */}
                    <div className="bg-white rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50">
                        <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider mb-2">Narration Script</p>
                        <p className="text-sm text-[var(--text-primary)] leading-relaxed italic">&ldquo;{data.slides[current].narration}&rdquo;</p>
                    </div>
                </div>
            )}
        </div>
    );
}
