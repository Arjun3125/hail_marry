"use client";

import useEmblaCarousel from "embla-carousel-react";
import { motion } from "framer-motion";
import { 
    ChevronLeft, 
    ChevronRight, 
    Layers3, 
    CheckCircle2, 
    XCircle, 
    RotateCcw, 
    Trophy,
    GraduationCap,
    Sparkles
} from "lucide-react";
import { useEffect, useState, useCallback } from "react";
import { useLanguage } from "@/i18n/LanguageProvider";
import { Skeleton } from "boneyard-js/react";
import { useTelemetry } from "@/hooks/useTelemetry";

export interface FlashcardState {
    selectedIndex: number;
    flippedIndex: number | null;
    mastery: Record<number, boolean>;
}

type Flashcard = { front: string; back: string };

interface FlashcardDeckProps {
    cards: Flashcard[];
    initialState?: FlashcardState;
    onStateChange?: (state: FlashcardState) => void;
    isLoading?: boolean;
}

export function FlashcardDeck({ cards, initialState, onStateChange, isLoading = false }: FlashcardDeckProps) {
    const { t } = useLanguage();
    const [emblaRef, emblaApi] = useEmblaCarousel({ loop: false, align: "center", skipSnaps: false });
    const [selectedIndex, setSelectedIndex] = useState(initialState?.selectedIndex ?? 0);
    const [flippedIndex, setFlippedIndex] = useState<number | null>(initialState?.flippedIndex ?? null);
    const [mastery, setMastery] = useState<Record<number, boolean>>(initialState?.mastery ?? {});
    const [struggleCount, setStruggleCount] = useState<Record<number, number>>({});
    const { record } = useTelemetry();

    // Sync state to parent
    useEffect(() => {
        onStateChange?.({
            selectedIndex,
            flippedIndex,
            mastery
        });
    }, [selectedIndex, flippedIndex, mastery, onStateChange]);

    const onSelect = useCallback(() => {
        if (!emblaApi) return;
        setSelectedIndex(emblaApi.selectedScrollSnap());
        setFlippedIndex(null);
    }, [emblaApi]);

    useEffect(() => {
        if (!emblaApi) return;
        queueMicrotask(() => onSelect());
        emblaApi.on("select", onSelect);
        return () => {
            emblaApi.off("select", onSelect);
        };
    }, [emblaApi, onSelect]);

    const handleFlip = useCallback(() => {
        setFlippedIndex(prev => prev === selectedIndex ? null : selectedIndex);
    }, [selectedIndex]);

    const handleMastery = useCallback((index: number, known: boolean) => {
        const nextMastery = { ...mastery, [index]: known };
        setMastery(nextMastery);
        
        if (!known) {
            setStruggleCount(prev => ({
                ...prev,
                [index]: (prev[index] || 0) + 1
            }));
        }

        // Record telemetry
        record({
            eventName: "flashcard_mastered",
            eventFamily: "educational",
            surface: "ai_studio",
            metadata: {
                topic: "General",
                cardIndex: index,
                rating: known ? 5 : 2,
                struggles: struggleCount[index] || 0
            },
        });

        // Auto-advance if known and not last card
        if (known && index < cards.length - 1) {
            setTimeout(() => {
                emblaApi?.scrollNext();
            }, 400);
        }
    }, [mastery, cards.length, emblaApi, record, struggleCount]);

    const resetDeck = () => {
        setMastery({});
        setSelectedIndex(0);
        setFlippedIndex(null);
        emblaApi?.scrollTo(0);
    };

    // Keyboard Shortcuts
    useEffect(() => {
        const handleKeyDown = (e: KeyboardEvent) => {
            if (e.code === "Space" || e.code === "Enter") {
                e.preventDefault();
                handleFlip();
            } else if (e.code === "ArrowRight") {
                emblaApi?.scrollNext();
            } else if (e.code === "ArrowLeft") {
                emblaApi?.scrollPrev();
            } else if (flippedIndex === selectedIndex) {
                if (e.key === "1") handleMastery(selectedIndex, false);
                if (e.key === "2") handleMastery(selectedIndex, true);
            }
        };

        window.addEventListener("keydown", handleKeyDown);
        return () => window.removeEventListener("keydown", handleKeyDown);
    }, [handleFlip, flippedIndex, selectedIndex, emblaApi, handleMastery]);

    const knownCount = Object.values(mastery).filter(Boolean).length;
    const progress = (Object.keys(mastery).length / cards.length) * 100;
    const masteryRate = Math.round((knownCount / cards.length) * 100);

    return (
        <Skeleton name="flashcard-deck" loading={isLoading}>
            <div className="flex flex-col gap-6 rounded-[2.5rem] border border-[var(--border)] bg-[rgba(15,23,42,0.3)] p-6 backdrop-blur-xl">
            {/* Header / Mastery Progress */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="flex h-10 w-10 items-center justify-center rounded-2xl bg-amber-500/10 text-amber-500 shadow-inner">
                        <Layers3 className="h-5 w-5" />
                    </div>
                    <div>
                        <h3 className="text-sm font-bold text-[var(--text-primary)]">{t("ai_studio.flashcards.title")}</h3>
                        <div className="flex items-center gap-2">
                            <div className="h-1.5 w-24 overflow-hidden rounded-full bg-white/5">
                                <motion.div 
                                    initial={{ width: 0 }}
                                    animate={{ width: `${progress}%` }}
                                    className="h-full bg-amber-500"
                                />
                            </div>
                            <span className="text-[10px] uppercase tracking-widest text-[var(--text-muted)]" aria-live="polite">
                                {t("ai_studio.flashcards.progress").replace("{current}", String(Object.keys(mastery).length)).replace("{total}", String(cards.length))}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="text-right">
                    <p className="text-[10px] font-semibold uppercase tracking-tighter text-[var(--text-muted)]">{t("ai_studio.flashcards.mastery")}</p>
                    <p className="text-lg font-black text-emerald-400">{masteryRate}%</p>
                </div>
            </div>

            {/* Carousel Area */}
            <div className="relative">
                <div className="overflow-hidden" ref={emblaRef}>
                    <div className="flex">
                        {cards.map((card, index) => {
                            const flipped = flippedIndex === index;
                            const isKnown = mastery[index] === true;
                            const isLearning = mastery[index] === false;

                            return (
                                <div key={`${card.front}-${index}`} className="min-w-0 flex-[0_0_100%] px-2">
                                    <div className="perspective-[1500px]">
                                        <motion.div
                                            onClick={() => setFlippedIndex(flipped ? null : index)}
                                            animate={{ 
                                                rotateY: flipped ? 180 : 0,
                                                scale: selectedIndex === index ? 1 : 0.95,
                                                opacity: selectedIndex === index ? 1 : 0.4
                                            }}
                                            transition={{ duration: 0.6, type: "spring", stiffness: 260, damping: 20 }}
                                            className="relative cursor-pointer"
                                            style={{ transformStyle: "preserve-3d", height: "320px" }}
                                            role="button"
                                            aria-label={`Flashcard ${index + 1}: ${flipped ? 'Answer' : 'Question'}`}
                                            aria-pressed={flipped}
                                        >
                                            {/* Front Side */}
                                            <div
                                                className="absolute inset-0 flex flex-col rounded-[2.5rem] border border-white/10 bg-gradient-to-br from-indigo-500/20 to-indigo-600/5 p-8 shadow-2xl backdrop-blur-md"
                                                style={{ backfaceVisibility: "hidden" }}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[10px] font-bold uppercase tracking-[0.4em] text-indigo-400/80">{t("ai_studio.quiz.question")}</span>
                                                    {isKnown && <CheckCircle2 className="h-4 w-4 text-emerald-400" />}
                                                    {isLearning && <XCircle className="h-4 w-4 text-amber-400" />}
                                                </div>
                                                <div className="flex flex-1 items-center justify-center text-center">
                                                    <p className="text-xl font-bold leading-relaxed text-[var(--text-primary)]">
                                                        {card.front}
                                                    </p>
                                                </div>
                                                <div className="text-center text-[10px] font-medium text-[var(--text-muted)]">
                                                    {t("ai_studio.flashcards.flip")}
                                                </div>
                                            </div>

                                            {/* Back Side */}
                                            <div
                                                className="absolute inset-0 flex flex-col rounded-[2.5rem] border border-emerald-500/20 bg-gradient-to-br from-emerald-500/10 to-teal-600/5 p-8 shadow-2xl backdrop-blur-md"
                                                style={{ transform: "rotateY(180deg)", backfaceVisibility: "hidden" }}
                                            >
                                                <div className="flex items-center justify-between">
                                                    <span className="text-[10px] font-bold uppercase tracking-[0.4em] text-emerald-400/80">{t("ai_studio.quiz.explanation")}</span>
                                                    <GraduationCap className="h-4 w-4 text-emerald-400" />
                                                </div>
                                                <div className="flex flex-1 items-center justify-center overflow-y-auto py-4 text-center">
                                                    <p className="text-base font-medium leading-loose text-emerald-50">
                                                        {card.back}
                                                    </p>
                                                </div>
                                                
                                                {/* Self-Assessment Buttons */}
                                                <div className="flex flex-col gap-2 pt-4" onClick={(e) => e.stopPropagation()}>
                                                    {(struggleCount[index] || 0) >= 3 && (
                                                        <motion.button
                                                            initial={{ opacity: 0, scale: 0.9 }}
                                                            animate={{ opacity: 1, scale: 1 }}
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                const prompt = `I'm struggling with this card: "${card.front}". Can you explain it simply?`;
                                                                window.dispatchEvent(new CustomEvent('mascot-hint', { detail: { prompt } }));
                                                            }}
                                                            className="flex w-full items-center justify-center gap-2 rounded-xl bg-indigo-600/90 py-2.5 text-[10px] font-bold uppercase text-white shadow-xl transition-all hover:bg-indigo-500 hover:scale-[1.02] active:scale-[0.98]"
                                                        >
                                                            <Sparkles className="h-3.5 w-3.5" /> 
                                                            {t("ai_studio.tools.flashcards.get_hint") || "Get an AI Hint"}
                                                        </motion.button>
                                                    )}
                                                    <div className="flex gap-2 w-full">
                                                        <button
                                                            onClick={() => handleMastery(index, false)}
                                                            className={`flex-1 flex items-center justify-center gap-2 rounded-2xl py-2.5 text-[10px] font-bold uppercase transition-all ${
                                                                isLearning ? "bg-amber-500 text-white shadow-lg" : "bg-white/5 text-amber-200/60 hover:bg-white/10"
                                                            }`}
                                                        >
                                                            <RotateCcw className="h-3 w-3" /> {t("ai_studio.flashcards.still_learning")} (1)
                                                        </button>
                                                        <button
                                                            onClick={() => handleMastery(index, true)}
                                                            className={`flex-1 flex items-center justify-center gap-2 rounded-2xl py-2.5 text-[10px] font-bold uppercase transition-all ${
                                                                isKnown ? "bg-emerald-500 text-white shadow-lg" : "bg-white/5 text-emerald-200/60 hover:bg-white/10"
                                                            }`}
                                                        >
                                                            <Trophy className="h-3 w-3" /> {t("ai_studio.flashcards.know_it")} (2)
                                                        </button>
                                                    </div>
                                                </div>
                                            </div>
                                        </motion.div>
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </div>

                {/* Navigation arrows overlay */}
                <button
                    onClick={() => emblaApi?.scrollPrev()}
                    className="absolute -left-4 top-1/2 -translate-y-1/2 rounded-full border border-white/10 bg-black/40 p-2 text-white/50 transition hover:bg-black/60 hover:text-white"
                    aria-label="Previous card"
                >
                    <ChevronLeft className="h-5 w-5" />
                </button>
                <button
                    onClick={() => emblaApi?.scrollNext()}
                    className="absolute -right-4 top-1/2 -translate-y-1/2 rounded-full border border-white/10 bg-black/40 p-2 text-white/50 transition hover:bg-black/60 hover:text-white"
                    aria-label="Next card"
                >
                    <ChevronRight className="h-5 w-5" />
                </button>
            </div>

            {/* Footer controls */}
            <div className="flex items-center justify-between border-t border-white/5 pt-4">
                <div className="text-[10px] font-semibold uppercase tracking-widest text-[var(--text-muted)]">
                    {t("ai_studio.quiz.question")} {selectedIndex + 1} of {cards.length}
                </div>
                <button
                    onClick={resetDeck}
                    className="flex items-center gap-2 text-[10px] font-bold uppercase text-indigo-400 transition hover:text-indigo-300"
                >
                    <RotateCcw className="h-3 w-3" /> {t("ai_studio.flashcards.reset")}
                </button>
            </div>
            </div>
        </Skeleton>
    );
}
