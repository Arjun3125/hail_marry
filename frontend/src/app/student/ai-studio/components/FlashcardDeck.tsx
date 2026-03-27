"use client";

import { useState, useCallback, useEffect } from "react";
import { ChevronLeft, ChevronRight, RotateCw, Shuffle, Bookmark, CheckCircle2, XCircle } from "lucide-react";

interface Flashcard {
    id: string;
    front: string;
    back: string;
    tags?: string[];
}

interface FlashcardDeckProps {
    cards: Flashcard[];
    title?: string;
    onComplete?: (stats: DeckStats) => void;
    onSave?: (cardId: string) => void;
}

interface DeckStats {
    totalCards: number;
    reviewedCards: number;
    flippedCards: number;
    timeSpent: number;
}

export function FlashcardDeck({ cards, title = "Flashcard Deck", onComplete, onSave }: FlashcardDeckProps) {
    const [currentIndex, setCurrentIndex] = useState(0);
    const [isFlipped, setIsFlipped] = useState(false);
    const [swipeDirection, setSwipeDirection] = useState<"left" | "right" | null>(null);
    const [knownCards, setKnownCards] = useState<Set<string>>(new Set());
    const [unknownCards, setUnknownCards] = useState<Set<string>>(new Set());
    const [startTime] = useState(() => Date.now());
    const [flipCount, setFlipCount] = useState(0);
    const [elapsedTime, setElapsedTime] = useState(0);

    // Update elapsed time every second
    useEffect(() => {
        const interval = setInterval(() => {
            setElapsedTime(Math.floor((Date.now() - startTime) / 1000));
        }, 1000);
        return () => clearInterval(interval);
    }, [startTime]);

    const currentCard = cards[currentIndex];
    const progress = ((currentIndex + 1) / cards.length) * 100;

    const handleNext = useCallback(() => {
        if (currentIndex < cards.length - 1) {
            setCurrentIndex((prev) => prev + 1);
            setIsFlipped(false);
            setSwipeDirection(null);
        } else {
            // Complete deck
            const stats: DeckStats = {
                totalCards: cards.length,
                reviewedCards: currentIndex + 1,
                flippedCards: flipCount,
                timeSpent: Math.floor((Date.now() - startTime) / 1000),
            };
            onComplete?.(stats);
        }
    }, [currentIndex, cards.length, flipCount, startTime, onComplete]);

    const handlePrevious = useCallback(() => {
        if (currentIndex > 0) {
            setCurrentIndex((prev) => prev - 1);
            setIsFlipped(false);
            setSwipeDirection(null);
        }
    }, [currentIndex]);

    const handleFlip = useCallback(() => {
        setIsFlipped((prev) => !prev);
        if (!isFlipped) {
            setFlipCount((prev) => prev + 1);
        }
    }, [isFlipped]);

    const handleMarkKnown = useCallback(() => {
        if (currentCard) {
            setKnownCards((prev) => new Set([...prev, currentCard.id]));
            setSwipeDirection("right");
            setTimeout(handleNext, 300);
        }
    }, [currentCard, handleNext]);

    const handleMarkUnknown = useCallback(() => {
        if (currentCard) {
            setUnknownCards((prev) => new Set([...prev, currentCard.id]));
            setSwipeDirection("left");
            setTimeout(handleNext, 300);
        }
    }, [currentCard, handleNext]);

    // Keyboard shortcuts
    const handleKeyDown = useCallback(
        (e: React.KeyboardEvent) => {
            switch (e.key) {
                case "ArrowRight":
                case " ":
                    e.preventDefault();
                    handleNext();
                    break;
                case "ArrowLeft":
                    e.preventDefault();
                    handlePrevious();
                    break;
                case "ArrowUp":
                case "ArrowDown":
                case "f":
                    e.preventDefault();
                    handleFlip();
                    break;
                case "k":
                    e.preventDefault();
                    handleMarkKnown();
                    break;
                case "u":
                    e.preventDefault();
                    handleMarkUnknown();
                    break;
            }
        },
        [handleNext, handlePrevious, handleFlip, handleMarkKnown, handleMarkUnknown]
    );

    if (!currentCard) {
        return (
            <div className="flex flex-col items-center justify-center h-full p-8 text-center">
                <div className="w-16 h-16 rounded-full bg-gradient-to-br from-emerald-500 to-green-600 flex items-center justify-center mb-4">
                    <CheckCircle2 className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-[var(--text-primary)] mb-2">Deck Complete!</h3>
                <p className="text-sm text-[var(--text-muted)] mb-4">
                    You reviewed {cards.length} cards in {elapsedTime} seconds
                </p>
                <div className="flex gap-4 text-sm">
                    <span className="flex items-center gap-1 text-emerald-600">
                        <CheckCircle2 className="w-4 h-4" />
                        {knownCards.size} known
                    </span>
                    <span className="flex items-center gap-1 text-rose-600">
                        <XCircle className="w-4 h-4" />
                        Don&apos;t Know ({unknownCards.size}) to review
                    </span>
                </div>
            </div>
        );
    }

    return (
        <div
            className="flex flex-col h-full focus:outline-none"
            onKeyDown={handleKeyDown}
            tabIndex={0}
        >
            {/* Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-[var(--border)]">
                <div>
                    <h2 className="font-semibold text-[var(--text-primary)]">{title}</h2>
                    <p className="text-xs text-[var(--text-muted)]">
                        Card {currentIndex + 1} of {cards.length}
                    </p>
                </div>
                <div className="flex items-center gap-2">
                    <button
                        onClick={() => onSave?.(currentCard.id)}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Save card"
                    >
                        <Bookmark className="w-4 h-4" />
                    </button>
                    <button
                        onClick={() => {
                            // TODO: Implement shuffle - shuffle cards array
                        }}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] transition-colors"
                        title="Shuffle"
                    >
                        <Shuffle className="w-4 h-4" />
                    </button>
                </div>
            </div>

            {/* Progress Bar */}
            <div className="h-1 bg-[var(--border)]">
                <div
                    className="h-full bg-gradient-to-r from-emerald-500 to-green-600 transition-all duration-300"
                    style={{ width: `${progress}%` }}
                />
            </div>

            {/* Card Area */}
            <div className="flex-1 flex items-center justify-center p-8">
                <div
                    className={`relative w-full max-w-xl aspect-[3/2] cursor-pointer transition-transform duration-300 ${
                        swipeDirection === "left" ? "-translate-x-full opacity-0" : ""
                    } ${swipeDirection === "right" ? "translate-x-full opacity-0" : ""}`}
                    onClick={handleFlip}
                >
                    {/* Card Container */}
                    <div
                        className={`absolute inset-0 rounded-2xl shadow-xl transition-all duration-500 transform-gpu preserve-3d ${
                            isFlipped ? "rotate-y-180" : ""
                        }`}
                        style={{
                            transformStyle: "preserve-3d",
                            transform: isFlipped ? "rotateY(180deg)" : "rotateY(0deg)",
                        }}
                    >
                        {/* Front */}
                        <div
                            className="absolute inset-0 backface-hidden rounded-2xl bg-gradient-to-br from-emerald-500 to-teal-600 p-8 flex flex-col items-center justify-center text-white"
                            style={{ backfaceVisibility: "hidden" }}
                        >
                            <span className="text-xs uppercase tracking-wider opacity-75 mb-4">Question</span>
                            <p className="text-xl font-medium text-center leading-relaxed">{currentCard.front}</p>
                            <p className="absolute bottom-6 text-xs opacity-60">Click or press F to flip</p>
                        </div>

                        {/* Back */}
                        <div
                            className="absolute inset-0 backface-hidden rounded-2xl bg-[var(--bg-card)] border border-[var(--border)] p-8 flex flex-col items-center justify-center text-[var(--text-primary)]"
                            style={{
                                backfaceVisibility: "hidden",
                                transform: "rotateY(180deg)",
                            }}
                        >
                            <span className="text-xs uppercase tracking-wider text-[var(--text-muted)] mb-4">
                                Answer
                            </span>
                            <p className="text-xl font-medium text-center leading-relaxed">{currentCard.back}</p>
                            {currentCard.tags && (
                                <div className="flex flex-wrap justify-center gap-2 mt-4">
                                    {currentCard.tags.map((tag) => (
                                        <span
                                            key={tag}
                                            className="px-2 py-1 text-[10px] bg-[var(--surface-hover)] text-[var(--text-muted)] rounded-full"
                                        >
                                            {tag}
                                        </span>
                                    ))}
                                </div>
                            )}
                        </div>
                    </div>
                </div>
            </div>

            {/* Controls */}
            <div className="px-6 py-4 border-t border-[var(--border)]">
                {/* Navigation */}
                <div className="flex items-center justify-between mb-4">
                    <button
                        onClick={handlePrevious}
                        disabled={currentIndex === 0}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] disabled:opacity-30 transition-colors"
                    >
                        <ChevronLeft className="w-5 h-5" />
                    </button>

                    <button
                        onClick={handleFlip}
                        className="flex items-center gap-2 px-4 py-2 rounded-lg bg-[var(--bg-page)] hover:bg-[var(--surface-hover)] text-[var(--text-secondary)] text-sm transition-colors border border-[var(--border)]"
                    >
                        <RotateCw className="w-4 h-4" />
                        Flip (F)
                    </button>

                    <button
                        onClick={handleNext}
                        disabled={currentIndex === cards.length - 1}
                        className="p-2 rounded-lg hover:bg-[var(--surface-hover)] text-[var(--text-muted)] disabled:opacity-30 transition-colors"
                    >
                        <ChevronRight className="w-5 h-5" />
                    </button>
                </div>

                {/* Self-Assessment */}
                <div className="flex gap-3">
                    <button
                        onClick={handleMarkUnknown}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-rose-500/10 hover:bg-rose-500/20 text-rose-600 transition-colors"
                    >
                        <XCircle className="w-4 h-4" />
                        <span className="text-sm font-medium">Don&apos;t Know (U)</span>
                    </button>
                    <button
                        onClick={handleMarkKnown}
                        className="flex-1 flex items-center justify-center gap-2 px-4 py-3 rounded-xl bg-emerald-500/10 hover:bg-emerald-500/20 text-emerald-600 transition-colors"
                    >
                        <CheckCircle2 className="w-4 h-4" />
                        <span className="text-sm font-medium">Know It (K)</span>
                    </button>
                </div>
            </div>

            {/* Keyboard Help */}
            <div className="px-6 py-2 text-center border-t border-[var(--border)] bg-[var(--surface-hover)]">
                <p className="text-[10px] text-[var(--text-muted)]">
                    ← → Navigate • F Flip • K Know • U Unknown • Space Next
                </p>
            </div>
        </div>
    );
}
