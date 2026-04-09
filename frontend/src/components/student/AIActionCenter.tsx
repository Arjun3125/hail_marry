import { ArrowRight, BrainCircuit, Mic2, Sparkles, Target, Video } from "lucide-react";

export function AIActionCenter({
    recommendations,
    weakTopics,
}: {
    recommendations: string[];
    weakTopics: string[];
}) {
    const mainRec = recommendations.length > 0 ? recommendations[0] : "Explore new study paths";
    const topics = weakTopics.slice(0, 2);

    return (
        <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(160deg,rgba(16,26,44,0.96),rgba(9,15,28,0.98))] p-6 shadow-[0_20px_44px_rgba(2,6,23,0.38)] transition-all duration-300 hover:border-[rgba(129,140,248,0.35)]">
            <div className="pointer-events-none absolute -right-24 top-0 h-56 w-56 rounded-full bg-[rgba(168,85,247,0.15)] blur-[70px]" />
            <div className="pointer-events-none absolute -left-24 bottom-0 h-56 w-56 rounded-full bg-[rgba(59,130,246,0.12)] blur-[70px]" />

            <div className="relative z-10">
                <div className="mb-6 flex items-start justify-between">
                    <div className="flex items-center gap-3">
                        <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-[rgba(99,102,241,0.18)] text-violet-300">
                            <BrainCircuit className="h-6 w-6" />
                        </div>
                        <div>
                            <h3 className="font-manrope text-xl font-bold text-[var(--text-primary)]">Study Path Wizard</h3>
                            <p className="font-inter text-sm text-[var(--text-muted)]">Your AI mentor</p>
                        </div>
                    </div>
                    <div className="flex h-8 items-center gap-1.5 rounded-full border border-emerald-400/30 bg-emerald-400/10 px-3 text-xs font-semibold text-emerald-300">
                        <span className="relative flex h-2 w-2">
                            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-300 opacity-75" />
                            <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-300" />
                        </span>
                        Online
                    </div>
                </div>

                <div className="mb-6 rounded-2xl border border-violet-400/20 bg-[rgba(99,102,241,0.09)] p-4">
                    <div className="flex items-start gap-3">
                        <Sparkles className="mt-0.5 h-5 w-5 shrink-0 text-violet-300" />
                        <p className="font-inter text-sm leading-relaxed text-[var(--text-secondary)]">
                            {`I analyzed your recent tests. ${mainRec.replace("Recommended: ", "")}.`}
                        </p>
                    </div>
                </div>

                <div className="mb-8">
                    <div className="mb-3 flex items-center gap-2">
                        <Target className="h-4 w-4 text-[var(--text-muted)]" />
                        <span className="font-inter text-xs font-semibold uppercase tracking-wider text-[var(--text-muted)]">Upcoming quests</span>
                    </div>
                    <div className="flex flex-wrap gap-2">
                        {topics.map((topic, i) => (
                            <div key={i} className="flex cursor-pointer items-center gap-2 rounded-lg border border-[var(--border)] bg-[rgba(15,23,42,0.72)] px-3 py-2 text-sm font-medium text-[var(--text-secondary)] transition-colors hover:border-violet-400/30 hover:bg-[rgba(99,102,241,0.14)] hover:text-[var(--text-primary)]">
                                <div className="h-2 w-2 rounded-full bg-indigo-400" />
                                {topic}
                            </div>
                        ))}
                        {topics.length === 0 ? <span className="text-sm text-[var(--text-muted)]">All caught up.</span> : null}
                    </div>
                </div>

                <div className="mb-4 grid grid-cols-2 gap-3">
                    <a href="/student/audio-overview" className="flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-[rgba(15,23,42,0.72)] py-3 text-xs font-bold text-[var(--text-secondary)] transition-colors hover:border-rose-400/30 hover:bg-rose-400/10 hover:text-[var(--text-primary)]">
                        <Mic2 className="h-3.5 w-3.5 text-rose-400" />
                        Audio Hub
                    </a>
                    <a href="/student/video-overview" className="flex items-center justify-center gap-2 rounded-xl border border-[var(--border)] bg-[rgba(15,23,42,0.72)] py-3 text-xs font-bold text-[var(--text-secondary)] transition-colors hover:border-blue-400/30 hover:bg-blue-400/10 hover:text-[var(--text-primary)]">
                        <Video className="h-3.5 w-3.5 text-blue-400" />
                        Video Hub
                    </a>
                </div>

                <button className="group flex w-full items-center justify-between rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-md shadow-violet-500/30 transition-all duration-300 hover:shadow-lg hover:shadow-violet-500/45 hover:-translate-y-0.5">
                    Continue Learning Path
                    <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
                </button>
            </div>
        </div>
    );
}
