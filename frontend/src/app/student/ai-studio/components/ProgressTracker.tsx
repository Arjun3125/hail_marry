"use client";

import { useState, useEffect } from "react";
import { Trophy, Target, Clock, Zap, TrendingUp, Award, BookOpen, Brain } from "lucide-react";

interface ProgressTrackerProps {
    sessionStats: {
        startTime: number;
        questionsAsked: number;
        toolsUsed: string[];
        cardsReviewed?: number;
        quizScore?: number;
    };
}

interface Achievement {
    id: string;
    title: string;
    description: string;
    icon: React.ElementType;
    unlocked: boolean;
    color: string;
}

export function ProgressTracker({ sessionStats }: ProgressTrackerProps) {
    const [elapsedTime, setElapsedTime] = useState(0);
    const [showAchievements, setShowAchievements] = useState(false);

    // Update timer every second
    useEffect(() => {
        const interval = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - sessionStats.startTime) / 1000));
        }, 1000);
        return () => clearInterval(interval);
    }, [sessionStats.startTime]);

    // Format time as MM:SS
    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60);
        const secs = seconds % 60;
        return `${mins}:${secs.toString().padStart(2, "0")}`;
    };

    // Calculate achievements
    const achievements: Achievement[] = [
        {
            id: "first_question",
            title: "First Question",
            description: "Asked your first question",
            icon: BookOpen,
            unlocked: sessionStats.questionsAsked >= 1,
            color: "text-blue-500",
        },
        {
            id: "five_questions",
            title: "Curious Mind",
            description: "Asked 5 questions in a session",
            icon: Brain,
            unlocked: sessionStats.questionsAsked >= 5,
            color: "text-purple-500",
        },
        {
            id: "tool_master",
            title: "Tool Master",
            description: "Used 3+ different tools",
            icon: Zap,
            unlocked: sessionStats.toolsUsed.length >= 3,
            color: "text-amber-500",
        },
        {
            id: "quiz_wizard",
            title: "Quiz Wizard",
            description: "Scored 80%+ on a quiz",
            icon: Trophy,
            unlocked: (sessionStats.quizScore ?? 0) >= 80,
            color: "text-emerald-500",
        },
    ];

    const unlockedCount = achievements.filter((a) => a.unlocked).length;

    return (
        <div className="bg-[var(--bg-card)] border border-[var(--border)] rounded-xl p-4">
            <div className="flex items-center justify-between mb-4">
                <div className="flex items-center gap-2">
                    <Target className="w-4 h-4 text-indigo-500" />
                    <span className="text-sm font-medium text-[var(--text-primary)]">Session Progress</span>
                </div>
                <button
                    onClick={() => setShowAchievements(!showAchievements)}
                    className="flex items-center gap-1 text-xs text-[var(--text-muted)] hover:text-[var(--text-primary)]"
                >
                    <Award className="w-3 h-3" />
                    {unlockedCount}/{achievements.length}
                </button>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-2 gap-3 mb-4">
                <div className="bg-[var(--bg-page)] rounded-lg p-3">
                    <div className="flex items-center gap-2 text-[var(--text-muted)] mb-1">
                        <Clock className="w-3 h-3" />
                        <span className="text-[10px] uppercase tracking-wider">Time</span>
                    </div>
                    <span className="text-lg font-semibold text-[var(--text-primary)]">
                        {formatTime(elapsedTime)}
                    </span>
                </div>
                <div className="bg-[var(--bg-page)] rounded-lg p-3">
                    <div className="flex items-center gap-2 text-[var(--text-muted)] mb-1">
                        <TrendingUp className="w-3 h-3" />
                        <span className="text-[10px] uppercase tracking-wider">Questions</span>
                    </div>
                    <span className="text-lg font-semibold text-[var(--text-primary)]">
                        {sessionStats.questionsAsked}
                    </span>
                </div>
            </div>

            {/* Tools Used */}
            {sessionStats.toolsUsed.length > 0 && (
                <div className="mb-4">
                    <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-2">
                        Tools Used
                    </p>
                    <div className="flex flex-wrap gap-1">
                        {sessionStats.toolsUsed.map((tool) => (
                            <span
                                key={tool}
                                className="px-2 py-1 text-[10px] bg-indigo-500/10 text-indigo-600 rounded-full"
                            >
                                {tool}
                            </span>
                        ))}
                    </div>
                </div>
            )}

            {/* Achievements */}
            {showAchievements && (
                <div className="space-y-2 border-t border-[var(--border)] pt-3">
                    <p className="text-[10px] text-[var(--text-muted)] uppercase tracking-wider mb-2">
                        Achievements
                    </p>
                    {achievements.map((achievement) => (
                        <div
                            key={achievement.id}
                            className={`flex items-center gap-3 p-2 rounded-lg ${
                                achievement.unlocked
                                    ? "bg-[var(--bg-page)]"
                                    : "bg-[var(--bg-page)] opacity-50"
                            }`}
                        >
                            <achievement.icon className={`w-4 h-4 ${achievement.color}`} />
                            <div className="flex-1">
                                <p className="text-xs font-medium text-[var(--text-primary)]">
                                    {achievement.title}
                                </p>
                                <p className="text-[10px] text-[var(--text-muted)]">
                                    {achievement.description}
                                </p>
                            </div>
                            {achievement.unlocked && (
                                <Trophy className="w-3 h-3 text-amber-500" />
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
}
