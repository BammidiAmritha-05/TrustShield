import React from 'react';
import { VoiceAnalysisPayload } from '../types/backend';
import { Mic, Volume2, AlertCircle, CheckCircle2, HelpCircle } from 'lucide-react';
import { normalizeVoiceScores } from '../utils/voice_score';

interface VoiceAuthenticityCardProps {
  voice: VoiceAnalysisPayload | null;
}

export const VoiceAuthenticityCard: React.FC<VoiceAuthenticityCardProps> = ({ voice }) => {
  if (!voice || voice.status !== 'available') {
    return (
      <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 text-slate-400">
        <div className="flex items-center justify-between mb-2">
          <h3 className="font-semibold text-slate-200 flex items-center gap-2">
            <Mic className="w-5 h-5 text-sky-400" /> Voice Authenticity Analysis
          </h3>
          <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400">AASIST-L Ready</span>
        </div>
        <p className="text-xs text-slate-400">
          Not enough audio evidence yet. Audio stream is analyzed for synthetic/spoofed voice characteristics once audio chunks are received.
        </p>
      </div>
    );
  }

  const { syntheticPercentage: synthPct, bonaFidePercentage: bonaPct, rawSyntheticScore } = normalizeVoiceScores(voice);

  const getQualityBadge = (q?: string) => {
    switch (q) {
      case 'GOOD':
      case 'good':
        return <span className="text-xs px-2 py-0.5 rounded bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 uppercase">GOOD SNR</span>;
      case 'LOW_SNR':
        return <span className="text-xs px-2 py-0.5 rounded bg-amber-500/20 text-amber-300 border border-amber-500/30 uppercase">LOW SNR</span>;
      case 'CLIPPED':
        return <span className="text-xs px-2 py-0.5 rounded bg-rose-500/20 text-rose-300 border border-rose-500/30 uppercase">CLIPPED</span>;
      case 'SHORT_DURATION':
        return <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700 uppercase">SHORT DURATION</span>;
      default:
        return null;
    }
  };

  return (
    <div className="bg-slate-900 border border-slate-800 rounded-2xl p-5 shadow-lg">
      <div className="flex items-center justify-between mb-3 border-b border-slate-800 pb-3">
        <div className="flex items-center gap-2">
          <Mic className="w-5 h-5 text-sky-400" />
          <h3 className="font-semibold text-slate-100">Voice Authenticity (AASIST-L)</h3>
        </div>
        {getQualityBadge(voice.quality)}
      </div>

      {/* Visual Indicator Bar */}
      <div className="mb-4">
        <div className="flex justify-between items-baseline mb-2 text-xs">
          <span className="text-slate-400">Bona Fide (Natural): <strong className="text-emerald-400 font-mono">{bonaPct}%</strong></span>
          <span className="text-slate-400">Synthetic Evidence: <strong className="text-rose-400 font-mono">{synthPct}%</strong></span>
        </div>
        <div className="h-3 w-full bg-slate-800 rounded-full overflow-hidden flex p-0.5 border border-slate-700">
          <div className="bg-emerald-500 h-full rounded-l-full transition-all duration-300" style={{ width: `${bonaPct}%` }} />
          <div className="bg-rose-500 h-full rounded-r-full transition-all duration-300" style={{ width: `${synthPct}%` }} />
        </div>
      </div>

      {/* Explanation Banner */}
      <div className="bg-slate-950 p-3 rounded-xl border border-slate-800 text-xs text-slate-300 flex items-start gap-2">
        <Volume2 className="w-4 h-4 text-sky-400 flex-shrink-0 mt-0.5" />
        <div>
          {rawSyntheticScore > 0.5 ? (
            <p className="text-amber-300">
              Acoustic analysis indicates <strong>possible synthetic / spoofed voice characteristics</strong>. Exercise caution regarding unverified identity claims.
            </p>
          ) : (
            <p className="text-emerald-300">
              Acoustic analysis shows <strong>natural voice characteristics</strong> (Bona Fide).
            </p>
          )}
          <span className="text-[10px] text-slate-500 block mt-1">
            Note: Voice authenticity score represents acoustic evidence only and does NOT equal scam probability.
          </span>
        </div>
      </div>
    </div>
  );
};
