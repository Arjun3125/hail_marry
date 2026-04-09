import { Award, CalendarCheck, TrendingUp, Zap } from "lucide-react";

export function GamificationHero({
    streak,
    attendance,
    marks,
}: {
    streak: number;
    attendance: number;
    marks: number;
}) {
    return (
        <div className="relative overflow-hidden rounded-3xl border border-[var(--border)] bg-[linear-gradient(145deg,rgba(18,28,47,0.95),rgba(10,16,30,0.96))] p-8 shadow-[0_20px_48px_rgba(2,6,23,0.4)]">
            <div className="pointer-events-none absolute -right-16 -top-20 h-56 w-56 rounded-full bg-[rgba(129,140,248,0.16)] blur-[72px]" />
            <div className="pointer-events-none absolute -bottom-20 -left-16 h-56 w-56 rounded-full bg-[rgba(59,130,246,0.14)] blur-[72px]" />

            <div className="relative z-10 flex flex-col items-start justify-between gap-8 md:flex-row md:items-center">
                <div className="flex items-center gap-6">
                    <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-violet-500 to-indigo-500 text-white shadow-[0_12px_28px_rgba(99,102,241,0.45)]">
                        <Zap className="h-10 w-10 fill-current text-yellow-300" />
                        <div className="absolute -right-2 -top-2 flex h-8 w-8 items-center justify-center rounded-full border-2 border-[var(--bg-card)] bg-yellow-400 text-sm font-bold text-yellow-900">
                            <Award className="h-4 w-4" />
                        </div>
                    </div>
                    <div>
                        <h2 className="font-inter text-sm font-semibold uppercase tracking-wider text-[var(--text-muted)]">Current streak</h2>
                        <div className="mt-1 flex items-baseline gap-2">
                            <span className="font-manrope text-4xl font-extrabold text-[var(--text-primary)]">{streak}</span>
                            <span className="font-inter text-lg font-medium text-[var(--text-muted)]">days</span>
                        </div>
                        <p className="mt-1 text-sm font-medium text-indigo-300">Momentum is active. Keep this streak alive.</p>
                    </div>
                </div>

                <div className="flex gap-8 border-l border-[var(--border)] pl-8">
                    <div>
                        <div className="mb-1 flex items-center gap-2 text-[var(--text-muted)]">
                            <CalendarCheck className="h-4 w-4 text-violet-400" />
                            <span className="font-inter text-sm font-medium">Attendance</span>
                        </div>
                        <div className="font-manrope text-3xl font-bold text-[var(--text-primary)]">{attendance}%</div>
                    </div>
                    <div>
                        <div className="mb-1 flex items-center gap-2 text-[var(--text-muted)]">
                            <TrendingUp className="h-4 w-4 text-indigo-400" />
                            <span className="font-inter text-sm font-medium">Avg marks</span>
                        </div>
                        <div className="font-manrope text-3xl font-bold text-[var(--text-primary)]">{marks}%</div>
                    </div>
                </div>
            </div>
        </div>
    );
}
