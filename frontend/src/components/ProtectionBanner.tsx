import React from 'react';
import {
  ProtectionLevel,
  ProtectionUpdatePayload,
  ActionGateDecision,
  ActionGatePayload,
  RecoveryPayload,
} from '../types/backend';
import { ShieldCheck, AlertTriangle, ShieldAlert, AlertOctagon, HelpCircle, Flag } from 'lucide-react';

interface ProtectionBannerProps {
  protection: ProtectionUpdatePayload | null;
  actionGate?: ActionGatePayload | null;
  recovery?: RecoveryPayload | null;
}

export const ProtectionBanner: React.FC<ProtectionBannerProps> = ({
  protection,
  actionGate,
  recovery,
}) => {
  if (!protection || protection.status !== 'available') {
    return (
      <div className="bg-slate-900/60 border border-slate-800 rounded-2xl p-6 flex items-center gap-4 text-slate-400">
        <HelpCircle className="w-8 h-8 text-slate-500 flex-shrink-0" />
        <div>
          <h3 className="font-semibold text-slate-200">Protection Engine Initializing</h3>
          <p className="text-sm text-slate-400">
            Monitoring conversation stream for suspicious patterns, urgent requests, and unverifiable claims...
          </p>
        </div>
      </div>
    );
  }

  const level: ProtectionLevel = protection.protection_level || 'SAFE';

  const getStyle = (lvl: ProtectionLevel) => {
    switch (lvl) {
      case 'HIGH_RISK':
      case 'SUSPICIOUS':
        return {
          bg: 'bg-rose-950/80 border-rose-600/60 text-rose-100',
          badge: 'bg-rose-600 text-white',
          icon: <ShieldAlert className="w-9 h-9 text-rose-400 flex-shrink-0" />,
        };
      case 'CAUTION':
        return {
          bg: 'bg-amber-950/80 border-amber-600/60 text-amber-100',
          badge: 'bg-amber-600 text-white',
          icon: <AlertTriangle className="w-9 h-9 text-amber-400 flex-shrink-0" />,
        };
      case 'UNCERTAIN':
        return {
          bg: 'bg-slate-900 border-slate-700 text-slate-200',
          badge: 'bg-slate-700 text-slate-200',
          icon: <HelpCircle className="w-9 h-9 text-slate-400 flex-shrink-0" />,
        };
      case 'SAFE':
      default:
        return {
          bg: 'bg-emerald-950/80 border-emerald-600/60 text-emerald-100',
          badge: 'bg-emerald-600 text-white',
          icon: <ShieldCheck className="w-9 h-9 text-emerald-400 flex-shrink-0" />,
        };
    }
  };

  const getActionGateStyle = (gate: ActionGateDecision) => {
    switch (gate) {
      case 'BLOCK_AND_VERIFY':
        return {
          bg: 'bg-rose-950/50 border-rose-500/40',
          text: 'text-rose-100',
          icon: <Flag className="w-6 h-6 text-rose-400" />,
        };

      case 'PAUSE_AND_VERIFY':
        return {
          bg: 'bg-amber-950/50 border-amber-500/40',
          text: 'text-amber-100',
          icon: <AlertTriangle className="w-6 h-6 text-amber-400" />,
        };

      case 'HOLD_FOR_VERIFICATION':
        return {
          bg: 'bg-sky-950/50 border-sky-500/40',
          text: 'text-sky-100',
          icon: <ShieldCheck className="w-6 h-6 text-sky-400" />,
        };

      case 'WARN':
        return {
          bg: 'bg-yellow-950/50 border-yellow-500/40',
          text: 'text-yellow-100',
          icon: <AlertTriangle className="w-6 h-6 text-yellow-400" />,
        };

      case 'ALLOW':
      default:
        return {
          bg: 'bg-emerald-950/50 border-emerald-500/40',
          text: 'text-emerald-100',
          icon: <ShieldCheck className="w-6 h-6 text-emerald-400" />,
        };
    }
  };

  const style = getStyle(level);

  return (
    <div
      role="region"
      aria-live="polite"
      aria-label="Safety Protection Guidance"
      className={`border rounded-2xl p-6 transition-all duration-300 shadow-xl ${style.bg}`}
    >
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4 border-b border-white/10 pb-4 mb-4">
        <div className="flex items-center gap-4">
          {style.icon}
          <div>
            <div className="flex items-center gap-3">
              <span className={`text-xs font-bold uppercase tracking-wider px-2.5 py-1 rounded-md ${style.badge}`}>
                {typeof level === 'string' ? level.replace(/_/g, ' ') : 'SAFE'}
              </span>
              <h2 className="text-xl font-bold text-white">
                {typeof protection.recommended_action === 'string' ? protection.recommended_action.replace(/_/g, ' ') : 'NO ACTION REQUIRED'}
              </h2>
            </div>
            {protection.why && <p className="text-sm text-slate-300 mt-1">{protection.why}</p>}
          </div>
        </div>

        {protection.user_confirmation_required && (
          <div className="px-3 py-1.5 rounded-lg bg-black/40 border border-white/10 text-xs font-medium text-amber-300 flex items-center gap-1.5 self-start md:self-auto">
            <AlertOctagon className="w-4 h-4 text-amber-400" />
            Human User Confirmation Required
          </div>
        )}
      </div>

      {/* Guidance Grid */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
        {protection.do && (
          <div className="bg-black/30 border border-emerald-500/20 rounded-xl p-4">
            <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider block mb-1">
              ✓ Recommended Action (DO)
            </span>
            <p className="text-slate-200">{protection.do}</p>
          </div>
        )}

        {protection.do_not && (
          <div className="bg-black/30 border border-rose-500/20 rounded-xl p-4">
            <span className="text-xs font-bold text-rose-400 uppercase tracking-wider block mb-1">
              ✕ Restricted Action (DO NOT)
            </span>
            <p className="text-slate-200">{protection.do_not}</p>
          </div>
        )}

        {protection.verify && (
          <div className="bg-black/30 border border-sky-500/20 rounded-xl p-4">
            <span className="text-xs font-bold text-sky-400 uppercase tracking-wider block mb-1">
              🔍 Verification Step
            </span>
            <p className="text-slate-200">{protection.verify}</p>
          </div>
        )}
      </div>

      {/* Action Gate Section */}
      {actionGate && actionGate.status === 'available' && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div
            className={`border rounded-xl p-4 ${
              getActionGateStyle(actionGate.gate_decision).bg
            }`}
          >
            <div className="flex items-center gap-3 mb-3">
              {getActionGateStyle(actionGate.gate_decision).icon}

              <div>
                <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-0.5">
                  ACTION GATE
                </span>

                <span
                  className={`text-lg font-bold ${
                    getActionGateStyle(actionGate.gate_decision).text
                  }`}
                >
                  {actionGate.gate_decision.replace(/_/g, ' ')}
                </span>
              </div>
            </div>

            {actionGate.recommended_action && (
              <div className="mt-3 text-sm">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  RECOMMENDED ACTION
                </span>

                <p className={getActionGateStyle(actionGate.gate_decision).text}>
                  {actionGate.recommended_action.replace(/_/g, ' ')}
                </p>
              </div>
            )}

            {actionGate.reason && (
              <div className="mt-3 text-sm">
                <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
                  REASON
                </span>

                <p className="text-slate-200">
                  {actionGate.reason}
                </p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Recovery Section */}
      {recovery && recovery.status === 'available' && recovery.recovery_required && (
        <div className="mt-4 pt-4 border-t border-white/10">
          <div className="border rounded-xl p-4 bg-slate-950/50 border-slate-600/40">
            <div className="mb-3">
              <span className="text-xs font-bold uppercase tracking-wider text-slate-400 block mb-1">
                RECOVERY GUIDANCE
              </span>

              <h3 className="text-lg font-bold text-white">
                {recovery.title}
              </h3>

              <p className="text-sm text-slate-400 mt-1">
                Severity: {recovery.severity}
              </p>
            </div>

            <div className="space-y-2">
              {recovery.steps.map((step, index) => (
                <div key={index} className="flex gap-3 text-sm">
                  <span className="text-slate-400 font-semibold">
                    {index + 1}.
                  </span>

                  <p className="text-slate-200">
                    {step}
                  </p>
                </div>
              ))}
            </div>

            {!recovery.external_action_taken && (
              <p className="text-xs text-slate-400 mt-4">
                TrustShield has not taken any external recovery action.
              </p>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

