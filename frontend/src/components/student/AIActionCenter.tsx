import React from "react";
import { Sparkles, ArrowRight, Target, BrainCircuit } from "lucide-react";

export function AIActionCenter({ recommendations, weakTopics }: { recommendations: string[], weakTopics: string[] }) {
  const mainRec = recommendations.length > 0 ? recommendations[0] : "Explore new study paths";
  const topics = weakTopics.slice(0, 2);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-white/60 p-6 shadow-[0_4px_24px_rgba(0,0,0,0.04)] backdrop-blur-md border-none group transition-all duration-300 hover:shadow-[0_8px_32px_rgba(99,14,212,0.1)]">
        
      <div className="flex justify-between items-start mb-6">
        <div className="flex items-center gap-3">
          <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-100 text-violet-600">
            <BrainCircuit className="h-6 w-6" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-slate-800 font-manrope">Study Path Wizard</h3>
            <p className="text-sm text-slate-500 font-inter">Your AI Mentor</p>
          </div>
        </div>
        <div className="flex h-8 items-center gap-1.5 rounded-full bg-green-50 px-3 text-xs font-semibold text-green-700">
          <span className="relative flex h-2 w-2">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-green-400 opacity-75"></span>
            <span className="relative inline-flex h-2 w-2 rounded-full bg-green-500"></span>
          </span>
          Online
        </div>
      </div>

      <div className="mb-6 rounded-xl bg-gradient-to-br from-surface to-surface-low p-4 pr-12 shadow-inner border-l-4 border-violet-500">
        <div className="flex items-start gap-3">
            <Sparkles className="h-5 w-5 text-violet-500 mt-0.5 shrink-0" />
            <p className="text-slate-700 font-medium font-inter text-sm leading-relaxed">
            {`I've analyzed your recent tests. ${mainRec.replace("Recommended: ", "")}.`}
            </p>
        </div>
      </div>

      <div className="mb-8">
        <div className="flex items-center gap-2 mb-3">
            <Target className="h-4 w-4 text-slate-400" />
            <span className="text-xs font-semibold uppercase tracking-wider text-slate-500 font-inter">Upcoming Quests</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {topics.map((topic, i) => (
            <div key={i} className="flex items-center gap-2 rounded-lg bg-white px-3 py-2 text-sm font-medium text-slate-700 shadow-sm transition-colors hover:bg-violet-50 hover:text-violet-700 cursor-pointer">
              <div className="h-2 w-2 rounded-full bg-indigo-400" />
              {topic}
            </div>
          ))}
          {topics.length === 0 && <span className="text-sm text-slate-400">All caught up!</span>}
        </div>
      </div>

      <button className="flex w-full items-center justify-between rounded-xl bg-gradient-to-r from-violet-600 to-indigo-600 px-6 py-3.5 text-sm font-semibold text-white shadow-md shadow-violet-500/20 transition-all duration-300 hover:shadow-lg hover:shadow-violet-500/40 hover:-translate-y-0.5">
        Continue Learning Path
        <ArrowRight className="h-4 w-4 transition-transform group-hover:translate-x-1" />
      </button>

    </div>
  );
}
