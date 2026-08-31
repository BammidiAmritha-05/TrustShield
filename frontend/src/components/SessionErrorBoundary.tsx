import React from 'react';
import { Shield, AlertTriangle, RefreshCw, ArrowLeft } from 'lucide-react';

interface ErrorBoundaryProps {
  children: React.ReactNode;
}

interface ErrorBoundaryState {
  hasError: boolean;
  error: Error | null;
}

export class SessionErrorBoundary extends React.Component<ErrorBoundaryProps, ErrorBoundaryState> {
  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, error: null };
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo): void {
    console.error('TrustShield SessionErrorBoundary caught:', error, errorInfo);
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="max-w-2xl mx-auto px-4 py-16 text-center">
          <div className="bg-slate-900 border border-rose-500/30 rounded-2xl p-8 shadow-xl">
            <div className="w-14 h-14 rounded-2xl bg-rose-500/20 border border-rose-500/40 flex items-center justify-center text-rose-400 mx-auto mb-6">
              <AlertTriangle className="w-7 h-7" />
            </div>
            <h2 className="text-xl font-bold text-white mb-2">
              TrustShield couldn't load this protection session.
            </h2>
            <p className="text-sm text-slate-400 mb-6">
              An unexpected error occurred while rendering the session view. This does not affect your backend data.
            </p>
            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => this.setState({ hasError: false, error: null })}
                className="bg-indigo-600 hover:bg-indigo-500 text-white px-5 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-2 transition-colors"
              >
                <RefreshCw className="w-4 h-4" /> Retry
              </button>
              <a
                href="/"
                className="bg-slate-800 hover:bg-slate-700 text-slate-200 px-5 py-2.5 rounded-xl font-semibold text-sm flex items-center gap-2 transition-colors border border-slate-700"
              >
                <ArrowLeft className="w-4 h-4" /> Back to Home
              </a>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
