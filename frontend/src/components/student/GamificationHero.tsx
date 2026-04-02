import React from "react";
import { Award, Zap, TrendingUp, CalendarCheck } from "lucide-react";

export function GamificationHero({ streak, attendance, marks }: { streak: number; attendance: number; marks: number }) {
  return (
    <div className="relative overflow-hidden rounded-2xl bg-white/40 p-8 shadow-[0_8px_32px_rgba(37,0,90,0.06)] backdrop-blur-xl border-none">
      {/* Background Gradient Orbs */}
      <div className="absolute -top-24 -right-24 w-64 h-64 rounded-full bg-violet-500/20 blur-[80px]" />
      <div className="absolute -bottom-24 -left-24 w-64 h-64 rounded-full bg-indigo-500/20 blur-[80px]" />

      <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-8">
        
        {/* Streak Section */}
        <div className="flex items-center gap-6">
          <div className="relative flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-violet-600 to-indigo-600 text-white shadow-lg shadow-violet-500/30">
            <Zap className="h-10 w-10 fill-current text-yellow-300" />
            <div className="absolute -top-2 -right-2 flex h-8 w-8 items-center justify-center rounded-full bg-yellow-400 text-sm font-bold text-yellow-900 border-2 border-white">
              <Award className="h-4 w-4" />
            </div>
          </div>
          <div>
            <h2 className="text-sm font-semibold uppercase tracking-wider text-slate-500 font-inter">Current Streak</h2>
            <div className="mt-1 flex items-baseline gap-2">
              <span className="text-4xl font-extrabold text-slate-800 font-manrope">{streak}</span>
              <span className="text-lg font-medium text-slate-500 font-inter">Days</span>
            </div>
            <p className="text-sm text-indigo-600 font-medium mt-1">You're unstoppable! 🔥</p>
          </div>
        </div>

        {/* KPIs Section */}
        <div className="flex gap-8 border-l border-slate-200/50 pl-8">
          <div>
            <div className="flex items-center gap-2 text-slate-500 mb-1">
              <CalendarCheck className="h-4 w-4 text-violet-500" />
              <span className="text-sm font-medium font-inter">Attendance</span>
            </div>
            <div className="text-3xl font-bold text-slate-800 font-manrope">{attendance}%</div>
          </div>
          <div>
            <div className="flex items-center gap-2 text-slate-500 mb-1">
              <TrendingUp className="h-4 w-4 text-indigo-500" />
              <span className="text-sm font-medium font-inter">Avg Marks</span>
            </div>
            <div className="text-3xl font-bold text-slate-800 font-manrope">{marks}%</div>
          </div>
        </div>

      </div>
    </div>
  );
}
