"use client";

import { useEffect, useState } from "react";
import { Headphones, Loader2, Mic, PlayCircle, StopCircle, Volume2 } from "lucide-react";

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

type DialogueLine = { speaker: string; text: string };
type AudioData = { dialogue: DialogueLine[]; title: string; duration_estimate: string };
type AIJobStatus = "queued" | "running" | "completed" | "failed";
type AudioHistoryItem = {
    id: string;
    title: string;
    created_at: string | null;
    content: AudioData;
};

const formats = [
    { id: "deep_dive", label: "Deep dive", desc: "Two hosts unpack the topic more fully" },
    { id: "brief", label: "Brief", desc: "A quick summary for revision" },
    { id: "debate", label: "Debate", desc: "Two perspectives challenge each other" },
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
    const [history, setHistory] = useState<AudioHistoryItem[]>([]);

    useEffect(() => {
        const loadHistory = async () => {
            try {
                const payload = await api.student.studyToolHistory("audio_overview", 6) as { items?: AudioHistoryItem[] };
                const items = payload.items || [];
                setHistory(items);
                if (items.length > 0) {
                    setData(items[0].content);
                    setTopic(items[0].title);
                }
            } catch {
                // History is a non-blocking enhancement for demo mode.
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
                const job = await api.ai.jobStatus(jobId) as { status: AIJobStatus; error?: string; result?: AudioData; poll_after_ms?: number };
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
            const job = await api.ai.enqueueAudioOverviewJob({ topic: topic.trim(), format }) as { job_id: string; status: AIJobStatus };
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
        const femaleVoice = voices.find((voice) => voice.name.includes("Female") || voice.name.includes("Zira") || voice.name.includes("Samantha")) || voices[0];
        const maleVoice = voices.find((voice) => voice.name.includes("Male") || voice.name.includes("David") || voice.name.includes("Daniel")) || voices[1] || voices[0];

        let index = 0;
        const speakNext = () => {
            if (!data || index >= data.dialogue.length) {
                setPlaying(false);
                setCurrentLine(-1);
                return;
            }
            const line = data.dialogue[index];
            setCurrentLine(index);
            const utt = new SpeechSynthesisUtterance(line.text);
            utt.voice = line.speaker === "Anika" ? femaleVoice : maleVoice;
            utt.pitch = line.speaker === "Anika" ? 1.15 : 0.9;
            utt.rate = 0.95;
            utt.onend = () => { index += 1; speakNext(); };
            utt.onerror = () => { index += 1; speakNext(); };
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
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Headphones className="h-3.5 w-3.5" />Audio Overview</PrismHeroKicker>}
                    title="Turn a topic into an audio revision conversation"
                    description="Use this tool when reading feels heavy and listening will help you revise. The output is still grounded to the topic you request, but delivered in a more accessible study format."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Selected format</span>
                        <strong className="prism-status-value">{formats.find((item) => item.id === format)?.label ?? format}</strong>
                        <span className="prism-status-detail">Current audio style for the next generation request</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Job status</span>
                        <strong className="prism-status-value">{jobStatus ?? "Idle"}</strong>
                        <span className="prism-status-detail">Queue and generation state for the current request</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Segments ready</span>
                        <strong className="prism-status-value">{data?.dialogue.length ?? 0}</strong>
                        <span className="prism-status-detail">Conversation turns available in the current audio draft</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Saved drafts</span>
                        <strong className="prism-status-value">{history.length}</strong>
                        <span className="prism-status-detail">Seeded audio overviews already available in this demo workspace</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-audio-overview" onRetry={() => window.location.reload()} /> : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismSectionHeader title="Generate audio" description="Enter a topic, choose the listening style that matches your study goal, and generate a narrated revision conversation." />
                    <input value={topic} onChange={(e) => setTopic(e.target.value)} onKeyDown={(e) => { if (e.key === "Enter") void generate(); }} placeholder="Enter a topic, for example Photosynthesis or French Revolution" className="w-full rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-4 py-3 text-sm text-[var(--text-primary)]" />
                    <div className="grid gap-3 md:grid-cols-3">
                        {formats.map((item) => (
                            <button key={item.id} type="button" onClick={() => setFormat(item.id)} className={`rounded-2xl border px-4 py-4 text-left transition ${format === item.id ? "border-[var(--primary)] bg-[rgba(96,165,250,0.08)]" : "border-[var(--border)] bg-[rgba(255,255,255,0.03)]"}`}>
                                <p className="text-sm font-semibold text-[var(--text-primary)]">{item.label}</p>
                                <p className="mt-2 text-xs leading-5 text-[var(--text-secondary)]">{item.desc}</p>
                            </button>
                        ))}
                    </div>
                    <button onClick={() => void generate()} disabled={loading || !topic.trim()} className="prism-action" type="button">
                        {loading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Mic className="h-4 w-4" />}
                        Generate audio overview
                    </button>
                </PrismPanel>

                {loading ? (
                    <PrismPanel className="p-8">
                        <p className="text-sm text-[var(--text-secondary)]">{jobStatus === "queued" ? "Waiting for the worker to pick up your audio request..." : "Generating the audio script now..."}</p>
                    </PrismPanel>
                ) : data ? (
                    <div className="space-y-6">
                        <div className="grid gap-6 xl:grid-cols-[0.92fr_1.08fr]">
                            <PrismPanel className="space-y-5 p-5">
                                <PrismSectionHeader title={data.title} description={`Estimated listening time: ${data.duration_estimate}`} actions={playing ? <button onClick={stopPlaying} className="prism-action-secondary" type="button"><StopCircle className="h-4 w-4" />Stop</button> : <button onClick={playAll} className="prism-action" type="button"><PlayCircle className="h-4 w-4" />Play all</button>} />
                                <p className="text-sm leading-6 text-[var(--text-secondary)]">Listen through the full conversation or read the scripted segments on the right when you want slower revision.</p>
                            </PrismPanel>
                            <PrismPanel className="space-y-3 p-5">
                                <PrismSectionHeader title="Dialogue script" description="Each segment is narrated in order, with the active line highlighted while speech playback is running." />
                                {data.dialogue.map((line, index) => (
                                    <div key={`${line.speaker}-${index}`} className={`rounded-2xl border px-4 py-3 transition ${currentLine === index ? "border-[var(--primary)] bg-[rgba(96,165,250,0.08)]" : "border-[var(--border)] bg-[rgba(255,255,255,0.03)]"}`}>
                                        <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">
                                            {line.speaker}
                                            {currentLine === index ? <Volume2 className="ml-1 inline h-3 w-3 text-[var(--primary)]" /> : null}
                                        </p>
                                        <p className="mt-2 text-sm leading-6 text-[var(--text-primary)]">{line.text}</p>
                                    </div>
                                ))}
                            </PrismPanel>
                        </div>
                        {history.length > 1 ? (
                            <PrismPanel className="space-y-3 p-5">
                                <PrismSectionHeader title="Recent audio drafts" description="Load one of the seeded demo conversations to show how revision output evolved over the last six months." />
                                <div className="grid gap-3 md:grid-cols-2 xl:grid-cols-3">
                                    {history.map((item) => (
                                        <button
                                            key={item.id}
                                            type="button"
                                            onClick={() => {
                                                setData(item.content);
                                                setTopic(item.title);
                                                setPlaying(false);
                                                setCurrentLine(-1);
                                            }}
                                            className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] p-4 text-left transition hover:border-[var(--primary)] hover:bg-[rgba(96,165,250,0.08)]"
                                        >
                                            <p className="text-sm font-semibold text-[var(--text-primary)]">{item.title}</p>
                                            <p className="mt-1 text-xs text-[var(--text-secondary)]">{item.created_at ? new Date(item.created_at).toLocaleDateString() : "Saved draft"}</p>
                                        </button>
                                    ))}
                                </div>
                            </PrismPanel>
                        ) : null}
                    </div>
                ) : (
                    <PrismPanel className="p-6">
                        <EmptyState icon={Headphones} title="No audio overview yet" description="Generate the first audio draft to turn a topic into a spoken revision aid." eyebrow="Ready to generate" />
                    </PrismPanel>
                )}
            </PrismSection>
        </PrismPage>
    );
}
