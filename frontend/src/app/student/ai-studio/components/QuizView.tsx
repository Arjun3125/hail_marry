import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { CheckCircle2, XCircle, ChevronRight, RotateCcw, Award, Brain } from "lucide-react";
import { useLanguage } from "@/i18n/LanguageProvider";
import { Skeleton } from "boneyard-js/react";
import { useTelemetry } from "@/hooks/useTelemetry";

type QuizQuestion = {
    question?: string;
    q?: string;
    options?: string[];
    correct?: string;
    answer?: string | number;
    explanation?: string;
};

export interface QuizState {
    currentIndex: number;
    selectedOption: number | null;
    isAnswered: boolean;
    score: number;
    showResults: boolean;
}

interface QuizViewProps {
    questions: QuizQuestion[];
    onComplete?: (score: number, total: number) => void;
    initialState?: QuizState;
    onStateChange?: (state: QuizState) => void;
    isLoading?: boolean;
}

export function QuizView({ questions, onComplete, initialState, onStateChange, isLoading = false }: QuizViewProps) {
    const { t } = useLanguage();
    const [currentIndex, setCurrentIndex] = useState(initialState?.currentIndex ?? 0);
    const [selectedOption, setSelectedOption] = useState<number | null>(initialState?.selectedOption ?? null);
    const [isAnswered, setIsAnswered] = useState(initialState?.isAnswered ?? false);
    const [score, setScore] = useState(initialState?.score ?? 0);
    const [showResults, setShowResults] = useState(initialState?.showResults ?? false);
    const { record } = useTelemetry();

    // Sync state to parent
    useEffect(() => {
        onStateChange?.({
            currentIndex,
            selectedOption,
            isAnswered,
            score,
            showResults
        });
    }, [currentIndex, selectedOption, isAnswered, score, showResults, onStateChange]);

    const question = questions[currentIndex];
    const questionText = question?.question || question?.q || "Untitled question";
    const options = question?.options || [];
    const correctAnswer = String(question?.correct ?? question?.answer ?? "");

    const handleOptionSelect = (index: number) => {
        if (isAnswered) return;
        setSelectedOption(index);
        setIsAnswered(true);

        const isCorrect = String(options[index]) === correctAnswer;
        if (isCorrect) {
            setScore(prev => prev + 1);
        }
    };

    const handleNext = () => {
        if (currentIndex < questions.length - 1) {
            setCurrentIndex(prev => prev + 1);
            setSelectedOption(null);
            setIsAnswered(false);
        } else {
            setShowResults(true);
            onComplete?.(score, questions.length);
            
            // Record telemetry
            record({
                eventName: "quiz_completed",
                eventFamily: "educational",
                surface: "ai_studio",
                metadata: {
                    topic: "General", // Topic context could be improved in future sprints
                    score: score,
                    total: questions.length,
                },
            });
        }
    };

    const handleRestart = () => {
        setCurrentIndex(0);
        setSelectedOption(null);
        setIsAnswered(false);
        setScore(0);
        setShowResults(false);
    };

    if (showResults) {
        const percentage = Math.round((score / questions.length) * 100);
        return (
            <motion.div 
                initial={{ opacity: 0, scale: 0.95 }}
                animate={{ opacity: 1, scale: 1 }}
                className="rounded-3xl border border-[var(--border)] bg-[rgba(15,23,42,0.6)] p-8 text-center backdrop-blur-md"
            >
                <div className="mx-auto mb-6 flex h-20 w-20 items-center justify-center rounded-3xl bg-gradient-to-br from-indigo-500/20 to-violet-600/20 shadow-xl">
                    <Award className="h-10 w-10 text-indigo-400" />
                </div>
                <h3 className="mb-2 text-2xl font-bold text-[var(--text-primary)]">{t("ai_studio.quiz.results")}</h3>
                <p className="mb-6 text-[var(--text-muted)]">{t("student.performance")}</p>
                
                <div className="mb-8 grid grid-cols-2 gap-4">
                    <div className="rounded-2xl border border-[var(--border)] bg-black/20 p-4">
                        <p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">{t("ai_studio.quiz.score")}</p>
                        <p className="text-2xl font-bold text-indigo-400">{score} / {questions.length}</p>
                    </div>
                    <div className="rounded-2xl border border-[var(--border)] bg-black/20 p-4">
                        <p className="text-xs uppercase tracking-widest text-[var(--text-muted)]">{t("ai_studio.quiz.accuracy")}</p>
                        <p className="text-2xl font-bold text-emerald-400">{percentage}%</p>
                    </div>
                </div>

                <div className="flex flex-col items-stretch gap-3">
                    <button
                        onClick={handleRestart}
                        className="flex items-center justify-center gap-2 rounded-2xl bg-indigo-500 px-6 py-3.5 font-semibold text-white transition hover:bg-indigo-600 hover:shadow-lg active:scale-[0.98]"
                    >
                        <RotateCcw className="h-4 w-4" />
                        {t("ai_studio.quiz.retake")}
                    </button>
                    <p className="text-[10px] text-[var(--text-muted)]">{t("student.ai_assistant")}</p>
                </div>
            </motion.div>
        );
    }

    return (
        <Skeleton name="quiz-view" loading={isLoading}>
            <div className="rounded-3xl border border-[var(--border)] bg-[rgba(15,23,42,0.4)] backdrop-blur-sm">
            {/* Header / Progress */}
            <div className="flex items-center justify-between border-b border-[var(--border)] px-6 py-4">
                <div className="flex items-center gap-2">
                    <Brain className="h-4 w-4 text-indigo-400" />
                    <span className="text-xs font-semibold uppercase tracking-widest text-[var(--text-muted)]">{t("ai_studio.title")}</span>
                </div>
                <span className="text-xs font-medium text-[var(--text-secondary)]">
                    {t("ai_studio.quiz.question")} {currentIndex + 1} / {questions.length}
                </span>
            </div>

            {/* Content */}
            <div className="p-6">
                <AnimatePresence mode="wait">
                    <motion.div
                        key={currentIndex}
                        initial={{ opacity: 0, x: 20 }}
                        animate={{ opacity: 1, x: 0 }}
                        exit={{ opacity: 0, x: -20 }}
                        transition={{ duration: 0.3 }}
                        className="space-y-6"
                    >
                        <h4 className="text-lg font-medium leading-8 text-[var(--text-primary)]">
                            {questionText}
                        </h4>

                        <div className="grid gap-3" role="radiogroup">
                            {options.map((option, index) => {
                                const optionText = String(option);
                                const isCorrect = optionText === correctAnswer;
                                const isSelected = selectedOption === index;
                                
                                let stateStyles = "border-[var(--border)] bg-black/10 hover:border-indigo-500/50 hover:bg-indigo-500/5";
                                if (isAnswered) {
                                    if (isCorrect) {
                                        stateStyles = "border-emerald-500/50 bg-emerald-500/10 text-emerald-100 ring-1 ring-emerald-500/30";
                                    } else if (isSelected) {
                                        stateStyles = "border-red-500/50 bg-red-500/10 text-red-100 ring-1 ring-red-500/30";
                                    } else {
                                        stateStyles = "border-[var(--border)] bg-black/5 opacity-50";
                                    }
                                }

                                return (
                                    <button
                                        key={`${currentIndex}-${index}`}
                                        onClick={() => handleOptionSelect(index)}
                                        disabled={isAnswered}
                                        role="radio"
                                        aria-checked={isSelected}
                                        className={`group relative flex items-center gap-4 rounded-2xl border px-5 py-4 text-left text-sm transition-all ${stateStyles}`}
                                    >
                                        <div className={`flex h-6 w-6 shrink-0 items-center justify-center rounded-full border text-[10px] font-bold ${
                                            isAnswered && isCorrect ? "border-emerald-500 bg-emerald-500 text-white" : 
                                            isAnswered && isSelected && !isCorrect ? "border-red-500 bg-red-500 text-white" :
                                            "border-[var(--border)] group-hover:border-indigo-500"
                                        }`}>
                                            {isAnswered && isCorrect ? <CheckCircle2 className="h-3.5 w-3.5" /> : 
                                             isAnswered && isSelected && !isCorrect ? <XCircle className="h-3.5 w-3.5" /> : 
                                             String.fromCharCode(65 + index)}
                                        </div>
                                        <span className="flex-1">{optionText}</span>
                                    </button>
                                );
                            })}
                        </div>

                        {isAnswered && question.explanation && (
                            <motion.div 
                                initial={{ opacity: 0, height: 0 }}
                                animate={{ opacity: 1, height: "auto" }}
                                className="rounded-2xl border border-indigo-500/20 bg-indigo-500/5 p-4 text-xs italic text-indigo-200/80"
                            >
                                <p className="mb-1 font-semibold uppercase tracking-wider text-indigo-400/80">{t("ai_studio.quiz.explanation")}</p>
                                {question.explanation}
                            </motion.div>
                        )}
                    </motion.div>
                </AnimatePresence>
            </div>

            {/* Footer */}
            <div className="flex items-center justify-end border-t border-[var(--border)] px-6 py-4">
                <button
                    onClick={handleNext}
                    disabled={!isAnswered}
                    className="flex items-center gap-2 rounded-xl bg-white px-5 py-2.5 text-xs font-bold text-black transition hover:bg-white/90 disabled:cursor-not-allowed disabled:opacity-30"
                >
                    {currentIndex < questions.length - 1 ? t("ai_studio.quiz.next") : t("ai_studio.quiz.results")}
                    <ChevronRight className="h-3.5 w-3.5" />
                </button>
            </div>
            </div>
        </Skeleton>
    );
}
