"use client";

import { useEffect, useState } from "react";
import { ChevronLeft, ChevronRight, Loader2, PauseCircle, PlayCircle, Presentation, Volume2 } from "lucide-react";

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
import { api } from "@/lib/api";

type Slide = { title: string; bullets: string[]; narration: string };
type VideoData = { slides: Slide[]; presentation_title: string; total_slides: number };
type AIJobStatus = "queued" | "running" | "completed" | "failed";
type VideoHistoryItem = {
    id: string;
    title: string;
    created_at: string | null;
    content: VideoData;
};

const colors = [
    "from-blue-600 to-indigo-700",
    "from-emerald-600 to-teal-700",
    "from-violet-600 to-purple-700",
    "from-amber-600 to-orange-700",
    "from-rose-600 to-pink-700",
    "from-cyan-600 to-blue-700",
];

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
    const [history, setHistory] = useState<VideoHistoryItem[]>([]);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const payload = await api.student.studyToolHistory("video_overview", 6) as { items?: VideoHistoryItem[] };
                const items = payload.items || [];
                setHistory(items);
                if (items.length > 0) {
                    setData(items[0].content);
                    setTopic(items[0].title);
                    setCurrent(0);
                }
            } catch {
                // History is optional for non-demo usage.
            }
        };

        void loadHistory();
    }, []);

    useEffect(() => {
        if (!jobId) return;
        let cancelled = false;
        let timer: ReturnType<typeof setTimeout> | null = null;

        const poll = async () => {
            try {
                const job = await api.ai.jobStatus(jobId) as { status: AIJobStatus; error?: string; result?: VideoData; poll_after_ms?: number };
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
                timer = setTimeout(() => void poll(), job.poll_after_ms ?? 2000);
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
            const job = await api.ai.enqueueVideoOverviewJob({ topic: topic.trim(), num_slides: 6 }) as { job_id: string; status: AIJobStatus };
            setJobId(job.job_id);
            setJobStatus(job.status);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Cannot connect to backend");
            setLoading(false);
        }
    };

    const speakSlide = (index: number) => {
        if (!data || index >= data.slides.length) return;
        window.speechSynthesis.cancel();
        const utt = new SpeechSynthesisUtterance(data.slides[index].narration);
        utt.rate = 0.95;
        setSpeakingSlide(index);
        utt.onend = () => setSpeakingSlide(-1);
        utt.onerror = () => setSpeakingSlide(-1);
        window.speechSynthesis.speak(utt);
    };

    const autoPlay = () => {
        if (!data || autoPlaying) return;
        window.speechSynthesis.cancel();
        setAutoPlaying(true);
        setCurrent(0);
        let index = 0;
        const playNext = () => {
            if (!data || index >= data.slides.length) {
                setAutoPlaying(false);
                setSpeakingSlide(-1);
                return;
            }
            setCurrent(index);
            setSpeakingSlide(index);
            const utt = new SpeechSynthesisUtterance(data.slides[index].narration);
            utt.rate = 0.93;
            utt.onend = () => { index += 1; setTimeout(playNext, 500); };
            utt.onerror = () => { index += 1; setTimeout(playNext, 500); };
            window.speechSynthesis.speak(utt);
        };
        playNext();
    };

    const stopAutoPlay = () => {
        window.speechSynthesis.cancel();
        setAutoPlaying(false);
        setSpeakingSlide(-1);
    };

    return (
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Presentation className="h-3.5 w-3.5" />Video Overview</PrismHeroKicker>}
                    title="Turn a topic into a narrated slide-style explanation"
                    description="Use this when you want visual structure as well as explanation. The output is designed to feel like a compact revision presentation rather than a long chapter read."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Job status</span>
                        <strong className="prism-status-value">{jobStatus ?? "Idle"}</strong>
                        <span className="prism-status-detail">Queue and generation state for the current request</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Slides ready</span>
                        <strong className="prism-status-value">{data?.total_slides ?? 0}</strong>
                        <span className="prism-status-detail">Narrated slides available in the current presentation</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Current slide</span>
                        <strong className="prism-status-value">{data ? current + 1 : 0}</strong>
                        <span className="prism-status-detail">Slide currently open in the presentation viewer</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Saved decks</span>
                        <strong className="prism-status-value">{history.length}</strong>
                        <span className="prism-status-detail">Seeded presentation drafts already stored in the demo workspace</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-video-overview" onRetry={() => window.location.reload()} /> : null}

                {!data && (
                    <PrismPanel className="space-y-5 p-5">
                        <PrismSectionHeader title="Generate presentation" description="Enter a topic and the system will turn it into a narrated, slide-based explanation you can read or listen through." />
                        <input value={topic} onChange={(e) => setTopic(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") void generate(); }} placeholder="Enter a topic, for example Water Cycle or Indian Independence" className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)]" />
                        <button onClick={() => void generate()} disabled={loading || !topic.trim()} className="prism-action" type="button">
                            {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Presentation className="h-4 w-4" />}
                            Generate presentation
                        </button>
                    </PrismPanel>
                )}

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">{jobStatus === "queued" ? "Waiting for the worker to start this presentation..." : "Generating narrated slides..."}</p>
                    </PrismPanel>
                ) : data && data.slides.length > 0 ? (
                    <div className="space-y-5">
                        <PrismPanel className="p-4">
                            <div className="flex flex-wrap items-center justify-between gap-3">
                                <div>
                                    <h2 className="text-base font-semibold text-[var(--text-primary)]">{data.presentation_title}</h2>
                                    <p className="text-sm text-[var(--text-secondary)]">{data.total_slides} slides in the current presentation</p>
                                </div>
                                <div className="flex flex-wrap gap-2">
                                    {autoPlaying ? (
                                        <button onClick={stopAutoPlay} className="prism-action-secondary" type="button"><PauseCircle className="h-4 w-4" />Stop</button>
                                    ) : (
                                        <button onClick={autoPlay} className="prism-action" type="button"><PlayCircle className="h-4 w-4" />Auto-play</button>
                                    )}
                                    <button onClick={() => { setData(null); setTopic(""); }} className="prism-action-secondary" type="button">New topic</button>
                                </div>
                            </div>
                        </PrismPanel>

                        <div className={`rounded-3xl bg-gradient-to-br ${colors[current % colors.length]} p-8 text-white shadow-[var(--shadow-card)]`}>
                            <p className="text-[10px] uppercase tracking-[0.2em] text-white/70">Slide {current + 1} of {data.slides.length}</p>
                            <h3 className="mt-3 text-2xl font-bold">{data.slides[current].title}</h3>
                            <ul className="mt-6 space-y-3">
                                {data.slides[current].bullets.map((bullet, index) => (
                                    <li key={index} className="flex items-start gap-3">
                                        <span className="mt-1.5 h-2 w-2 rounded-full bg-white/70" />
                                        <span className="text-sm leading-7">{bullet}</span>
                                    </li>
                                ))}
                            </ul>
                            <div className="mt-8 flex flex-wrap items-center justify-between gap-3 border-t border-white/20 pt-4">
                                <button onClick={() => setCurrent(Math.max(0, current - 1))} disabled={current === 0} className="prism-action-secondary" type="button"><ChevronLeft className="h-4 w-4" />Previous</button>
                                <button onClick={() => speakSlide(current)} className="prism-action-secondary" type="button"><Volume2 className={`h-4 w-4 ${speakingSlide === current ? "animate-pulse" : ""}`} />{speakingSlide === current ? "Speaking..." : "Narrate slide"}</button>
                                <button onClick={() => setCurrent(Math.min(data.slides.length - 1, current + 1))} disabled={current === data.slides.length - 1} className="prism-action-secondary" type="button">Next<ChevronRight className="h-4 w-4" /></button>
                            </div>
                        </div>

                        <div className="grid gap-3 md:grid-cols-3 xl:grid-cols-6">
                            {data.slides.map((slide, index) => (
                                <button key={index} onClick={() => { setCurrent(index); if (!autoPlaying) speakSlide(index); }} className={`rounded-2xl border p-3 text-left transition ${index === current ? "border-[var(--primary)] bg-[rgba(96,165,250,0.08)]" : "border-[var(--border)] bg-[rgba(255,255,255,0.03)]"}`} type="button">
                                    <p className="text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">{index + 1}</p>
                                    <p className="mt-2 text-sm font-medium text-[var(--text-primary)] line-clamp-2">{slide.title}</p>
                                </button>
                            ))}
                        </div>

                        <PrismPanel className="p-5">
                            <PrismSectionHeader title="Narration script" description="Read the narration directly when you want to revise without audio playback." />
                            <p className="mt-4 text-sm leading-7 text-[var(--text-primary)]">{data.slides[current].narration}</p>
                        </PrismPanel>

                        {history.length > 1 ? (
                            <PrismPanel className="p-5">
                                <PrismSectionHeader title="Recent presentation drafts" description="Switch between seeded demo decks to show how the student has used this tool across the six-month window." />
                                <div className="mt-4 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                                    {history.map((item) => (
                                        <button
                                            key={item.id}
                                            type="button"
                                            onClick={() => {
                                                setData(item.content);
                                                setTopic(item.title);
                                                setCurrent(0);
                                                stopAutoPlay();
                                            }}
                                            className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4 text-left transition hover:border-[var(--primary)] hover:bg-[rgba(96,165,250,0.08)]"
                                        >
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "Saved deck"}</p>
                                        </button>
                                    ))}
                                </div>
                            </PrismPanel>
                        ) : null}
                    </div>
                ) : (
                    <PrismPanel className="p-6">
                        <EmptyState icon={Presentation} title="No video overview yet" description="Generate the first narrated presentation to turn a topic into a slide-based revision flow." eyebrow="Ready to generate" />
                    </PrismPanel>
                )}
            </PrismSection>
        </PrismPage>
    );
}
