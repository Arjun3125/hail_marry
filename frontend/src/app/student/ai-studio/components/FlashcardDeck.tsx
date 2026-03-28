"use client";

import useEmblaCarousel from "embla-carousel-react";
import { motion } from "framer-motion";
import { ChevronLeft, ChevronRight, Layers3 } from "lucide-react";
import { useEffect, useState } from "react";

type Flashcard = { front: string; back: string };

export function FlashcardDeck({ cards }: { cards: Flashcard[] }) {
    const [emblaRef, emblaApi] = useEmblaCarousel({ loop: false, align: "center" });
    const [selectedIndex, setSelectedIndex] = useState(0);
    const [flippedIndex, setFlippedIndex] = useState<number | null>(null);

    useEffect(() => {
        if (!emblaApi) return;
        const onSelect = () => {
            setSelectedIndex(emblaApi.selectedScrollSnap());
            setFlippedIndex(null);
        };
        onSelect();
        emblaApi.on("select", onSelect);
        return () => {
            emblaApi.off("select", onSelect);
        };
    }, [emblaApi]);

    return (
        <div className="rounded-2xl border border-[var(--border)] bg-[var(--bg-page)] p-4">
            <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                    <div className="rounded-lg bg-amber-500/15 p-2 text-amber-400">
                        <Layers3 className="h-4 w-4" />
                    </div>
                    <div>
                        <p className="text-sm font-medium text-[var(--text-primary)]">Flashcard deck</p>
                        <p className="text-xs text-[var(--text-muted)]">Swipe or click through your revision set</p>
                    </div>
                </div>
                <div className="text-xs text-[var(--text-secondary)]">
                    Card {selectedIndex + 1} of {cards.length}
                </div>
            </div>

            <div className="overflow-hidden" ref={emblaRef}>
                <div className="flex">
                    {cards.map((card, index) => {
                        const flipped = flippedIndex === index;
                        return (
                            <div key={`${card.front}-${index}`} className="min-w-0 flex-[0_0_100%] px-1">
                                <button
                                    type="button"
                                    onClick={() => setFlippedIndex(flipped ? null : index)}
                                    className="block h-[260px] w-full perspective-[1200px] text-left"
                                >
                                    <motion.div
                                        animate={{ rotateY: flipped ? 180 : 0 }}
                                        transition={{ duration: 0.45 }}
                                        className="relative h-full w-full rounded-[28px] border border-[var(--border)]"
                                        style={{ transformStyle: "preserve-3d" }}
                                    >
                                        <div
                                            className="absolute inset-0 rounded-[28px] bg-gradient-to-br from-amber-500/25 to-orange-500/10 p-6"
                                            style={{ backfaceVisibility: "hidden" }}
                                        >
                                            <p className="text-[10px] uppercase tracking-[0.3em] text-[var(--text-muted)]">Front</p>
                                            <div className="mt-8 text-xl font-semibold text-[var(--text-primary)]">
                                                {card.front}
                                            </div>
                                        </div>
                                        <div
                                            className="absolute inset-0 rounded-[28px] bg-gradient-to-br from-indigo-500/20 to-cyan-500/10 p-6"
                                            style={{ transform: "rotateY(180deg)", backfaceVisibility: "hidden" }}
                                        >
                                            <p className="text-[10px] uppercase tracking-[0.3em] text-[var(--text-muted)]">Back</p>
                                            <div className="mt-8 text-base leading-7 text-[var(--text-primary)]">
                                                {card.back}
                                            </div>
                                        </div>
                                    </motion.div>
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>

            <div className="mt-4 flex items-center justify-between">
                <button
                    type="button"
                    onClick={() => emblaApi?.scrollPrev()}
                    disabled={!emblaApi?.canScrollPrev()}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-xs text-[var(--text-secondary)] transition disabled:opacity-40"
                >
                    <ChevronLeft className="h-3.5 w-3.5" />
                    Previous
                </button>
                <p className="text-xs text-[var(--text-muted)]">Click a card to flip it</p>
                <button
                    type="button"
                    onClick={() => emblaApi?.scrollNext()}
                    disabled={!emblaApi?.canScrollNext()}
                    className="inline-flex items-center gap-1.5 rounded-lg border border-[var(--border)] px-3 py-2 text-xs text-[var(--text-secondary)] transition disabled:opacity-40"
                >
                    Next
                    <ChevronRight className="h-3.5 w-3.5" />
                </button>
            </div>
        </div>
    );
}
