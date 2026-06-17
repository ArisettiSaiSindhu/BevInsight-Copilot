import React from 'react';
import { TrendingUp, Zap, AlertTriangle } from 'lucide-react';

export default function BusinessHealth({ health }) {
  if (!health) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <div className="glass-panel bg-gradient-to-br from-slate-950/60 to-slate-900/60 p-4 rounded-xl border border-white/5 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">WoW Growth Rate</span>
          <strong className="text-2xl font-extrabold block text-teal-400 mt-1">{health.growth_rate}</strong>
        </div>
        <TrendingUp className="w-8 h-8 text-teal-400/30" />
      </div>

      <div className="glass-panel bg-gradient-to-br from-slate-950/60 to-slate-900/60 p-4 rounded-xl border border-white/5 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Promotion Uplift</span>
          <strong className="text-2xl font-extrabold block text-purple-400 mt-1">{health.promo_uplift}</strong>
        </div>
        <Zap className="w-8 h-8 text-purple-400/30" />
      </div>

      <div className="glass-panel bg-gradient-to-br from-slate-950/60 to-slate-900/60 p-4 rounded-xl border border-white/5 flex items-center justify-between">
        <div>
          <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Aggregated Risk Score</span>
          <strong className="text-2xl font-extrabold block text-red-500 mt-1">{health.risk_score}</strong>
        </div>
        <AlertTriangle className="w-8 h-8 text-red-500/30" />
      </div>
    </div>
  );
}
