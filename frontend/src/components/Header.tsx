import React, { useEffect, useState } from 'react';
import { Shield, Activity, RefreshCw, CheckCircle2, AlertCircle } from 'lucide-react';
import { getHealth } from '../services/api';
import { HealthResponse } from '../types/backend';
import { Link } from 'react-router-dom';

export const Header: React.FC = () => {
  const [health, setHealth] = useState<HealthResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);

  const fetchStatus = async () => {
    setLoading(true);
    try {
      const data = await getHealth();
      setHealth(data);
    } catch (e) {
      setHealth(null);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStatus();
    const interval = setInterval(fetchStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  const isAllReady =
    health &&
    health.ai_readiness &&
    typeof health.ai_readiness === 'object' &&
    Object.values(health.ai_readiness).every((status) => status === 'READY');

  return (
    <header className="border-b border-slate-800 bg-slate-950/80 backdrop-blur sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-3 sm:px-6 lg:px-8 h-14 sm:h-16 flex items-center justify-between gap-2">
        {/* Brand Logo */}
        <Link to="/" className="flex items-center gap-2 sm:gap-3 group flex-shrink-0">
          <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-xl bg-teal-500/10 border border-teal-500/30 flex items-center justify-center text-teal-400 group-hover:border-teal-400 transition-colors flex-shrink-0">
            <Shield className="w-5 h-5 sm:w-6 sm:h-6" />
          </div>
          <div>
            <div className="flex items-center gap-1.5 sm:gap-2">
              <span className="font-bold text-base sm:text-lg tracking-tight text-white">TRUSTSHIELD</span>
              <span className="text-[9px] sm:text-[10px] font-semibold px-1.5 sm:px-2 py-0.5 rounded bg-teal-500/10 text-teal-300 border border-teal-500/20">
                ACTIVE
              </span>
            </div>
            <p className="text-[11px] text-slate-400 hidden sm:block">AI Security & Verification Engine</p>
          </div>
        </Link>

        {/* Center Nav Links (Desktop Only: hidden on mobile) */}
        <nav className="hidden md:flex items-center gap-1 sm:gap-2">
          <Link
            to="/"
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-900 transition-colors"
          >
            Protect
          </Link>
          <Link
            to="/history"
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-900 transition-colors"
          >
            History
          </Link>
          <Link
            to="/safety"
            className="px-3 py-1.5 rounded-lg text-xs font-semibold text-slate-300 hover:text-white hover:bg-slate-900 transition-colors"
          >
            Safety Center
          </Link>
        </nav>

        {/* Backend System Readiness Indicator */}
        <div className="flex items-center gap-2 sm:gap-4 flex-shrink-0">
          <div className="flex items-center gap-1.5 sm:gap-2 px-2.5 sm:px-3 py-1 sm:py-1.5 rounded-lg bg-slate-900 border border-slate-800 text-xs">
            <Activity className="w-3.5 h-3.5 text-slate-400 flex-shrink-0" />
            <span className="text-slate-400 hidden md:inline">System:</span>
            {loading ? (
              <span className="text-slate-400 flex items-center gap-1">
                <RefreshCw className="w-3 h-3 animate-spin" /> <span className="hidden sm:inline">Checking...</span>
              </span>
            ) : isAllReady ? (
              <span className="text-emerald-400 font-semibold flex items-center gap-1">
                <CheckCircle2 className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="hidden sm:inline">All AI Modules Ready</span>
                <span className="sm:hidden">Ready</span>
              </span>
            ) : health ? (
              <span className="text-amber-400 font-semibold flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="hidden sm:inline">Partial Readiness</span>
                <span className="sm:hidden">Partial</span>
              </span>
            ) : (
              <span className="text-rose-400 font-semibold flex items-center gap-1">
                <AlertCircle className="w-3.5 h-3.5 flex-shrink-0" />
                <span className="hidden sm:inline">Backend Offline</span>
                <span className="sm:hidden">Offline</span>
              </span>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
