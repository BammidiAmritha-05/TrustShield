import React from 'react';
import { ProtectionUpdatePayload } from '../types/backend';
import { ShieldCheck, AlertOctagon, ArrowRight, Check, X, Search } from 'lucide-react';

interface ActionGuidanceProps {
  protection: ProtectionUpdatePayload | null;
}

export const ActionGuidance: React.FC<ActionGuidanceProps> = ({ protection }) => {
  if (!protection || protection.status !== 'available') {
    return null;
  }

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center gap-2 mb-4 border-b border-slate-800 pb-3">
        <ShieldCheck className="w-5 h-5 text-indigo-400" />
        <h3 className="font-semibold text-slate-100">Human Safety & Intervention Guidance</h3>
      </div>

      <div className="space-y-3 text-sm">
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
              <Check className="w-4 h-4 text-emerald-400" /> Recommended Action (DO)
            </span>
            <p className="text-emerald-100 font-medium">{protection.do}</p>
          </div>
        )}

        {protection.do_not && (
          <div className="bg-rose-950/20 border border-rose-500/30 p-3 rounded-xl">
            <span className="text-xs font-semibold text-rose-400 uppercase tracking-wider flex items-center gap-1.5 mb-1">
              <X className="w-4 h-4 text-rose-400" /> Restricted Action (DO NOT)
            </span>
            <p className="text-rose-100 font-medium">{protection.do_not}</p>
          </div>
        )}

        {protection.verify && (
          <div className="bg-sky-950/20 border border-sky-500/30 p-3 rounded-xl">
            <span className="text-xs font-semibold text-sky-400 uppercase tracking-wider flex items-center gap-1.5 mb-1">
              <Search className="w-4 h-4 text-sky-400" /> Verification Protocol (VERIFY)
            </span>
            <p className="text-sky-100 font-medium">{protection.verify}</p>
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
      </div>
    </div>
  );
};
