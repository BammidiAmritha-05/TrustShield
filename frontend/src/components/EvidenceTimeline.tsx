import React from 'react';
import { TimelineTurn, RiskLevel } from '../types/backend';
import { Clock, ShieldAlert, ShieldCheck } from 'lucide-react';

interface EvidenceTimelineProps {
  timeline: TimelineTurn[];
}

export const EvidenceTimeline: React.FC<EvidenceTimelineProps> = ({ timeline }) => {
  if (!timeline || timeline.length === 0) {
    return null;
  }

  const formatRiskLevel = (riskLevel?: string | null, index?: number | null) => {
    if (riskLevel && typeof riskLevel === 'string') {
      return riskLevel.replace(/_/g, ' ');
    }
    if (typeof index === 'number') {
      if (index >= 75) return 'HIGH RISK';
      if (index >= 40) return 'CAUTION';
      return 'SAFE';
    }
    return 'SAFE';
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
        <Clock className="w-5 h-5 text-indigo-400" />
        <h3 className="font-semibold text-slate-100">Temporal Evidence Progression</h3>
      </div>

      <div className="space-y-3 relative before:absolute before:inset-0 before:left-3.5 before:w-0.5 before:bg-slate-800">
        {timeline.map((turn, index) => {
          const turnNumber = turn.turn_number ?? turn.turn_index ?? index + 1;
          const riskIndex = turn.risk_index ?? turn.temporal_risk ?? turn.instantaneous_risk ?? 0;
          const resolvedLevel: RiskLevel = turn.risk_level ?? (riskIndex >= 75 ? 'HIGH_RISK' : riskIndex >= 40 ? 'MODERATE_RISK' : 'LOW_RISK');
          const isHighRisk = resolvedLevel === 'HIGH_RISK' || resolvedLevel === 'CRITICAL_RISK';
          const isModerate = resolvedLevel === 'MODERATE_RISK';
          const timestampLabel = turn.timestamp ? new Date(turn.timestamp).toLocaleTimeString() : undefined;

          return (
            <div key={`${turnNumber}-${index}`} className="flex items-start gap-4 relative z-10 pl-2">
              <div
                className={`w-4 h-4 rounded-full border-2 flex-shrink-0 mt-1 ${
                  isHighRisk
                    ? 'bg-rose-600 border-rose-400'
                    : isModerate
                    ? 'bg-amber-600 border-amber-400'
                    : 'bg-emerald-600 border-emerald-400'
                }`}
              />
              <div className="flex-1 bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs">
                <div className="flex justify-between items-center mb-1">
                  <span className="font-bold text-slate-200">Turn {turnNumber}</span>
                  <span className="text-[10px] text-slate-500 font-mono">{timestampLabel}</span>
                </div>
                <div className="flex justify-between items-center text-slate-300">
                  <span>
                    Risk Level:{' '}
                    <strong className={isHighRisk ? 'text-rose-400' : isModerate ? 'text-amber-400' : 'text-emerald-400'}>
                      {formatRiskLevel(resolvedLevel, riskIndex)}
                    </strong>
                  </span>
                  <span className="font-mono text-slate-400">Index: {riskIndex} / 100</span>
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};
