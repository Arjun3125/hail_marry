"use client";

import { useCallback, useEffect, useState } from "react";
import { Volume2, Loader2, VolumeX, GraduationCap, CalendarCheck, Award, Clock, FileText, Activity, ShieldCheck, Sparkles } from "lucide-react";

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

    const load = useCallback(async () => {
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
    }, []);

    useEffect(() => {
        void load();
    }, [load]);

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
        <div className="max-w-4xl mx-auto space-y-6">
            <RoleStartPanel role="parent" />

            {error && (
                <div className="rounded-xl border border-[var(--error)]/30 bg-error-subtle px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            )}

            {loading ? (
                <div className="flex flex-col items-center justify-center p-20 min-h-[50vh]">
                    <Loader2 className="w-10 h-10 animate-spin text-[var(--accent-indigo)] mb-4" />
                    <p className="text-sm font-medium text-[var(--text-muted)] animate-pulse">Syncing child&apos;s records...</p>
                </div>
            ) : data ? (
                <>
                    {/* ─── Hero Banner ─── */}
                    <div className="relative overflow-hidden rounded-[var(--radius)] glass-panel border border-[var(--border-light)] shadow-2xl p-8 mb-8 isolate min-h-[220px] flex flex-col justify-end stagger-1">
                        {/* Background Gradients */}
                        <div className="absolute inset-0 bg-gradient-to-br from-indigo-500/10 via-purple-500/5 to-transparent z-[-1]" />
                        <div className="absolute top-0 right-0 w-96 h-96 bg-purple-500/20 blur-[100px] rounded-full translate-x-1/3 -translate-y-1/3 z-[-1]" />
                        
                        <div className="flex flex-col md:flex-row md:items-end justify-between gap-6">
                            <div>
                                <div className="flex items-center gap-2 mb-3">
                                    <div className="px-3 py-1 rounded-full bg-[var(--accent-purple)]/10 border border-[var(--accent-purple)]/20 text-[10px] uppercase tracking-widest font-bold text-[var(--accent-purple)] flex items-center gap-1.5 w-fit">
                                        <ShieldCheck className="w-3 h-3" />
                                        Guardian View Active
                                    </div>
                                </div>
                                <h1 className="text-4xl md:text-5xl font-black text-[var(--text-primary)] tracking-tight mb-2">
                                    {`${data.child.name}'s Dashboard`}
                                </h1>
                                <p className="text-sm text-[var(--text-muted)] flex items-center gap-2">
                                    <GraduationCap className="w-4 h-4 text-[var(--accent-purple)]" />
                                    {data.child.class ? `Class ${data.child.class}` : "Student Profile"} • {data.child.email}
                                </p>
                            </div>
                            
                            {/* Audio Report Action Card */}
                            <div className="bg-[var(--bg-card)]/80 backdrop-blur-md rounded-2xl p-4 border border-[var(--border-light)] shadow-lg max-w-sm flex gap-4 items-center shrink-0">
                                <button
                                    onClick={() => void playAudioReport()}
                                    disabled={audioLoading}
                                    className={`relative flex items-center justify-center w-14 h-14 rounded-full transition-all duration-300 shadow-md shrink-0 ${speaking
                                            ? "bg-gradient-to-tr from-rose-500 to-pink-600 text-white animate-pulse"
                                            : "bg-gradient-to-tr from-indigo-500 to-purple-600 text-white hover:scale-105 hover:shadow-indigo-500/20 hover:shadow-xl"
                                        } disabled:opacity-50`}
                                >
                                    {audioLoading ? (
                                        <Loader2 className="w-6 h-6 animate-spin" />
                                    ) : speaking ? (
                                        <VolumeX className="w-6 h-6" />
                                    ) : (
                                        <Volume2 className="w-6 h-6 ml-0.5" />
                                    )}
                                    {speaking && (
                                        <span className="absolute -inset-2 rounded-full border-2 border-rose-500 animate-ping opacity-20" />
                                    )}
                                </button>
                                <div>
                                    <h3 className="text-sm font-bold text-[var(--text-primary)]">Listen to Update</h3>
                                    <p className="text-xs text-[var(--text-muted)] leading-tight mt-0.5">
                                        {speaking ? "Playing AI summary..." : "Hear an AI-generated audio report of recent performance."}
                                    </p>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* ─── Metrics Grid ─── */}
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8 stagger-2">
                        {/* Attendance */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-6 shadow-[var(--shadow-card)] card-hover relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                                <CalendarCheck className="w-24 h-24 text-[var(--status-blue)] -mr-4 -mt-4 transform rotate-12" />
                            </div>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-blue-500/10 flex items-center justify-center">
                                    <CalendarCheck className="w-4 h-4 text-blue-500" />
                                </div>
                                <h2 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">Attendance</h2>
                            </div>
                            <div className="relative">
                                <span className={`text-4xl font-black tracking-tighter ${data.attendance_pct >= 75 ? "text-emerald-500" : "text-rose-500"}`}>
                                    {data.attendance_pct}%
                                </span>
                                {data.attendance_pct < 75 && (
                                    <p className="text-xs text-rose-500 font-medium mt-2 flex items-center gap-1">
                                        <ShieldCheck className="w-3 h-3" />
                                        Attention Required
                                    </p>
                                )}
                            </div>
                        </div>

                        {/* Average/Latest Marks */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-6 shadow-[var(--shadow-card)] card-hover relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                                <Award className="w-24 h-24 text-[var(--accent-purple)] -mr-4 -mt-4 transform rotate-12" />
                            </div>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-purple-500/10 flex items-center justify-center">
                                    <Activity className="w-4 h-4 text-purple-500" />
                                </div>
                                <h2 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">Latest Score</h2>
                            </div>
                            {data.latest_mark ? (
                                <div className="relative">
                                    <span className="text-4xl font-black tracking-tighter text-[var(--text-primary)]">
                                        {data.latest_mark.percentage}%
                                    </span>
                                    <p className="text-xs text-[var(--text-muted)] mt-2 font-medium bg-[var(--bg-page)] w-fit px-2 py-1 rounded border border-[var(--border-light)]">
                                        {data.latest_mark.subject} <span className="opacity-50 mx-1">•</span> {data.latest_mark.exam}
                                    </p>
                                </div>
                            ) : (
                                <p className="text-sm text-[var(--text-muted)] mt-4">No recent marks</p>
                            )}
                        </div>

                        {/* Assignments / Tasks */}
                        <div className="bg-[var(--bg-card)] rounded-[var(--radius)] p-6 shadow-[var(--shadow-card)] card-hover relative overflow-hidden group">
                            <div className="absolute top-0 right-0 p-6 opacity-5 group-hover:opacity-10 transition-opacity">
                                <FileText className="w-24 h-24 text-[var(--status-amber)] -mr-4 -mt-4 transform rotate-12" />
                            </div>
                            <div className="flex items-center gap-3 mb-4">
                                <div className="w-8 h-8 rounded-lg bg-amber-500/10 flex items-center justify-center">
                                    <Sparkles className="w-4 h-4 text-amber-500" />
                                </div>
                                <h2 className="text-xs font-bold text-[var(--text-muted)] uppercase tracking-widest">Pending Work</h2>
                            </div>
                            <div className="relative">
                                <span className={`text-4xl font-black tracking-tighter ${data.pending_assignments > 0 ? "text-amber-500" : "text-emerald-500"}`}>
                                    {data.pending_assignments}
                                </span>
                                <p className="text-xs text-[var(--text-muted)] mt-2 font-medium">
                                    assignments due this week
                                </p>
                            </div>
                        </div>
                    </div>

                    {/* ─── Schedule Insight ─── */}
                    <div className="bg-[var(--bg-card)] rounded-[var(--radius)] shadow-[var(--shadow-card)] border border-[var(--border)] overflow-hidden stagger-3">
                        <div className="p-5 border-b border-[var(--border-light)] bg-[var(--bg-page)]/50 backdrop-blur-sm">
                            <h2 className="text-sm font-bold text-[var(--text-primary)] flex items-center gap-2">
                                <Clock className="w-4 h-4 text-[var(--accent-indigo)]" />
                                Immediate Schedule Insight
                            </h2>
                        </div>
                        <div className="p-6">
                            {data.next_class ? (
                                <div className="flex items-center gap-4">
                                    <div className="hidden sm:flex flex-col items-center justify-center w-20 h-20 bg-gradient-to-b from-indigo-500/10 to-indigo-600/5 rounded-2xl border border-indigo-500/10 shrink-0">
                                        <span className="text-xs font-bold text-indigo-500 uppercase tracking-wide">{DAYS[data.next_class.day] || "Day"}</span>
                                        <span className="text-xl font-black text-[var(--text-primary)]">{data.next_class.start_time.split(':')[0]}</span>
                                    </div>
                                    <div className="flex-1">
                                        <div className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded text-[10px] font-bold bg-indigo-500/10 text-indigo-600 mb-2">
                                            <div className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                                            UP NEXT
                                        </div>
                                        <h3 className="text-xl font-bold text-[var(--text-primary)] mb-1">{data.next_class.subject}</h3>
                                        <p className="text-sm text-[var(--text-muted)]">
                                            {data.next_class.start_time} - {data.next_class.end_time}
                                        </p>
                                    </div>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center justify-center py-6">
                                    <div className="w-12 h-12 bg-[var(--bg-page)] rounded-full flex items-center justify-center mb-3">
                                        <CalendarCheck className="w-5 h-5 text-[var(--text-muted)] opacity-50" />
                                    </div>
                                    <p className="text-sm text-[var(--text-muted)] font-medium">No upcoming classes scheduled.</p>
                                </div>
                            )}
                        </div>
                    </div>
                </>
            ) : null}
        </div>
    );
}
