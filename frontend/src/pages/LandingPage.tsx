import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, Mic, MessageSquare, ArrowRight, CheckCircle2, Lock, FileCheck } from 'lucide-react';
import { useSession } from '../context/SessionContext';
import { InteractionType } from '../types/backend';

export const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const { startNewSession } = useSession();

  const [interactionType, setInteractionType] = useState<InteractionType>('text');
  const [consent, setConsent] = useState<boolean>(false);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleStartSession = async () => {
    if (!consent) return;
    setLoading(true);
    setError(null);

    try {
      const newSession = await startNewSession(interactionType, consent);
      navigate(`/session/${newSession.session_id}`);
    } catch (e: any) {
      setError(e.message || 'Failed to initialize session');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="w-full max-w-4xl mx-auto px-3 sm:px-4 py-8 sm:py-12">
      {/* Hero Section */}
      <div className="text-center mb-8 sm:mb-12">
        <div className="inline-flex items-center gap-2 px-3 py-1 sm:px-3.5 sm:py-1.5 rounded-full bg-teal-500/10 border border-teal-500/30 text-teal-300 text-[11px] sm:text-xs font-semibold mb-4 sm:mb-6">
          <Shield className="w-3.5 h-3.5 sm:w-4 sm:h-4 text-teal-400 flex-shrink-0" /> Active Security & Verification Layer
        </div>
        <h1 className="text-2xl sm:text-4xl md:text-5xl font-extrabold tracking-tight text-white mb-3 sm:mb-4 leading-tight">
          Pause, verify, and stay safe before taking sensitive actions.
        </h1>
        <p className="text-xs sm:text-base md:text-lg text-slate-400 max-w-2xl mx-auto leading-relaxed px-1">
          Real-time multi-modal protection analyzing voice authenticity, coercion patterns, multi-turn risk, and official welfare scheme claims.
        </p>
      </div>

      {/* Main Configuration Card */}
      <div className="bg-slate-900/90 border border-slate-800 rounded-2xl sm:rounded-3xl p-4 sm:p-6 md:p-8 shadow-2xl mb-8 sm:mb-12">
        <h2 className="text-base sm:text-lg font-bold text-white mb-4 sm:mb-6 flex items-center gap-2">
          Start Protection Session
        </h2>

        {error && (
          <div className="mb-4 sm:mb-6 p-3 sm:p-4 rounded-xl sm:rounded-2xl bg-rose-950/60 border border-rose-600/40 text-rose-200 text-xs">
            {error}
          </div>
        )}

        {/* Mode Selector */}
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 sm:gap-4 mb-6 sm:mb-8">
          <button
            type="button"
            onClick={() => setInteractionType('text')}
            className={`p-4 sm:p-6 rounded-xl sm:rounded-2xl border text-left transition-all ${
              interactionType === 'text'
                ? 'bg-teal-950/40 border-teal-500 text-white shadow-lg shadow-teal-950/30'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 mb-3 sm:mb-4">
              <MessageSquare className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <h3 className="font-bold text-sm sm:text-base text-slate-100 mb-1">Text Message Protection</h3>
            <p className="text-[11px] sm:text-xs text-slate-400 leading-relaxed">
              Analyze suspicious text messages, payment requests, lottery claims, or bank SMS alerts.
            </p>
          </button>

          <button
            type="button"
            onClick={() => setInteractionType('voice')}
            className={`p-4 sm:p-6 rounded-xl sm:rounded-2xl border text-left transition-all ${
              interactionType === 'voice'
                ? 'bg-teal-950/40 border-teal-500 text-white shadow-lg shadow-teal-950/30'
                : 'bg-slate-950 border-slate-800 text-slate-400 hover:border-slate-700'
            }`}
          >
            <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-sky-500/10 border border-sky-500/30 flex items-center justify-center text-sky-400 mb-3 sm:mb-4">
              <Mic className="w-4 h-4 sm:w-5 sm:h-5" />
            </div>
            <h3 className="font-bold text-sm sm:text-base text-slate-100 mb-1">Voice Call Protection</h3>
            <p className="text-[11px] sm:text-xs text-slate-400 leading-relaxed">
              Stream live call audio for AASIST-L voice authenticity, Whisper transcription, and real-time guidance.
            </p>
          </button>
        </div>

        {/* Consent Checkbox */}
        <div className="bg-slate-950 p-3.5 sm:p-4 rounded-xl sm:rounded-2xl border border-slate-800 mb-6 sm:mb-8 flex items-start gap-2.5 sm:gap-3">
          <input
            type="checkbox"
            id="consent"
            checked={consent}
            onChange={(e) => setConsent(e.target.checked)}
            className="mt-1 w-4 h-4 rounded border-slate-700 text-teal-600 focus:ring-teal-500 bg-slate-900 flex-shrink-0"
          />
          <label htmlFor="consent" className="text-[11px] sm:text-xs text-slate-300 leading-relaxed cursor-pointer select-none">
            <strong className="text-white font-semibold block mb-0.5">Explicit User Consent Required</strong>
            I grant explicit consent to start a protection session. Audio and text streams will be processed strictly in-memory per session turn and evaluated against official verification registries.
          </label>
        </div>

        {/* CTA Button */}
        <button
          type="button"
          onClick={handleStartSession}
          disabled={!consent || loading}
          className="w-full py-3.5 sm:py-4 rounded-xl sm:rounded-2xl bg-teal-600 hover:bg-teal-500 disabled:opacity-50 disabled:cursor-not-allowed text-white font-bold text-xs sm:text-sm tracking-wide flex items-center justify-center gap-2 transition-all shadow-xl shadow-teal-900/30"
        >
          {loading ? 'Initializing Session...' : 'Start Protection Session'}
          <ArrowRight className="w-4 h-4" />
        </button>
      </div>

      {/* Feature Highlights Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6 text-xs">
        <div className="bg-slate-900/70 border border-slate-800/80 p-5 rounded-2xl">
          <div className="w-8 h-8 rounded-lg bg-teal-500/10 border border-teal-500/20 text-teal-400 flex items-center justify-center mb-3">
            <Shield className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-slate-200 mb-1">Human-Centered Invariants</h4>
          <p className="text-slate-400 leading-relaxed">
            Zero autonomous execution. Explicit human confirmation required for all safe intervention guidance.
          </p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800/80 p-5 rounded-2xl">
          <div className="w-8 h-8 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 flex items-center justify-center mb-3">
            <FileCheck className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-slate-200 mb-1">Tier-1 Official Verification</h4>
          <p className="text-slate-400 leading-relaxed">
            Claims verified against official government registries (.gov.in) and institutional bank policies (bank.sbi).
          </p>
        </div>

        <div className="bg-slate-900/70 border border-slate-800/80 p-5 rounded-2xl">
          <div className="w-8 h-8 rounded-lg bg-sky-500/10 border border-sky-500/20 text-sky-400 flex items-center justify-center mb-3">
            <Lock className="w-4 h-4" />
          </div>
          <h4 className="font-bold text-slate-200 mb-1">Local & Memory-Only</h4>
          <p className="text-slate-400 leading-relaxed">
            Temporary audio and text processing is purged immediately upon session completion.
          </p>
        </div>
      </div>
    </div>
  );
};
