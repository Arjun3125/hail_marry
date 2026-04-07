'use client';

import React from 'react';
import { Target, TrendingUp, AlertCircle, BookOpen } from 'lucide-react';

interface TopicMastery {
  topic: string;
  score: number;
  level: string;
  last_activity: string;
}

interface MasteryMapProps {
  masteryData: TopicMastery[];
  onFocusTopic?: (topic: string) => void;
}

export const MasteryMap: React.FC<MasteryMapProps> = ({ masteryData, onFocusTopic }) => {
  const getScoreColor = (score: number) => {
    if (score >= 80) return 'bg-emerald-500';
    if (score >= 50) return 'bg-amber-500';
    return 'bg-rose-500';
  };

  const getScoreText = (score: number) => {
    if (score >= 80) return 'text-emerald-400';
    if (score >= 50) return 'text-amber-400';
    return 'text-rose-400';
  };

  return (
    <div className="bg-[#1a1a1a]/80 backdrop-blur-xl border border-white/5 rounded-2xl p-6 shadow-2xl">
      <div className="flex items-center justify-between mb-6">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <Target className="w-5 h-5 text-indigo-400" />
          Mastery Insights
        </h3>
        <span className="text-xs text-white/40 bg-white/5 px-2 py-1 rounded-full uppercase tracking-wider font-medium">
          Live Tracking
        </span>
      </div>

      <div className="space-y-5">
        {masteryData.length > 0 ? (
          masteryData.map((item, idx) => (
            <div 
              key={idx}
              className="group cursor-pointer"
              onClick={() => onFocusTopic?.(item.topic)}
            >
              <div className="flex justify-between items-end mb-2">
                <div>
                  <p className="text-sm font-medium text-white/90 group-hover:text-indigo-300 transition-colors">
                    {item.topic}
                  </p>
                  <p className="text-[10px] text-white/40 uppercase tracking-tighter">
                    Last active {new Date(item.last_activity).toLocaleDateString()}
                  </p>
                </div>
                <span className={`text-sm font-bold tabular-nums ${getScoreText(item.score)}`}>
                  {Math.round(item.score)}%
                </span>
              </div>
              <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden">
                <div 
                  className={`h-full rounded-full transition-all duration-1000 ease-out ${getScoreColor(item.score)}`}
                  style={{ width: `${item.score}%` }}
                />
              </div>
            </div>
          ))
        ) : (
          <div className="py-8 flex flex-col items-center text-center">
            <div className="w-12 h-12 rounded-full bg-white/5 flex items-center justify-center mb-4">
              <BookOpen className="w-6 h-6 text-white/20" />
            </div>
            <p className="text-sm text-white/40 max-w-[200px]">
              Complete your first quiz or flashcard deck to see mastery data.
            </p>
          </div>
        )}
      </div>

      {masteryData.some(m => m.score < 50) && (
        <div className="mt-8 p-4 bg-rose-500/10 border border-rose-500/20 rounded-xl">
          <div className="flex gap-3">
             <AlertCircle className="w-5 h-5 text-rose-400 shrink-0" />
             <div>
               <p className="text-xs font-semibold text-rose-300 uppercase letter-spacing-wider">Critical Gap Detected</p>
	               <p className="text-xs text-rose-200/70 mt-1">
	                 You&apos;re struggling with {masteryData.find(m => m.score < 50)?.topic}. Try the &quot;Mastery Rebuild&quot; tool.
	               </p>
             </div>
          </div>
        </div>
      )}
      
      <button className="w-full mt-6 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-xs font-semibold text-white/80 transition-all flex items-center justify-center gap-2">
        <TrendingUp className="w-4 h-4" />
        View Full Analytics
      </button>
    </div>
  );
};
