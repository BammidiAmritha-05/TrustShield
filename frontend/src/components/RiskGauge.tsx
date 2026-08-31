import React from 'react';
import { RiskUpdatePayload } from '../types/backend';
import { Shield, AlertTriangle, Info, CheckCircle2 } from 'lucide-react';

interface RiskGaugeProps {
  risk: RiskUpdatePayload | null;
}

export const RiskGauge: React.FC<RiskGaugeProps> = ({ risk }) => {
  if (!risk || risk.status !== 'available') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-slate-400">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-semibold text-slate-200 flex items-center gap-2">
            <Shield className="w-5 h-5 text-indigo-400" /> Multi-Turn Risk Assessment
          </h3>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">Awaiting Evidence</span>
        </div>
        <p className="text-xs text-slate-400">Risk accumulation engine ready. Monitoring stream...</p>
      </div>
    );
  }

  const score = risk.risk_index ?? 0;
  const level = risk.risk_level || 'LOW_RISK';
  const confidencePct = Math.round((risk.confidence ?? 1.0) * 100);

  const getRiskBadgeColor = (lvl: string) => {
    switch (lvl) {
      case 'HIGH_RISK':
      case 'CRITICAL_RISK':
        return 'bg-rose-500/20 text-rose-300 border-rose-500/40';
      case 'MODERATE_RISK':
        return 'bg-amber-500/20 text-amber-300 border-amber-500/40';
      case 'UNCERTAIN':
        return 'bg-slate-800 text-slate-300 border-slate-700';
      case 'LOW_RISK':
      default:
        return 'bg-emerald-500/20 text-emerald-300 border-emerald-500/40';
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Shield className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-slate-100">Hybrid Risk Engine</h3>
        </div>
        <div className="flex items-center gap-2">
          <span className={`text-xs font-semibold px-2.5 py-1 rounded-md border ${getRiskBadgeColor(level)}`}>
            {typeof level === 'string' ? level.replace(/_/g, ' ') : 'LOW RISK'}
          </span>
        </div>
      </div>

      {/* Score Bar */}
      <div className="mb-5">
        <div className="flex justify-between items-baseline mb-2">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold">Accumulated Risk Index</span>
          <span className="text-2xl font-bold mono text-white">
            {score} <span className="text-xs text-slate-500 font-normal">/ 100</span>
          </span>
        </div>
        <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden p-0.5 border border-slate-700">
          <div
            className={`h-full rounded-full transition-all duration-500 ${
              score >= 55 ? 'bg-rose-500' : score >= 25 ? 'bg-amber-500' : 'bg-emerald-500'
            }`}
            style={{ width: `${Math.min(score, 100)}%` }}
          />
        </div>
        <div className="flex justify-between text-[10px] text-slate-500 mt-1 font-mono">
          <span>0 (SAFE)</span>
          <span>25 (MODERATE)</span>
          <span>55 (HIGH)</span>
          <span>80 (CRITICAL)</span>
        </div>
      </div>

      {/* Confidence Pill */}
      <div className="flex items-center justify-between text-xs bg-slate-950 p-2.5 rounded-lg border border-slate-800/80 mb-4">
        <span className="text-slate-400">Engine Confidence:</span>
        <span className="font-semibold text-indigo-300 mono">{confidencePct}%</span>
      </div>

      {/* Explanation */}
      {risk.explanation && (
        <div className="mb-4 text-xs bg-indigo-950/30 border border-indigo-500/20 p-3 rounded-xl text-indigo-200">
          <div className="flex items-center gap-1.5 font-semibold text-indigo-400 mb-1">
            <Info className="w-3.5 h-3.5" /> Context Analysis
          </div>
          <p>{risk.explanation}</p>
        </div>
      )}

      {/* Contributing Signals */}
      {risk.contributing_signals && risk.contributing_signals.length > 0 && (
        <div className="mb-4">
          <span className="text-xs font-semibold text-slate-400 block mb-2">Contributing Evidence Signals</span>
          <div className="flex flex-wrap gap-1.5">
            {risk.contributing_signals.map((sig, idx) => {
              const name = sig.signal || sig.signal_name || 'Signal';
              const pts = Math.round(sig.points ?? sig.weight ?? 0);
              return (
                <span
                  key={idx}
                  className="text-[11px] px-2.5 py-1 rounded-md bg-slate-800 text-slate-300 border border-slate-700 font-mono"
                >
                  {name.replace(/_/g, ' ')} ({pts > 0 ? `+${pts}` : pts})
                </span>
              );
            })}
          </div>
        </div>
      )}

      {/* Policy Violations */}
      {risk.safety_policy_violations && risk.safety_policy_violations.length > 0 && (
        <div>
          <span className="text-xs font-semibold text-rose-400 block mb-2 flex items-center gap-1">
            <AlertTriangle className="w-3.5 h-3.5" /> Safety Policy Violations Triggered
          </span>
          <ul className="space-y-1 text-xs text-rose-300">
            {risk.safety_policy_violations.map((pol, idx) => {
              const label = typeof pol === 'string' ? pol : (pol.reason || pol.name || pol.policy_id || 'Policy violation triggered');
              const key = typeof pol === 'string' ? `${pol}-${idx}` : (pol.policy_id ? `${pol.policy_id}-${idx}` : `pol-${idx}`);
              return (
                <li key={key} className="flex items-start gap-1.5 bg-rose-950/40 p-2 rounded border border-rose-500/20">
                  <span className="text-rose-500">•</span> {label}
                </li>
              );
            })}
          </ul>
        </div>
      )}
    </div>
  );
};
