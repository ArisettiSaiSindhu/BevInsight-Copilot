import React, { useState, useEffect } from 'react';
import { Sliders, Activity, TrendingUp, AlertTriangle } from 'lucide-react';

export default function DecisionSimulator() {
  const [simDiscount, setSimDiscount] = useState(0);
  const [simInventory, setSimInventory] = useState(0);
  const [simPromoWeeks, setSimPromoWeeks] = useState(0);
  const [simSalesDrop, setSimSalesDrop] = useState(0);
  const [simResult, setSimResult] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSimulate = async () => {
    setLoading(true);
    try {
      const res = await fetch(
        `/api/simulate?discount_change=${simDiscount}&inventory_change=${simInventory}&promo_weeks_change=${simPromoWeeks}&sales_drop_change=${simSalesDrop}`
      );
      const data = await res.json();
      setSimResult(data);
    } catch (err) {
      console.error('Simulation fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const delayDebounceFn = setTimeout(() => {
      handleSimulate();
    }, 400);
    return () => clearTimeout(delayDebounceFn);
  }, [simDiscount, simInventory, simPromoWeeks, simSalesDrop]);

  return (
    <div className="p-6 space-y-6">
      <div>
        <h2 className="text-xl font-bold tracking-tight">Scenario Decision Simulator</h2>
        <p className="text-xs text-slate-400 mt-0.5">Model adjustments in pricing, safety inventories, and promotional weeks to forecast outcomes.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-6">
        {/* Sliders */}
        <div className="md:col-span-5 glass-panel bg-slate-950/40 p-6 rounded-xl border border-white/5 space-y-6">
          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-white/5 pb-2">Simulation Parameters</h3>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400 font-bold">Promotional Discount Adjustments</span>
              <span className="text-teal-400 font-mono font-bold">{simDiscount >= 0 ? `+${simDiscount}` : simDiscount}%</span>
            </div>
            <input type="range" min="-15" max="25" value={simDiscount} onChange={(e) => setSimDiscount(parseFloat(e.target.value))} className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-teal-400" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400 font-bold">Safety Stock Levels</span>
              <span className="text-purple-400 font-mono font-bold">{simInventory >= 0 ? `+${simInventory}` : simInventory}%</span>
            </div>
            <input type="range" min="-10" max="40" value={simInventory} onChange={(e) => setSimInventory(parseFloat(e.target.value))} className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-purple-400" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400 font-bold">Promotional Extensions</span>
              <span className="text-blue-400 font-mono font-bold">{simPromoWeeks >= 0 ? `+${simPromoWeeks}` : simPromoWeeks} Weeks</span>
            </div>
            <input type="range" min="-4" max="6" value={simPromoWeeks} onChange={(e) => setSimPromoWeeks(parseInt(e.target.value))} className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-blue-400" />
          </div>

          <div className="space-y-2">
            <div className="flex justify-between text-xs">
              <span className="text-slate-400 font-bold">Market Demand Shifts</span>
              <span className="text-red-400 font-mono font-bold">{simSalesDrop >= 0 ? `+${simSalesDrop}` : simSalesDrop}%</span>
            </div>
            <input type="range" min="-30" max="15" value={simSalesDrop} onChange={(e) => setSimSalesDrop(parseFloat(e.target.value))} className="w-full h-1 bg-slate-800 rounded-lg appearance-none cursor-pointer accent-red-400" />
          </div>
        </div>

        {/* Forecast Display */}
        <div className="md:col-span-7 glass-panel bg-slate-950/60 p-6 rounded-xl border border-white/5 relative flex flex-col justify-between min-h-[300px]">
          {loading && (
            <div className="absolute inset-0 bg-slate-950/80 rounded-xl flex items-center justify-center z-10 backdrop-blur-sm">
              <div className="text-center">
                <div className="w-8 h-8 border-2 border-teal-400 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                <p className="text-xs text-slate-400">Recalculating forecast model...</p>
              </div>
            </div>
          )}

          <h3 className="text-xs font-bold uppercase tracking-wider text-slate-300 border-b border-white/5 pb-2">Forecasted Outcomes</h3>

          {simResult ? (
            <div className="space-y-6 mt-4">
              <div className="grid grid-cols-2 gap-4">
                <div className="bg-slate-900/50 p-4 border border-white/5 rounded-xl text-center">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Estimated Revenue Shift</span>
                  <strong className={`text-2xl font-extrabold block mt-2 ${simResult.simulated_metrics.revenue >= simResult.base_metrics.revenue ? 'text-emerald-400' : 'text-red-400'}`}>
                    {simResult.revenue_change}
                  </strong>
                </div>
                <div className="bg-slate-900/50 p-4 border border-white/5 rounded-xl text-center">
                  <span class="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Expected Volume Uplift</span>
                  <strong className={`text-2xl font-extrabold block mt-2 ${simResult.simulated_metrics.units_sold >= simResult.base_metrics.units_sold ? 'text-emerald-400' : 'text-red-400'}`}>
                    {simResult.sales_uplift}
                  </strong>
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div className="bg-slate-900/30 p-3 rounded-lg border border-white/5 text-center">
                  <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Stockouts</span>
                  <strong className="text-lg font-bold block text-slate-200 mt-1">{simResult.simulated_metrics.stockouts}</strong>
                </div>
                <div className="bg-slate-900/30 p-3 rounded-lg border border-white/5 text-center">
                  <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Inventory Risk</span>
                  <strong className={`text-lg font-bold block mt-1 ${simResult.inventory_risk === 'High' ? 'text-red-400' : (simResult.inventory_risk === 'Medium' ? 'text-amber-400' : 'text-emerald-400')}`}>
                    {simResult.inventory_risk}
                  </strong>
                </div>
                <div className="bg-slate-900/30 p-3 rounded-lg border border-white/5 text-center">
                  <span className="text-[9px] text-slate-400 font-bold uppercase tracking-wider block">Confidence</span>
                  <strong className="text-lg font-bold block text-blue-400 mt-1">{simResult.confidence}%</strong>
                </div>
              </div>
            </div>
          ) : (
            <div className="flex-grow flex items-center justify-center text-slate-500 text-xs">
              Recalculating forecast model parameters...
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
