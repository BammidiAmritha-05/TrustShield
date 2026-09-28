import React from 'react';
import {
  ActionGatePayload,
  ProtectionUpdatePayload,
  RecoveryPayload,
} from '../types/backend';
import {
  ShieldCheck,
  Check,
  X,
  Search,
  Flag,
  AlertTriangle,
} from 'lucide-react';

interface ActionGuidanceProps {
  protection: ProtectionUpdatePayload | null;
  actionGate: ActionGatePayload | null;
  recovery: RecoveryPayload | null;
}

export const ActionGuidance: React.FC<ActionGuidanceProps> = ({
  protection,
  actionGate,
  recovery,
}) => {
  if (!protection || protection.status !== 'available') {
    return null;
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
        <ShieldCheck className="w-5 h-5 text-indigo-400" />
        <h3 className="font-semibold text-slate-100">
          Human Safety & Intervention Guidance
        </h3>
      </div>

      <div className="space-y-3 text-sm">

        {actionGate && actionGate.status === 'available' && (
          <div className="bg-slate-950 p-4 rounded-xl border border-slate-800">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <Flag className="w-4 h-4" />
              Action Gate
            </span>

            <p className="text-lg text-slate-100 font-bold">
              {actionGate.gate_decision.replace(/_/g, ' ')}
            </p>

            {actionGate.reason && (
              <p className="text-xs text-slate-400 mt-2">
                {actionGate.reason}
              </p>
            )}

            <div className="flex flex-wrap gap-2 mt-3 text-xs">
              <span className="px-2 py-1 rounded bg-slate-800 text-slate-300">
                Proceed: {actionGate.can_proceed ? 'Yes' : 'No'}
              </span>

              <span className="px-2 py-1 rounded bg-slate-800 text-slate-300">
                Verification: {actionGate.requires_verification ? 'Required' : 'Not required'}
              </span>
            </div>
          </div>
        )}

        {protection.recommended_action && (
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block mb-1">
              Recommended Action
            </span>
            <p className="text-slate-200">
              {protection.recommended_action.replace(/_/g, ' ')}
            </p>
          </div>
        )}

        {protection.why && (
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span className="text-xs font-semibold text-indigo-400 uppercase tracking-wider block mb-1">
              Risk Rationale (WHY)
            </span>
            <p className="text-slate-200">{protection.why}</p>
          </div>
        )}

        {protection.do && (
          <div className="bg-emerald-950/20 border border-emerald-500/30 p-3 rounded-xl">
            <span className="text-xs font-semibold text-emerald-400 uppercase tracking-wider flex items-center gap-1.5 mb-1">
              <Check className="w-4 h-4" />
              Recommended Action (DO)
            </span>
            <p className="text-emerald-100 font-medium">
              {protection.do}
            </p>
          </div>
        )}

        {protection.do_not && (
          <div className="bg-rose-950/20 border border-rose-500/30 p-3 rounded-xl">
            <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5 mb-1">
              <X className="w-4 h-4" />
              Restricted Action (DO NOT)
            </span>
            <p className="text-rose-100 font-medium">
              {protection.do_not}
            </p>
          </div>
        )}

        {protection.verify && (
          <div className="bg-sky-950/20 border border-sky-500/30 p-3 rounded-xl">
            <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider flex items-center gap-1.5 mb-1">
              <Search className="w-4 h-4" />
              Verification Protocol (VERIFY)
            </span>
            <p className="text-sky-100 font-medium">
              {protection.verify}
            </p>
          </div>
        )}

        {protection.draft_verification_message && (
          <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wider block mb-1">
              Suggested Verification Message Draft
            </span>
            <p className="text-xs font-mono text-slate-300 bg-black/40 p-2.5 rounded border border-slate-800">
              "{protection.draft_verification_message}"
            </p>
          </div>
        )}

        {recovery &&
          recovery.status === 'available' &&
          recovery.recovery_required && (
          <div className="bg-amber-950/30 border border-amber-500/30 p-4 rounded-xl">
            <span className="text-xs font-semibold text-amber-400 uppercase tracking-wider flex items-center gap-1.5 mb-2">
              <AlertTriangle className="w-4 h-4" />
              Recovery Guidance
            </span>

            <h4 className="font-semibold text-amber-100 mb-2">
              {recovery.title}
            </h4>

            {recovery.recovery_required && (
              <div className="mb-3 text-xs text-amber-300 font-semibold">
                Severity: {recovery.severity}
              </div>
            )}

            <ol className="space-y-2 list-decimal list-inside text-sm text-slate-200">
              {recovery.steps.map((step, index) => (
                <li key={index}>{step}</li>
              ))}
            </ol>

            <div className="mt-3 text-xs text-slate-400">
              No external action was taken automatically.
            </div>
          </div>
        )}
      </div>
    </div>
  );
};