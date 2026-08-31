import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Shield, Clock, MessageSquare, Mic, ArrowRight, RefreshCw, AlertCircle } from 'lucide-react';
import { getSessions } from '../services/api';
import { SessionResponse } from '../types/backend';

export const HistoryPage: React.FC = () => {
  const [sessions, setSessions] = useState<SessionResponse[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchHistory = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getSessions();
      setSessions(data || []);
    } catch (err: any) {
      setError(err.message || 'Failed to load protection history');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchHistory();
  }, []);

  return (
    <div className="w-full max-w-4xl mx-auto px-3 sm:px-4 py-6 sm:py-10 space-y-6 sm:space-y-8">
      <div className="flex items-center justify-between border-b border-slate-800 pb-4 sm:pb-6">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 sm:w-10 sm:h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 flex-shrink-0">
            <Clock className="w-4 h-4 sm:w-5 sm:h-5" />
          </div>
          <div className="min-w-0">
            <h1 className="text-xl sm:text-2xl font-bold text-white truncate">Protection History</h1>
            <p className="text-xs text-slate-400 truncate">Recorded security sessions and verification outcomes</p>
          </div>
        </div>
        <button
          onClick={fetchHistory}
          disabled={loading}
          className="px-3 py-1.5 sm:py-2 rounded-xl bg-slate-900 border border-slate-800 hover:bg-slate-800 text-xs font-semibold text-slate-300 flex items-center gap-2 transition-colors disabled:opacity-50 flex-shrink-0"
        >
          <RefreshCw className={loading ? 'w-3.5 h-3.5 animate-spin' : 'w-3.5 h-3.5'} />
          <span className="hidden sm:inline">Refresh</span>
        </button>
      </div>

      {error && (
        <div className="p-3.5 sm:p-4 rounded-xl sm:rounded-2xl bg-rose-950/40 border border-rose-800/40 text-rose-300 text-xs flex items-center gap-2">
          <AlertCircle className="w-4 h-4 flex-shrink-0" />
          <span className="break-words">{error}</span>
        </div>
      )}

      {loading ? (
        <div className="space-y-3">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 sm:h-20 rounded-xl sm:rounded-2xl bg-slate-900/50 border border-slate-800 animate-pulse" />
          ))}
        </div>
      ) : sessions.length === 0 ? (
        <div className="text-center py-12 sm:py-16 bg-slate-900/40 border border-slate-800/80 rounded-2xl sm:rounded-3xl p-6 sm:p-8">
          <Shield className="w-10 h-10 sm:w-12 sm:h-12 text-slate-600 mx-auto mb-3 sm:mb-4" />
          <h3 className="text-sm sm:text-base font-semibold text-slate-200 mb-1">No Protection Sessions Yet</h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mb-5 sm:mb-6">
            Start a text or voice protection session from the home screen to analyze requests and claims in real-time.
          </p>
          <Link
            to="/"
            className="inline-flex items-center gap-2 px-4 py-2.5 rounded-xl bg-teal-600 hover:bg-teal-500 text-white text-xs font-semibold shadow-lg shadow-teal-900/20 transition-all"
          >
            Start Protection Session <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {sessions.map((sess) => {
            const isEnded = sess.status === 'ended';
            const isVoice = sess.interaction_type === 'voice';
            const dateLabel = sess.created_at ? new Date(sess.created_at).toLocaleString() : 'Unknown date';
            return (
              <Link
                key={sess.session_id}
                to={isEnded ? '/session/' + sess.session_id + '/summary' : '/session/' + sess.session_id}
                className="block bg-slate-900/80 text-slate-300 hover:bg-slate-900 border border-slate-800/80 hover:border-slate-700 rounded-xl sm:rounded-2xl p-3.5 sm:p-4 transition-all duration-200 group shadow-sm"
              >
                <div className="flex items-center justify-between gap-2">
                  <div className="flex items-center gap-2.5 sm:gap-3 min-w-0">
                    <div
                      className={
                        isVoice
                          ? 'w-8 h-8 sm:w-9 sm:h-9 rounded-xl flex items-center justify-center bg-sky-500/10 border border-sky-500/30 text-sky-400 flex-shrink-0'
                          : 'w-8 h-8 sm:w-9 sm:h-9 rounded-xl flex items-center justify-center bg-indigo-500/10 border border-indigo-500/30 text-indigo-400 flex-shrink-0'
                      }
                    >
                      {isVoice ? <Mic className="w-4 h-4" /> : <MessageSquare className="w-4 h-4" />}
                    </div>
                    <div className="min-w-0">
                      <div className="flex items-center gap-1.5 sm:gap-2 flex-wrap">
                        <span className="font-bold text-slate-100 text-xs sm:text-sm">#{sess.session_id.slice(0, 8)}</span>
                        <span className="text-[9px] sm:text-[10px] uppercase font-semibold px-1.5 sm:px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700">
                          {sess.interaction_type}
                        </span>
                        <span
                          className={
                            isEnded
                              ? 'text-[9px] sm:text-[10px] font-semibold px-1.5 sm:px-2 py-0.5 rounded bg-slate-800 text-slate-400 border border-slate-700'
                              : 'text-[9px] sm:text-[10px] font-semibold px-1.5 sm:px-2 py-0.5 rounded bg-emerald-500/10 text-emerald-300 border border-emerald-500/30'
                          }
                        >
                          {isEnded ? 'Completed' : 'Active'}
                        </span>
                      </div>
                      <span className="text-[11px] sm:text-xs text-slate-400 mt-0.5 block truncate">{dateLabel}</span>
                    </div>
                  </div>
                  <div className="flex items-center gap-2 sm:gap-3 flex-shrink-0">
                    <span className="text-xs text-slate-400 font-mono hidden md:inline-block">
                      {sess.event_count} events
                    </span>
                    <ArrowRight className="w-4 h-4 text-slate-500 group-hover:text-slate-300 group-hover:translate-x-0.5 transition-all" />
                  </div>
                </div>
              </Link>
            );
          })}
        </div>
      )}
    </div>
  );
};
