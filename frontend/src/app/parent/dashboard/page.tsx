"use client";

import { useEffect, useState } from "react";
import { Volume2, Loader2, VolumeX, GraduationCap, CalendarCheck, Award, FileText } from "lucide-react";

import { api } from "@/lib/api";

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
};

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
                {data ? (
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
                        {speaking ? "Stop" : "🔊 Listen to Report"}
                    </button>
                ) : null}
            </div>

            {error ? (
                <div className="rounded-xl border border-[var(--error)]/30 bg-red-50 px-4 py-3 text-sm text-[var(--error)]">
                    {error}
                </div>
            ) : null}

            {loading ? (
                <div className="bg-[var(--bg-card)] rounded-2xl shadow-[var(--shadow-card)] p-12 text-center border border-[var(--border)]/50">
                    <Loader2 className="w-8 h-8 mx-auto text-teal-500 animate-spin mb-3" />
                    <p className="text-sm text-[var(--text-muted)]">Loading dashboard...</p>
                </div>
            ) : data ? (
                <>
                    {/* Child Profile Card */}
                    <div className="bg-gradient-to-r from-teal-500 to-emerald-600 rounded-2xl p-5 text-white shadow-lg">
                        <p className="text-[10px] uppercase tracking-widest opacity-70 mb-1">Your Child</p>
                        <p className="text-xl font-bold">{data.child.name}</p>
                        <div className="flex items-center gap-3 mt-2">
                            <span className="text-xs opacity-80">{data.child.email}</span>
                            {data.child.class ? (
                                <span className="text-[10px] font-bold bg-white/20 px-2.5 py-0.5 rounded-full">
                                    {data.child.class}
                                </span>
                            ) : null}
                        </div>
                    </div>

                    {/* Stats Grid */}
                    <div className="grid md:grid-cols-3 gap-3">
                        <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 hover:shadow-md transition-all duration-200">
                            <div className="flex items-center gap-2 mb-3">
                                <div className="p-1.5 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600">
                                    <CalendarCheck className="w-3.5 h-3.5 text-white" />
                                </div>
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Attendance</p>
                            </div>
                            <p className={`text-3xl font-black ${data.attendance_pct >= 75 ? "text-emerald-600" : "text-rose-600"}`}>
                                {data.attendance_pct}%
                            </p>
                            {data.attendance_pct < 75 && (
                                <p className="text-[10px] text-rose-500 mt-1 font-medium">⚠ Below 75% threshold</p>
                            )}
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 hover:shadow-md transition-all duration-200">
                            <div className="flex items-center gap-2 mb-3">
                                <div className="p-1.5 rounded-lg bg-gradient-to-br from-amber-500 to-orange-600">
                                    <Award className="w-3.5 h-3.5 text-white" />
                                </div>
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Avg Marks</p>
                            </div>
                            <p className={`text-3xl font-black ${data.avg_marks >= 60 ? "text-emerald-600" : "text-amber-600"}`}>
                                {data.avg_marks}%
                            </p>
                        </div>
                        <div className="bg-[var(--bg-card)] rounded-2xl p-5 shadow-[var(--shadow-card)] border border-[var(--border)]/50 hover:shadow-md transition-all duration-200">
                            <div className="flex items-center gap-2 mb-3">
                                <div className="p-1.5 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600">
                                    <FileText className="w-3.5 h-3.5 text-white" />
                                </div>
                                <p className="text-[10px] font-bold text-[var(--text-muted)] uppercase tracking-wider">Pending</p>
                            </div>
                            <p className={`text-3xl font-black ${data.pending_assignments === 0 ? "text-emerald-600" : "text-violet-600"}`}>
                                {data.pending_assignments}
                            </p>
                            <p className="text-[10px] text-[var(--text-muted)] mt-1">assignments</p>
                        </div>
                    </div>
                </>
            ) : (
                <p className="text-sm text-[var(--text-muted)]">No data available.</p>
            )}
        </div>
    );
}
