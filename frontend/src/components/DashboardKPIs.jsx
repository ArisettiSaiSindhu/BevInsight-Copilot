import React from 'react';
import { DollarSign, ShoppingBag, Percent, Award, Map, AlertTriangle, TrendingUp } from 'lucide-react';

export default function DashboardKPIs({ kpis }) {
  if (!kpis) return null;

  return (
    <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
      {/* KPI 1 */}
      <div className="glass-panel bg-slate-950/40 p-4 rounded-xl border border-white/5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Total Revenue</span>
        <strong className="text-xl font-extrabold mt-1 block">
          ${kpis.total_revenue.toLocaleString(undefined, { minimumFractionDigits: 2 })}
        </strong>
        <span className="text-[10px] text-emerald-400 flex items-center gap-1 mt-1">
          <TrendingUp className="w-3 h-3" /> +11.4% WoW
        </span>
      </div>

      {/* KPI 2 */}
      <div className="glass-panel bg-slate-950/40 p-4 rounded-xl border border-white/5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Units Sold</span>
        <strong className="text-xl font-extrabold mt-1 block">
          {kpis.total_units_sold.toLocaleString()}
        </strong>
        <span className="text-[10px] text-slate-500 mt-1 block">Bottles / Cans</span>
      </div>

      {/* KPI 3 */}
      <div className="glass-panel bg-slate-950/40 p-4 rounded-xl border border-white/5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Promo Revenue Share</span>
        <strong className="text-xl font-extrabold mt-1 block">{kpis.promo_revenue_pct}%</strong>
        <span className="text-[10px] text-slate-500 mt-1 block">of gross turnover</span>
      </div>

      {/* KPI 4 */}
      <div className="glass-panel bg-slate-950/40 p-4 rounded-xl border border-white/5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Top Brand</span>
        <strong className="text-sm font-bold mt-2 truncate block">{kpis.top_product}</strong>
        <span className="text-[10px] text-slate-500 block">Category leader</span>
      </div>

      {/* KPI 5 */}
      <div className="glass-panel bg-slate-950/40 p-4 rounded-xl border border-white/5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Top Region</span>
        <strong className="text-xl font-extrabold mt-1 block">{kpis.top_region}</strong>
        <span className="text-[10px] text-slate-500 mt-1 block">South runner-up</span>
      </div>

      {/* KPI 6 */}
      <div className="glass-panel bg-slate-950/40 p-4 rounded-xl border border-white/5">
        <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Inventory Risks</span>
        <strong className="text-xl font-extrabold mt-1 text-red-500 block">{kpis.inventory_risk_count}</strong>
        <span className="text-[10px] text-red-400 mt-1 block font-medium">Critical Stockouts</span>
      </div>
    </div>
  );
}
