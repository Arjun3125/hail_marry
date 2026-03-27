"use client";

import { useState, useCallback, useEffect } from "react";
import { CheckCircle2, XCircle, HelpCircle, Timer, ChevronRight, RotateCcw, Trophy } from "lucide-react";

interface QuizQuestion {
    id: string;
    question: string;
    options: string[];
    correctAnswer: string;
    explanation?: string;
    difficulty?: "easy" | "medium" | "hard";
    topic?: string;
}

interface QuizViewProps {
    questions: QuizQuestion[];
    title?: string;
    onComplete?: (results: QuizResults) => void;
    onRetry?: () => void;
}

interface QuizResults {
    score: number;
    totalQuestions: number;
    correctAnswers: number;
    timeSpent: number;
    questionsByDifficulty: {
        easy: { total: number; correct: number };
        medium: { total: number; correct: number };
        hard: { total: number; correct: number };
    };
}

export function QuizView({ questions, title = "Quiz", onComplete, onRetry }: QuizViewProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [selectedAnswer, setSelectedAnswer] = useState<string | null>(null);
    const [isAnswered, setIsAnswered] = useState(false);
    const [answers, setAnswers] = useState<Record<string, { selected: string; correct: boolean; time: number }>>({});
    const [startTime] = useState(() => Date.now());
    const [questionStartTime, setQuestionStartTime] = useState(() => Date.now());
    const [showResults, setShowResults] = useState(false);
    const [elapsedTime, setElapsedTime] = useState(0);

    // Update elapsed time every second
    useEffect(() => {
        const interval = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        return () => clearInterval(interval);
    }, [startTime]);

    const currentQuestion = questions[currentIndex];
    const progress = ((currentIndex) / questions.length) * 100;

    const handleSelectAnswer = useCallback((answer: string) => {
        if (isAnswered) return;

        setSelectedAnswer(answer);
        setIsAnswered(true);

        const isCorrect = answer === currentQuestion.correctAnswer;
        const timeSpent = Math.floor((Date.now() - questionStartTime) / 1000);

        setAnswers((prev) => ({
            ...prev,
            [currentQuestion.id]: { selected: answer, correct: isCorrect, time: timeSpent },
        }));
    }, [currentQuestion, isAnswered, questionStartTime]);

    const handleNext = useCallback(() => {
        if (currentIndex < questions.length - 1) {
            setCurrentIndex((prev) => prev + 1);
            setSelectedAnswer(null);
            setIsAnswered(false);
            setQuestionStartTime(Date.now());
        } else {
            // Calculate results
            const results: QuizResults = {
                score: Object.values(answers).filter((a) => a.correct).length,
                totalQuestions: questions.length,
                correctAnswers: Object.values(answers).filter((a) => a.correct).length,
                timeSpent: Math.floor((Date.now() - startTime) / 1000),
                questionsByDifficulty: {
                    easy: { total: 0, correct: 0 },
                    medium: { total: 0, correct: 0 },
                    hard: { total: 0, correct: 0 },
                },
            };

            questions.forEach((q) => {
                const difficulty = q.difficulty || "medium";
                results.questionsByDifficulty[difficulty].total++;
                if (answers[q.id]?.correct) {
                    results.questionsByDifficulty[difficulty].correct++;
                }
            });

            setShowResults(true);
            onComplete?.(results);
        }
    }, [currentIndex, questions, answers, startTime, onComplete]);

    const handleRetry = useCallback(() => {
        setCurrentIndex(0);
        setSelectedAnswer(null);
        setIsAnswered(false);
        setAnswers({});
        setShowResults(false);
        setQuestionStartTime(Date.now());
        onRetry?.();
    }, [onRetry]);

    // Results screen
    if (showResults) {
        const correctCount = Object.values(answers).filter((a) => a.correct).length;
        const percentage = Math.round((correctCount / questions.length) * 100);

        return (
            <div className="flex flex-col h-full p-8 overflow-y-auto">
                <div className="max-w-2xl mx-auto w-full">
                    {/* Score Header */}
                    <div className="text-center mb-8">
                        <div className={`w-20 h-20 rounded-full flex items-center justify-center mx-auto mb-4 ${
                            percentage >= 80 ? "bg-emerald-500" : percentage >= 60 ? "bg-amber-500" : "bg-rose-500"
                        }`}>
                            <Trophy className="w-10 h-10 text-white" />
                        </div>
                        <h2 className="text-2xl font-bold text-[var(--text-primary)] mb-2">Quiz Complete!</h2>
                        <p className="text-sm text-[var(--text-muted)]">
                            You scored {correctCount} out of {questions.length}
                        </p>
                    </div>

                    {/* Score Breakdown */}
                    <div className="bg-[var(--bg-card)] rounded-2xl p-6 mb-6 border border-[var(--border)]">
                        <div className="grid grid-cols-3 gap-4 mb-6">
                            <div className="text-center p-4 bg-emerald-500/10 rounded-xl">
                                <p className="text-2xl font-bold text-emerald-600">{correctCount}</p>
                                <p className="text-xs text-[var(--text-muted)]">Correct</p>
                            </div>
                            <div className="text-center p-4 bg-rose-500/10 rounded-xl">
                                <p className="text-2xl font-bold text-rose-600">{questions.length - correctCount}</p>
                                <p className="text-xs text-[var(--text-muted)]">Incorrect</p>
                            </div>
                            <div className="text-center p-4 bg-blue-500/10 rounded-xl">
                                <p className="text-2xl font-bold text-blue-600">{percentage}%</p>
                                <p className="text-xs text-[var(--text-muted)]">Score</p>
                            </div>
                        </div>

                        {/* Difficulty Breakdown */}
                        <div className="space-y-2">
                            {["easy", "medium", "hard"].map((diff) => {
                                const diffQuestions = questions.filter((q) => q.difficulty === diff);
                                if (diffQuestions.length === 0) return null;
                                const diffCorrect = diffQuestions.filter((q) => answers[q.id]?.correct).length;
                                const diffPercent = Math.round((diffCorrect / diffQuestions.length) * 100);

                                return (
                                    <div key={diff} className="flex items-center gap-3">
                                        <span className="w-16 text-xs capitalize text-[var(--text-muted)]">{diff}</span>
                                        <div className="flex-1 h-2 bg-[var(--border)] rounded-full overflow-hidden">
                                            <div
                                                className={`h-full rounded-full ${
                                                    diffPercent >= 80 ? "bg-emerald-500" : diffPercent >= 60 ? "bg-amber-500" : "bg-rose-500"
                                                }`}
                                                style={{ width: `${diffPercent}%` }}
                                            />
                                        </div>
                                        <span className="w-12 text-xs text-right text-[var(--text-muted)]">
                                            {diffCorrect}/{diffQuestions.length}
                                        </span>
                                    </div>
                                );
                            })}
                        </div>
                    </div>

                    {/* Question Review */}
                    <div className="space-y-3 mb-6">
                        <h3 className="text-sm font-medium text-[var(--text-primary)]">Review</h3>
                        {questions.map((q, idx) => {
                            const answer = answers[q.id];
                            const isCorrect = answer?.correct;

                            return (
                                <div
                                    key={q.id}
                                    className={`p-4 rounded-xl border ${
                                        isCorrect ? "border-emerald-500/30 bg-emerald-500/5" : "border-rose-500/30 bg-rose-500/5"
                                    }`}
                                >
                                    <div className="flex items-start gap-3">
                                        <div className={`mt-0.5 ${isCorrect ? "text-emerald-500" : "text-rose-500"}`}>
                                            {isCorrect ? <CheckCircle2 className="w-5 h-5" /> : <XCircle className="w-5 h-5" />}
                                        </div>
                                        <div className="flex-1">
                                            <p className="text-sm text-[var(--text-primary)] mb-1">
                                                {idx + 1}. {q.question}
                                            </p>
                                            <p className="text-xs text-[var(--text-muted)]">
                                                Your answer: {answer?.selected} • Correct: {q.correctAnswer}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                        <button
                            onClick={handleRetry}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-[var(--bg-card)] hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] border border-[var(--border)] transition-colors"
                        >
                            <RotateCcw className="w-4 h-4" />
                            Retry Quiz
                        </button>
                        <button
                            onClick={() => {
                                // Navigate back or close
                            }}
                            className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-gradient-to-r from-indigo-500 to-violet-600 text-white hover:shadow-lg transition-all"
                        >
                            Continue Learning
                            <ChevronRight className="w-4 h-4" />
                        </button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="flex flex-col h-full">
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                <div>
                    <h2 className="font-semibold text-[var(--text-primary)]">{title}</h2>
                    <p className="text-xs text-[var(--text-muted)]">
                        Question {currentIndex + 1} of {questions.length}
                    </p>
                </div>
                <div className="flex items-center gap-2 text-xs text-[var(--text-muted)]">
                    <Timer className="w-4 h-4" />
                    {elapsedTime}s
                </div>
            </div>

            {/* Progress */}
            <div className="h-1 bg-[var(--border)]">
                <div
                    className="h-full bg-gradient-to-r from-violet-500 to-purple-600 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {/* Question */}
            <div className="flex-1 overflow-y-auto p-6">
                <div className="max-w-2xl mx-auto">
                    {/* Difficulty Badge */}
                    {currentQuestion.difficulty && (
                        <div className="mb-4">
                            <span className={`inline-flex items-center px-2 py-1 text-[10px] rounded-full font-medium ${
                                currentQuestion.difficulty === "easy"
                                    ? "bg-emerald-500/10 text-emerald-600"
                                    : currentQuestion.difficulty === "medium"
                                    ? "bg-amber-500/10 text-amber-600"
                                    : "bg-rose-500/10 text-rose-600"
                            }`}>
                                {currentQuestion.difficulty.charAt(0).toUpperCase() + currentQuestion.difficulty.slice(1)}
                            </span>
                        </div>
                    )}

                    {/* Question Text */}
                    <h3 className="text-lg font-medium text-[var(--text-primary)] mb-6">
                        {currentQuestion.question}
                    </h3>

                    {/* Options */}
                    <div className="space-y-3">
                        {currentQuestion.options.map((option) => {
                            const isSelected = selectedAnswer === option;
                            const isCorrect = option === currentQuestion.correctAnswer;
                            const showCorrect = isAnswered && isCorrect;
                            const showIncorrect = isAnswered && isSelected && !isCorrect;

                            return (
                                <button
                                    key={option}
                                    onClick={() => handleSelectAnswer(option)}
                                    disabled={isAnswered}
                                    className={`w-full p-4 rounded-xl border-2 text-left transition-all ${
                                        showCorrect
                                            ? "border-emerald-500 bg-emerald-500/10"
                                            : showIncorrect
                                            ? "border-rose-500 bg-rose-500/10"
                                            : isSelected
                                            ? "border-violet-500 bg-violet-500/10"
                                            : "border-[var(--border)] hover:border-violet-500/50 hover:bg-[var(--surface-hover)]"
                                    }`}
                                >
                                    <div className="flex items-center gap-3">
                                        <div
                                            className={`w-6 h-6 rounded-full border-2 flex items-center justify-center ${
                                                showCorrect
                                                    ? "border-emerald-500 bg-emerald-500"
                                                    : showIncorrect
                                                    ? "border-rose-500 bg-rose-500"
                                                    : isSelected
                                                    ? "border-violet-500 bg-violet-500"
                                                    : "border-[var(--border)]"
                                            }`}
                                        >
                                            {showCorrect && <CheckCircle2 className="w-4 h-4 text-white" />}
                                            {showIncorrect && <XCircle className="w-4 h-4 text-white" />}
                                        </div>
                                        <span className="text-sm text-[var(--text-primary)]">{option}</span>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    {/* Explanation */}
                    {isAnswered && currentQuestion.explanation && (
                        <div className="mt-6 p-4 rounded-xl bg-blue-500/10 border border-blue-500/20">
                            <div className="flex items-start gap-2">
                                <HelpCircle className="w-4 h-4 text-blue-500 mt-0.5" />
                                <div>
                                    <p className="text-xs font-medium text-blue-600 mb-1">Explanation</p>
                                    <p className="text-sm text-[var(--text-secondary)]">{currentQuestion.explanation}</p>
                                </div>
                            </div>
                        </div>
                    )}
                </div>
            </div>

            {/* Footer */}
            <div className="px-6 py-4 border-t border-[var(--border)]">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4 text-sm">
                        {isAnswered && (
                            <span className={answers[currentQuestion.id]?.correct ? "text-emerald-600" : "text-rose-600"}>
                                {answers[currentQuestion.id]?.correct ? "Correct!" : "Incorrect"}
                            </span>
                        )}
                    </div>
                    <button
                        onClick={handleNext}
                        disabled={!isAnswered}
                        className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-gradient-to-r from-violet-500 to-purple-600 text-white font-medium disabled:opacity-50 disabled:cursor-not-allowed hover:shadow-lg transition-all"
                    >
                        {currentIndex === questions.length - 1 ? "Finish" : "Next"}
                        <ChevronRight className="w-4 h-4" />
                    </button>
                </div>
            </div>
        </div>
    );
}
