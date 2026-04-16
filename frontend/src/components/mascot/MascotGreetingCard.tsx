"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import Image from "next/image";
import { ArrowRight } from "lucide-react";

import { api } from "@/lib/api";

type GreetingData = {
    greeting: string;
    chips: string[];
    has_urgent: boolean;
};

export function MascotGreetingCard({ role }: { role: string }) {
    const [data, setData] = useState<GreetingData | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        api.mascot
            .greeting()
            .then((res) => setData(res as GreetingData))
            .catch(() => {
                /* silently render nothing on error */
            })
            .finally(() => setLoading(false));
    }, []);

    if (!loading && data === null) return null;

    const assistantHref = `/${role}/assistant`;

    return (
        <div
            className="rounded-2xl border border-cyan-500/30 bg-gradient-to-br from-slate-900/60 to-slate-800/40 p-4 flex items-start gap-4"
            style={{ boxShadow: "0 0 20px rgba(0, 212, 255, 0.08)" }}
        >
            {/* Owl avatar */}
            <div className="flex-shrink-0 w-12 h-12 flex items-center justify-center">
                <Image
                    src="/images/mascot-owl-bg.png"
                    alt="VidyaOS Mascot"
                    width={48}
                    height={48}
                    className="object-contain drop-shadow-lg"
                    style={{ filter: "drop-shadow(0 0 8px rgba(0, 212, 255, 0.4))" }}
                />
            </div>

            {/* Content */}
            <div className="flex-1 min-w-0">
                {loading ? (
                    <div className="space-y-2">
                        <div className="h-4 w-3/4 rounded-full bg-[var(--bg-card)] animate-pulse" />
                        <div className="h-3 w-1/2 rounded-full bg-[var(--bg-card)] animate-pulse" />
                    </div>
                ) : (
                    <>
                        <p className="text-sm text-[var(--text-primary)] leading-snug mb-3">
                            {data?.greeting}
                        </p>
                        <div className="flex flex-wrap items-center gap-2">
                            {data?.chips.map((chip) => (
                                <Link
                                    key={chip}
                                    href={`${assistantHref}?q=${encodeURIComponent(chip)}`}
                                    className="rounded-full border border-cyan-500/30 bg-cyan-500/5 px-3 py-1 text-xs text-cyan-300 hover:bg-cyan-500/10 transition-colors"
                                >
                                    {chip}
                                </Link>
                            ))}
                            <Link
                                href={assistantHref}
                                className="ml-auto flex items-center gap-1 text-xs text-cyan-400 hover:text-cyan-300 transition-colors"
                            >
                                Open assistant
                                <ArrowRight className="h-3 w-3" />
                            </Link>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}
