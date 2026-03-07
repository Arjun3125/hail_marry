"use client";

import { useEffect, useMemo, useState } from "react";
import { Bot, ExternalLink, Youtube } from "lucide-react";

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

    const subjects = useMemo(
        () => Array.from(new Set(lectures.map((lecture) => lecture.subject))).sort(),
        [lectures]
    );

    const filteredLectures = useMemo(() => {
        if (selectedSubject === "all") {
            return lectures;
        }
        return lectures.filter((lecture) => lecture.subject === selectedSubject);
    }, [lectures, selectedSubject]);

    useEffect(() => {
        if (selectedSubject !== "all" && !subjects.includes(selectedSubject)) {
            setSelectedSubject("all");
        }
    }, [subjects, selectedSubject]);

    return (
        <div>
            <div className="mb-6">
                <h1 className="text-2xl font-bold text-[var(--text-primary)]">Lecture Library</h1>
                <p className="text-sm text-[var(--text-secondary)]">Video lectures uploaded by your teachers.</p>
            </div>

            {error ? (
                <div className="mb-4 rounded-[var(--radius)] border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                    Loading lectures...
                </div>
            ) : lectures.length === 0 ? (
                <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-5 shadow-[var(--shadow-card)] text-sm text-[var(--text-muted)]">
                    No lectures available for your class.
                </div>
            ) : (
                <div>
                    <div className="mb-4">
                        <label className="text-xs font-medium text-[var(--text-secondary)] mr-2">Subject</label>
                        <select
                            value={selectedSubject}
                            onChange={(event) => setSelectedSubject(event.target.value)}
                            className="px-3 py-2 text-sm border border-[var(--border)] rounded-[var(--radius-sm)] bg-[var(--bg-card)] text-[var(--text-primary)]"
                        >
                            <option value="all">All Subjects</option>
                            {subjects.map((subject) => (
                                <option key={subject} value={subject}>
                                    {subject}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="grid md:grid-cols-2 gap-4">
                    {filteredLectures.map((lecture, i) => (
                        <div key={`${lecture.title}-${i}`} className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] overflow-hidden">
                            <div className="h-36 bg-gradient-to-br from-[var(--primary-light)] to-[var(--primary)] flex items-center justify-center">
                                <Youtube className="w-12 h-12 text-white/80" />
                            </div>
                            <div className="p-4">
                                <p className="text-xs text-[var(--primary)] font-medium mb-1">{lecture.subject}</p>
                                <h3 className="text-sm font-semibold text-[var(--text-primary)] mb-3">{lecture.title}</h3>

                                <div className="flex items-center justify-between gap-2">
                                    {lecture.has_transcript ? (
                                        <span className="text-[10px] font-medium text-[var(--success)] bg-green-50 px-2 py-0.5 rounded-full">
                                            Transcript available
                                        </span>
                                    ) : (
                                        <span className="text-[10px] font-medium text-[var(--text-muted)] bg-[var(--bg-page)] px-2 py-0.5 rounded-full">
                                            Transcript pending
                                        </span>
                                    )}
                                    <div className="flex items-center gap-3">
                                        <a
                                            href={lecture.youtube_url}
                                            target="_blank"
                                            rel="noreferrer"
                                            className="flex items-center gap-1 text-xs font-medium text-[var(--primary)] hover:underline"
                                        >
                                            <ExternalLink className="w-3 h-3" /> Open
                                        </a>
                                        <a href="/student/ai" className="flex items-center gap-1 text-xs font-medium text-[var(--primary)] hover:underline">
                                            <Bot className="w-3 h-3" /> Ask AI
                                        </a>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))}
                    </div>
                </div>
            )}
        </div>
    );
}
