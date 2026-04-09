"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, ExternalLink, Youtube } from "lucide-react";

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

type LectureItem = {
    title: string;
    subject: string;
    youtube_url: string;
    has_transcript: boolean;
};

export default function LecturesPage() {
    const [lectures, setLectures] = useState<LectureItem[]>([]);
    const [selectedSubject, setSelectedSubject] = useState<string>("all");
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.student.lectures();
                setLectures((payload || []) as LectureItem[]);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load lectures");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const subjects = useMemo(() => Array.from(new Set(lectures.map((lecture) => lecture.subject))).sort(), [lectures]);
    const filteredLectures = useMemo(() => selectedSubject === "all" ? lectures : lectures.filter((lecture) => lecture.subject === selectedSubject), [lectures, selectedSubject]);

    useEffect(() => {
        if (selectedSubject !== "all" && !subjects.includes(selectedSubject)) {
            setSelectedSubject("all");
        }
    }, [subjects, selectedSubject]);

    return (
        <PrismPage variant="workspace" className="space-y-6">
            <PrismSection className="space-y-6">
                <PrismPageIntro
                    kicker={<PrismHeroKicker><Youtube className="h-3.5 w-3.5" />Lecture Library</PrismHeroKicker>}
                    title="Use your teacher's lecture library as a study shelf"
                    description="Browse recorded lessons by subject, open the source video, and move into the student assistant when you want help understanding a lecture more deeply."
                />

                <div className="prism-status-strip">
                    <div className="prism-status-item">
                        <span className="prism-status-label">Lectures</span>
                        <strong className="prism-status-value">{lectures.length}</strong>
                        <span className="prism-status-detail">Recorded lecture items currently available to you</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">Subjects</span>
                        <strong className="prism-status-value">{subjects.length}</strong>
                        <span className="prism-status-detail">Subjects represented in the current lecture library</span>
                    </div>
                    <div className="prism-status-item">
                        <span className="prism-status-label">With transcript</span>
                        <strong className="prism-status-value">{lectures.filter((lecture) => lecture.has_transcript).length}</strong>
                        <span className="prism-status-detail">Lectures already carrying transcript support</span>
                    </div>
                </div>

                {error ? <ErrorRemediation error={error} scope="student-lectures" onRetry={() => window.location.reload()} /> : null}

                <PrismPanel className="space-y-5 p-5">
                    <PrismSectionHeader
                        title="Lecture collection"
                        description="Filter by subject when you want a tighter revision set, or leave the view open to browse everything available."
                        actions={(
                            <select value={selectedSubject} onChange={(event) => setSelectedSubject(event.target.value)} className="rounded-2xl border border-[var(--border)] bg-[rgba(255,255,255,0.03)] px-3 py-2 text-sm text-[var(--text-primary)]">
                                <option value="all">All subjects</option>
                                {subjects.map((subject) => <option key={subject} value={subject}>{subject}</option>)}
                            </select>
                        )}
                    />

                    {loading ? (
                        <p className="text-sm text-[var(--text-secondary)]">Loading lectures...</p>
                    ) : lectures.length === 0 ? (
                        <EmptyState icon={Youtube} title="No lectures available yet" description="Recorded lessons will appear here once your teachers publish them for your class." eyebrow="Library empty" />
                    ) : (
                        <div className="grid gap-4 md:grid-cols-2">
                            {filteredLectures.map((lecture, index) => (
                                <PrismPanel key={`${lecture.title}-${index}`} className="overflow-hidden p-0">
                                    <div className="flex h-36 items-center justify-center bg-[linear-gradient(135deg,rgba(96,165,250,0.22),rgba(59,130,246,0.12))]">
                                        <Youtube className="h-12 w-12 text-[var(--text-primary)]" />
                                    </div>
                                    <div className="space-y-4 p-4">
                                        <div>
                                            <p className="text-xs font-semibold uppercase tracking-[0.14em] text-[var(--primary)]">{lecture.subject}</p>
                                            <h3 className="mt-2 text-base font-semibold text-[var(--text-primary)]">{lecture.title}</h3>
                                        </div>
                                        <div className="flex flex-wrap items-center justify-between gap-2">
                                            <span className={`rounded-full px-2.5 py-1 text-[10px] font-semibold uppercase tracking-[0.14em] ${lecture.has_transcript ? "bg-success-subtle text-status-green" : "bg-[var(--bg-page)] text-[var(--text-muted)]"}`}>
                                                {lecture.has_transcript ? "Transcript available" : "Transcript pending"}
                                            </span>
                                            <div className="flex flex-wrap gap-2">
                                                <a href={lecture.youtube_url} target="_blank" rel="noreferrer" className="prism-action-secondary">
                                                    <ExternalLink className="h-3.5 w-3.5" />
                                                    Open
                                                </a>
                                                <a href="/student/assistant" className="prism-action-secondary">
                                                    <Bot className="h-3.5 w-3.5" />
                                                    Ask AI
                                                </a>
                                            </div>
                                        </div>
                                    </div>
                                </PrismPanel>
                            ))}
                        </div>
                    )}
                </PrismPanel>
            </PrismSection>
        </PrismPage>
    );
}
