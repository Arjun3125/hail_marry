"use client";

import { useEffect, useState } from "react";
import { Headphones, PlayCircle, StopCircle, Loader2, Mic, Volume2 } from "lucide-react";
import { api } from "@/lib/api";

type DialogueLine = { speaker: string; text: string };
type AudioData = { dialogue: DialogueLine[]; title: string; duration_estimate: string };
type AIJobStatus = "queued" | "running" | "completed" | "failed";

const formats = [
    { id: "deep_dive", label: "🎧 Deep Dive", desc: "2 hosts discuss in-depth" },
    { id: "brief", label: "⚡ Brief", desc: "Quick 3-min summary" },
    { id: "debate", label: "⚔️ Debate", desc: "Two sides argue" },
];

export default function AudioOverviewPage() {
    const [topic, setTopic] = useState("");
    const [format, setFormat] = useState("deep_dive");
    const [loading, setLoading] = useState(false);
    const [data, setData] = useState<AudioData | null>(null);
    const [error, setError] = useState<string | null>(null);
    const [playing, setPlaying] = useState(false);
    const [currentLine, setCurrentLine] = useState(-1);
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
                    result?: AudioData;
                    poll_after_ms?: number;
                };

                if (cancelled) return;
                setJobStatus(job.status);

                if (job.status === "completed" && job.result) {
                    setData(job.result);
                    setLoading(false);
                    setJobId(null);
                    return;
                }

                if (job.status === "failed") {
                    setError(job.error || "Failed to generate audio overview");
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
            const job = await api.ai.enqueueAudioOverviewJob({
                topic: topic.trim(),
                format,
            }) as { job_id: string; status: AIJobStatus };
            setJobId(job.job_id);
            setJobStatus(job.status);
        } catch (err) {
            setError(err instanceof Error ? err.message : "Cannot connect to backend");
            setLoading(false);
        }
    };

    const playAll = () => {
        if (!data || playing) return;
        window.speechSynthesis.cancel();
        setPlaying(true);

        const voices = window.speechSynthesis.getVoices();
        const femaleVoice = voices.find(v => v.name.includes("Female") || v.name.includes("Zira") || v.name.includes("Samantha")) || voices[0];
        const maleVoice = voices.find(v => v.name.includes("Male") || v.name.includes("David") || v.name.includes("Daniel")) || voices[1] || voices[0];

        let i = 0;
        const speakNext = () => {
            if (i >= data.dialogue.length) {
                setPlaying(false);
                setCurrentLine(-1);
                return;
            }
            const line = data.dialogue[i];
            setCurrentLine(i);
            const utt = new SpeechSynthesisUtterance(line.text);
            utt.voice = line.speaker === "Anika" ? femaleVoice : maleVoice;
            utt.pitch = line.speaker === "Anika" ? 1.15 : 0.9;
            utt.rate = 0.95;
            utt.onend = () => { i++; speakNext(); };
            utt.onerror = () => { i++; speakNext(); };
            window.speechSynthesis.speak(utt);
        };
        speakNext();
    };

    const stopPlaying = () => {
        window.speechSynthesis.cancel();
        setPlaying(false);
        setCurrentLine(-1);
    };

    return (
        <div className="max-w-3xl mx-auto">
            {/* Header */}
            <div className="mb-5">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 shadow-lg">
                        <Headphones className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Audio Overview</h1>
                        <p className="text-xs text-[var(--text-muted)]">AI-generated podcast from your study materials</p>
                    </div>
                </div>
            </div>

            {/* Input */}
            <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 mb-5">
                <input
                    value={topic}
                    onChange={(e) => setTopic(e.target.value)}
                    onKeyDown={(e) => { if (e.key === "Enter") void generate(); }}
                    placeholder="Enter a topic — e.g. Photosynthesis, French Revolution..."
                    className="w-full px-4 py-3 text-sm bg-[var(--bg-page)] border-0 rounded-xl focus:outline-none focus:ring-2 focus:ring-violet-500/50 mb-3"
                />
                <div className="flex items-center gap-2 mb-3">
                    {formats.map((f) => (
                        <button
                            key={f.id}
                            onClick={() => setFormat(f.id)}
                            className={`flex-1 px-3 py-2.5 rounded-xl text-xs font-medium transition-all ${format === f.id
                                    ? "bg-gradient-to-r from-violet-500 to-purple-600 text-white shadow-md"
                                    : "bg-[var(--bg-page)] text-[var(--text-secondary)] hover:bg-[var(--border)]/30"
                                }`}
                        >
                            {f.label}
                        </button>
                    ))}
                </div>
                <button
                    onClick={() => void generate()}
                    disabled={loading || !topic.trim()}
                    className="w-full px-5 py-3 bg-gradient-to-r from-violet-500 to-purple-600 text-white text-sm font-bold rounded-xl hover:shadow-lg transition-all disabled:opacity-40 flex items-center justify-center gap-2 hover:scale-[1.01]"
                >
                    {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Mic className="w-4 h-4" />}
                    Generate Podcast
                </button>
            </div>

            {error && (
                <div className="mb-4 rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">{error}</div>
            )}

            {loading && (
                <div className="bg-[var(--bg-card)] rounded-2xl p-12 shadow-[var(--shadow-card)] text-center border border-[var(--border)]/50">
                    <div className="w-14 h-14 mx-auto mb-4 rounded-xl bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center animate-pulse">
                        <Headphones className="w-7 h-7 text-white" />
                    </div>
                    <p className="text-sm font-medium text-[var(--text-primary)]">
                        {jobStatus === "queued" ? "Queued for generation..." : "Generating podcast script..."}
                    </p>
                    <p className="text-xs text-[var(--text-muted)] mt-1">
                        {jobStatus === "queued"
                            ? "Waiting for the AI worker to pick up your request"
                            : "The AI hosts are preparing to discuss your topic"}
                    </p>
                </div>
            )}

            {/* Podcast Player */}
            {!loading && data && (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] border border-[var(--border)]/50 overflow-hidden">
                    {/* Player Header */}
                    <div className="bg-gradient-to-r from-violet-500 to-purple-600 p-5 text-white">
                        <p className="text-[10px] uppercase tracking-widest opacity-70 mb-1">Now Playing</p>
                        <h2 className="text-lg font-bold">{data.title}</h2>
                        <div className="flex items-center gap-3 mt-3">
                            <p className="text-xs opacity-80">⏱ {data.duration_estimate} • {data.dialogue.length} segments</p>
                        </div>
                        <div className="flex items-center gap-2 mt-4">
                            {!playing ? (
                                <button onClick={playAll} className="flex items-center gap-2 px-5 py-2.5 bg-white/20 hover:bg-white/30 rounded-xl text-sm font-bold transition-all">
                                    <PlayCircle className="w-5 h-5" /> Play All
                                </button>
                            ) : (
                                <button onClick={stopPlaying} className="flex items-center gap-2 px-5 py-2.5 bg-white/20 hover:bg-white/30 rounded-xl text-sm font-bold transition-all">
                                    <StopCircle className="w-5 h-5" /> Stop
                                </button>
                            )}
                        </div>
                    </div>

                    {/* Dialogue */}
                    <div className="p-5 space-y-3 max-h-[500px] overflow-y-auto">
                        {data.dialogue.map((line, i) => {
                            const isAnika = line.speaker === "Anika";
                            const isActive = currentLine === i;
                            return (
                                <div
                                    key={i}
                                    className={`flex gap-3 p-3 rounded-xl transition-all duration-300 ${isActive ? "bg-violet-50 ring-2 ring-violet-300 scale-[1.01]" : "hover:bg-[var(--bg-page)]"
                                        }`}
                                >
                                    <div className={`w-9 h-9 rounded-full flex items-center justify-center flex-shrink-0 font-bold text-xs text-white shadow-sm ${isAnika ? "bg-gradient-to-br from-pink-500 to-rose-600" : "bg-gradient-to-br from-blue-500 to-indigo-600"
                                        }`}>
                                        {line.speaker[0]}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <p className={`text-[10px] font-bold uppercase tracking-wider mb-1 ${isAnika ? "text-pink-600" : "text-blue-600"}`}>
                                            {line.speaker}
                                            {isActive && <Volume2 className="w-3 h-3 inline ml-1 animate-pulse" />}
                                        </p>
                                        <p className="text-sm text-[var(--text-primary)] leading-relaxed">{line.text}</p>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>
            )}
        </div>
    );
}
