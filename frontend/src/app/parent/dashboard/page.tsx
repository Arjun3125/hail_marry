"use client";

import { useEffect, useState } from "react";
import { Volume2, Loader2, VolumeX, GraduationCap, CalendarCheck, Award, Clock, FileText } from "lucide-react";

import { api } from "@/lib/api";
import { RoleStartPanel } from "@/components/RoleStartPanel";

type ParentDashboard = {
    child: {
        id: string;
        name: string;
        email: string;
        class: string | null;
    };
    attendance_pct: number;
    avg_marks: number;
    pending_assignments: number;
    latest_mark: {
        subject: string;
        exam: string;
        percentage: number;
        date: string | null;
    } | null;
    next_class: {
        day: number;
        start_time: string;
        end_time: string;
        subject: string;
    } | null;
};

const DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];

export default function ParentDashboardPage() {
    const [data, setData] = useState<ParentDashboard | null>(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);
    const [speaking, setSpeaking] = useState(false);
    const [audioLoading, setAudioLoading] = useState(false);

    useEffect(() => {
        const load = async () => {
            try {
                setLoading(true);
                setError(null);
                const payload = await api.parent.dashboard();
                setData(payload as ParentDashboard);
            } catch (err) {
                setError(err instanceof Error ? err.message : "Failed to load dashboard");
            } finally {
                setLoading(false);
            }
        };
        void load();
    }, []);

    const playAudioReport = async () => {
        if (speaking) {
            window.speechSynthesis.cancel();
            setSpeaking(false);
            return;
        }
        try {
            setAudioLoading(true);
            const report = (await api.parent.audioReport()) as { text: string };
            const utterance = new SpeechSynthesisUtterance(report.text);
            utterance.rate = 0.9;
            utterance.onend = () => setSpeaking(false);
            utterance.onerror = () => setSpeaking(false);
            window.speechSynthesis.speak(utterance);
            setSpeaking(true);
        } catch {
            setError("Failed to load audio report");
        } finally {
            setAudioLoading(false);
        }
    };

    return (
        <div className="max-w-3xl mx-auto space-y-6">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-2.5 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-600 shadow-lg">
                        <GraduationCap className="w-5 h-5 text-white" />
                    </div>
                    <div>
                        <h1 className="text-2xl font-bold text-[var(--text-primary)]">Parent Dashboard</h1>
                        <p className="text-xs text-[var(--text-muted)]">Track your child&apos;s progress in one place</p>
                    </div>
                </div>
            </div>

            <RoleStartPanel role="parent" />

            {error ? (
                <div className="rounded-xl border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-12 text-center border border-[var(--border)]/50">
                    <Loader2 className="w-8 h-8 mx-auto text-teal-500 animate-spin mb-3" />
                    <p className="text-sm text-[var(--text-muted)]">Loading dashboard...</p>
                </div>
            ) : data ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] border border-[var(--border)]/50 p-6 space-y-6">
                    <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
                        <div>
                            <p className="text-[10px] uppercase tracking-widest text-[var(--text-muted)] mb-1">Your Child</p>
                            <p className="text-xl font-bold text-[var(--text-primary)]">{data.child.name}</p>
                            <div className="flex items-center gap-3 mt-2 text-xs text-[var(--text-muted)]">
                                <span>{data.child.email}</span>
                                {data.child.class ? (
                                    <span className="text-[10px] font-bold bg-info-badge px-2.5 py-0.5 rounded-full text-status-blue">
                                        {data.child.class}
                                    </span>
                                ) : null}
                            </div>
                        </div>
                        <button
                            onClick={() => void playAudioReport()}
                            disabled={audioLoading}
                            className={`flex items-center gap-2 px-5 py-2.5 rounded-xl text-sm font-bold transition-all duration-200 hover:scale-[1.02] shadow-md ${speaking
                                    ? "bg-gradient-to-r from-red-500 to-rose-600 text-white hover:shadow-lg"
                                    : "bg-gradient-to-r from-violet-500 to-purple-600 text-white hover:shadow-lg"
                                } disabled:opacity-40`}
                        >
                            {audioLoading ? (
                                <Loader2 className="w-4 h-4 animate-spin" />
                            ) : speaking ? (
                                <VolumeX className="w-4 h-4" />
                            ) : (
                                <Volume2 className="w-4 h-4" />
                            )}
                            {speaking ? "Stop" : "ðŸ”Š Listen to Report"}
                        </button>
                    </div>

                    <div className="grid gap-4 md:grid-cols-3">
                        <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-page)] p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <CalendarCheck className="w-4 h-4 text-status-blue" />
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Attendance</p>
                            </div>
                            <p className={`text-3xl font-black ${data.attendance_pct >= 75 ? "text-status-emerald" : "text-status-red"}`}>
                                {data.attendance_pct}%
                            </p>
                            {data.attendance_pct < 75 && (
                                <p className="text-[10px] text-status-red mt-1 font-medium">Below 75% threshold</p>
                            )}
                        </div>
                        <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-page)] p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Award className="w-4 h-4 text-status-amber" />
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Latest Marks</p>
                            </div>
                            {data.latest_mark ? (
                                <>
                                    <p className="text-2xl font-black text-[var(--text-primary)]">{data.latest_mark.percentage}%</p>
                                    <p className="text-xs text-[var(--text-muted)]">
                                        {data.latest_mark.subject} â€¢ {data.latest_mark.exam}
                                    </p>
                                </>
                            ) : (
                                <p className="text-sm text-[var(--text-muted)]">No marks yet</p>
                            )}
                        </div>
                        <div className="rounded-xl border border-[var(--border)] bg-[var(--bg-page)] p-4">
                            <div className="flex items-center gap-2 mb-2">
                                <Clock className="w-4 h-4 text-status-violet" />
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Next Class</p>
                            </div>
                            {data.next_class ? (
                                <>
                                    <p className="text-lg font-semibold text-[var(--text-primary)]">{data.next_class.subject}</p>
                                    <p className="text-xs text-[var(--text-muted)]">
                                        {DAYS[data.next_class.day] || "Day"} â€¢ {data.next_class.start_time} - {data.next_class.end_time}
                                    </p>
                                </>
                            ) : (
                                <p className="text-sm text-[var(--text-muted)]">No upcoming classes</p>
                            )}
                        </div>
                    </div>

                    <div className="flex items-center gap-3 text-xs text-[var(--text-muted)]">
                        <FileText className="w-3 h-3" />
                        {data.pending_assignments} pending assignments this week
                    </div>
                </div>
            ) : (
                <p className="text-sm text-[var(--text-muted)]">No data available.</p>
            )}
        </div>
    );
}
