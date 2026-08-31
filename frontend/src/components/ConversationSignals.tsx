import React from 'react';
import { SignalUpdatePayload } from '../types/backend';
import { MessageSquare, AlertOctagon, UserX, Zap, CheckCircle2 } from 'lucide-react';

interface ConversationSignalsProps {
  signals: SignalUpdatePayload | null;
}

export const ConversationSignals: React.FC<ConversationSignalsProps> = ({ signals }) => {
  if (!signals || signals.status !== 'available') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-slate-400">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-200 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-indigo-400" /> Conversation Signals
          </h3>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">NLP Ready</span>
        </div>
        <p className="text-xs text-slate-400">Conversation NLP pipeline ready. Waiting for transcript text...</p>
      </div>
    );
  }

  const manipulation = signals.manipulation;
  const activeTactics = manipulation
    ? Object.entries(manipulation)
        .filter(([_, active]) => active)
        .map(([key]) => key.replace(/_/g, ' '))
    : [];

  const impersonation = signals.impersonation;
  const requestedAction = signals.requested_action;
  const intent = signals.intent;

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-4 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-indigo-400" />
          <h3 className="font-semibold text-slate-100">Conversation Intelligence Signals</h3>
        </div>
        <span className="text-xs text-slate-400 font-mono">NLP Engine Active</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        {/* Intent & Requested Action */}
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Intent & Requested Action
          </span>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Detected Intent:</span>
              <span className="font-semibold text-slate-200">{typeof intent?.type === 'string' ? intent.type.replace(/_/g, ' ') : 'None'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Requested Action:</span>
              <span className="font-semibold text-amber-400">{typeof requestedAction?.type === 'string' ? requestedAction.type.replace(/_/g, ' ') : 'None'}</span>
            </div>
            {requestedAction?.sensitivity && (
              <div className="flex justify-between">
                <span className="text-slate-400">Action Sensitivity:</span>
                <span
                  className={`font-semibold ${
                    requestedAction.sensitivity === 'HIGH' || requestedAction.sensitivity === 'CRITICAL'
                      ? 'text-rose-400'
                      : 'text-slate-300'
                  }`}
                >
                  {requestedAction.sensitivity}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Impersonation Indicator */}
        <div className="bg-slate-950 p-3 rounded-xl border border-slate-800">
          <span className="text-[11px] font-semibold text-slate-400 uppercase tracking-wider block mb-1">
            Identity & Impersonation
          </span>
          <div className="space-y-1 text-xs">
            <div className="flex justify-between">
              <span className="text-slate-400">Claimed Identity:</span>
              <span className="font-semibold text-slate-200">{typeof impersonation?.claimed_identity === 'string' ? impersonation.claimed_identity.replace(/_/g, ' ') : 'Unclaimed'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-slate-400">Impersonation Flag:</span>
              <span className={`font-semibold ${impersonation?.possible_impersonation ? 'text-amber-400' : 'text-emerald-400'}`}>
                {impersonation?.possible_impersonation ? 'POSSIBLE IMPERSONATION' : 'UNVERIFIED / NORMAL'}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Active Manipulation Tactics Grid */}
      <div>
        <span className="text-xs font-semibold text-slate-400 block mb-2">Active Manipulation Tactics Detected</span>
        {activeTactics.length > 0 ? (
          <div className="flex flex-wrap gap-2">
            {activeTactics.map((tactic, idx) => (
              <span
                key={idx}
                className="text-xs px-3 py-1 rounded-lg bg-amber-500/20 text-amber-300 border border-amber-500/30 font-semibold uppercase tracking-wider flex items-center gap-1.5"
              >
                <Zap className="w-3.5 h-3.5 text-amber-400" />
                {tactic}
              </span>
            ))}
          </div>
        ) : (
          <div className="text-xs text-emerald-400 bg-emerald-950/30 border border-emerald-500/20 p-2.5 rounded-lg flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
            No psychological manipulation tactics detected in current turn.
          </div>
        )}
      </div>
    </div>
  );
};
