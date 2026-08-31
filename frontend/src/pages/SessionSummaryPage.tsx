import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useSession } from '../context/SessionContext';
import { Shield, Clock, ShieldCheck, ShieldAlert, FileCheck, Mic, ArrowLeft, RefreshCw } from 'lucide-react';
import { normalizeVoiceScores } from '../utils/voice_score';

export const SessionSummaryPage: React.FC = () => {
  const { sessionId } = useParams<{ sessionId: string }>();
  const {
    session,
    risk,
    protection,
    claimVerification,
    voiceAuthenticity,
    signals,
    timeline,
    resetSessionState,
  } = useSession();

  const finalLevel = protection?.protection_level || risk?.risk_level || 'SAFE';
  const finalRiskIndex = risk?.risk_index ?? 0;

  return (
    <div className="w-full max-w-4xl mx-auto px-3 sm:px-4 py-6 sm:py-10 space-y-6 sm:space-y-8">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-slate-800 pb-4 sm:pb-6">
        <div>
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 flex-shrink-0">
              <Shield className="w-5 h-5 sm:w-6 sm:h-6" />
            </div>
            <div className="min-w-0">
              <h1 className="text-xl sm:text-2xl font-bold text-white truncate">Session Protection Summary</h1>
              <p className="text-xs text-slate-400 truncate">Session ID: #{sessionId}</p>
            </div>
          </div>
        </div>

        <Link
          to="/"
          onClick={resetSessionState}
          className="self-start sm:self-auto bg-slate-900 hover:bg-slate-800 border border-slate-700 text-slate-200 px-3.5 sm:px-4 py-2 sm:py-2.5 rounded-xl text-xs font-semibold flex items-center gap-2 transition-all shadow-sm"
        >
          <ArrowLeft className="w-4 h-4" /> Start New Session
        </Link>
      </div>

      {/* Overview Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 sm:gap-4">
        <div className="bg-slate-900/80 border border-slate-800 p-4 sm:p-5 rounded-xl sm:rounded-2xl">
          <span className="text-[11px] sm:text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
            Final Protection Level
          </span>
          <span className="text-lg sm:text-xl font-bold text-white uppercase">
            {typeof finalLevel === 'string' ? finalLevel.replace(/_/g, ' ') : 'SAFE'}
          </span>
        </div>

        <div className="bg-slate-900/80 border border-slate-800 p-4 sm:p-5 rounded-xl sm:rounded-2xl">
          <span className="text-[11px] sm:text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
            Accumulated Risk Index
          </span>
          <span className="text-xl font-bold text-indigo-400 mono">
            {finalRiskIndex} <span className="text-xs text-slate-500 font-normal">/ 100</span>
          </span>
        </div>

        <div className="bg-slate-900 border border-slate-800 p-5 rounded-2xl">
          <span className="text-xs text-slate-400 uppercase tracking-wider font-semibold block mb-1">
            Interaction Type
          </span>
          <span className="text-xl font-bold text-slate-200 capitalize">
            {session?.interaction_type || 'Voice / Text'} Mode
          </span>
        </div>
      </div>

      {/* Recommended Action Summary */}
      {protection && (
        <div className="bg-slate-900/80 border border-slate-800 rounded-2xl p-6 space-y-4 shadow-xl">
          <h2 className="text-base font-bold text-white flex items-center gap-2 border-b border-slate-800 pb-3">
            <ShieldCheck className="w-5 h-5 text-teal-400" /> Final Safety & Action Recommendation
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 text-xs">
            {protection.do && (
              <div className="bg-emerald-950/30 border border-emerald-500/20 p-4 rounded-xl">
                <span className="font-bold text-emerald-400 uppercase tracking-wider block mb-1">Recommended Action (DO)</span>
                <p className="text-slate-200">{protection.do}</p>
              </div>
            )}

            {protection.do_not && (
              <div className="bg-rose-950/30 border border-rose-500/20 p-4 rounded-xl">
                <span className="font-bold text-rose-400 uppercase tracking-wider block mb-1">Restricted Action (DO NOT)</span>
                <p className="text-slate-200">{protection.do_not}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Claim Verification & Voice Authenticity Summary */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Claim Summary */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <h3 className="font-bold text-white text-sm flex items-center gap-2 border-b border-slate-800 pb-3">
            <FileCheck className="w-4 h-4 text-emerald-400" /> Claim Verification Summary
          </h3>
          {claimVerification && claimVerification.status === 'available' ? (
            <div className="text-xs space-y-2">
              <div className="flex justify-between">
                <span className="text-slate-400">Entity:</span>
                <span className="font-semibold text-slate-200">{claimVerification.entity?.name || 'None'}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Verification Status:</span>
                <span className="font-bold text-emerald-400">{claimVerification.verification?.overall_status}</span>
              </div>
              {claimVerification.sources && claimVerification.sources.length > 0 && (
                <div className="pt-2 border-t border-slate-800">
                  <span className="text-slate-400 block mb-1">Verified Official Source:</span>
                  <a
                    href={claimVerification.sources[0].url}
                    target="_blank"
                    rel="noreferrer"
                    className="text-sky-400 font-mono underline"
                  >
                    {claimVerification.sources[0].url}
                  </a>
                </div>
              )}
            </div>
          ) : (
            <p className="text-xs text-slate-500">No verifiable claims were evaluated during this session.</p>
          )}
        </div>

        {/* Voice Authenticity Summary */}
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-3">
          <h3 className="font-bold text-white text-sm flex items-center gap-2 border-b border-slate-800 pb-3">
            <Mic className="w-4 h-4 text-sky-400" /> Voice Authenticity Summary
          </h3>
          {voiceAuthenticity && voiceAuthenticity.status === 'available' ? (
            (() => {
              const { syntheticPercentage, bonaFidePercentage } = normalizeVoiceScores(voiceAuthenticity);
              return (
                <div className="text-xs space-y-2">
                  <div className="flex justify-between">
                    <span className="text-slate-400">Synthetic Voice Evidence:</span>
                    <span className="font-bold text-rose-400 font-mono">
                      {syntheticPercentage}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-slate-400">Bona Fide (Natural):</span>
                    <span className="font-bold text-emerald-400 font-mono">
                      {bonaFidePercentage}%
                    </span>
                  </div>
                </div>
              );
            })()
          ) : (
            <p className="text-xs text-slate-500">No audio stream voice analysis was performed for this session.</p>
          )}
        </div>
      </div>

      {/* Temporal Timeline */}
      {timeline.length > 0 && (
        <div className="bg-slate-900 border border-slate-800 rounded-2xl p-6 space-y-4">
          <h3 className="font-bold text-white text-sm border-b border-slate-800 pb-3">
            Temporal Progression Log
          </h3>
          <div className="space-y-2 text-xs">
            {timeline.map((turn, index) => {
              const turnNumber = turn.turn_number ?? turn.turn_index ?? index + 1;
              const riskLevel = turn.risk_level ?? 'UNKNOWN';
              const formattedRiskLevel = typeof riskLevel === 'string' ? riskLevel.replace(/_/g, ' ') : 'UNKNOWN';
              const riskIndex = turn.risk_index ?? turn.instantaneous_risk ?? 0;

              return (
                <div key={`${turnNumber}-${index}`} className="flex justify-between items-center bg-slate-950 p-3 rounded-xl border border-slate-800">
                  <span className="font-semibold text-slate-300">Turn #{turnNumber}</span>
                  <span className="text-slate-400 font-mono">Risk Level: {formattedRiskLevel} ({riskIndex}/100)</span>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};
